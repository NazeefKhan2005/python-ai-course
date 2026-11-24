# Build log

What each build session did, newest first. Read the block below at the start of every session (`CLAUDE.md` §9).

## Current state / Next step

**Current state (2026-11-24):** Stages 0, 1 and 2 are done. The platform is in place, byte for byte from the spec, except for two macOS fixes to the setup page: the `libomp` step and the certificate step. `site/data/` now holds the course datasets:
* 18 generated files from 11 seeded datasets (`tools/make_datasets.py`);
* `glove-mini.json`, a 2,368-word GloVe subset;
* `docs/`, the 18-page Colibrí handbook.

`site/data/README.md` documents all of them. `python tools/ci.py --partial` passes every step, including 12 new dataset tests. `course.json` holds the kit's sample: M03-L04 is the only written lesson. The site is live at https://nazeefkhan2005.github.io/python-ai-course/ from the public repository https://github.com/NazeefKhan2005/python-ai-course. Every push to `main` runs `ci.py --partial` and then deploys. Stage 2 and the two fixes passed the checks on GitHub's Linux runner in pull request #1 and were merged into `main` on 2026-11-24.

**Exercise data (decided 2026-11-24):** tests build their own data (`CLAUDE.md` §2, "Exercise data"). When a module is built, apply the notes in "Decision · Exercise data" below to the M05, M08, M11, M12 and M16 projects, M13-L04 E1, M17-L07 E1 and M18-L05 E1.

**Next step:** Stage 3, the site shell pages: `syllabus.html`, `glossary.html` and `certificate.html` (`spec/11`). Start `claude` with `.venv` active and type `/stage 3`.

## Check · Stage 2 on GitHub's Linux runner (2026-11-24)

**Done**

* Pushed the branch `stage-2-datasets` and opened pull request #1. The branch holds Stage 2 (`df3fd25`), the exercise-data decision (`857685c`) and the certificate step (`aa74c48`). For a pull request, the workflow runs the check job but not the deploy job.
* The check job passed in 4 min 17 s on the `ubuntu-26.04` runner image (x64, CPython 3.15.2): https://github.com/NazeefKhan2005/python-ai-course/actions/runs/45297406514. Its `ci.py --partial` printed "CI passed". The step results were:
  * "52 passed in 23.87s" (the 12 dataset tests included)
  * library checks: 22 PASS, "all checks passed"
  * ruff: "All checks passed!"
  * "build --check: all generated files up to date"
  * "check_site: 4 page(s), 0 problem(s)"
  * "check_coverage: 4 page(s), 0 error(s), 5 pending"
  * "check_content: 4 page(s), 41 blocks compiled, 29 examples, 9 sessions, 4 exercises, 2 quizzes, 0 skipped, 0 problem(s)"
  * the spec/05 patterns: the same line as on the Mac
  * "smoke_pages: 51 of 51 checks passed"
* So a fresh run of `make_datasets.py` on Linux x64 gives the same bytes as the files made on macOS (Apple silicon), and the SQLite files give the same dump.
* `main` was fast-forwarded to the pull request's commits, plus this entry, and pushed. That push runs the checks again and deploys.

**Open issues**

* GitHub's `ubuntu-latest` is now Ubuntu 26.04. `BUILD-AND-DEPLOY.md` ("On Windows or Linux") still says that WSL 2 with Ubuntu 24.04 "matches GitHub's runner". That part of the sentence is out of date.

## Fix · The macOS certificate step (2026-11-24)

**Done**

* `site/setup.html`: the macOS part of step 1 has a new pitfall callout. It says that Python from the python.org installer cannot check HTTPS certificates until **Install Certificates.command** has run. pip still works, but two kinds of download fail with `CERTIFICATE_VERIFY_FAILED`: `urllib.request` (M15-L04, Phase 3) and torchvision's pretrained weights (Phase 5). The callout gives `"/Applications/Python 3.15/Install Certificates.command"` as a copyable command, and the troubleshooting table has a row for the same error.
* `BUILD-AND-DEPLOY.md` §1 now runs the script after installing Python, and §7 has a troubleshooting row.
* Checked on this Mac:
  * The venv's `ssl.get_default_verify_paths().openssl_cafile` is `/Library/Frameworks/Python.framework/Versions/3.15/etc/openssl/cert.pem`, and that file does not exist.
  * `urllib.request.urlopen("https://www.python.org")` fails with `<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1147)>`.
  * The script installs certifi into the framework Python and points that path at certifi's bundle, so it also fixes the virtual environments made from that Python.
  * The script has not been run on this Mac yet: the owner runs it once (§1).
