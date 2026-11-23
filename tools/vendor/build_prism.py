"""Build site/assets/vendor/prism.bundle.js: Prism core + the languages the course uses.

Run once (and when upgrading Prism):  npm install prismjs@1.30.0 && python tools/vendor/build_prism.py
Prism is MIT-licensed; the licence header is kept at the top of the bundle.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "node_modules/prismjs/components"
# Order matters: dependencies first (clike before javascript; markup before docker/xml-based ones).
LANGUAGES = ["clike", "markup", "css", "javascript", "python", "bash", "sql", "json", "yaml", "toml", "docker", "ini"]

parts = [
    "/*! Prism 1.30.0 | MIT License | https://prismjs.com | bundled for this course: core + "
    + ", ".join(LANGUAGES) + " */",
    # manual mode: the course highlights code itself (no automatic pass over the page)
    "window.Prism = window.Prism || {}; window.Prism.manual = true;",
    (COMPONENTS / "prism-core.min.js").read_text(encoding="utf-8"),
]
parts += [(COMPONENTS / f"prism-{lang}.min.js").read_text(encoding="utf-8") for lang in LANGUAGES]
out = ROOT / "site/assets/vendor/prism.bundle.js"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")
