"""Verify every piece of code on the course pages by running it with real Python.

  python tools/check_content.py                     # all pages under site/
  python tools/check_content.py site/modules/m03-data-structures/l04-dictionaries.html
  python tools/check_content.py --update-outputs    # rewrite x-output blocks from real runs
  python tools/check_content.py -j 8 --skip-missing # parallel; skip examples whose libraries are absent

Checks: x-python blocks compile; examples (figure.example) print exactly their x-output, twice, under
two hash seeds; x-pycon sessions pass doctest; exercise tests pass on the solution and fail on the
starter (write_tests: catch every mutant); quiz specs are valid and predict answers match real output.
"""
from __future__ import annotations

import argparse
import difflib
import doctest
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packs import LEARNER, SHARED_FILES, exercises
from pagekit import Node, Page, dedent, replace_scripts, site_pages

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SEEDS = ("0", "1")

HARNESS = r'''
import builtins, doctest, os, runpy, sys, traceback
sys.path[0] = os.getcwd()  # import helper files that sit next to the example, like `python example.py` would
sys.stderr = sys.stdout  # interleave like a terminal does
def _input(prompt=""):
    sys.stdout.write(str(prompt))
    line = sys.stdin.readline()
    if not line:
        raise EOFError("EOF when reading a line")
    line = line.rstrip("\n")
    print(line)  # a terminal echoes what you type
    return line
builtins.input = _input
mode, path = sys.argv[1], sys.argv[2]
if mode == "pycon":
    flags = doctest.ELLIPSIS if sys.argv[3] == "ellipsis" else 0
    text = open(path, encoding="utf-8").read()
    test = doctest.DocTestParser().get_doctest(text, {"__name__": "__main__"}, "session", path, 0)
    runner = doctest.DocTestRunner(verbose=False, optionflags=flags | doctest.REPORT_UDIFF)
    result = runner.run(test, out=sys.stdout.write, clear_globs=True)
    sys.exit(1 if result.failed else 0)
sys.argv = [path, *sys.argv[3:]]
try:
    runpy.run_path(path, run_name="__main__")
except SystemExit:
    raise
except BaseException as exc:
    sys.stdout.flush()
    print("Traceback (most recent call last):\n  ...")
    print("".join(traceback.format_exception_only(exc)), end="")
    sys.exit(1)
'''


