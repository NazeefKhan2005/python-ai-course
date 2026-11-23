"""Static checks for every page: structure, accessibility, markers, reference rows, links, manifest.

  python tools/check_site.py            # all pages under site/
  python tools/check_site.py PAGE...    # some pages (links to other pages are still checked)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pagekit import (
    CHANGES,
    CODE_TYPES,
    EXERCISE_KINDS,
    KINDS,
    LEVEL_RANK,
    LEVELS,
    Page,
    api_id,
    root_prefix,
    site_pages,
)

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGE_KINDS = {"home", "lesson", "setup", "reference", "project", "exam", "index"}
SCRIPTS = ["assets/vendor/prism.bundle.js", "assets/js/manifest.js", "assets/js/course.js"]
SPECIAL_SECTIONS = {"outcomes", "run-locally", "api-reference", "exercises", "quiz", "summary", "next-steps"}
TOKENS = {"python", "pytest", "pip"}
MAX_MINOR = 15


def load_manifest(site: Path) -> dict:
    text = (site / "assets/js/manifest.js").read_text(encoding="utf-8")
    match = re.search(r"^window\.COURSE = (\{.*\});\s*$", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit("manifest.js must contain one line: window.COURSE = {...};")
    return json.loads(match.group(1))


def planned_files(site: Path, manifest: dict) -> set[Path]:
    return {(site / m["path"] / l["file"]).resolve() for m in manifest["modules"] for l in m["lessons"] if l.get("planned")}


def check_page(page: Page, site: Path, manifest: dict, cache: dict) -> list[str]:
    errs: list[str] = [f"structure: {e}" for e in page.errors]
    add = errs.append
    rel = page.path.relative_to(site).as_posix()
    html_el, body = page.first("html"), page.body
    if not page.source.lstrip().lower().startswith("<!doctype html>"):
        add("must start with <!doctype html>")
    if html_el is None or not html_el.get("lang"):
        add('<html> needs lang="en"')
    if not page.first("meta", charset="utf-8"):
        add('missing <meta charset="utf-8">')
    if not page.first("meta", name="viewport"):
        add("missing viewport meta")
    title = page.first("title")
    if title is None or not title.text():
        add("missing <title>")
    if body is None:
        return errs + ["missing <body>"]
    kind = body.get("data-page")
    if kind not in PAGE_KINDS:
        add(f"body data-page must be one of {sorted(PAGE_KINDS)}")
    prefix = root_prefix(site, page.path)
    if body.get("data-root") != prefix:
        add(f'body data-root must be "{prefix}"')
    srcs = [n.get("src") for n in page.all("script") if n.get("src")]
    if [s.removeprefix(prefix) for s in srcs] != SCRIPTS:
        add(f"scripts must be exactly {SCRIPTS} (relative to data-root), in that order")
    for node in page.all("script"):
        if node.get("src") and "defer" not in node.attrs:
            add(f"{node.describe()}: external scripts need defer")
        if node.get("type") == "module":
            add(f"{node.describe()}: no ES modules (pages must work from file://)")
        if not node.get("src") and node.get("type") not in CODE_TYPES and node.parent.tag != "head":
            add(f"{node.describe()}: unknown script type {node.get('type')!r}")
    if not page.first("link", rel="stylesheet"):
        add("missing course.css stylesheet")

    ids = {}
    for node in page.root.iter():
        for attr in node.attrs:
            if attr.startswith("on"):
                add(f"{node.describe()}: inline event handler {attr}= (use course.js)")
        if (ident := node.get("id")) is not None:
            if not re.fullmatch(r"[A-Za-z][\w.:-]*", ident):
                add(f"{node.describe()}: invalid id {ident!r}")
            if ident in ids:
                add(f"duplicate id {ident!r} (lines {ids[ident].line} and {node.line})")
            ids[ident] = node

    # headings: one h1, no skipped levels
    heads = [n for n in page.root.iter() if re.fullmatch(r"h[1-6]", n.tag)]
    if sum(1 for n in heads if n.tag == "h1") != 1:
        add("exactly one <h1> per page")
    last = 0
    for n in heads:
        level = int(n.tag[1])
        if level > last + 1:
            add(f"{n.describe()}: heading skips from h{last} to h{level}")
        last = level
        if not n.text():
            add(f"{n.describe()}: empty heading")

    # images, links
    for img in page.all("img"):
        if "alt" not in img.attrs:
            add(f"{img.describe()}: missing alt")
        elif not img.get("src", "").startswith(("http", "data:")) and not (page.path.parent / img.get("src", "")).exists():
            add(f"{img.describe()}: image not found: {img.get('src')}")
    for a in page.all("a"):
        href = a.get("href")
        if href is None:
            add(f"{a.describe()}: <a> without href")
            continue
        if not a.text() and not a.get("aria-label"):
            add(f"{a.describe()}: link without text")
        if a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
            add(f"{a.describe()}: target=_blank needs rel=noopener")
        parts = urlsplit(href)
        if parts.scheme or href.startswith(("//", "mailto:")):
            continue
        target = (page.path.parent / unquote(parts.path)).resolve() if parts.path else page.path
        if parts.path and not target.exists():
            if target in cache.setdefault("planned", planned_files(site, manifest)):
                continue  # a lesson listed in course.json as planned: allowed, shown as "coming soon"
            if not (a.get("data-pack") is not None and target.suffix == ".zip"):  # packs appear after build
                add(f"{a.describe()}: broken link {href}")
            continue
        if parts.fragment and target.suffix == ".html":
            other = cache.setdefault(target, Page(target) if target != page.path else page)
            if parts.fragment not in other.ids() and parts.fragment not in ("main", "top"):
                add(f"{a.describe()}: missing anchor #{parts.fragment} in {target.name}")

    # levels and markers
    for node in page.root.iter():
        level = node.get("data-level")
        if level is None:
            continue
        if level not in LEVELS:
            add(f"{node.describe()}: data-level must be one of {LEVELS}")
            continue
        outer = next((a.get("data-level") for a in node.ancestors() if a.get("data-level") in LEVEL_RANK), None)
        if outer and LEVEL_RANK[level] < LEVEL_RANK[outer]:
            add(f"{node.describe()}: {level} content inside {outer} content (a child can't be more essential)")
    main = page.first("main")
    if kind == "lesson" and main is not None:
        for sec in main.elements():
            if sec.tag == "section" and not (sec.classes & SPECIAL_SECTIONS) and not sec.get("data-level"):
                add(f"{sec.describe()}: content sections need data-level ({'/'.join(LEVELS)})")
            if sec.tag == "section" and not sec.get("id"):
                add(f"{sec.describe()}: sections need an id (for links and the table of contents)")
    for aside in page.all("aside", cls="callout"):
        if aside.get("data-kind") not in KINDS:
            add(f"{aside.describe()}: callout data-kind must be one of {sorted(KINDS)}")
        if aside.get("data-kind") == "version" and not aside.get("data-version"):
            add(f"{aside.describe()}: version callouts need data-version")
    for node in page.root.iter():
        version = node.get("data-version")
        if version is not None and not re.fullmatch(rf"3\.(\d|1[0-{MAX_MINOR - 10}])", version):
            add(f"{node.describe()}: data-version must look like 3.12 (3.0-3.{MAX_MINOR})")
    for span in page.all("span", cls="version"):
        if span.get("data-change") not in CHANGES or not span.get("data-version"):
            add(f"{span.describe()}: span.version needs data-version and data-change ({'/'.join(sorted(CHANGES))})")

    # reference rows
    for node in page.root.iter():
        names = (node.get("data-api") or "").split()
        if not node.get("data-api") and "data-api" not in node.attrs:
            continue
        if not names:
            add(f"{node.describe()}: empty data-api")
            continue
        if not node.closest(lambda a: a.has_class("api-reference")):
            add(f"{node.describe()}: data-api rows belong inside section.api-reference")
        if node.get("id") != api_id(names[0]):
            add(f"{node.describe()}: id must be {api_id(names[0])!r}")
        if node.get("data-level") not in LEVELS and not any(a.get("data-level") for a in node.ancestors()):
            add(f"{node.describe()}: reference rows need data-level")
        if node.text().startswith("TODO") or "TODO " in node.text():
            add(f"{node.describe()}: unfinished row (TODO)")
    for sec in page.all("section", cls="api-reference"):
        if not sec.get("data-api-targets") and not sec.get("data-api-free"):
            add(f"{sec.describe()}: api-reference sections declare data-api-targets")
        for table in (n for n in sec.iter() if n.tag == "table"):
            heads = [n for n in table.iter() if n.tag == "th"]
            if not heads or any(th.get("scope") not in ("col", "row") for th in heads):
                add(f"{table.describe()}: table headers need scope=col/row")
            if not any(n.tag == "caption" for n in table.iter()):
                add(f"{table.describe()}: tables need a <caption>")

    # code blocks
    for node in page.all("script"):
        stype = node.get("type")
        holder = node.parent
        if stype == "text/x-output" and not (holder.has_class("example") and any(
                n.get("type") == "text/x-python" for n in holder.elements())):
            add(f"{node.describe()}: x-output belongs in figure.example next to its x-python")
        if stype in ("text/x-stdin", "text/x-file") and not (holder.has_class("example") or holder.has_class("exercise")):
            add(f"{node.describe()}: {stype} belongs in figure.example or article.exercise")
        if stype == "text/x-file" and not node.get("data-name"):
            add(f"{node.describe()}: x-file needs data-name")
        if stype == "text/x-shell":
            for token in re.findall(r"\{(\w+)\}", page.raw(node)):
                if token not in TOKENS:
                    add(f"{node.describe()}: unknown command token {{{token}}} (use {sorted(TOKENS)})")
        if stype == "text/x-code" and not node.get("data-lang"):
            add(f"{node.describe()}: x-code needs data-lang")
        if "\t" in page.raw(node):
            add(f"{node.describe()}: tabs in code (use spaces)")
    for fig in page.all("figure", cls="example"):
        n_py = sum(1 for n in fig.elements() if n.get("type") == "text/x-python")
        if n_py != 1:
            add(f"{fig.describe()}: an example has exactly one x-python block")
        if fig.get("data-raises") and not re.fullmatch(r"[A-Z]\w*(Error|Exception|Warning|Exit|Interrupt|Group)?", fig.get("data-raises")):
            add(f"{fig.describe()}: data-raises must be an exception class name")

    # lesson parts
    lesson_id = body.get("data-lesson-id")
    if kind == "lesson":
        lessons = {l["id"]: (m, l) for m in manifest["modules"] for l in m["lessons"]}
        if lesson_id not in lessons:
            add(f"lesson id {lesson_id!r} is not in course.json")
        else:
            m, l = lessons[lesson_id]
            if f"{m['path']}{l['file']}" != rel:
                add(f"course.json says {lesson_id} lives at {m['path']}{l['file']}, not {rel}")
        if not page.first("meta", name="description"):
            add("lesson pages need <meta name=description>")
        for cls in ("outcomes", "run-locally", "summary"):
            if not page.first("section", cls=cls):
                add(f"lesson pages need section.{cls}")
        run = page.first("section", cls="run-locally")
        if run and page.first("article", cls="exercise"):
            packs = [a for a in run.iter() if a.tag == "a" and "data-pack" in a.attrs]
            if not packs or packs[0].get("href") != f"{prefix}downloads/{lesson_id}.zip":
                add(f"section.run-locally needs <a data-pack href=\"{prefix}downloads/{lesson_id}.zip\">")
    numbers = []
    for ex in page.all("article", cls="exercise"):
        ident, file = ex.get("id", ""), ex.get("data-file", "")
        match = re.fullmatch(rf"{re.escape(lesson_id or '')}-e(\d+)", ident)
        if not match:
            add(f"{ex.describe()}: exercise ids are {lesson_id}-eN")
        else:
            numbers.append(int(match.group(1)))
            if not re.fullmatch(rf"e{match.group(1)}_[a-z0-9_]+\.py", file):
                add(f"{ex.describe()}: data-file must be e{match.group(1)}_<name>.py")
        if ex.get("data-kind") not in EXERCISE_KINDS:
            add(f"{ex.describe()}: data-kind must be one of {sorted(EXERCISE_KINDS)}")
        roles = [n.get("data-role") for n in ex.iter() if n.tag == "script" and n.get("data-role")]
        need = {"starter", "solution"} | ({"target", "mutants"} if ex.get("data-kind") == "write_tests" else {"tests"})
        if set(need) - set(roles) or len(roles) != len(set(roles)):
            add(f"{ex.describe()}: needs exactly one script for each of {sorted(need)}")
        if not any(n.tag == "ol" and n.has_class("hints") for n in ex.iter()):
            add(f"{ex.describe()}: add an <ol class=\"hints\"> (2-3 graded hints)")
        if not any(n.tag in ("h3", "h4") for n in ex.iter()):
            add(f"{ex.describe()}: exercise needs a heading")
    if numbers and sorted(numbers) != list(range(1, len(numbers) + 1)):
        add("exercises must be numbered e1, e2, ... without gaps")
    for quiz in page.all("section", cls="quiz"):
        if quiz.get("id") not in (f"{lesson_id}-quiz", f"{lesson_id}-warmup"):
            add(f"{quiz.describe()}: quiz id must be {lesson_id}-quiz (or {lesson_id}-warmup for the opening retrieval quiz)")
    if kind == "lesson":
        kinds = {a.get("data-kind") for a in page.all("aside", cls="callout")}
        for needed in ("pitfall", "job", "interview"):
            if needed not in kinds:
                add(f"lesson pages need at least one {needed!r} callout (spec/06 §5)")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pages", nargs="*", type=Path)
    ap.add_argument("--site", type=Path, default=SITE)
    args = ap.parse_args(argv)
    site = args.site.resolve()
    manifest = load_manifest(site)
    paths = [p.resolve() for p in args.pages] or site_pages(site)
    cache: dict = {}
    total = 0
    for path in paths:
        page = cache.setdefault(path, Page(path))
        for err in check_page(page, site, manifest, cache):
            print(f"{path.relative_to(site)}: {err}")
            total += 1
    known = {f"{m['path']}{l['file']}" for m in manifest["modules"] for l in m["lessons"] if not l.get("planned")}
    if not args.pages:
        for rel in sorted(known):
            if not (site / rel).exists():
                print(f"course.json: lesson file {rel} does not exist")
                total += 1
    print(f"check_site: {len(paths)} page(s), {total} problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
