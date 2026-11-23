"""Tests for the build and check tools. Run: python -m pytest tools/tests -q"""
from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
FIX = Path(__file__).parent / "fixtures"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "learner"))

import api_skeleton
import build
import check_content
import check_coverage
import check_libraries
import check_pins
import check_site
import course_helpers
import export_exercises
import pagekit

spec = importlib.util.spec_from_file_location("learner_conftest", TOOLS / "learner" / "conftest.py")
learner_conftest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(learner_conftest)
SAMPLE = ROOT / "site/modules/m03-data-structures/l04-dictionaries.html"


# ---------------------------------------------------------------------- pagekit
@pytest.mark.parametrize("raw, expected", [
    ("\n    a\n      b\n    ", "a\n  b"),                   # closing line sets the base indent
    ("\n      two\n      lines\n    ", "  two\n  lines"),    # ...so all-indented output survives
    ("  x\n  y", "x\ny"),                                    # no closing line: common indent
    ("\n\n    keep\n\n    blank\n  ", "  keep\n\n  blank"),   # inner blank lines stay, edges go
    ("  ragged\nleft\n", "  ragged\nleft"),                  # never cuts into text
    ("one line", "one line"),
])
def test_dedent(raw, expected):
    assert pagekit.dedent(raw) == expected


def test_parser_reports_structure_errors():
    page = pagekit.Page("x.html", "<html><body><p>open<div></div></body></html>")
    assert any("closes <p>" in e for e in page.errors)
    assert any("never closed" in e for e in pagekit.Page("y.html", "<main><section>").errors)


def test_replace_scripts_round_trip():
    page = pagekit.Page(FIX / "bad-lesson.html")
    out = next(n for n in page.scripts("text/x-output"))
    new_source = pagekit.replace_scripts(page, {out: "['a', 'b']\n  indented"})
    again = pagekit.Page("z.html", new_source)
    assert again.code(next(iter(again.scripts("text/x-output")))) == "['a', 'b']\n  indented"
    assert new_source.count("\n") == page.source.count("\n") + 1


def test_api_id():
    assert pagekit.api_id("dict.get") == "api-dict-get"
    assert pagekit.api_id("dict_keys.__and__") == "api-dict_keys-__and__"
    assert pagekit.api_id("syntax:dict-display") == "api-syntax-dict-display"


# ---------------------------------------------------------------------- check_content
def run_checker(paths, update=False):
    checker = check_content.Checker(sys.executable, 4, skip_missing=True, update=update)
    checker.check([pagekit.Page(p) for p in paths], {"compile", "examples", "exercises", "quizzes"})
    return checker.report


def test_good_fixture_passes():
    report = run_checker([FIX / "good-lesson.html"])
    assert [str(p) for p in report.problems] == []
    assert report.counts["examples"] == 7 and report.counts["exercises"] == 2 and report.counts["sessions"] == 1


def test_bad_fixture_problems_are_reported():
    text = "\n".join(str(p) for p in run_checker([FIX / "bad-lesson.html"]).problems)
    for expected in ["output differs", "different output under different hash seeds", "exited with status 1",
                     "does not compile", "already pass on the starter", "answer does not match",
                     "answer must be an option index"]:
        assert expected in text, expected


def test_update_outputs_rewrites_only_wrong_outputs(tmp_path):
    page_path = tmp_path / "bad.html"
    shutil.copy(FIX / "bad-lesson.html", page_path)
    report = run_checker([page_path], update=True)
    for page, replacements in report.updates.items():
        page.path.write_text(pagekit.replace_scripts(page, replacements), encoding="utf-8")
    assert "['a', 'b']" in page_path.read_text()
    remaining = "\n".join(str(p) for p in run_checker([page_path]).problems)
    assert "ex-wrong" not in remaining and "hash seeds" in remaining  # nondeterminism is never "accepted"


def test_quiz_validation():
    bad = {"id": "q", "questions": [
        {"type": "short", "prompt": "?", "accept_regex": "(?P<x>a)", "explanation": "e"},
        {"type": "multi", "prompt": "?", "options": ["a", "b"], "answer": [0, 0], "explanation": "e"},
        {"type": "order", "prompt": "?", "items": ["a", "b"], "explanation": "e"},
        {"type": "essay", "prompt": "?"}]}
    errors = "\n".join(check_content.validate_quiz(bad, "q"))
    assert "JavaScript" in errors and "duplicate" in errors and "3+ distinct items" in errors and "type must be" in errors