def normalize(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip("\n")


@dataclass
class Problem:
    page: Page
    node: Node
    message: str

    def __str__(self) -> str:
        return f"{self.page.path.relative_to(ROOT) if self.page.path.is_relative_to(ROOT) else self.page.path}:{self.node.line}: {self.message}"


@dataclass
class Report:
    problems: list[Problem] = field(default_factory=list)
    updates: dict = field(default_factory=dict)  # Page -> {node: new text}
    counts: dict = field(default_factory=lambda: {"compiled": 0, "examples": 0, "sessions": 0,
                                                  "exercises": 0, "quizzes": 0, "skipped": 0})


class Checker:
    def __init__(self, python: str, jobs: int, skip_missing: bool, update: bool):
        self.python, self.jobs, self.skip_missing, self.update = python, jobs, skip_missing, update
        self.report = Report()
        self.tmp = Path(tempfile.mkdtemp(prefix="course-check-"))
        (self.tmp / "harness.py").write_text(HARNESS, encoding="utf-8")
        self.missing_cache: dict[str, bool] = {}
        out = subprocess.run([python, "-c", "import sys; print(*sys.version_info[:2])"], capture_output=True, text=True,
                             check=True)
        self.version = tuple(int(x) for x in out.stdout.split())

    def too_new(self, node: Node) -> bool:
        """data-python="3.16" on the block or an ancestor: only checked by that Python or newer."""
        holder = node if node.get("data-python") else node.closest(lambda a: a.get("data-python"))
        if holder is None:
            return False
        if tuple(int(x) for x in holder.get("data-python").split(".")) > self.version:
            self.report.counts["skipped"] += 1
            return True
        return False

    # ------------------------------------------------------------------ running
    def env(self, seed: str) -> dict:
        keep = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "SYSTEMROOT", "TMP", "TEMP", "LANG")}
        return {**keep, "PYTHONHASHSEED": seed, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
                "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg", "NO_COLOR": "1", "PYTHON_COLORS": "0",
                "TERM": "dumb", "COLUMNS": "80", "LINES": "24"}

    def run(self, args: list[str], cwd: Path, seed="0", stdin="", timeout=60) -> tuple[int, str]:
        try:
            done = subprocess.run([self.python, *args], cwd=cwd, input=stdin, capture_output=True, text=True,
                                  timeout=timeout, env=self.env(seed), check=False)
        except subprocess.TimeoutExpired:
            return -1, f"(timed out after {timeout} s)"
        output = (done.stdout + done.stderr).replace(str(cwd) + os.sep, "")
        return done.returncode, output

    def workdir(self, name: str, files: dict[str, str]) -> Path:
        folder = Path(tempfile.mkdtemp(prefix=re.sub(r"\W", "_", name)[:40] + "-", dir=self.tmp))
        for rel, text in files.items():
            (folder / rel).parent.mkdir(parents=True, exist_ok=True)
            (folder / rel).write_text(text, encoding="utf-8")
        return folder

    def missing(self, node: Node) -> list[str]:
        names = (node.get("data-requires") or "").split()
        for name in names:
            if name not in self.missing_cache:
                self.missing_cache[name] = importlib.util.find_spec(name) is None
        return [n for n in names if self.missing_cache[n]]

    def problem(self, page, node, message):
        self.report.problems.append(Problem(page, node, message))

    # ------------------------------------------------------------------ checks
    def compile_all(self, page: Page):
        for node in page.scripts("text/x-python"):
            if self.too_new(node):
                continue
            code = page.code(node)
            if "</script" in page.raw(node).lower():
                self.problem(page, node, "code contains '</script' (the page would break)")
            expect = node.get("data-expect")
            try:
                compile(code, f"{page.path.name}:{node.line}", "exec", dont_inherit=True)
                if expect == "SyntaxError":
                    self.problem(page, node, 'marked data-expect="SyntaxError" but compiles')
            except SyntaxError as err:
                if expect != "SyntaxError":
                    self.problem(page, node, f"does not compile: {err.msg} (code line {err.lineno})")
            self.report.counts["compiled"] += 1

    def example(self, page: Page, figure: Node):
        scripts = [n for n in figure.iter() if n.tag == "script"]
        code = next((n for n in scripts if n.get("type") == "text/x-python"), None)
        out = next((n for n in scripts if n.get("type") == "text/x-output"), None)
        if code is None or out is None or self.too_new(figure):
            return  # display-only figure (check_site enforces the structure rules) or needs a newer Python
        if (missing := self.missing(figure)):
            if self.skip_missing:
                self.report.counts["skipped"] += 1
                return
            self.problem(page, figure, f"needs {', '.join(missing)} (install it, or pass --skip-missing)")
            return
        files = {n.get("data-name"): page.code(n) + "\n" for n in scripts if n.get("type") == "text/x-file"}
        name = code.get("data-file") or "example.py"
        files[name] = page.code(code) + "\n"
        stdin = next((page.code(n) + "\n" for n in scripts if n.get("type") == "text/x-stdin"), "")
        args = (figure.get("data-args") or "").split()
        want_exit = int(figure.get("data-exit") or (1 if figure.get("data-raises") else 0))
        timeout = int(figure.get("data-timeout") or 60)
        runs = []
        for seed in SEEDS:
            folder = self.workdir(f"{page.path.stem}-{figure.get('id', figure.line)}", files)
            status, text = self.run([str(self.tmp / "harness.py"), "script", name, *args], folder, seed, stdin, timeout)
            runs.append((status, normalize(text)))
        status, got = runs[0]
        self.report.counts["examples"] += 1
        label = f"example {figure.get('id') or ''}".strip()
        if status != want_exit:
            self.problem(page, figure, f"{label} exited with status {status} (expected {want_exit}):\n{indent(got)}")
            return
        if raises := figure.get("data-raises"):
            last = got.rsplit("\n", 1)[-1]
            if not last.startswith(raises):
                self.problem(page, figure, f"{label} should raise {raises}, last line was: {last}")
                return
        if figure.get("data-output") == "sample":
            return
        want = normalize(page.code(out))
        ellipsis = figure.get("data-match") == "ellipsis"
        if all(matches(want, text, ellipsis) for _, text in runs):
            return
        if not ellipsis and runs[0][1] != runs[1][1]:
            self.problem(page, figure, f"{label} prints different output under different hash seeds "
                                       "(set iteration order?):\n" + diff(runs[0][1], runs[1][1]))
        elif self.update and not ellipsis:
            self.report.updates.setdefault(page, {})[out] = got
        else:
            self.problem(page, figure, f"{label} output differs from the page"
                         + ("" if ellipsis else " (run with --update-outputs to accept)") + ":\n" + diff(want, got))

    def session(self, page: Page, node: Node):
        holder = node.closest(lambda a: a.get("data-requires")) or node
        if self.too_new(node):
            return
        if self.missing(holder) and self.skip_missing:
            self.report.counts["skipped"] += 1
            return
        files = {"session.txt": page.code(node) + "\n"}
        owner = node.closest(lambda a: a.has_class("exercise"))
        if owner is not None:  # a session in an exercise statement runs against the solution
            ex = next((e for e in exercises(page) if e.node is owner), None)
            if ex is not None and "solution" in ex.roles:
                files.update(ex.files("solution"))
        folder = self.workdir(f"{page.path.stem}-pycon", files)
        flag = "ellipsis" if (node.get("data-match") or (holder.get("data-match"))) == "ellipsis" else "-"
        for seed in SEEDS:
            status, text = self.run([str(self.tmp / "harness.py"), "pycon", "session.txt", flag], folder, seed)
            if status != 0:
                self.problem(page, node, f"interactive session does not match real Python (seed {seed}):\n{indent(text)}")
                break
        self.report.counts["sessions"] += 1

    def exercise(self, page: Page, ex):
        prefix = f"exercise {ex.id}"
        need = {"starter", "solution"} | ({"target"} if ex.kind == "write_tests" else {"tests"})
        if (absent := need - ex.roles.keys()):
            self.problem(page, ex.node, f"{prefix} is missing: {', '.join(sorted(absent))}")
            return
        if (missing := self.missing(ex.node)):
            if self.skip_missing:
                self.report.counts["skipped"] += 1
                return
            self.problem(page, ex.node, f"{prefix} needs {', '.join(missing)}")
            return
        shared = {name: (LEARNER / name).read_text(encoding="utf-8") for name in SHARED_FILES if name != "conftest.py"}
        for variant, should_pass in (("solution", True), ("starter", False)):
            folder = self.workdir(f"{ex.id}-{variant}", {**shared, **ex.files(variant)})
            status, text = self.run(["-m", "pytest", "-q", "-p", "no:cacheprovider", ex.test_file], folder, timeout=180)
            if should_pass and status != 0:
                self.problem(page, ex.node, f"{prefix}: tests fail on the solution:\n{indent(tail(text))}")
                return
            if not should_pass and status == 0:
                self.problem(page, ex.node, f"{prefix}: tests already pass on the starter code")
            if not should_pass and status == 5:
                self.problem(page, ex.node, f"{prefix}: pytest collected no tests")
        self.report.counts["exercises"] += 1

    def quiz(self, page: Page, section: Node):
        spec_node = next((n for n in section.iter() if n.tag == "script" and n.has_class("quiz-spec")), None)
        if spec_node is None:
            self.problem(page, section, "quiz without <script type=\"application/json\" class=\"quiz-spec\">")
            return
        try:
            spec = json.loads(page.raw(spec_node))
        except ValueError as err:
            self.problem(page, spec_node, f"quiz spec is not valid JSON: {err}")
            return
        for message in validate_quiz(spec, section.get("id")):
            self.problem(page, spec_node, message)
        for i, q in enumerate(spec.get("questions", []), 1):
            if q.get("type") == "predict" and isinstance(q.get("code"), str):
                folder = self.workdir(f"{spec.get('id')}-q{i}", {"predict.py": dedent(q["code"]) + "\n"})
                _, text = self.run([str(self.tmp / "harness.py"), "script", "predict.py"], folder)
                if normalize(text) != normalize(str(q.get("answer", ""))):
                    self.problem(page, spec_node, f"quiz question {i}: answer does not match real output:\n"
                                 + diff(normalize(str(q.get('answer', ''))), normalize(text)))
        self.report.counts["quizzes"] += 1

    # ------------------------------------------------------------------ driver
    def check(self, pages: list[Page], only: set[str]):
        tasks = []
        for page in pages:
            if "compile" in only:
                self.compile_all(page)
            if "examples" in only:
                tasks += [(self.example, page, f) for f in page.all("figure", cls="example")]
                tasks += [(self.session, page, n) for n in page.scripts("text/x-pycon")]
            if "exercises" in only:
                tasks += [(self.exercise, page, ex) for ex in exercises(page)]
            if "quizzes" in only:
                tasks += [(self.quiz, page, s) for s in page.all("section", cls="quiz")]
        with ThreadPoolExecutor(max_workers=self.jobs) as pool:
            for future in [pool.submit(fn, page, item) for fn, page, item in tasks]:
                future.result()


