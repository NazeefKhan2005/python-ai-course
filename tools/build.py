"""Regenerate every derived file from course.json and the pages. Commit the results (the site must work
from file:// with no build step on the learner's side).

  python tools/build.py           # write manifest.js, search-index.js, api-index.html, exercise packs
  python tools/build.py --check   # fail if any generated file is out of date (CI)

Derived files:
  site/assets/js/manifest.js      window.COURSE = {course.json + exercises/quiz/pack per lesson}
  site/assets/js/search-index.js  window.SEARCH_INDEX = [lessons, sections, reference rows, terms, exercises]
  site/api-index.html             A-Z index of every reference row, grouped by target
  site/downloads/*.zip            exercise packs (tools/export_exercises.py)
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_exercises import lesson_pages, packs
from packs import exercises
from pagekit import Page, site_pages

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SHELL = ROOT / "templates" / "page-shell.html"


def manifest(course: dict, site: Path) -> dict:
    data = json.loads(json.dumps(course))
    found = {lesson["id"]: page for _, lesson, page in lesson_pages(course, site)}
    for module in data["modules"]:
        for lesson in module["lessons"]:
            page = found.get(lesson["id"])
            if page is None:
                continue
            desc = page.first("meta", name="description")
            lesson["description"] = desc.get("content", "") if desc else ""
            items = exercises(page)
            lesson["exercises"] = [{"id": e.id, "title": e.title, "optional": e.optional} for e in items]
            quizzes = [q.get("id") for q in page.all("section", cls="quiz")]
            lesson["quiz"] = next((q for q in quizzes if q.endswith("-quiz")), None)
            lesson["pack"] = f"downloads/{lesson['id']}.zip" if items else None
    return data


def search_entries(site: Path, course: dict) -> list[dict]:
    labels = {f"{m['path']}{l['file']}": f"{l['id'].upper()} {l['title']}" for m in course["modules"] for l in m["lessons"]}
    out = []
    for path in site_pages(site):
        page = Page(path)
        if page.body is None or page.body.get("data-generated") is not None:
            continue
        rel = path.relative_to(site).as_posix()
        h1 = page.first("h1")
        where = labels.get(rel, h1.text() if h1 else rel)
        desc = page.first("meta", name="description")
        out.append({"t": h1.text() if h1 else rel, "u": rel, "k": page.kind,
                    "s": desc.get("content", "") if desc else "", "m": where})
        for node in page.root.iter():
            ident = node.get("id")
            if not ident:
                continue
            level = Page.level_of(node) or ""
            if node.tag in ("h2", "h3"):
                out.append({"t": node.text(), "u": f"{rel}#{ident}", "k": "section", "l": level, "m": where})
            elif node.get("data-api"):
                cells = [n for n in node.elements() if n.tag in ("td", "th")]
                code = next((n.text() for n in node.iter() if n.tag == "code"), node.get("data-api"))
                out.append({"t": code, "a": node.get("data-api"), "u": f"{rel}#{ident}", "k": "api", "l": level,
                            "s": cells[1].text()[:140] if len(cells) > 1 else "", "m": where})
            elif node.tag == "dfn":
                out.append({"t": node.text(), "u": f"{rel}#{ident}", "k": "term", "l": level, "m": where})
            elif node.tag == "article" and node.has_class("exercise"):
                title = next((n.text() for n in node.iter() if n.tag in ("h3", "h4")), ident)
                out.append({"t": title, "u": f"{rel}#{ident}", "k": "exercise", "m": where})
    return out


def api_index(entries: list[dict]) -> str:
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        if entry["k"] != "api":
            continue
        for name in entry["a"].split():
            key = name.split(":")[0] + ":" if ":" in name else name.split(".")[0]
            groups.setdefault(key, []).append({**entry, "name": name})
    nice = {"kw:": "Keywords", "module:": "Standard-library atlas", "syntax:": "Syntax", "concept:": "Concepts"}
    parts = [('<p class="lead">Every name documented in a reference table, with a link to its row. '
              'Use the search box (press <kbd>/</kbd>) to jump straight to one.</p>')]
    toc = []
    for key in sorted(groups, key=str.lower):
        anchor = "idx-" + "".join(ch if ch.isalnum() or ch in "_-" else "-" for ch in key).strip("-")
        title = nice.get(key, key)
        toc.append(f'<li><a href="#{anchor}">{html.escape(title)}</a></li>')
        items = "".join(
            f'<li><a href="{html.escape(e["u"])}"><code>{html.escape(e["name"])}</code></a>'
            f' <span class="muted">{html.escape(e["m"])}</span></li>'
            for e in sorted(groups[key], key=lambda e: e["name"].lower()))
        parts.append(f'<section id="{anchor}"><h2>{html.escape(title)}</h2><ul class="api-index">{items}</ul></section>')
    if not groups:
        parts.append("<p>No reference tables yet.</p>")
    body = f'<nav aria-label="Index sections"><ul class="chips">{"".join(toc)}</ul></nav>' + "".join(parts)
    shell = SHELL.read_text(encoding="utf-8")
    return (shell.replace("{{title}}", "API index").replace("{{description}}", "A-Z index of every documented name")
            .replace("{{root}}", "").replace("{{page}}", "reference").replace("{{content}}", body))


def outputs(site: Path = SITE) -> dict[str, bytes]:
    course = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
    files = {
        "assets/js/manifest.js": ("window.COURSE = " + json.dumps(manifest(course, site), ensure_ascii=False,
                                                                    separators=(",", ":")) + ";\n").encode(),
    }
    entries = search_entries(site, course)
    files["assets/js/search-index.js"] = ("window.SEARCH_INDEX = " + json.dumps(
        entries, ensure_ascii=False, separators=(",", ":")) + ";\n").encode()
    files["api-index.html"] = api_index(entries).encode()
    files.update(packs(course, site))
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    stale = 0
    for rel, data in outputs().items():
        path = SITE / rel
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                print(f"out of date: site/{rel}")
                stale += 1
        elif not path.exists() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(f"wrote site/{rel}")
    if args.check:
        print(f"build --check: {'all generated files up to date' if not stale else f'{stale} stale file(s): run python tools/build.py'}")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