* `site/setup.html` now departs from `spec/04` §6 in two places (`DECISIONS.md`).

**Checks:** `build.py` had nothing to regenerate (exit 0). `ci.py --partial` printed "CI passed". The step results were:
* "52 passed in 9.25s"
* library checks: "all checks passed"
* ruff: "All checks passed!"
* "build --check: all generated files up to date"
* "check_site: 4 page(s), 0 problem(s)"
* "check_coverage: 4 page(s), 0 error(s), 5 pending"
* "check_content: 4 page(s), 41 blocks compiled, 29 examples, 9 sessions, 4 exercises, 2 quizzes, 0 skipped, 0 problem(s)"
* the spec/05 patterns: "check_content: 1 page(s), 18 blocks compiled, 0 examples, 0 sessions, 6 exercises, 1 quizzes, 0 skipped, 0 problem(s)"
* "smoke_pages: 51 of 51 checks passed", including axe-core on the setup page in both themes

## Decision · Exercise data (2026-11-24)

**Done**

* The owner chose option 3 from the first Stage 2 open issue: **tests build their own data**. It is recorded in a new `CLAUDE.md` §2 row, "Exercise data", and in `DECISIONS.md`. The pack contract and `packs.py` are unchanged.
* The same rule covers lesson examples. `check_content.py` runs each verified example in an empty temporary folder with only its `x-file` blocks, so an example that reads `data/sales.csv` would fail. Examples either inline a small file or build their data in code. The full files in `site/data/` are downloads for the learner's own runs; a page shows no output from them that was not produced by a verified run.

**How to apply it when each module is built.** Write each test's data with a fixed seed, keep it small so the tests stay fast, and use the same format as the file in `site/data/`. Then a function that passes the tests also works on the full file.

* **M05 project:** the test writes a log in the `server_logs.txt` format to `tmp_path`. It has known counts by level, a known top 3 of error messages and a known busiest hour, plus edge cases: a blank line, and a level the learner's code has not seen. The project page links `server_logs.txt` so that learners also run `analyze_log` on it.
* **M08 project:** the test writes a log over several days, with traceback continuation lines and cut-off lines, like `server_logs_large.txt`.
* **M11 project:** tests build small arrays (a checkerboard, a ramp, flat shapes) and compare each filter with a NumPy reference.
* **M12 project:** the test writes a small messy CSV with the columns of `food_delivery_messy.csv`, containing each kind of problem at least once.
* **M13-L04 E1:** the test builds a seeded DataFrame with the columns of `student_performance.csv` and compares the 8 answers with a reference computed in the test, within a tolerance.
* **M16 project:** tests build a seeded table with the housing columns and check the comparison logic: every model is fitted, and the baseline is beaten.
* **M17-L07 E1 and M18-L05 E1:** a compact seeded generator in the test file builds data with the fraud columns or the SMS message styles. The targets (recall ≥ 0.80 at precision ≥ 0.30, and the F1 threshold) are calibrated on that data, not on the full files.
* Not affected: M22-L02 E1 and E2 take the vectors as an argument, so their tests pass small vector dictionaries. P5 is graded with a rubric, not with pytest.

**Checks:** only documentation changed (`CLAUDE.md`, `DECISIONS.md`, `BUILD_LOG.md`). Nothing to build.

## Stage 2 · Datasets (2026-11-23)

**Done**

