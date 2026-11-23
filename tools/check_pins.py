"""Find pinned libraries whose newer releases on PyPI can install on the course's Python.

  python tools/check_pins.py            # every requirements file in site/downloads
  python tools/check_pins.py --strict   # exit 1 if any pin can move up (the weekly workflow)
  python tools/check_pins.py FILE...    # only these files (-r includes are followed)

A release counts as usable when it has a wheel for the course's Python ("python" in
course.json) on any platform: a wheel for that version, an abi3 wheel for an older one, a
pure-Python wheel, or no wheels at all (a source-only release such as PySpark). Pre-releases
and yanked files are ignored. Newer releases that are not usable are listed, and the pin stays.
Needs network access to pypi.org; nothing else in CI does. After moving a pin, run
tools/check_libraries.py and tools/ci.py: a new release can change outputs on the pages.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "site" / "downloads"
PIN = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)(\[[^\]]*\])?==([^\s;]+)")
WHEEL_TAG = re.compile(r"(cp|py)(\d)(\d*)")


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def read_pins(path: Path, seen: set[Path] | None = None) -> dict[str, tuple[str, Path]]:
    """name -> (pinned version, file) for every `name==version` line, following -r includes."""
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen:
        return {}
    seen.add(path)
    pins: dict[str, tuple[str, Path]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith(("-r ", "--requirement ")):
            pins.update(read_pins(path.parent / line.split(maxsplit=1)[1], seen))
        elif m := PIN.fullmatch(line.split(";", 1)[0].strip()):
            pins[canonical(m[1])] = (m[3], path)
        else:
            raise ValueError(f"{path.name}: not an exact pin (name==version): {line!r}")
    return pins


def installs_on(files: list[dict], python: str) -> bool:
    """True if this release can install on CPython `python` ("3.15") on some platform."""
    major, minor = (int(part) for part in python.split(".")[:2])
    files = [f for f in files if not f.get("yanked")]
    wheels = [f["filename"] for f in files if f["filename"].endswith(".whl")]
    if not wheels:  # source only: pure-Python projects such as PySpark build anywhere
        return any(f["filename"].endswith((".tar.gz", ".zip")) for f in files)
    for name in wheels:
        py_tags, abi, _platform = name[:-4].split("-")[-3:]
        for tag in py_tags.split("."):
            m = WHEEL_TAG.fullmatch(tag)
            if not m or int(m[2]) != major:
                continue
            kind, tag_minor = m[1], int(m[3]) if m[3] else None
            if kind == "py" and tag_minor in (None, minor) and abi == "none":
                return True
            if kind == "cp" and tag_minor == minor and abi in (f"cp{major}{minor}", "abi3", "none"):
                return True
            if kind == "cp" and abi == "abi3" and tag_minor is not None and tag_minor <= minor:
                return True
    return False


@dataclass
class Result:
    name: str
    pinned: str
    file: Path
    newest: str = ""                                  # newest usable release
    skipped: list[str] = field(default_factory=list)  # newer, but no wheel for the course's Python
    error: str = ""

    @property
    def status(self) -> str:
        if self.error:
            return "error"
        return "update" if Version(self.newest) > Version(self.pinned) else "current"


def fetch_pypi(name: str) -> dict:
    request = urllib.request.Request(f"https://pypi.org/pypi/{name}/json",
                                     headers={"User-Agent": "python-ai-course check_pins"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def check_one(name: str, pinned: str, file: Path, python: str, fetch) -> Result:
    result = Result(name, pinned, file, newest=pinned)
    try:
        releases = fetch(name)["releases"]
    except (OSError, ValueError, KeyError) as err:  # network, 404, bad JSON: report, carry on
        result.error = f"{type(err).__name__}: {err}"
        return result
    versions = []
    for text, files in releases.items():
        try:
            version = Version(text)
        except InvalidVersion:
            continue
        if not version.is_prerelease and files and version > Version(pinned):
            versions.append((version, text, files))
    for version, text, files in sorted(versions, reverse=True):
        if installs_on(files, python):
            result.newest = text
            break
        result.skipped.append(text)
    return result


def check(pins: dict[str, tuple[str, Path]], python: str, fetch=fetch_pypi, jobs: int = 8) -> list[Result]:
    with cf.ThreadPoolExecutor(jobs) as pool:
        futures = [pool.submit(check_one, name, version, file, python, fetch)
                   for name, (version, file) in sorted(pins.items())]
        return [f.result() for f in futures]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--strict", action="store_true", help="exit 1 when a pin can move up")
    ap.add_argument("--python", help="target Python (default: course.json)")
    args = ap.parse_args(argv)
    python = args.python or json.loads((ROOT / "course.json").read_text(encoding="utf-8"))["python"]
    pins: dict[str, tuple[str, Path]] = {}
    for file in args.files or sorted(DOWNLOADS.glob("requirements-*.txt")):
        pins.update(read_pins(file))
    results = check(pins, python)
    width = max(len(r.name) for r in results)
    for r in results:
        note = {"current": "current", "update": f"update to {r.newest}", "error": r.error}[r.status]
        if r.skipped:
            note += f" (skipped, no wheel for Python {python}: {', '.join(r.skipped[:3])}"
            note += "...)" if len(r.skipped) > 3 else ")"
        print(f"{r.name:<{width}}  {r.pinned:<12} {note}  [{r.file.name}]")
    updates = sum(r.status == "update" for r in results)
    errors = sum(r.status == "error" for r in results)
    print(f"\n{len(results)} pins for Python {python}: {updates} can move up, {errors} errors")
    if errors:
        return 2
    return 1 if args.strict and updates else 0


if __name__ == "__main__":
    raise SystemExit(main())
