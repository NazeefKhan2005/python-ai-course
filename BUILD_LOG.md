# Build log

What each build session did, newest first. Read the block below at the start of every session (`CLAUDE.md` §9).

## Current state / Next step

**Current state (2026-11-23):** Stages 0 and 1 are done. The platform is in place, byte for byte from the spec: `course.json`, the templates, `course.js`, `course.css`, the home and setup pages, every tool, the learner helpers, the unit tests, the workflows, the sample lesson M03-L04 and `examples/spec05-examples.html`. The Prism bundle and fonts are built. `python tools/ci.py --partial` passes every step. `course.json` holds the kit's sample: M03-L04 is the only written lesson.

**Next step:** Stage 2, the datasets (`spec/11`). Start `claude` with `.venv` active and type `/stage 2`. Separately, fix the open `libomp` issue below in a small task of its own (it changes `site/setup.html` and `BUILD-AND-DEPLOY.md`).

## Stage 1 · The platform (2026-11-23)

**Done**

* A script read every block fenced with four backticks in `spec/04` (§1–26), `spec/07` §4 and `spec/08` §8, and took each file's path from the heading above it. That gave 39 files. All 39 are now byte-identical to the spec, and every line count matches the `spec/04` contents table. The script wrote 32 of them. The other 7 are the requirements files from Stage 0, already identical, so the script left them alone. New: `course.json`, `templates/{page-shell,lesson-template}.html`, `site/{index,setup}.html`, `site/assets/js/course.js`, `site/assets/css/course.css`, `site/modules/m03-data-structures/l04-dictionaries.html`, `tools/{pagekit,packs,check_site,check_content,check_coverage,api_skeleton,export_exercises,build,ci,check_pins,check_libraries}.py`, `tools/coverage.json`, `tools/smoke_pages.mjs`, `tools/vendor/build_{prism,fonts}.py`, `tools/learner/{conftest,course_helpers,course_mocks}.py`, `tools/tests/test_tools.py` and its two fixtures, `examples/spec05-examples.html` and `.github/workflows/{site,pins}.yml`. Nothing was changed from the spec.
* npm packages went in with one `npm install --no-save` command: `prismjs@1.30.0`, `@fontsource-variable/atkinson-hyperlegible-next@5.3.0`, `@fontsource-variable/atkinson-hyperlegible-mono@5.3.0`, `puppeteer-core@25` (resolved to 25.18.1) and `axe-core@4.14.1`. Use one command for all of them: a later `npm install --no-save` removes the packages installed by an earlier one. `node_modules/` is git-ignored.
* `tools/vendor/build_prism.py` printed "wrote site/assets/vendor/prism.bundle.js (33 KB)". `tools/vendor/build_fonts.py` printed "wrote 5 fonts to site/assets/fonts (116 KB)". A lesson loads three of the fonts (87 KB). `course.js` + `course.css` + `prism.bundle.js` come to 151,687 bytes, which matches the 152 KB in `spec/03` §10.
* `python tools/build.py` wrote `manifest.js`, `search-index.js`, `api-index.html`, `site/downloads/m03-l04.zip` and `all-exercises.zip`.
* The `.gitkeep` files are gone from the 8 folders that now have files. They stay in `site/{career,projects,exams,data,notebooks}/`.

**Checks** (`python tools/ci.py --partial`, first run, no fixes needed: "CI passed")

* unit tests: "40 passed in 9.30s"
* library checks: "Python 3.15.2: 22 checks", 22 PASS, "all checks passed"
* ruff on `tools/`: "All checks passed!"
* `build.py --check`: "build --check: all generated files up to date"
* `check_site.py`: "check_site: 4 page(s), 0 problem(s)"
* `check_coverage.py --partial`: "check_coverage: 4 page(s), 0 error(s), 5 pending". With `-v`, all 6 targets show complete: `class:dict` (31 names), `frozendict` (23), `types.MappingProxyType` (24), `dict_items` (23), `dict_keys` (23) and `dict_values` (6). The 5 pending items are course-wide: 133 required targets, 19 keywords used in verified code, 40 keyword rows, 49 AST node types and 186 standard-library atlas rows. They fill in module by module.
* `check_content.py`: "check_content: 4 page(s), 41 blocks compiled, 29 examples, 9 sessions, 4 exercises, 2 quizzes, 0 skipped, 0 problem(s)"
* spec/05 patterns: "check_content: 1 page(s), 18 blocks compiled, 0 examples, 0 sessions, 6 exercises, 1 quizzes, 0 skipped, 0 problem(s)"
* browser: "smoke_pages: 51 of 51 checks passed". That includes axe-core with 0 WCAG 2.2 A/AA problems on the lesson, home, setup and API index pages in both themes, and on the lesson at phone width.

**Open issues**

* Still open from Stage 0: the `libomp` line for macOS is missing from the setup page and from `BUILD-AND-DEPLOY.md` §1. Stage 1 copied the setup page unchanged, so the fix can go in now, as its own commit.

