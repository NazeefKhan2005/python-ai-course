"""pagekit: read course pages for the build and check tools (standard library only).

Course pages are strict HTML: every non-void element is closed explicitly, so a small parser can
build a full tree, report the exact source offsets of every <script>, and let tools rewrite
script contents in place (check_content.py --update-outputs).
"""
from __future__ import annotations

import bisect
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
RAW_TEXT = {"script", "style"}
LEVELS = ("essential", "extra", "advanced")
LEVEL_RANK = {name: rank for rank, name in enumerate(LEVELS)}
LEVEL_LABELS = {"essential": "Essential", "extra": "Extra info", "advanced": "Advanced"}
KINDS = {
    "tip": "Tip", "pitfall": "Common mistake", "version": "Version note", "interview": "Interview",
    "job": "On the job", "hood": "Under the hood", "try": "Try it yourself", "deprecated": "Deprecated",
    "performance": "Performance", "security": "Security", "note": "Note",
}
CHANGES = {"added", "changed", "deprecated", "removed"}
CODE_TYPES = {"text/x-python", "text/x-output", "text/x-pycon", "text/x-shell", "text/x-stdin", "text/x-file",
              "text/x-code", "application/json"}
EXERCISE_KINDS = {"function", "program", "fix", "refactor", "write_tests"}