# ---------------------------------------------------------------------- coverage
CONFIG = json.loads(check_coverage.CONFIG.read_text())
IGNORE = set(CONFIG["ignore_dunders"])


def test_dict_surface():
    required = check_coverage.resolve("class:dict").required(IGNORE)
    assert {"dict", "dict.get", "dict.__or__", "dict.__class_getitem__", "dict.__hash__"} <= required
    assert "dict.__init__" not in required and "dict.__sizeof__" not in required


def test_subclasses_skip_builtin_and_target_bases():
    counter = check_coverage.resolve("class:collections.Counter")
    names = counter.required(IGNORE)
    assert "Counter.most_common" in names and "Counter.get" not in names  # dict's get belongs to dict


def test_helper_bases_are_included():
    pytest.importorskip("pandas")
    names = check_coverage.resolve("class:pandas.DataFrame").required(IGNORE)
    assert {"DataFrame.head", "DataFrame.loc", "DataFrame.groupby"} <= names


def test_module_alias_lookup_prefers_longest():
    page = pagekit.Page("p.html", """<main><section class="api-reference" data-api-targets="module:os.path">
    <table><tr id="api-os-path-join" data-api="os.path.join" data-level="essential"><td>x</td></tr></table></section></main>""")
    res = check_coverage.check([page], CONFIG, partial=True)
    assert not [e for e in res.errors if "does not belong" in e or "does not exist" in e]
    assert any("os.path" in e and "without a row" in e for e in res.errors)


def test_coverage_flags_missing_unknown_and_stale():
    page = pagekit.Page("p.html", """<main><section class="api-reference" data-api-targets="class:dict">
    <table><tr data-api="dict.gett"><td>x</td></tr><tr data-api="list.append"><td>y</td></tr></table></section></main>""")
    config = {**CONFIG, "exclude": {"dict": {"__nope__": "stale"}}}
    text = "\n".join(check_coverage.check([page], config, partial=True).errors)
    assert "dict.gett does not exist" in text and "list.append' does not belong" in text
    assert "stale exclusion dict.__nope__" in text and "without a row" in text


def test_soft_keywords_are_found_in_code():
    _, words = check_coverage.syntax_used([(None, "match x:\n    case _:\n        pass\ntype Pair = tuple[int, int]\n")])
    assert {"match", "case", "_", "type"} <= words
    if sys.version_info >= (3, 15):
        assert "lazy" in check_coverage.syntax_used([(None, "lazy import json\n")])[1]


def test_sample_lesson_targets_are_complete():
    res = check_coverage.check([pagekit.Page(SAMPLE)], CONFIG, partial=True)
    assert res.errors == []
    assert sum("complete" in n for n in res.notes) >= 5


def test_api_skeleton_covers_every_required_name():
    rows = api_skeleton.rows("class:dict", None)
    names = {r.split('data-api="')[1].split('"')[0] for r in rows}
    assert names == check_coverage.resolve("class:dict").required(IGNORE)
    assert all('data-level="TODO"' in r for r in rows)


# ---------------------------------------------------------------------- packs and the learner side
def test_completion_code_format_and_stability():
    code = learner_conftest.completion_code("m03-l04-e1")
    assert len(code) == 9 and code[4] == "-" and code == learner_conftest.completion_code("m03-l04-e1")
    assert code != learner_conftest.completion_code("m03-l04-e2")


def test_exports_are_deterministic():
    course = json.loads((ROOT / "course.json").read_text())
    first, second = export_exercises.packs(course), export_exercises.packs(course)
    assert first == second and "downloads/m03-l04.zip" in first
    names = zipfile.ZipFile(io.BytesIO(first["downloads/m03-l04.zip"])).namelist()
    assert {"m03-l04/conftest.py", "m03-l04/pack.json", "m03-l04/e1_word_freq.py", "m03-l04/test_e4_first_unique.py",
            "m03-l04/README.md", "m03-l04/course_helpers.py"} <= set(names)
    assert not any("solution" in n for n in names)


