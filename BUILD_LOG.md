# Build log

What each build session did, newest first. Read the block below at the start of every session (`CLAUDE.md` §9).

## Current state / Next step

**Current state (2026-11-23):** Stage 0 is done. The repository is on git branch `main` with the layout of `CLAUDE.md` §5, `.gitignore`, `DECISIONS.md`, this log and a short `README.md`. `.venv` has Python 3.15.2, the version the kit was verified with, and all 65 pinned libraries at their pinned versions; all 22 of the kit's library checks pass. There are no tools, templates, pages or `course.json` yet: Stage 1 adds them.

**Next step:** Stage 1, the platform (`spec/11`). Quit Claude Code, run `source .venv/bin/activate`, start `claude` again and type `/stage 1`.

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
