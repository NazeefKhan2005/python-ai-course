"""Tests for tools/make_datasets.py and site/data/. Run: python -m pytest tools/tests -q"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import make_datasets

DATA = make_datasets.DATA
README = (DATA / "README.md").read_text(encoding="utf-8")
GLOVE = DATA / "glove-mini.json"


@pytest.fixture(scope="module")
def runs():
    """Two independent runs of every generator."""
    return make_datasets.generate(), make_datasets.generate()


def readme_row(name: str) -> str:
    """The row of the README's file table that starts with `name`."""
    rows = [line for line in README.splitlines() if line.startswith(f"| `{name}` |")]
    assert len(rows) == 1, f"site/data/README.md needs exactly one table row for {name}, found {len(rows)}"
    return rows[0]


# ---------------------------------------------------------------------- generated files
def test_two_runs_give_identical_bytes(runs):
    first, second = runs
    assert sorted(first) == sorted(second)
    changed = sorted(name for name in first if first[name] != second[name])
    assert not changed, f"these files differ between two runs (an unseeded random source?): {changed}"


def test_every_file_is_at_most_2_mb(runs):
    files, _ = runs
    sizes = {name: len(data) for name, data in files.items()} | {GLOVE.name: GLOVE.stat().st_size}
    too_big = {name: size for name, size in sizes.items() if size > make_datasets.MAX_BYTES}
    assert not too_big, f"spec/03 §9 allows at most 2 MB per file: {too_big}"


def test_site_data_matches_a_fresh_run(runs):
    files, _ = runs
    problems = make_datasets.compare(files, DATA)
    assert not problems, f"site/data is stale; run python tools/make_datasets.py: {problems}"


def test_datasets_are_independent(runs):
    files, _ = runs
    alone = make_datasets.generate(["sms"])
    assert alone == {"sms_small.csv": files["sms_small.csv"]}, "one dataset must not depend on another's draws"
    seeds = [d.seed for d in make_datasets.DATASETS]
    assert len(set(seeds)) == len(seeds), "every dataset needs its own seed"


def test_check_mode_reports_changed_and_unexpected_files(tmp_path, capsys):
    assert make_datasets.main(["sms", "--out", str(tmp_path)]) == 0
    assert make_datasets.main(["sms", "--check", "--out", str(tmp_path)]) == 0
    with (tmp_path / "sms_small.csv").open("a", encoding="utf-8") as f:
        f.write("9999,ham,an extra line\n")
    (tmp_path / "stray.csv").write_text("a,b\n", encoding="utf-8")
    capsys.readouterr()
    assert make_datasets.main(["sms", "--check", "--out", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "sms_small.csv: bytes differ" in out and "stray.csv: not made by make_datasets.py" in out, out


# ---------------------------------------------------------------------- README
def test_readme_documents_every_file_and_its_shape(runs):
    files, _ = runs
    for name, data in files.items():
        shape = make_datasets.shape(name, data)
        assert shape in readme_row(name), f"README row for {name} should say {shape!r}"
    words = len(json.loads(GLOVE.read_text(encoding="utf-8")))
    assert f"{words:,} words" in readme_row(GLOVE.name)
    pages = len(list((DATA / "docs").glob("*.md")))
    assert f"{pages} pages" in readme_row("docs/")


def test_readme_states_the_licences():
    assert "CC0 1.0" in README and "PDDL" in README and "Pennington" in README


# ---------------------------------------------------------------------- GloVe subset
GLOVE_LINES = [
    "the 0.1 0.2\n",
    "of -0.00001 0.5\n",        # rounds to -0.0, written as 0.0
    "x1 1.0 2.0\n",             # not alphabetic: skipped unless asked for
    "bad 1.0\n",                # wrong dimension: skipped
    "cat 0.123456 -0.98765\n",
    "dog 0.3 0.4\n",
]


def test_glove_subset_keeps_frequent_and_requested_words():
    data = make_datasets.glove_subset(GLOVE_LINES, top=2, words=["dog"])
    assert data == make_datasets.glove_subset(GLOVE_LINES, top=2, words=["dog"])
    vectors = json.loads(data)
    assert list(vectors) == ["the", "of", "dog"], "frequency order: the top words, then the requested ones"
    assert vectors["of"] == [0.0, 0.5] and str(vectors["of"][0]) == "0.0"


def test_glove_subset_rounds_to_4_decimals():
    vectors = json.loads(make_datasets.glove_subset(GLOVE_LINES, top=2, words=["cat"]))
    assert vectors["cat"] == [0.1235, -0.9877]


def test_glove_subset_fails_on_a_missing_word():
    with pytest.raises(ValueError, match="zebra"):
        make_datasets.glove_subset(GLOVE_LINES, top=2, words=["dog", "zebra"])


def test_glove_mini_has_every_lesson_word():
    vectors = json.loads(GLOVE.read_text(encoding="utf-8"))
    assert len(vectors) >= make_datasets.GLOVE_TOP
    assert set(make_datasets.GLOVE_WORDS) <= set(vectors), "rebuild glove-mini.json with --glove"
    assert {len(v) for v in vectors.values()} == {50}


# ---------------------------------------------------------------------- handbook
def test_handbook_pages_have_a_header():
    pages = {}
    for path in sorted((DATA / "docs").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---\n\n# ", text, re.DOTALL)
        assert match, f"{path.name}: start with a header between --- lines, then a # title"
        meta = dict(line.split(": ", 1) for line in match.group(1).splitlines())
        assert {"id", "title", "owner", "updated", "status", "audience"} <= set(meta), path.name
        assert meta["status"] in {"current", "archived"}, path.name
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["updated"]), path.name
        assert meta["id"] not in pages, f"{path.name}: id {meta['id']} is used twice"
        pages[meta["id"]] = meta
    for page_id, meta in pages.items():
        if meta["status"] == "archived":
            assert meta.get("replaced_by") in pages, f"{page_id}: an archived page names the page that replaced it"