def test_learner_pack_prints_codes_only_for_fully_passing_files(tmp_path):
    course = json.loads((ROOT / "course.json").read_text())
    data = export_exercises.packs(course)["downloads/m03-l04.zip"]
    zipfile.ZipFile(io.BytesIO(data)).extractall(tmp_path)
    pack = tmp_path / "m03-l04"
    page = pagekit.Page(SAMPLE)
    solution = next(e for e in check_content.exercises(page) if e.id == "m03-l04-e1").roles["solution"]
    (pack / "e1_word_freq.py").write_text(solution + "\n")
    run = lambda *args: subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
                                       cwd=pack, capture_output=True, text=True, check=False).stdout
    out = run()
    assert f"PASSED  code {learner_conftest.completion_code('m03-l04-e1')}" in out
    assert "m03-l04-e2" in out and "not passing yet" in out
    partial = run("-k", "counts_repeated")
    assert "only some tests ran" in partial and "PASSED  code" not in partial


def test_course_helpers(tmp_path):
    script = tmp_path / "echo.py"
    script.write_text("name = input('Name? ')\nprint('Hi', name)\n")
    assert course_helpers.run_program(script, stdin="Ada\n").endswith("Hi Ada\n")
    slow = lambda n: sum(1 for i in range(n) for j in range(n))
    fast = lambda n: n * n
    with pytest.raises(AssertionError, match="took"):
        course_helpers.assert_fast_enough(slow, fast, 400, factor=5)
    code = tmp_path / "loops.py"
    code.write_text("total = 0\nfor x in range(3):\n    total += x\nprint(sorted([2, 1]))\n")
    with pytest.raises(AssertionError, match="For"):
        course_helpers.assert_no_syntax(code, nodes=(__import__("ast").For,))
    with pytest.raises(AssertionError, match="sorted"):
        course_helpers.assert_no_syntax(code, calls=("sorted",))


def test_check_tests_catches_weak_tests(tmp_path):
    (tmp_path / "leap.py").write_text("def is_leap(y):\n    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)\n")
    mutants = {"every 4th year": "def is_leap(y):\n    return y % 4 == 0\n"}
    weak = tmp_path / "test_weak.py"
    weak.write_text("from leap import is_leap\n\ndef test_basic():\n    assert is_leap(2024)\n")
    with pytest.raises(AssertionError, match="every 4th year"):
        course_helpers.check_tests(weak, "leap", mutants)
    strong = tmp_path / "test_strong.py"
    strong.write_text("from leap import is_leap\n\ndef test_rules():\n    assert is_leap(2024) and not is_leap(1900)\n")
    course_helpers.check_tests(strong, "leap", mutants)


# ---------------------------------------------------------------------- check_site and build
def make_site(tmp_path: Path, lesson_html: str) -> Path:
    site = tmp_path / "site"
    (site / "assets/js").mkdir(parents=True)
    (site / "m").mkdir()
    manifest = {"modules": [{"id": "m99", "path": "m/", "lessons": [{"id": "m99-l01", "file": "l01.html"}]}]}
    (site / "assets/js/manifest.js").write_text("window.COURSE = " + json.dumps(manifest) + ";\n")
    (site / "m/l01.html").write_text(lesson_html)
    return site


def test_check_site_catches_authoring_mistakes(tmp_path):
    shell = SAMPLE.read_text()
    head, rest = shell.split('<main id="main" class="content">', 1)
    tail = rest.split("</main>", 1)[1]
    head = head.replace('data-lesson-id="m03-l04" data-root="../../"', 'data-lesson-id="m99-l01" data-root="../"').replace("../../", "../")
    body = """<main id="main" class="content"><h1>T</h1>
      <section id="s1"><h2>No level</h2><h4>skipped h3</h4></section>
      <section id="s2" data-level="extra"><p data-level="essential">too essential</p><a href="missing.html">x</a></section>
      <section class="api-reference" id="ref" data-api-targets="class:dict"><table><caption>c</caption>
      <thead><tr><th scope="col">a</th></tr></thead><tbody><tr id="wrong" data-api="dict.get"><td>TODO later</td></tr></tbody></table></section>
      <aside class="callout" data-kind="shout"><p>?</p></aside>
    </main>"""
    site = make_site(tmp_path, head + body + tail)
    page = pagekit.Page(site / "m/l01.html")
    errors = "\n".join(check_site.check_page(page, site, check_site.load_manifest(site), {}))
    for expected in ["content sections need data-level", "skips from h2 to h4", "a child can't be more essential",
                     "broken link missing.html", "id must be 'api-dict-get'", "unfinished row", "callout data-kind",
                     "lesson pages need section.outcomes"]:
        assert expected in errors, expected