QUESTION_TYPES = {"mcq", "multi", "predict", "short", "order"}


def validate_quiz(spec: dict, section_id: str | None) -> list[str]:
    errors = []
    if spec.get("id") != section_id:
        errors.append(f"quiz id {spec.get('id')!r} must equal the section id {section_id!r}")
    questions = spec.get("questions")
    if not isinstance(questions, list) or not questions:
        return errors + ["quiz needs a non-empty questions list"]
    for i, q in enumerate(questions, 1):
        kind = q.get("type")
        where = f"question {i} ({kind})"
        if kind not in QUESTION_TYPES:
            errors.append(f"question {i}: type must be one of {sorted(QUESTION_TYPES)}")
            continue
        if not str(q.get("prompt", "")).strip():
            errors.append(f"{where}: empty prompt")
        if not str(q.get("explanation", "")).strip() and not q.get("explanations"):
            errors.append(f"{where}: add an explanation (shown after checking)")
        options = q.get("options", [])
        if kind in ("mcq", "multi"):
            if len(options) < 2 or len(set(options)) != len(options):
                errors.append(f"{where}: needs 2+ distinct options")
            answer = q.get("answer")
            picks = [answer] if kind == "mcq" else answer
            if not isinstance(picks, list) or not picks or any(not isinstance(a, int) or not 0 <= a < len(options) for a in picks):
                errors.append(f"{where}: answer must be {'an option index' if kind == 'mcq' else 'a list of option indexes'}")
            elif kind == "multi" and len(set(picks)) != len(picks):
                errors.append(f"{where}: duplicate answer indexes")
            if "explanations" in q and len(q["explanations"]) != len(options):
                errors.append(f"{where}: explanations must have one entry per option")
        elif kind == "predict":
            if not isinstance(q.get("code"), str) or "answer" not in q:
                errors.append(f"{where}: needs code and answer")
        elif kind == "short":
            accept, pattern = q.get("accept", []), q.get("accept_regex")
            if not accept and not pattern:
                errors.append(f"{where}: needs accept and/or accept_regex")
            if pattern:
                try:
                    re.compile(pattern)
                except re.error as err:
                    errors.append(f"{where}: bad accept_regex: {err}")
                if re.search(r"\(\?P<|\(\?[aiLmsux]+\)|\\[AZ]", pattern):
                    errors.append(f"{where}: accept_regex must also work in JavaScript (no (?P<, inline flags, \\A, \\Z)")
        elif kind == "order":
            items = q.get("items", [])
            if len(items) < 3 or len(set(items)) != len(items):
                errors.append(f"{where}: needs 3+ distinct items (in the correct order)")
    return errors


