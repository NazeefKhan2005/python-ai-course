"""Copy the course fonts into site/assets/fonts/: Atkinson Hyperlegible Next (text) and Mono (code).

Run once (and when upgrading the fonts):
  npm install --no-save @fontsource-variable/atkinson-hyperlegible-next@5.3.0 \\
      @fontsource-variable/atkinson-hyperlegible-mono@5.3.0
  python tools/vendor/build_fonts.py
Both are variable fonts (weights 200-800) from the Braille Institute, under the SIL Open Font License 1.1;
the licence is copied next to the files. course.css declares them with @font-face and unicode-range, so a
browser downloads only the subsets and styles a page uses. Without these files the pages fall back to
system fonts.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "node_modules/@fontsource-variable"
OUT = ROOT / "site/assets/fonts"
FILES = {
    "atkinson-hyperlegible-next": ["latin-wght-normal", "latin-ext-wght-normal", "latin-wght-italic"],
    "atkinson-hyperlegible-mono": ["latin-wght-normal", "latin-ext-wght-normal"],
}

OUT.mkdir(parents=True, exist_ok=True)
total = 0
for family, variants in FILES.items():
    for variant in variants:
        src = PACKAGES / family / "files" / f"{family}-{variant}.woff2"
        shutil.copyfile(src, OUT / src.name)
        total += src.stat().st_size
    shutil.copyfile(PACKAGES / family / "LICENSE", OUT / f"{family}-LICENSE.txt")
print(f"wrote {sum(map(len, FILES.values()))} fonts to {OUT.relative_to(ROOT)} ({total // 1024} KB)")