def test_sample_site_is_clean_and_built():
    site = ROOT / "site"
    manifest = check_site.load_manifest(site)
    for path in pagekit.site_pages(site):
        assert check_site.check_page(pagekit.Page(path), site, manifest, {}) == [], path.name
    stale = [rel for rel, data in build.outputs().items() if (site / rel).read_bytes() != data]
    assert stale == [], "run python tools/build.py"


# ------------------------------------------------------------- pins and libraries
def test_read_pins_follows_includes_and_rejects_ranges(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("pytest==9.2.0\n", encoding="utf-8")
    (tmp_path / "a.txt").write_text("# tools\n-r sub/b.txt\nNumPy==2.5.5  # arrays\npsycopg[binary]==3.3.9\n",
                                    encoding="utf-8")
    pins = check_pins.read_pins(tmp_path / "a.txt")
    assert {name: version for name, (version, _) in pins.items()} == {
        "pytest": "9.2.0", "numpy": "2.5.5", "psycopg": "3.3.9"}
    (tmp_path / "c.txt").write_text("pandas>=3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exact pin"):
        check_pins.read_pins(tmp_path / "c.txt")


@pytest.mark.parametrize("filename, ok", [
    ("x-1.0-cp315-cp315-manylinux_2_28_x86_64.whl", True),
    ("x-1.0-cp314-cp314-win_amd64.whl", False),
    ("x-1.0-cp315-cp315t-macosx_11_0_arm64.whl", False),     # free-threaded build only
    ("x-1.0-cp310-abi3-manylinux_2_28_x86_64.whl", True),     # stable ABI: 3.10 and later
    ("x-1.0-cp316-abi3-manylinux_2_28_x86_64.whl", False),
    ("x-1.0-py3-none-any.whl", True),
    ("x-1.0-py2.py3-none-any.whl", True),
    ("x-1.0-py3-none-manylinux_2_17_x86_64.whl", True),       # platform wheel for any Python 3
    ("x-1.0.tar.gz", True),                                    # source only (pure Python)
])
def test_installs_on(filename, ok):
    assert check_pins.installs_on([{"filename": filename}], "3.15") is ok


def test_newest_usable_release_skips_prereleases_and_missing_wheels():
    def wheel(tag):
        return [{"filename": f"a-0-{tag}-{tag}-linux_x86_64.whl"}]

    releases = {"0.9": wheel("cp315"), "1.0": wheel("cp315"), "1.1": wheel("cp315"),
                "1.2rc1": wheel("cp315"), "1.3": wheel("cp314")}

    def fetch(name):
        if name == "b":
            raise OSError("offline")
        return {"releases": releases}

    pins = {"a": ("1.0", Path("requirements-x.txt")), "b": ("2.0", Path("requirements-x.txt"))}
    a, b = check_pins.check(pins, "3.15", fetch)
    assert (a.status, a.newest, a.skipped) == ("update", "1.1", ["1.3"])
    assert b.status == "error" and "offline" in b.error


def test_every_pin_has_a_library_check_and_one_download():
    pins = check_pins.read_pins(check_libraries.DEV_REQUIREMENTS)
    assert sorted(pins) == sorted(check_libraries.IMPORTS)
    files = sorted((ROOT / "site/downloads").glob("requirements-*.txt"))
    names = [name for f in files for name in check_pins.read_pins(f)]
    assert len(names) == len(set(names)) == len(pins)      # each library in exactly one learner file
    setup = (ROOT / "site/setup.html").read_text(encoding="utf-8")
    assert all(f'href="downloads/{f.name}"' in setup for f in files)