def matches(want: str, got: str, ellipsis: bool) -> bool:
    if not ellipsis:
        return want == got
    return doctest.OutputChecker().check_output(want + "\n", got + "\n", doctest.ELLIPSIS)


def diff(want: str, got: str) -> str:
    lines = difflib.unified_diff(want.split("\n"), got.split("\n"), "page", "real Python", lineterm="", n=2)
    return indent("\n".join(lines))


def indent(text: str) -> str:
    return "\n".join("    " + line for line in text.split("\n"))


def tail(text: str, n: int = 30) -> str:
    return "\n".join(text.strip().split("\n")[-n:])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="*", type=Path)
    ap.add_argument("--update-outputs", action="store_true", help="rewrite x-output blocks that differ")
    ap.add_argument("--skip-missing", action="store_true", help="skip code whose data-requires libraries are absent")
    ap.add_argument("--only", default="compile,examples,exercises,quizzes")
    ap.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--python", default=sys.executable, help="interpreter used to run the code")
    args = ap.parse_args(argv)
    paths = args.pages or site_pages(SITE)
    pages = [Page(p) for p in paths]
    pages = [p for p in pages if p.kind in ("lesson", "reference", "project", "exam", "setup", "home")]
    checker = Checker(args.python, args.jobs, args.skip_missing, args.update_outputs)
    checker.check(pages, set(args.only.split(",")))
    report = checker.report
    for page, replacements in report.updates.items():
        page.path.write_text(replace_scripts(page, replacements), encoding="utf-8")
        print(f"updated {len(replacements)} output block(s) in {page.path.name}")
    for problem in sorted(report.problems, key=str):
        print(f"FAIL {problem}")
    c = report.counts
    print(f"check_content: {len(pages)} page(s), {c['compiled']} blocks compiled, {c['examples']} examples, "
          f"{c['sessions']} sessions, {c['exercises']} exercises, {c['quizzes']} quizzes, {c['skipped']} skipped, "
          f"{len(report.problems)} problem(s)")
    return 1 if report.problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
