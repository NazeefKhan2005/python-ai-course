"""Course plugin for pytest. You don't need to edit (or understand) this file.

It does two things:
1. lets the tests import your exercise files from any working directory;
2. after a run, prints a completion code for every exercise whose tests ALL passed.
   Paste the code into the exercise on the lesson page to record it as passed.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    PACK = json.loads((HERE / "pack.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    PACK = {"lesson": "?", "exercises": []}
BY_FILE = {ex["tests"]: ex for ex in PACK.get("exercises", [])}
TESTED_ON = PACK.get("python", "3.15")


def completion_code(exercise_id: str) -> str:
    """FNV-1a (32-bit) of the exercise id: the lesson page computes the same value."""
    value = 0x811C9DC5
    for byte in ("pyai:" + exercise_id).encode("utf-8"):
        value = ((value ^ byte) * 0x01000193) & 0xFFFFFFFF
    text = f"{value:08X}"
    return f"{text[:4]}-{text[4:]}"


_collected: Counter = Counter()
_passed: Counter = Counter()
_problems: Counter = Counter()
_deselected: set = set()


def _file(nodeid: str) -> str:
    return Path(nodeid.split("::", 1)[0]).name


def pytest_report_header(config):
    version = ".".join(map(str, sys.version_info[:3]))
    lines = [f"course pack {PACK.get('lesson')}: Python {version} (course tested on {TESTED_ON})"]
    if sys.version_info < (3, 15):
        lines.append(f"WARNING: the course is verified on Python {TESTED_ON}; some exercises use features "
                     "your version lacks. See the setup page.")
    return lines


def pytest_deselected(items):
    _deselected.update(item.path.name for item in items)


def pytest_collection_finish(session):
    _collected.update(item.path.name for item in session.items)


def pytest_runtest_logreport(report):
    name = _file(report.nodeid)
    if report.when == "call" and report.passed:
        _passed[name] += 1
    elif report.failed or report.skipped:
        _problems[name] += 1


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not BY_FILE:
        return
    write = terminalreporter.write_line
    terminalreporter.section("course: completion codes")
    for tests, ex in BY_FILE.items():
        label = f"{ex['id']:<12} {ex['title'][:40]:<40}"
        total = _collected[tests]
        if total == 0:
            write(f"{label}  - not run")
        elif tests in _deselected:
            write(f"{label}  - only some tests ran; run the whole file to get a code")
        elif _passed[tests] == total and not _problems[tests]:
            write(f"{label}  PASSED  code {completion_code(ex['id'])}")
        else:
            write(f"{label}  {total - _passed[tests]} of {total} tests not passing yet")
    write("Paste a code into the matching exercise on the lesson page to record it as passed.")