## Stage 0 · Bootstrap the repository (2026-11-23)

**Done**

* `git init -b main`. The first commit, `091f2ec` "Add the build kit", holds the kit exactly as unzipped: the same 32 files as `python-ai-course-kit-v5.zip`, byte for byte (compared file by file with `cmp`). The two Finder `.DS_Store` files were left out (`DECISIONS.md`).
* The layout of `CLAUDE.md` §5: `site/` with `modules/`, `projects/`, `career/`, `exams/`, `notebooks/`, `data/`, `downloads/` and `assets/{css,js,vendor,fonts}/`; `templates/`; `tools/` with `vendor/`, `learner/` and `tests/fixtures/`; `examples/`; `.github/workflows/`. Empty folders hold an empty `.gitkeep`, except `site/assets/vendor/`, `site/assets/fonts/` and `.github/workflows/`, which Stage 1 fills. Delete each `.gitkeep` once its folder has files.
* `.gitignore` with the entries from `spec/11` Stage 0, plus `.DS_Store`, `.pytest_cache/`, `.hypothesis/` and `.ipynb_checkpoints/`. `git check-ignore` confirms each one.
* `README.md` rewritten as a short README for the course repository; the kit's README stays in the first commit.
* `tools/requirements-dev.txt` and the six `site/downloads/requirements-*.txt` copied from `spec/04` §23. A script compared each with the spec text: 7 of 7 byte-identical, 65 pins in all.
* `.venv` created with `python3.15 -m venv .venv` (Python 3.15.0 from python.org, pip 26.2.1), then `python -m pip install -r tools/requirements-dev.txt`: exit code 0, 344 packages, 3.5 GB on disk. Only PySpark and `antlr4-python3-runtime` were built from source, as `spec/04` §23 expects.
* `brew install libomp` (23.1.6): XGBoost and LightGBM load Homebrew's OpenMP runtime on macOS.
* Python 3.15.0 replaced with 3.15.2. A script, run by the owner under `sudo`, moved the python.org install of 3.15.0 to a folder in the Trash: `Python.framework`, the free-threaded `PythonT.framework`, `/Applications/Python 3.15`, the 18 links in `/usr/local/bin` and the 5 installer receipts. Then `python-3.15.2-macos11.pkg` from python.org was installed with its default components (its SHA-256 matches the release page; signed with the Python Software Foundation's Developer ID and notarized by Apple). `.venv` links to the framework, so it needed no reinstall. `python3.15 -m venv --upgrade .venv` set `pyvenv.cfg` to 3.15.2 and moved the venv's own pip from 26.2.1 to the bundled 26.2.2; the 344 installed packages are unchanged.

**Checks** (the course's check tools arrive in Stage 1)

* `pip check`: "No broken requirements found."
* Every pin of the six learner files against the installed version: "65 pins: 65 installed at the pinned version, 0 skipped by marker, 0 wrong or missing" (faiss-cpu's `sys_platform != "win32"` marker applies on macOS).
* The kit's own `check_libraries.py` (`spec/04` §26), run from a scratch copy against `.venv`: "Python 3.15.0: 22 checks", 20 PASS and "2 checks failed": `import 65 pinned libraries` and `XGBoost, LightGBM, SHAP, Optuna, imbalanced-learn, UMAP`. Both fail with `Library not loaded: @rpath/libomp.dylib` (from `lib_lightgbm.dylib` and `libxgboost.dylib`). The same check with scikit-learn's bundled `libomp.dylib` on `DYLD_LIBRARY_PATH`: "[PASS] XGBoost, LightGBM, SHAP, Optuna, imbalanced-learn, UMAP". PySpark's check passes with Java 27.0.1.
* After `brew install libomp` (libomp 23.1.6), the same full run: "Python 3.15.0: 22 checks", 22 PASS, "all checks passed".
* After the move to Python 3.15.2: `pip check` "No broken requirements found."; "65 pins: 65 installed at the pinned version, 0 skipped by marker, 0 wrong or missing"; library checks "Python 3.15.2: 22 checks", 22 PASS, "all checks passed".

**Environment:** macOS 26.5.1 on Apple silicon, Python 3.15.2 from python.org (with the free-threaded build), git 2.50.1, Homebrew with libomp 23.1.6 (keg-only), Node 26.13.1, Google Chrome, Java 27.0.1 (Oracle JDK), GitHub CLI 2.105.0.

**Open issues**

* The kit's setup instructions miss `libomp` for macOS: the `brew install` line in `BUILD-AND-DEPLOY.md` §1, and the learners' setup page before Phase 4 (`requirements-ml.txt`). Fix both after Stage 1, which copies `site/setup.html` from `spec/04` §6 byte for byte. The new `README.md` already mentions it.
* For elective E4: `import pyspark.pandas` warns "PySpark does not yet fully support pandas >= 3.0.0". The PySpark check passes; check the pandas-on-Spark examples when E4 is built.
