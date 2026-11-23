"""Build the downloadable exercise packs: site/downloads/<lesson-id>.zip and all-exercises.zip.

  python tools/export_exercises.py           # write the zips
  python tools/export_exercises.py --check   # fail if a zip is missing or out of date (CI)

Zips are deterministic (sorted names, fixed timestamps), so --check can compare bytes.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packs import exercises, pack_files
from pagekit import Page

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
STAMP = (2026, 1, 1, 0, 0, 0)


def zip_bytes(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, STAMP)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, files[name].encode("utf-8"))
    return buffer.getvalue()


def lesson_pages(course: dict, site: Path):
    for module in course["modules"]:
        for lesson in module["lessons"]:
            path = site / module["path"] / lesson["file"]
            if not lesson.get("planned") and path.exists():
                yield module, lesson, Page(path)


def packs(course: dict, site: Path = SITE) -> dict[str, bytes]:
    """Relative output path -> zip bytes, for every lesson that has exercises."""
    out, everything = {}, {}
    base = course.get("base_url", "")
    for module, lesson, page in lesson_pages(course, site):
        if not exercises(page):
            continue
        url = f"{base}{module['path']}{lesson['file']}" if base else f"site/{module['path']}{lesson['file']}"
        files = {f"{lesson['id']}/{name}": text for name, text in pack_files(page, lesson["title"], url).items()}
        out[f"downloads/{lesson['id']}.zip"] = zip_bytes(files)
        everything.update(files)
    if everything:
        out["downloads/all-exercises.zip"] = zip_bytes(everything)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    course = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
    stale = 0
    for rel, data in packs(course).items():
        path = SITE / rel
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                print(f"out of date: site/{rel} (run python tools/build.py)")
                stale += 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(f"wrote site/{rel} ({len(data) // 1024 + 1} KB)")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
