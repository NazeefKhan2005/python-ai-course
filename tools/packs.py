"""Exercise packs: the single definition of which files an exercise produces.

check_content.py builds the "solution" variant to prove the tests pass, and the "starter" variant to
prove they fail before the learner starts; export_exercises.py zips the starter variant for learners.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pagekit import Node, Page

LEARNER = Path(__file__).resolve().parent / "learner"
SHARED_FILES = ("conftest.py", "course_helpers.py", "course_mocks.py")
TESTED_ON = "3.15"


@dataclass
class Exercise:
    page: Page
    node: Node
    id: str
    title: str
    kind: str
    file: str
    optional: bool
    roles: dict[str, str] = field(default_factory=dict)  # starter/tests/solution/target -> code
    mutants: dict[str, str] = field(default_factory=dict)
    data_files: dict[str, str] = field(default_factory=dict)

    @property
    def stem(self) -> str:
        return self.file.removesuffix(".py")

    @property
    def test_file(self) -> str:
        """The file whose full pass earns the completion code."""
        return f"test_{self.stem}_check.py" if self.kind == "write_tests" else f"test_{self.file}"

    def files(self, variant: str) -> dict[str, str]:
        """Files for one exercise. variant: "starter" (what learners get) or "solution"."""
        files = dict(self.data_files)
        if self.kind == "write_tests":
            files[self.file] = self.roles["target"]
            files[f"test_{self.file}"] = self.roles[variant] + "\n"
            files[f"{self.stem}_mutants.json"] = json.dumps(self.mutants, indent=2) + "\n"
            files[self.test_file] = (
                f'"""Checks YOUR tests in test_{self.file}: they must pass on {self.file} and catch every bug."""\n'
                "from course_helpers import check_tests\n\n\n"
                "def test_your_tests_catch_every_bug():\n"
                f'    check_tests("test_{self.file}", module="{self.stem}", mutants="{self.stem}_mutants.json")\n')
        else:
            files[self.file] = self.roles[variant] + "\n"
            files[self.test_file] = self.roles["tests"] + "\n"
        return files


def exercises(page: Page) -> list[Exercise]:
    out = []
    for node in page.all("article", cls="exercise"):
        heading = next((n for n in node.iter() if n.tag in ("h3", "h4")), None)
        ex = Exercise(page, node, node.get("id", ""), heading.text() if heading else node.get("id", ""),
                      node.get("data-kind", "function"), node.get("data-file", ""), "data-optional" in node.attrs)
        for script in (n for n in node.iter() if n.tag == "script"):
            role, kind = script.get("data-role"), script.get("type")
            if kind == "text/x-file":
                ex.data_files[script.get("data-name", "")] = page.code(script) + "\n"
            elif role == "mutants":
                ex.mutants = json.loads(page.raw(script))
            elif role:
                ex.roles[role] = page.code(script)
        out.append(ex)
    return out


def pack_files(page: Page, lesson_title: str, lesson_url: str) -> dict[str, str]:
    """All files of a lesson's pack (starter variant), keyed by path inside the pack folder."""
    lesson = page.body.get("data-lesson-id")
    items = exercises(page)
    files: dict[str, str] = {}
    for ex in items:
        for name, text in ex.files("starter").items():
            if name in files and files[name] != text:
                raise ValueError(f"{lesson}: two exercises write different {name}")
            files[name] = text
    for name in SHARED_FILES:
        files[name] = (LEARNER / name).read_text(encoding="utf-8")
    meta = {"lesson": lesson, "title": lesson_title, "python": TESTED_ON,
            "exercises": [{"id": ex.id, "title": ex.title, "file": ex.file, "tests": ex.test_file,
                           "optional": ex.optional} for ex in items]}
    files["pack.json"] = json.dumps(meta, indent=2) + "\n"
    lines = [f"# {lesson.upper()} · {lesson_title} — exercise pack", "",
             f"Lesson page: {lesson_url}", "",
             "## How to work on these exercises", "",
             "1. Open this folder in your editor and in a terminal (see the course setup page).",
             "2. Install pytest once per environment: `python -m pip install pytest`",
             "3. Run every exercise's tests: `python -m pytest`",
             "   or a single exercise: `python -m pytest test_e1_....py`",
             "4. Edit the `eN_*.py` files until their tests pass. When a whole test file passes, pytest",
             "   prints a completion code: paste it into the exercise on the lesson page.", "",
             "On Windows use `py` instead of `python`; with uv use `uv run --with pytest pytest`.", "",
             "## Exercises", ""]
    for ex in items:
        extra = " (optional)" if ex.optional else ""
        edit = f"test_{ex.file}" if ex.kind == "write_tests" else ex.file
        lines.append(f"- **{ex.id}** {ex.title}{extra}: edit `{edit}`, check with `python -m pytest {ex.test_file}`")
    files["README.md"] = "\n".join(lines) + "\n"
    return dict(sorted(files.items()))
