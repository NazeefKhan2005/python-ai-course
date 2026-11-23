"""Run every check the way CI does. Stops at the first failing step.

  python tools/ci.py                # full course: everything must be complete
  python tools/ci.py --partial      # while building: unbuilt course-wide coverage is "pending"
  python tools/ci.py --no-browser   # skip the headless-Chrome smoke test
  python tools/ci.py --skip-missing # skip examples and library checks whose libraries are absent
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--partial", action="store_true")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--skip-missing", action="store_true", help="skip examples and library checks whose libraries are not installed")
    args = ap.parse_args(argv)
    py = sys.executable
    steps = [
        ("unit tests for the tools", [py, "-m", "pytest", "tools/tests", "-q", "-p", "no:cacheprovider"]),
        ("pinned libraries import and work", [py, "tools/check_libraries.py", "-j", "4"]
         + (["--skip-missing"] if args.skip_missing else [])),
        ("course code passes ruff", [py, "-m", "ruff", "check", "--no-cache", "tools"]),
        ("generated files are up to date", [py, "tools/build.py", "--check"]),
        ("site structure, links, markers", [py, "tools/check_site.py"]),
        ("reference coverage", [py, "tools/check_coverage.py"] + (["--partial"] if args.partial else [])),
        ("every example, session, exercise, quiz", [py, "tools/check_content.py"] + (["--skip-missing"] if args.skip_missing else [])),
        ("validated exercise patterns (spec/05 §11)", [py, "tools/check_content.py", "examples/spec05-examples.html"]
         + (["--skip-missing"] if args.skip_missing else [])),
    ]
    if not args.no_browser:
        if shutil.which("node") and (ROOT / "node_modules/puppeteer-core").exists():
            steps.append(("pages in headless Chrome", ["node", "tools/smoke_pages.mjs"]))
        else:
            print("note: skipping the browser smoke test (needs node and npm install puppeteer-core axe-core)")
    for title, cmd in steps:
        print(f"\n== {title}: {' '.join(cmd[1:] if cmd[0] == py else cmd)}", flush=True)
        if subprocess.run(cmd, cwd=ROOT, env={**os.environ, "PYTHON": py}, check=False).returncode:
            print(f"\nCI FAILED at: {title}")
            return 1
    print("\nCI passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