* Listed every dataset that the phase files and the project briefs (`spec/09`) need. `tools/make_datasets.py` generates 11 datasets, 18 files and 9.33 MB in all, into `site/data/` in about 1 second. Each dataset has its own `np.random.default_rng(seed)`, so changing one never changes another.

  | Dataset (seed) | Files | Used in |
  |---|---|---|
  | `server_logs` (101) | `server_logs.txt`: 1,696 lines | M05-L04, M05 project, M06-L01 |
  | `server_logs_large` (102) | `server_logs_large.txt`: 22,411 lines | M08-L02, M08 project, M10-L05 |
  | `images` (111) | `images.npz`: 6 `uint8` arrays | M11-L05, M11 project, E2 |
  | `shop` (121) | `customers.csv` (1,985 rows), `sales.csv` (11,824 rows), `shop.db` (5 tables) | M12, M13-L01, M15-L01 to L03 |
  | `food_delivery` (131) | `food_delivery.db` (150 restaurants, 16,682 orders), `food_delivery_customers.csv` (4,778 rows), `food_delivery_promotions.json` (12 codes), `food_delivery_messy.csv` (2,876 rows) | M12-L04, M12 project, M15, P3 |
  | `student_performance` (141) | `student_performance.csv`: 1,000 rows | M13-L03, M13-L04, M14 |
  | `housing` (161) | `housing_small.csv`: 1,500 rows | M16-L03, M16 project |
  | `telco_churn` (171) | `telco_churn.csv` (7,000 rows), `telco_churn_current.csv` (2,000 rows) | M17, M19, P4, M24, M25-L06, P6 |
  | `transactions_fraud` (181) | `transactions_fraud.csv`: 15,000 rows | M16-L07, M17-L07, M25-L07 |
  | `sms` (191) | `sms_small.csv`: 2,400 rows | M18-L05 |
  | `book_ratings` (201) | `books.csv` (400 rows), `ratings.csv` (32,164 rows) | M18-L08, E6, capstone |

* Each generator asserts the patterns its lessons rely on. If a later edit breaks one, the run fails at once instead of a lesson going wrong. The docstrings list what is planted; the README, which learners read, describes only the columns. The planted patterns:
  * **M05 logs:** busiest hour 13:00 (at least 10 lines ahead); the top errors are 34, 26, 17 and 11.
  * **M08 logs:** tracebacks and 6 cut-off lines.
  * **Shop:** a July sale and a Black Friday peak; regional trends; a tracking outage that leaves `channel` empty; 15 deleted customers whose orders remain; referrals; tied salaries for `RANK`.
  * **Food delivery (the P3 story):** in 2026-Q3 total orders rise 4.7% while repeat orders fall 13%. There are three causes:
    * the LOYAL10 promotion ends;
    * a courier shortage in Lima raises its late share from 0.15 to 0.44;
    * a paid-social campaign brings in customers who reorder less.

    It also has a censoring trap. The messy export has duplicates, label variants, decimal commas, mixed date formats, impossible values and more. The conditions in every promotion's name are enforced, so the data never contradicts them.
  * **Students:** Simpson's paradox for tutoring, outliers and missing values.
  * **Telco:** churn 0.217; Central is the noisiest region. The later batch has data drift and concept drift.
  * **Fraud:** 2.65% fraud, in bursts plus single cases. No single column gives it away.
  * **SMS:** wanted and unwanted versions of service notices; 3.9% duplicate texts.
  * **Ratings:** 3 hidden taste factors and missing-not-at-random ratings.
* `glove-mini.json`, built by `make_datasets.py --glove`:
  * Contents: 2,368 words with 50 dimensions (1.03 MB). These are the 2,000 most frequent alphabetic words plus 368 words chosen for the lessons: analogies, categories and job titles for bias probes.
  * Source: cut from `glove.6B.50d.txt` (SHA-256 `c99ba128…b4aa5b`). Only that member was fetched from `glove.6B.zip` on the official Hugging Face mirror, using HTTP range requests (about 80 MB instead of 862 MB).
  * Licence: PDDL, checked in the GloVe README.
  * Checks: analogies work (king − man + woman → queen; Peru : Lima = Colombia : Bogotá).
* `site/data/docs/` holds the hand-written handbook of Colibrí, the fictional food-delivery company.
  * 18 pages, about 5,300 words.
  * Each page starts with a header: id, title, owner, updated, status, audience.
  * The archived 2024 hybrid-work policy conflicts with the current one, which tests metadata filters.
  * `bogota-office-notes.md` contains a deliberate prompt-injection line for M23-L07, disclosed in the README.
* `site/data/README.md` covers:
  * the conventions;
  * a table of every file with its exact shape and lessons;
  * column tables for every file, with no spoilers;
  * licences: CC0 1.0, the owner's choice; GloVe under PDDL with its citation and source hash;
  * what is not in the folder, and how to rebuild it.