def dedent(text: str) -> str:
    """Normalise the text of a <script> code block. course.js implements the same rules.

    If the last line (the one holding </script>) is whitespace-only, its width is the base indent;
    otherwise the common indent of the non-blank lines is used. Each line loses at most the base
    indent, trailing whitespace is dropped, and so are blank lines at the start and the end.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    base = None
    if len(lines) > 1 and lines[-1].strip(" ") == "":
        base = len(lines[-1])
        lines = lines[:-1]
    lines = [line.rstrip() for line in lines]
    if base is None:
        base = min((len(line) - len(line.lstrip(" ")) for line in lines if line), default=0)
    out = [line[min(base, len(line) - len(line.lstrip(" "))):] for line in lines]
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


@dataclass(eq=False)
class Node:
    tag: str
    attrs: dict
    parent: Node | None
    line: int
    start: int
    children: list = field(default_factory=list)  # Node or str, in document order
    content_start: int = -1  # raw-text elements only: offsets of the text between the tags
    content_end: int = -1

    def get(self, name: str, default=None):
        return self.attrs.get(name, default)

    @property
    def classes(self) -> set[str]:
        return set((self.attrs.get("class") or "").split())

    def has_class(self, name: str) -> bool:
        return name in self.classes

    def iter(self):
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed([c for c in node.children if isinstance(c, Node)]))

    def elements(self):
        return [c for c in self.children if isinstance(c, Node)]

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def closest(self, predicate):
        return next((a for a in self.ancestors() if predicate(a)), None)

    def text(self) -> str:
        parts = []
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
            elif child.tag not in RAW_TEXT:
                parts.append(child.text())
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def describe(self) -> str:
        ident = f"#{self.attrs['id']}" if self.attrs.get("id") else ""
        return f"<{self.tag}{ident}> line {self.line}"


class _Parser(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", source)]
        self.root = Node("#document", {}, None, 1, 0)
        self.stack = [self.root]
        self.errors: list[str] = []

    def abs_pos(self) -> int:
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        names = [name for name, _ in attrs]
        if len(names) != len(set(names)):
            self.errors.append(f"line {self.getpos()[0]}: duplicate attribute on <{tag}>")
        node = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.stack[-1],
                    self.getpos()[0], self.abs_pos())
        self.stack[-1].children.append(node)
        if tag in RAW_TEXT:
            node.content_start = node.start + len(self.get_starttag_text())
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID:
            self.errors.append(f"line {self.getpos()[0]}: <{tag}/> is not a void element; close it with </{tag}>")
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        line = self.getpos()[0]
        if tag in VOID:
            self.errors.append(f"line {line}: </{tag}> closes a void element")
            return
        if self.stack[-1].tag == tag:
            node = self.stack.pop()
        elif any(n.tag == tag for n in self.stack[1:]):
            self.errors.append(f"line {line}: </{tag}> closes <{self.stack[-1].tag}> opened on line {self.stack[-1].line}")
            while self.stack[-1].tag != tag:
                self.stack.pop()
            node = self.stack.pop()
        else:
            self.errors.append(f"line {line}: stray </{tag}>")
            return
        if tag in RAW_TEXT:
            node.content_end = self.abs_pos()

    def handle_data(self, data):
        if self.stack[-1].tag not in RAW_TEXT:
            self.stack[-1].children.append(data)

    def close(self):
        super().close()
        for node in self.stack[1:]:
            self.errors.append(f"line {node.line}: <{node.tag}> is never closed")


class Page:
    def __init__(self, path: Path | str, source: str | None = None):
        self.path = Path(path)
        self.source = source if source is not None else self.path.read_text(encoding="utf-8")
        parser = _Parser(self.source)
        parser.feed(self.source)
        parser.close()
        self.root = parser.root
        self.errors = parser.errors
        self._line_starts = parser.line_starts

    # ------------------------------------------------------------------ queries
    def all(self, tag: str | None = None, cls: str | None = None, **attrs):
        out = []
        for node in self.root.iter():
            if node is self.root or (tag and node.tag != tag) or (cls and not node.has_class(cls)):
                continue
            if all((node.get(k.replace("_", "-")) == v) if v is not True else (k.replace("_", "-") in node.attrs)
                   for k, v in attrs.items()):
                out.append(node)
        return out

    def first(self, tag=None, cls=None, **attrs):
        found = self.all(tag, cls, **attrs)
        return found[0] if found else None

    @property
    def body(self) -> Node | None:
        return self.first("body")

    @property
    def kind(self) -> str:
        return (self.body.get("data-page") if self.body else None) or "page"

    def ids(self) -> dict[str, Node]:
        return {n.attrs["id"]: n for n in self.root.iter() if n.attrs.get("id")}

    def raw(self, node: Node) -> str:
        return self.source[node.content_start:node.content_end]

    def code(self, node: Node) -> str:
        return dedent(self.raw(node))

    def scripts(self, type_: str | None = None) -> list[Node]:
        return [n for n in self.all("script") if type_ is None or n.get("type") == type_]

    def line_of(self, offset: int) -> int:
        return bisect.bisect_right(self._line_starts, offset)

    @staticmethod
    def level_of(node: Node) -> str | None:
        for candidate in (node, *node.ancestors()):
            if candidate.get("data-level"):
                return candidate.get("data-level")
        return None


def replace_scripts(page: Page, replacements: dict[Node, str]) -> str:
    """Return page.source with the given <script> nodes' text replaced by `text` (dedented form).

    The new text is indented to the width of the existing closing line (or the <script> line),
    so the rewritten block reads exactly like a hand-written one.
    """
    source = page.source
    for node, text in sorted(replacements.items(), key=lambda item: -item[0].content_start):
        raw = page.raw(node)
        last = raw.replace("\r\n", "\n").split("\n")[-1]
        if "\n" in raw and last.strip(" ") == "":
            base = len(last)
        else:
            line_start = page._line_starts[page.line_of(node.start) - 1]
            base = len(source[line_start:node.start]) - len(source[line_start:node.start].lstrip(" "))
        pad = " " * base
        body = "\n".join((pad + line) if line else "" for line in text.split("\n"))
        source = source[:node.content_start] + "\n" + body + "\n" + pad + source[node.content_end:]
    return source


def site_pages(site: Path) -> list[Path]:
    return sorted(p for p in site.rglob("*.html") if "assets" not in p.relative_to(site).parts)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def api_id(name: str) -> str:
    """Anchor id of a reference row: api- + its first data-api name, dots as dashes (dict.get -> api-dict-get)."""
    return "api-" + re.sub(r"[^A-Za-z0-9_-]+", "-", name.replace(":", "-").replace(".", "-")).strip("-")


def root_prefix(site: Path, page: Path) -> str:
    """The data-root value a page needs: "" at the site root, "../../" two folders down."""
    return "../" * (len(page.relative_to(site).parts) - 1)
