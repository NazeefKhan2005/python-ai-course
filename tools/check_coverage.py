"""Prove the course covers "everything available": every public name of every declared target has a row.

  python tools/check_coverage.py             # whole course (CI)
  python tools/check_coverage.py --partial   # while the course is being built: unbuilt items are "pending"
  python tools/check_coverage.py --show class:dict   # print the required names of one target

Targets are declared on reference sections: <section class="api-reference" data-api-targets="class:dict
expr:dict_keys=type({}.keys()) module:json">. Rows name what they document: <tr data-api="dict.get">.
Coverage of a target is the union of rows on every page that declares it. Course-wide checks add every
keyword, every AST node type (in verified code), and every public standard-library module (kw:..., module:...
rows). Exclusions, each with a reason, live in tools/coverage.json.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import doctest
import fnmatch
import importlib
import importlib.util
import inspect
import io
import json
import keyword
import sys
import tokenize
import warnings
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pagekit import Page, site_pages

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CONFIG = Path(__file__).resolve().parent / "coverage.json"
FREE_NAMESPACES = ("syntax:", "concept:")


@dataclass
class Target:
    spec: str
    kind: str
    alias: str
    obj: object

    def full(self) -> set[str]:
        return {f"{self.alias}.{n}" for n in dir(self.obj)} | {self.alias}

    def required(self, ignore: set[str], documented_classes: frozenset = frozenset()) -> set[str]:
        """Module: __all__ (or public non-module names). Class: its own attributes plus those it inherits
        from helper bases (pandas NDFrame, matplotlib _AxesBase...), but not from builtins or from
        classes that are targets themselves (Counter doesn't repeat dict; Path doesn't repeat PurePath)."""
        if self.kind == "module":
            names = getattr(self.obj, "__all__", None)
            if names is None:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    names = [n for n in dir(self.obj) if not n.startswith("_")
                             and not inspect.ismodule(getattr(self.obj, n, None))]
            return {f"{self.alias}.{n}" for n in names}
        names = set()
        for cls in self.obj.__mro__:
            if cls is not self.obj and (cls.__module__ == "builtins" or cls in documented_classes):
                continue
            own = vars(cls)
            names |= {n for n in own if not n.startswith("_")}
            names |= {n for n in own if n.startswith("__") and n.endswith("__") and n not in ignore}
        return {self.alias} | {f"{self.alias}.{n}" for n in names}


def resolve(spec: str) -> Target:
    """class:dict | class:Counter=collections.Counter | module:json | expr:dict_keys=type({}.keys())"""
    kind, _, rest = spec.partition(":")
    alias, eq, path = rest.partition("=")
    if not eq:
        path = alias
        alias = path.rsplit(".", 1)[-1] if kind == "class" else path
    if kind == "module":
        obj = importlib.import_module(path)
    elif kind == "class":
        obj = _dotted(path)
        if not isinstance(obj, type):
            raise ValueError(f"{spec}: {path} is not a class")
    elif kind == "expr":
        obj = eval(path, {"__builtins__": builtins, "importlib": importlib})  # course-authored text only
        if not isinstance(obj, type):
            obj = type(obj)
    else:
        raise ValueError(f"{spec}: target kind must be class:, module: or expr:")
    return Target(spec, kind, alias, obj)


def _dotted(path: str):
    if "." not in path:
        return getattr(builtins, path)
    parts = path.split(".")
    for cut in range(len(parts) - 1, 0, -1):
        try:
            obj = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue
        for part in parts[cut:]:
            obj = getattr(obj, part)
        return obj
    raise ImportError(path)


# ---------------------------------------------------------------------- code inventory
def code_blocks(page: Page):
    """Every piece of Python on a page that the content checker verifies (compiled, run or tested)."""
    for node in page.scripts("text/x-python"):
        if node.get("data-expect") != "SyntaxError":
            yield node, page.code(node)
    for node in page.scripts("text/x-pycon"):
        examples = doctest.DocTestParser().get_examples(page.code(node))
        yield node, "\n".join(ex.source for ex in examples)


def syntax_used(blocks) -> tuple[set[str], set[str]]:
    nodes, words = set(), set()
    for _, code in blocks:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            nodes.add(type(node).__name__)
            if isinstance(node, ast.Match):
                words |= {"match", "case"}
            elif isinstance(node, ast.TypeAlias):
                words.add("type")
            elif isinstance(node, ast.MatchAs) and node.pattern is None and node.name is None:
                words.add("_")
            elif isinstance(node, (ast.Import, ast.ImportFrom)) and getattr(node, "is_lazy", 0):
                words.add("lazy")
        try:
            for tok in tokenize.generate_tokens(io.StringIO(code).readline):
                if tok.type == tokenize.NAME and keyword.iskeyword(tok.string):
                    words.add(tok.string)
        except (tokenize.TokenError, SyntaxError):
            pass
    return nodes, words


# ---------------------------------------------------------------------- checker
@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def excluded(name: str, rules: dict) -> bool:
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in rules)


def check(pages: list[Page], config: dict, partial: bool) -> Result:
    res = Result()
    ignore = set(config["ignore_dunders"])
    targets: dict[str, Target] = {}
    declared_on: dict[str, list[Page]] = {}
    rows: dict[str, list[tuple[Page, object]]] = {}
    version = sys.version_info[:2]

    for page in pages:
        for section in page.all("section", cls="api-reference"):
            for spec in (section.get("data-api-targets") or "").split():
                try:
                    target = targets.get(spec) or resolve(spec)
                except Exception as err:  # noqa: BLE001 - report any resolution failure
                    res.errors.append(f"{page.path.name}:{section.line}: cannot resolve target {spec}: {err}")
                    continue
                targets[spec] = target
                declared_on.setdefault(spec, []).append(page)
        for node in page.root.iter():
            for name in (node.get("data-api") or "").split():
                rows.setdefault(name, []).append((page, node))

    aliases = sorted({t.alias: t for t in targets.values()}.items(), key=lambda kv: -len(kv[0]))

    def owner(name: str):
        """The declared target a row name belongs to (longest alias wins: os.path before os)."""
        return next((t for alias, t in aliases if name == alias or name.startswith(alias + ".")), None)

    documented = set(rows)
    stdlib = {m for m in sys.stdlib_module_names if not m.startswith("_")} | set(config["stdlib"]["include"])

    # every row must name something real
    for name, places in sorted(rows.items()):
        page, node = places[0]
        where = f"{page.path.name}:{node.line}"
        newer = node.get("data-version") and tuple(map(int, node.get("data-version").split("."))) > version
        if name.startswith(FREE_NAMESPACES):
            continue
        if name.startswith("kw:"):
            if name[3:] not in keyword.kwlist + keyword.softkwlist:
                res.errors.append(f"{where}: {name} is not a Python keyword")
        elif name.startswith("module:"):
            top = name[7:].split(".")[0]
            if top not in stdlib and importlib.util.find_spec(top) is None and not newer:
                res.errors.append(f"{where}: {name} is not a module")
        else:
            target = owner(name)
            if target is None:
                res.errors.append(f"{where}: data-api {name!r} does not belong to any declared target")
            elif name not in target.full() and not newer:
                res.errors.append(f"{where}: {name} does not exist in this Python ({sys.version.split()[0]})")

    # every required name of every declared target needs a row (or an exclusion with a reason)
    exclusions = config["exclude"]
    classes = frozenset(t.obj for t in targets.values() if t.kind != "module")
    for spec, target in sorted(targets.items()):
        rules = exclusions.get(target.alias, {})
        for name, reason in rules.items():
            if not str(reason).strip():
                res.errors.append(f"coverage.json: exclusion {target.alias}.{name} needs a reason")
            full_name = f"{target.alias}.{name}"
            if not any(fnmatch.fnmatchcase(n, full_name) for n in target.full()):
                res.errors.append(f"coverage.json: stale exclusion {full_name} (no such attribute)")
        required = target.required(ignore, classes)
        missing = sorted(n for n in required - documented
                         if not excluded(n[len(target.alias) + 1:], rules))
        pages_ = ", ".join(sorted({p.path.name for p in declared_on[spec]}))
        if missing:
            res.errors.append(f"{spec} ({pages_}): {len(missing)} name(s) without a row: {', '.join(missing)}")
        else:
            res.notes.append(f"{spec}: complete ({len(required)} names)")

    def course_item(label: str, missing: list[str]):
        if not missing:
            res.notes.append(f"{label}: complete")
        elif partial:
            res.pending.append(f"{label}: {len(missing)} pending: {', '.join(missing)}")
        else:
            res.errors.append(f"{label}: {len(missing)} missing: {', '.join(missing)}")

    declared_specs = set(targets)
    course_item("required targets", sorted(set(config["required_targets"]) - declared_specs))
    nodes, words = syntax_used(b for page in pages for b in code_blocks(page))
    every_kw = keyword.kwlist + keyword.softkwlist
    course_item("keywords used in verified code", sorted(set(every_kw) - words))
    course_item("keyword reference rows", sorted(k for k in every_kw if f"kw:{k}" not in documented))
    leaf = {c.__name__ for c in vars(ast).values()
            if isinstance(c, type) and issubclass(c, ast.AST) and c is not ast.AST and not c.__subclasses__()}
    course_item("AST node types in verified code",
                sorted(n for n in leaf - nodes if n not in config["ast"]["exclude"]))
    stdlib_rules = config["stdlib"]["exclude"]
    course_item("standard-library atlas rows",
                sorted(m for m in stdlib if not excluded(m, stdlib_rules) and f"module:{m}" not in documented))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="*", type=Path)
    ap.add_argument("--partial", action="store_true", help="report unbuilt course-wide items as pending")
    ap.add_argument("--show", metavar="TARGET", help="print the required names of one target and exit")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if args.show:
        target = resolve(args.show)
        others = set()
        for spec in config["required_targets"]:
            if not spec.startswith("module:") and spec != args.show:
                with contextlib.suppress(Exception):  # a library that isn't installed
                    others.add(resolve(spec).obj)
        others = frozenset(others)
        print("\n".join(sorted(target.required(set(config["ignore_dunders"]), others))))
        return 0
    pages = [Page(p) for p in (args.pages or site_pages(SITE))]
    res = check(pages, config, args.partial)
    for line in res.errors:
        print(f"MISSING {line}" if "without a row" in line or "missing:" in line else f"ERROR {line}")
    for line in res.pending:
        print(f"pending {line[:300]}{'...' if len(line) > 300 else ''}")
    if args.verbose:
        for line in res.notes:
            print(f"ok {line}")
    print(f"check_coverage: {len(pages)} page(s), {len(res.errors)} error(s), {len(res.pending)} pending")
    return 1 if res.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