* `tools/tests/test_datasets.py` adds 12 tests:
  * two runs give identical bytes;
  * every file is at most 2 MB;
  * `site/data/` matches a fresh run;
  * datasets are independent, and seeds are unique;
  * `--check` reports changed and unexpected files;
  * the README row for every file states its shape and the licences;
  * GloVe subset rounding, ordering and missing-word errors, tested on a fixture;
  * `glove-mini.json` contains every lesson word;
  * every handbook page has a valid header.
* `site/data/.gitkeep` removed. A new `.gitattributes` marks `site/data/**` as `-text`, so git never converts line endings in the data (`DECISIONS.md`).
* Model checks on the final data (scratch scripts, not committed), for the module builders.
  * **Fraud**, seed 181, split by card 70/30 with `GroupShuffleSplit(random_state=0)`:
    * logistic regression at the default threshold catches only 48% of fraud;
    * on the raw columns, the best precision at recall 0.80 is 0.36 for HistGradientBoosting and 0.43 for logistic regression with `class_weight="balanced"`;
    * with an hour-of-day feature, 0.63 and 0.49;
    * so the M17-L07 E1 target (recall ≥ 0.80 at precision ≥ 0.30) can be met with threshold tuning. Check it again with the exercise's own split.
  * **SMS**, stratified 75/25 split: F1 0.957 (Naive Bayes on counts), 0.948 (logistic regression on TF-IDF), 0.971 (linear SVM on 1–2-grams). A threshold near 0.90 suits M18-L05 E1.
  * **Housing** (log price): R² 0.925 for linear and Ridge, 0.84 for k-NN and 0.92 for a random forest; the dummy model scores 0.
  * **Telco:** logistic regression AUC 0.81 overall, with Central the lowest region at 0.74. The same model scores 0.76 on the later batch.

**Checks**

* `make_datasets.py`: "make_datasets: wrote 18 file(s) to /Users/nazeef05/Projects/python-ai-course/site/data, 9.33 MB in all, largest 1.76 MB". `--check`: "make_datasets --check: 18 file(s), 0 problem(s)". Two separate runs and `site/data/` have the same SHA-256 for all 18 files, `.db` and `.npz` included.
* `build.py` had nothing to regenerate (exit 0).
* `ci.py --partial` printed "CI passed". The step results were:
  * "52 passed in 9.06s" (the 40 earlier tests plus the 12 new ones);
  * library checks: 22 PASS, "all checks passed";
  * ruff: "All checks passed!";
  * "build --check: all generated files up to date";
  * "check_site: 4 page(s), 0 problem(s)";
  * "check_coverage: 4 page(s), 0 error(s), 5 pending";
  * "check_content: 4 page(s), 41 blocks compiled, 29 examples, 9 sessions, 4 exercises, 2 quizzes, 0 skipped, 0 problem(s)";
  * the spec/05 patterns: "check_content: 1 page(s), 18 blocks compiled, 0 examples, 0 sessions, 6 exercises, 1 quizzes, 0 skipped, 0 problem(s)";
  * "smoke_pages: 51 of 51 checks passed".

**Open issues**

* **Packs cannot ship files from `site/data/`. Decide before the M05 project**, which is graded against `data/server_logs.txt`.
  * The conflict: the Phase 3 notes say "exercise packs include the files their tests read", but `tools/packs.py` ships only inline `x-file` blocks from inside the exercise article. A 1 MB CSV cannot sensibly go inline.
  * Option 1: let an `x-file` block name a file in `site/data/` for the pack to copy. This changes a platform contract (`spec/05` §3, `packs.py` and its tests; `CLAUDE.md` rule 12), so the owner must approve it.
  * Option 2: inline small samples.
  * Option 3: tests that build their own data.
  * **Decided 2026-11-24:** option 3, tests build their own data ("Decision · Exercise data" above).
