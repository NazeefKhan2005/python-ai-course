"""Print draft reference-table rows for a coverage target, one per required name.

  python tools/api_skeleton.py class:dict
  python tools/api_skeleton.py "expr:dict_keys=type({}.keys())" --var keys

Each row carries the real signature and the first docstring line as a TODO description. Rewrite every
description in course voice, set data-level, group related names into one row (data-api takes several
names), then remove the TODO markers: check_site.py rejects pages that still contain them.
"""
from __future__ import annotations

import argparse
import html
import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_coverage import CONFIG, resolve
from pagekit import api_id

SYNTAX = {
    "__getitem__": "{x}[key]", "__setitem__": "{x}[key] = value", "__delitem__": "del {x}[key]",
    "__contains__": "item in {x}", "__len__": "len({x})", "__iter__": "iter({x})", "__reversed__": "reversed({x})",
    "__repr__": "repr({x})", "__str__": "str({x})", "__hash__": "hash({x})", "__bool__": "bool({x})",
    "__format__": "format({x}, spec)", "__call__": "{x}(...)", "__eq__": "{x} == other", "__ne__": "{x} != other",
    "__lt__": "{x} < other", "__le__": "{x} <= other", "__gt__": "{x} > other", "__ge__": "{x} >= other",
    "__add__": "{x} + other", "__radd__": "other + {x}", "__iadd__": "{x} += other",
    "__sub__": "{x} - other", "__rsub__": "other - {x}", "__isub__": "{x} -= other",
    "__mul__": "{x} * other", "__rmul__": "other * {x}", "__imul__": "{x} *= other",
    "__truediv__": "{x} / other", "__rtruediv__": "other / {x}", "__itruediv__": "{x} /= other",
    "__floordiv__": "{x} // other", "__rfloordiv__": "other // {x}", "__ifloordiv__": "{x} //= other",
    "__mod__": "{x} % other", "__rmod__": "other % {x}", "__imod__": "{x} %= other",
    "__divmod__": "divmod({x}, other)", "__rdivmod__": "divmod(other, {x})",
    "__pow__": "{x} ** other", "__rpow__": "other ** {x}", "__ipow__": "{x} **= other",
    "__matmul__": "{x} @ other", "__rmatmul__": "other @ {x}", "__imatmul__": "{x} @= other",
    "__and__": "{x} &amp; other", "__rand__": "other &amp; {x}", "__iand__": "{x} &amp;= other",
    "__or__": "{x} | other", "__ror__": "other | {x}", "__ior__": "{x} |= other",
    "__xor__": "{x} ^ other", "__rxor__": "other ^ {x}", "__ixor__": "{x} ^= other",
    "__lshift__": "{x} &lt;&lt; n", "__rlshift__": "n &lt;&lt; {x}", "__ilshift__": "{x} &lt;&lt;= n",
    "__rshift__": "{x} &gt;&gt; n", "__rrshift__": "n &gt;&gt; {x}", "__irshift__": "{x} &gt;&gt;= n",
    "__neg__": "-{x}", "__pos__": "+{x}", "__abs__": "abs({x})", "__invert__": "~{x}",
    "__int__": "int({x})", "__float__": "float({x})", "__complex__": "complex({x})", "__index__": "operator.index({x})",
    "__round__": "round({x}, ndigits)", "__trunc__": "math.trunc({x})", "__floor__": "math.floor({x})",
    "__ceil__": "math.ceil({x})", "__bytes__": "bytes({x})", "__enter__": "with {x}:", "__exit__": "with {x}: (exit)",
    "__class_getitem__": "{cls}[T]", "__missing__": "subclass hook: called for a missing key",
    "__getattr__": "{x}.name (fallback)", "__setattr__": "{x}.name = value", "__delattr__": "del {x}.name",
    "__dir__": "dir({x})", "__copy__": "copy.copy({x})", "__deepcopy__": "copy.deepcopy({x})",
    "__buffer__": "memoryview({x})", "__release_buffer__": "(buffer protocol)", "__fspath__": "os.fspath({x})",
    "__await__": "await {x}", "__aiter__": "async for ... in {x}", "__anext__": "anext({x})",
    "__aenter__": "async with {x}:", "__aexit__": "async with {x}: (exit)", "__set_name__": "(descriptor setup)",
    "__get__": "(descriptor get)", "__set__": "(descriptor set)", "__delete__": "(descriptor delete)",
    "__instancecheck__": "isinstance(obj, {x})", "__subclasscheck__": "issubclass(cls, {x})",
    "__length_hint__": "operator.length_hint({x})", "__next__": "next({x})",
}


def signature(obj, name: str, var: str, cls_name: str) -> str:
    if name in SYNTAX:
        return SYNTAX[name].format(x=var, cls=cls_name)
    member = getattr(obj, name, None)
    try:
        sig = str(inspect.signature(member))
        sig = sig.replace("(self, ", "(").replace("(self)", "()").replace("(cls, ", "(")
        return html.escape(f"{var}.{name}{sig}") if callable(member) else html.escape(f"{var}.{name}")
    except (TypeError, ValueError):
        return html.escape(f"{var}.{name}" + ("(...)" if callable(member) else ""))


def first_line(obj) -> str:
    doc = inspect.getdoc(obj) or ""
    return html.escape(doc.strip().split("\n\n")[0].replace("\n", " ")[:160])


def rows(spec: str, var: str | None) -> list[str]:
    target = resolve(spec)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    names = sorted(target.required(set(config["ignore_dunders"])), key=lambda n: (n.count("__") > 0, n))
    var = var or (target.alias if target.kind == "module" else target.alias[0].lower())
    out = []
    for full in names:
        member = full[len(target.alias) + 1:] if full != target.alias else ""
        if not member:
            code, doc = html.escape(f"{target.alias}(...)"), first_line(target.obj)
        elif target.kind == "module":
            code, doc = html.escape(full), first_line(getattr(target.obj, member, None))
        else:
            code, doc = signature(target.obj, member, var, target.alias), first_line(getattr(target.obj, member, None))
        out.append(f'<tr id="{api_id(full)}" data-api="{full}" data-level="TODO">'
                   f'<td><code>{code}</code></td><td>TODO {doc}</td></tr>')
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--var", help="variable name used in examples (default: first letter of the class)")
    args = ap.parse_args(argv)
    print("\n".join(rows(args.target, args.var)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
