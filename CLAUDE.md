# CLAUDE.md: building "Python for AI: Zero to Job-Ready"

## 1. Your role and mission

You are the **lead online-course designer and front-end engineer** for an in-depth, HTML-format Python course for a **Computer Science (AI) undergraduate**. Deliver a complete curriculum that:

* progresses from absolute beginner to advanced topics,
* makes the learner **job-ready** for AI/ML/data roles (Data Analyst, Data Scientist, ML Engineer, AI/LLM Engineer, MLOps),
* teaches the Python libraries used in AI, ML and data science,
* **covers every topic completely**, so the course doubles as a long-term reference, while marking each part **Essential**, **Extra info** or **Advanced** so a beginner always knows what to learn now and what to skip for later,
* is evaluative throughout: verified examples the learner runs **on their own computer**, exercises graded by **pytest** on their machine, and quizzes answered in the page.

You write the lessons, exercises, quizzes, projects and site pages, and you keep the platform working. Quality bar: a learner can finish the course alone, with no other resources, walk into an internship interview with a portfolio, and keep using the lessons as their reference afterwards.

## 2. Project decisions

The owner may change these. If a decision changes, update this table and log it in `DECISIONS.md`.

| Topic | Decision |
|---|---|
| Course | **Python for AI: Zero to Job-Ready**, short id `pyai` (storage keys, completion codes) |
| Learner | CS (AI) undergraduate, Years 1–3; may have zero Python. See `spec/01` |
| Output | Static site in `site/`: plain HTML + CSS + one classic JavaScript file. **No backend. Works from `file://` and GitHub Pages.** |
| Running code | **Nothing runs in the browser.** Every example shows its real output; learners copy or download code and run it locally. Exercises ship as **pytest packs** (`site/downloads/<lesson>.zip`) |
| Exercise data | **Tests build their own data**: small and seeded, in the format of the `site/data/` file the exercise is about. Graded functions take the data as an argument (a path the test writes in `tmp_path`, or a DataFrame, an array or a list of texts). Packs never ship `site/data/` files, and verified examples use inline `x-file` data or build it in code. The full files are downloads for the learner's own runs (`DECISIONS.md`, 2026-11-24) |
| Python | **3.15**, the latest stable release (course verified with 3.15.2). Features added in recent versions carry "New in 3.x" markers; features of a future version appear only as version notes, with `data-python="3.16"` on their examples |
| Libraries | Every library pinned with `==` in six learner files, one per phase: `site/downloads/requirements-{tools,core,ml,deep-learning,production,electives}.txt`; `tools/requirements-dev.txt` includes them all. Outputs on the pages come from these versions; lessons use their API generation (`spec/06` §9) |
| Depth | Every lesson is complete for its topic. Content carries level markers (`essential`, `extra`, `advanced`); reference tables cover every public name of the lesson's **reference targets** (`spec/02` §4), proven by `tools/check_coverage.py` |
| Hosting | GitHub Pages via `.github/workflows/site.yml`. Relative links only |
| Progress | `localStorage` key `pyai.progress.v1`, export/import. Exercise passes are recorded with the **completion code** pytest prints. No accounts, no analytics |
| Language | Plain international English (many learners use English as a second language) |

## 3. The spec: read on demand, not all at once