* **The certificate step on macOS.** The python.org build of Python has no CA certificates until "Install Certificates.command" is run. Downloads with `urllib.request` then fail with `CERTIFICATE_VERIFY_FAILED`, as the GloVe download did here; it worked with `SSL_CERT_FILE` set to certifi's bundle. pip is not affected. The setup page needs this step before M15-L04, which teaches `urllib.request`. **Fixed 2026-11-24** ("Fix · The macOS certificate step" above).
* **Deferred datasets:** sentiment text, images for the M21 project and P5 option B, and the elective data (`DECISIONS.md`).
* **Cross-platform freshness.** `test_site_data_matches_a_fresh_run` compares the files made on macOS (Apple silicon) with a fresh run on GitHub's Linux runner. NumPy's draws are expected to be identical there; the first push will confirm it. **Confirmed 2026-11-24:** the test passed on GitHub's `ubuntu-26.04` runner (x64, CPython 3.15.2) in pull request #1 ("Check · Stage 2 on GitHub's Linux runner" above).
* For the record: `glove.6B.50d.txt` has 400,001 lines, each a distinct word with 50 values. The archive's CRC-32 matched on extraction, and GloVe's "400K vocab" is a rounded figure. Nothing to fix.

## Fix · The macOS OpenMP step (2026-11-23)

**Done**

* `site/setup.html` step 6 has a new pitfall callout. It says that on macOS, XGBoost and LightGBM (`requirements-ml.txt`, Phase 4) need the OpenMP library, which pip does not install. It quotes the error learners will see without it, `Library not loaded: @rpath/libomp.dylib`, and gives `brew install libomp` as a copyable command block. The troubleshooting table has a row for the same error.
* `BUILD-AND-DEPLOY.md` §1 now has a `brew install libomp` line, and §7 has a troubleshooting row for the failing XGBoost and LightGBM library check.
* As a result, `site/setup.html` no longer matches `spec/04` §6 byte for byte. The spec was left unchanged because it is read-only unless the owner asks (`DECISIONS.md`).

**Checks:** `build.py` had nothing to regenerate. `ci.py --partial` printed "CI passed". The step results were: "40 passed", 22 library checks passed, ruff "All checks passed!", "build --check: all generated files up to date", "check_site: 4 page(s), 0 problem(s)", "check_coverage: 4 page(s), 0 error(s), 5 pending", "check_content: … 0 problem(s)" for the pages and for the 6 pattern exercises, and "smoke_pages: 51 of 51 checks passed" (axe-core on the setup page in both themes included).

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

**Deploy** (`/deploy`, 2026-11-23)

* `gh repo create python-ai-course --public --source . --remote origin` made the repository. `gh api --method POST …/pages -f build_type=workflow` turned on Pages, and `main` was pushed.
* Run 45133356474 ("Check and publish the course") succeeded. The `check` job took 5m44s and `deploy` took 11s. The CPU-only PyTorch install step worked; `spec/04` §24 had not been able to verify it. On GitHub, `ci.py --partial` printed the same summary lines as locally: "40 passed", "Python 3.15.2: 22 checks … all checks passed", "check_site: 4 page(s), 0 problem(s)", "check_coverage: 4 page(s), 0 error(s), 5 pending", "check_content: … 29 examples, 9 sessions, 4 exercises, 2 quizzes, 0 skipped, 0 problem(s)", the 6 pattern exercises, "smoke_pages: 51 of 51 checks passed" and "CI passed".
* On the live site, the home page, `setup.html`, the M03-L04 lesson, `api-index.html`, the CSS, JS, Prism bundle, a font and `m03-l04.zip` all return HTTP 200, each the same size as the local file.

**Open issues**

* Still open from Stage 0: the `libomp` line for macOS is missing from the setup page and from `BUILD-AND-DEPLOY.md` §1. Stage 1 copied the setup page unchanged, so the fix can go in now, as its own commit. **Fixed** ("Fix · The macOS OpenMP step" above).

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

* The kit's setup instructions miss `libomp` for macOS: the `brew install` line in `BUILD-AND-DEPLOY.md` §1, and the learners' setup page before Phase 4 (`requirements-ml.txt`). Fix both after Stage 1, which copies `site/setup.html` from `spec/04` §6 byte for byte. The new `README.md` already mentions it. **Fixed** after Stage 1 ("Fix · The macOS OpenMP step").
* For elective E4: `import pyspark.pandas` warns "PySpark does not yet fully support pandas >= 3.0.0". The PySpark check passes; check the pandas-on-Spark examples when E4 is built.