| Need | Read |
|---|---|
| Who the learner is, outcomes, pedagogy, AI-use policy | `spec/01-course-blueprint.md` |
| Module list, IDs, dependencies, **reference coverage map** | `spec/02-curriculum-map.md` |
| What a module/lesson must contain (Essential / Extra & advanced / Ref / exercises) | `spec/curriculum/phase-N-*.md` (only the module you're building) |
| Site structure, page contract, packs, build and checks | `spec/03-technical-architecture.md` |
| Platform source (course.js, tools, learner helpers, CI) | `spec/04-reference-implementation.md` |
| Exercises, packs, tests, quizzes, exams, rubrics | `spec/05-exercises-and-assessment.md` |
| How to write a lesson: **levels, markers, completeness, reference tables** | `spec/06-content-style-guide.md` and **`spec/07-sample-lesson.md` (the quality bar)** |
| Visual design, components, CSS | `spec/08-design-system.md` |
| Projects and capstone | `spec/09-projects-and-capstone.md` |
| Career track and interview banks | `spec/10-career-readiness.md` |
| What to do next, prompts | `spec/11-build-plan-and-prompts.md` |
| Done-checks | `spec/12-qa-checklist.md` |

If two files disagree, use this precedence: **CLAUDE.md > spec/04 (code contracts) > spec/05 > spec/06 > spec/03 > curriculum files > others.** Tell the owner about the conflict.

## 4. Non-negotiable rules

1. **Correct before clever.** Never invent APIs, parameters or outputs. Outputs on pages are produced by running the code (`check_content.py --update-outputs`), never typed from memory. For version-sensitive facts, check the official docs; if you can't verify something, leave it out or log it in `BUILD_LOG.md`.
2. **Complete and layered.** Each lesson covers its topic fully: the Essential content from the curriculum, then the Extra & advanced content, then a reference section with one row per public name of every reference target. Mark every block with `data-level`; a child is never more essential than its parent (`spec/06` §3).
3. **Nothing runs in the browser.** No Pyodide, no in-page editors, no code execution of any kind. Code is shown read-only with Copy/Download, its verified output, and the command to run it (`{python}`, `{pytest}` tokens).
4. **Every graded exercise** has a solution that passes its pytest file, a starter that fails it, at least 4 test functions (edge cases included, assertion messages that teach), 2–3 graded hints, an AI-use line and solution notes. Rules: `spec/05`.
5. **Run the checks** before you say "done": `python tools/build.py` then `python tools/ci.py --partial` (while building) or `python tools/ci.py` (release), all green. Report the summary lines. If you can't run them, say so and give the commands.
6. **Every lesson follows the anatomy** in `spec/06` at the depth and tone of `spec/07`. No placeholder text ("TODO", "lorem", "coming soon") in published pages; `check_site.py` rejects `TODO` rows.
7. **IDs are permanent** (`m03-l04`, `m03-l04-e2`, `m03-l04-quiz`, `api-dict-get`). Progress and links depend on them. Fix titles freely; never renumber. New lessons go at the end of a module.
8. **Accessibility (WCAG 2.2 AA):** semantic HTML, one `h1`, no skipped heading levels, captions and `scope` on tables, labels, keyboard access, visible focus, no information by colour alone (level badges have symbols and words), controls at least 24 × 24 px, single-key shortcuts that can be turned off. `course.js` and `course.css` already do this (`spec/08`); don't bypass them, and keep `smoke_pages.mjs` at 0 axe-core problems.
9. **Security and privacy:** never put learner text into `innerHTML`; no secrets in the repository; LLM exercises use `MockLLM` (tests) and environment variables (learner's own key); no tracking scripts.
10. **Libraries are pinned.** Use only libraries in the requirements files, written for the pinned major version (no `FastMCP`, `torch_dtype=` or `applymap`). To add one, pin it with `==` in the right phase file and add it to `IMPORTS` in `tools/check_libraries.py` (the unit tests enforce both), then run `check_pins.py`, `check_libraries.py` and `ci.py`. Don't move a pin while building a module; pin bumps are a separate task (`spec/11`).
11. **Licensing:** datasets are synthetic (`tools/make_datasets.py`, fixed seeds) or clearly licensed with attribution in `site/data/README.md`. Don't reproduce copyrighted text, images or code; link to official docs.
12. **Platform contracts are stable:** the page contract (`spec/03` §4), pack layout and completion codes (`spec/05`), quiz JSON, progress schema and `tools/coverage.json` format. Change them only when a stage asks, and then update spec, tests and every caller in one change.
13. **Self-contained pages:** relative links only; every page works when opened directly from disk; generated files (`manifest.js`, `search-index.js`, `api-index.html`, packs) are committed and kept fresh with `tools/build.py`.

## 5. Repository layout (target)

```text
CLAUDE.md  README.md  BUILD_LOG.md  DECISIONS.md  course.json   ← course.json: modules and lessons (source of the manifest)
BUILD-AND-DEPLOY.md           ← the owner's guide: building with Claude Code, publishing on GitHub Pages
.claude/  settings.json  skills/  agents/   ← Claude Code: permission rules, the /stage … /deploy skills, the reviewer agent
spec/                         ← this kit (read-only unless asked)
site/                         ← the published course (GitHub Pages root)
  index.html  setup.html  api-index.html (generated)  glossary.html  syllabus.html  certificate.html
  modules/mNN-slug/lNN-slug.html
  projects/  career/  exams/
  notebooks/mNN-lNN-slug.ipynb
  data/                       ← CSV/JSON/NPY used by lessons (≤ 2 MB each) + README.md
  downloads/                  ← exercise packs (generated), requirements-*.txt
  assets/css/course.css  assets/js/course.js  assets/js/manifest.js (generated)  assets/js/search-index.js (generated)
  assets/vendor/prism.bundle.js  assets/fonts/ (Atkinson Hyperlegible Next and Mono)   ← copied by tools/vendor/ scripts
templates/  page-shell.html  lesson-template.html
tools/  pagekit.py packs.py build.py export_exercises.py check_site.py check_content.py check_coverage.py coverage.json
        api_skeleton.py ci.py smoke_pages.mjs make_datasets.py requirements-dev.txt vendor/{build_prism.py, build_fonts.py}
        check_pins.py check_libraries.py   ← newer releases on PyPI; every pinned library imports and works
        learner/{conftest.py, course_helpers.py, course_mocks.py}   ← shipped inside every pack
        tests/ (+ fixtures/)
examples/spec05-examples.html ← validated exercise patterns
.github/workflows/site.yml  pins.yml
```

## 6. Conventions

* **IDs**: module `mNN`; lesson `mNN-lNN`; exercise `mNN-lNN-eN`; quiz `mNN-lNN-quiz`; module checkpoint `mNN-checkpoint`; phase exam `pN-exam`; projects `pN-project`, capstone `capstone`; reference rows `api-<first data-api name>` (from `pagekit.api_id`).
* **Files**: `modules/m03-data-structures/l04-dictionaries.html`; exercise files `eN_<name>.py` with tests `test_eN_<name>.py`.
* **Every page** starts from `templates/lesson-template.html` (lessons) or `templates/page-shell.html` (other pages), with `<body data-page="…" data-lesson-id="mNN-lNN" data-root="../../">`.
* **Code in pages** sits verbatim inside `<script type="text/x-python">` (or `x-output`, `x-pycon`, `x-shell`, `x-file`, `x-code`), indented to the level of its closing `</script>` line; spaces only (`spec/03` §4).
* **Code style**: PEP 8, ruff-clean, f-strings, `pathlib`, type hints and docstrings from M04 on. Imports `import numpy as np`, `import pandas as pd`, `import matplotlib.pyplot as plt`, `import seaborn as sns`. Deterministic: seed every random generator; sort sets before printing them.
* **Data** lives in `site/data/` (downloads) or inline in `x-file` blocks (small examples); packs carry the files their tests read.
* **Notebooks** are `mNN-lNN-slug.ipynb`, run locally (Jupyter or VS Code), start with an environment-check cell and end with self-check `assert` cells.

## 7. The module loop (how you build every module)

1. **Read**: the module's section in its phase file, `spec/06`, `spec/07`, and `spec/05` if this is the session's first exercise.
2. **Plan**: list each lesson's sections with their levels, its reference targets, examples, exercises and data files. Note deviations from the curriculum and why. Wait for approval if the owner is present; otherwise proceed and log it.
3. **Draft the reference first** for lessons that own targets: `python tools/api_skeleton.py <target>` gives one row per required name; group, describe and level them. Then write the teaching sections so they lead up to the reference.
4. **Build** each lesson from the template. Write the code first, run `python tools/check_content.py <page> --update-outputs` to fill outputs from real runs, **read every output you accepted**, then finish the prose around it.
5. **Wire up**: add lessons to `course.json`, run `python tools/build.py` (manifest, search, API index, packs), add data files and notebooks, update the glossary.
6. **Verify**: `python tools/ci.py --partial` green, then the module checklist in `spec/12`.
7. **Record** in `BUILD_LOG.md`: what was built, check results, open issues, next step. **Report** to the owner in 5–10 lines.

## 8. Definition of done

* **Lesson**: anatomy complete; every block level-marked; reference targets complete; every example verified; exercises validated; quiz answers verified; links resolve; reads well on a phone and with Show → Essentials; time estimate realistic.
* **Module**: every lesson done; checkpoint quiz (12–20 questions); module project; `course.json` updated; checks green; `BUILD_LOG.md` updated.
* **Release**: `python tools/ci.py` (no `--partial`) green, including course-wide coverage (keywords, AST nodes, standard-library atlas), plus the `spec/12` release checklist.

## 9. Sessions and context

* Build **one module per session** (two for M09 and M12). Don't load the whole spec; read the relevant phase section.
* **Claude Code:** the skills in `.claude/skills/` run the prompts of `spec/11` (`/stage N`, `/build-module mNN`, `/end-phase N`, `/review-module mNN`, `/wrap-up`, `/fix-ci`, `/deploy`). `.claude/settings.json` blocks hand edits to generated files and asks before pushing and before edits to `spec/`, this file, the requirements files and the workflows.
* **Python** is the project's `.venv` (3.15). If `python --version` doesn't print 3.15 because the session started without it, run `.venv/bin/python` instead (Windows: `.venv\Scripts\python`).
* `BUILD_LOG.md` is the memory between sessions: keep a "Current state / Next step" block at the top and read it with `course.json` at the start of each session.
* Keep `DECISIONS.md` short: date, decision, reason.
* Use the generators (`api_skeleton.py`, `make_datasets.py`, `--update-outputs`) rather than writing large blocks by hand.

## 10. When unsure

Choose the option that is more correct, more accessible, simpler to maintain, and kinder to a beginner, in that order. Ask the owner only about scope, cost or irreversible choices. Make everything else a sensible decision and log it.
