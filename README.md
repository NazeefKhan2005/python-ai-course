# Python for AI: Zero to Job-Ready · Course Build Kit (v5)

This kit is a set of Markdown specification files. You give them to **Claude**, and Claude builds a complete, HTML-based Python course for a Computer Science (AI) student: from a learner's first line of Python to job-ready AI, machine-learning and data-science work.

This version reflects seven requests from the owner:

1. **Every lesson covers its topic completely** and doubles as a reference. Completeness is checked by a tool: each lesson owns "reference targets" (`dict`, `str`, `pandas.DataFrame`, `asyncio`…) and must document every public name of them, verified against the real objects in Python 3.15.
2. **Everything is marked by level**: ● **Essential**, ◆ **Extra info**, ▲ **Advanced**, plus kind markers (Tip, Common mistake, Version note, Under the hood, On the job, Interview, Try it yourself, Performance, Security, Deprecated). A **Show** switch hides what the learner doesn't need right now; Show → Essentials turns any lesson, reference tables included, into a cheat sheet.
3. **No code runs in the browser.** Learners run every example and exercise **on their own computer**. Pages show the code, the exact output real Python printed for it, and the command to run it. Exercises are pytest packs; a passing run prints a completion code that records progress on the page. Quizzes are still answered in the page.

4. **It targets Python 3.15**, the latest stable release: its new features are taught as current Python, and everything is verified with 3.15.2.
5. **Every library is pinned to its newest release that installs on Python 3.15**: 65 libraries, checked on 23 Nov 2026, in one requirements file per phase. A weekly check reports newer releases.
6. **A learning-first interface.** Type designed for legibility (Atkinson Hyperlegible, with its monospace for code), essentials highlighted like a highlighter pen, code + command + real output joined in one "run cell", an "On this page" rail that follows your reading, "continue where you left off", reading settings (text size, theme, Show, shortcuts) and WCAG 2.2 AA checked by axe-core on every build (`spec/08`).
7. **Built and published with Claude Code.** The kit carries a Claude Code project setup: skills that run each stage and module of the build plan (`/stage`, `/build-module`, `/end-phase`, `/review-module`, `/wrap-up`, `/fix-ci`, `/deploy`), permission rules that protect generated files and ask before anything is pushed, and an independent reviewer agent. **`BUILD-AND-DEPLOY.md`** walks you from an empty folder to the course on GitHub Pages, and the site publishes while it is being built.

The platform that makes this work (page behaviour, the build, the checks that run every example and exercise, the coverage checker, the learner's pytest plugin) is **already built and tested** in `spec/04`, so Claude builds on proven code.

---

## What Claude will build from this kit

| | |
|---|---|
| **Scope** | Orientation + 6 phases: 28 modules, 199 lessons (312 h of lessons), 6 portfolio projects and a capstone: about 430 study hours |
| **Depth** | Each lesson: essentials first, then extra and advanced sections, then complete reference tables for its targets. The coverage map (`spec/02` §4) assigns 139 targets, including every built-in type, the most-used standard-library modules, NumPy, pandas, Matplotlib, scikit-learn and PyTorch. Course-wide, every keyword, every piece of syntax and every standard-library module is covered |
| **Running code** | Verified examples with Copy/Download and a run command rendered for the learner's setup (`python`, `python3`, `py` or `uv`); predict-first examples; a setup guide for Windows, macOS and Linux |
| **Evaluation** | pytest exercise packs (functions, programs, data/plot/SQL/model tasks, relative speed checks, "write the tests" mutation exercises), completion codes, hint ladders, gated solutions, in-page quizzes (5 types), checkpoints, timed phase exams |
| **AI/ML/DS stack** | NumPy, pandas, Matplotlib/Seaborn, SciPy/statsmodels, scikit-learn, XGBoost/LightGBM, PyTorch, Hugging Face, LLM APIs, RAG, agents, FastAPI, Docker, MLflow, GitHub Actions |
| **Job readiness** | Git from day one, interview and on-the-job callouts in every lesson, a DSA module, ML system design, CV/GitHub guides, take-home simulations, mock interviews, deployed portfolio projects |
| **Quality** | Works offline from `file://` and on GitHub Pages, dark mode, mobile, text-size setting, print-friendly cheat sheets, WCAG 2.2 AA, client-side search and an A–Z API index. CI runs every example twice, every exercise, every quiz answer, the coverage check, a headless-browser test and axe-core accessibility checks, then deploys |

---

## The files

| File | Purpose | Claude needs it when… |
|---|---|---|
| `CLAUDE.md` | Master instructions: role, decisions, rules, conventions, workflow, definition of done | Always (Claude Code loads it automatically) |
| `BUILD-AND-DEPLOY.md` | **Your** guide: install the tools, run the sessions, publish on GitHub Pages, fix common problems | Before you start, and whenever you're unsure what to run next |
| `.claude/settings.json` | Claude Code permission rules: what runs without asking, what asks first (pushes, edits to `spec/` and `CLAUDE.md`), what is blocked (hand edits to generated files, force pushes) | Every Claude Code session (loaded automatically) |
| `.claude/skills/*/SKILL.md` | The `/stage`, `/build-module`, `/end-phase`, `/review-module`, `/wrap-up`, `/fix-ci` and `/deploy` commands, which follow `spec/11` | When you type the command |
| `.claude/agents/course-reviewer.md` | A strict reviewer that reads and reports but never edits; `/review-module` runs it in a fresh context | Critic passes |
| `spec/01-course-blueprint.md` | Learner persona, outcomes, competencies, pedagogy, learning paths, AI-use policy | Planning |
| `spec/02-curriculum-map.md` | Modules, hours, dependencies, **reference coverage map**, library and role coverage | Planning; `course.json` |
| `spec/curriculum/phase-0…6, electives` | Every lesson: **Essential**, **Extra & advanced · reference targets**, graded exercises; projects, interview questions | Building that module |
| `spec/03-technical-architecture.md` | How the site works, the page contract (levels, markers, code blocks, reference rows), packs, build, checks | Platform work; markup questions |
| `spec/04-reference-implementation.md` | **Tested source**: `course.js`, page templates, home and setup pages, every tool, the learner helpers, tests, CI | Stage 1 |
| `spec/05-exercises-and-assessment.md` | Exercise markup, packs, completion codes, test rules, helpers, quizzes, exams, rubrics, **validated patterns** | Writing any exercise or quiz |
| `spec/06-content-style-guide.md` | Voice, anatomy, **levels**, **complete coverage and reference tables**, callouts, outputs, code style | Writing any lesson |
| `spec/07-sample-lesson.md` | A finished, verified lesson (M03-L04 Dictionaries): the quality bar | Writing any lesson |
| `spec/08-design-system.md` | Tokens, the marker language, components, accessibility, the full stylesheet | UI work |
| `spec/09-projects-and-capstone.md` | Portfolio projects and capstone: briefs, requirements, rubrics | Building projects |
| `spec/10-career-readiness.md` | Career track content and interview question banks | M26 and the interview callouts |
| `spec/11-build-plan-and-prompts.md` | Staged build plan with **copy-paste prompts** | Every session (you use it too) |
| `spec/12-qa-checklist.md` | Automated and manual checks per lesson, module, phase and release | Before marking anything done |

---

## How to use the kit

### Option A: Claude Code (recommended)
Follow **`BUILD-AND-DEPLOY.md`**. In short:
1. Unzip the kit into a new folder **keeping the folder structure** (including the hidden `.claude/` folder), so `CLAUDE.md` sits at the root.
2. Start `claude` in that folder and accept the trust prompt. It reads `CLAUDE.md` and the project's skills automatically.
3. Run `/stage 0`, then `/stage 1`, then `/deploy` to publish the first version; continue with one stage or module per session (`/build-module m02`, …), ending each with `/wrap-up`.
4. Every push to `main` checks the course on GitHub and republishes it on GitHub Pages.

### Option B: a Claude Project (claude.ai)
1. Create a Project and upload **all** the `.md` files to its knowledge.
2. Paste the block below into the Project's custom instructions.
3. Start a new chat for each stage with the prompts in `spec/11`. Ask Claude to return each step's files (or a zip) and add them to your repository, then run the checks yourself (`python tools/ci.py --partial`) and paste the output back.

```text
You are building the course specified in this project's knowledge files.
CLAUDE.md is your master instruction file: follow its rules, conventions and
workflow exactly. Read only the spec files the current step needs (CLAUDE.md §3
says which). The tested code in spec/04 is the platform: reuse it verbatim
unless a step explicitly changes it. Nothing may run Python in the browser.
Build one module per chat. Before saying a step is done, run (or ask me to run)
python tools/ci.py --partial and report the results. Return every file you
create in full, with its path.
```

### Option C: a single chat
Attach `CLAUDE.md` plus the files the current stage needs (each stage in `spec/11` lists them), then paste that stage's prompt.

---

## Defaults chosen for you

Change any of these in `CLAUDE.md` §2; Claude will carry the change through.

| Decision | Default | Why |
|---|---|---|
| Format | Static HTML site: plain HTML, one CSS file, one classic script; no backend | Free to host, works offline and from `file://`, lasts for years |
| Running code | On the learner's computer; pages show verified output | The real professional workflow from day one; trustworthy outputs; light pages |
| Python | **3.15**, the latest stable release (verified with 3.15.2) | Lessons teach its new features as current Python, and every pinned library installs on it |
| Libraries | All 65 libraries pinned to their newest release that installs on 3.15, in six files, one per phase (e.g. NumPy 2.5.5, pandas 3.1.1, Polars 2.1.0, DuckDB 2.0.1, scikit-learn 1.9.1, PyTorch 2.15.0, transformers 5.24.0, FastAPI 0.165.0, MLflow 3.18.0); a weekly workflow reports newer releases (`spec/02` §5) | Outputs on the pages match what learners see; updates are deliberate, never a surprise |
| Exercises | pytest packs + completion codes | Real tests, precise feedback, progress recorded without accounts |
| Levels | Essential / Extra info / Advanced with a Show filter | Complete content without overwhelming beginners |
| Hosting | GitHub Pages via GitHub Actions | Free, shareable on a CV |
| Progress | Browser `localStorage`, export/import | Private, no server |
| Language | Plain international English | For learners whose first language isn't English |

## Facts verified while building this kit (22–23 Nov 2026)

* The reference implementation passed `tools/ci.py --partial` on **Python 3.15.2**: 40 unit tests for the tools; `check_libraries` (all 65 pinned libraries import, 21 functional checks pass); ruff 0.17.6 on the tools (0 findings); `check_site` 0 problems; `check_coverage` 6 targets complete for the sample (dict 31 names, dict_keys 23, dict_values 6, dict_items 23, frozendict 23, MappingProxyType 24); `check_content` 29 examples (each run twice under two hash seeds), 9 doctest sessions, 4 lesson exercises and 6 pattern exercises (each solution passes, each starter fails, all mutants caught), 3 quizzes, 0 problems; **51 of 51** headless-Chrome checks over `file://` (rendering, fonts, reading position, level filter, deep links, settings, shortcuts, exercises, quizzes, search, home, phone layout, 24 px targets), including axe-core's WCAG 2.2 A/AA rules on every page type in both themes and on the lesson at phone width, with **0 problems**. The repository was then rebuilt from the kit's Markdown alone and passed the same checks.
* The Claude Code setup was checked with Claude Code 2.1.330: it finds the seven skills and the reviewer agent, and `claude doctor` reports no invalid settings. The browser checks now find Chrome where macOS, Windows and Linux install it (the macOS and Windows lookups were tested by simulating those systems), so `tools/ci.py` runs unchanged on a Mac. The workflow's actions are at their newest major versions (checkout, setup-python and setup-node v7, configure-pages v6, upload-pages-artifact and deploy-pages v5). The workflow itself only runs on GitHub, so its first run is its real test.
* All **65 pinned libraries** were the newest releases on PyPI on 23 Nov 2026 that install on Python 3.15. They resolve to wheels on Linux (x86-64, glibc 2.39 or later), on macOS 15 or later on Apple silicon and on Windows (x64), apart from two pure-Python packages that install from source anywhere: PySpark, and ANTLR's Python runtime, which DVC needs through Hydra. Platform limits, now stated on the setup page: faiss-cpu has no Windows wheels (its pin carries `sys_platform != "win32"`, and the FAISS part of M23-L05 runs in WSL 2 on Windows); PyTorch has no Intel Mac wheels; orjson (needed by Gradio) has Python 3.15 wheels on Linux only for glibc 2.39 or later. Installed together in a fresh 3.15.2 environment they import and pass 21 functional checks (`tools/check_libraries.py`): PyTorch training on the CPU, a notebook run by the Jupyter kernel, ONNX export checked by ONNX's reference runtime, Prophet's Stan backend, a PySpark session with a Python UDF (Java 21), and more.
* Not installable on 3.15 yet, so taught as overview with a replacement the learner can run: **ONNX Runtime** 1.32.0 (wheels for 3.11–3.14 only; the course runs ONNX models with `onnx.reference`) and therefore **Chroma** 1.5.9, which requires it (FAISS instead); **Ray** 2.60.0; **statsforecast** 2.1.1 (statsmodels and Prophet instead); **LangGraph** 1.2.24 (its dependency zstandard has no 3.15 wheels); **Evidently** 0.7.23, which requires plotly < 6 and fails to import with pandas 3, while pandas 2 has no 3.15 wheels (River and drift statistics from scratch instead).
* Major-version changes the lessons follow, each confirmed by running it: pandas 3 (Copy-on-Write is the only mode, strings get the `str` dtype), DuckDB 2 (relations have no `fetchone()`), MCP 2 (`FastMCP` renamed `MCPServer`), transformers 5 (PyTorch only; `dtype=` replaces `torch_dtype=`), MLflow 3 (`name=` replaces `artifact_path=`), FastAPI (`on_event` deprecated in favour of lifespan), `torch.load` defaulting to `weights_only=True`, pytest 9 reading a native `[tool.pytest]` table, and ruff 0.16+ enabling 413 rules by default instead of 59 (the course's own tools were cleaned up to pass them).
* Python 3.15 (released 9 October 2026) adds lazy imports (`lazy` is a new soft keyword), the `frozendict` and `sentinel` built-ins, unpacking in comprehensions, UTF-8 as the default encoding, the `profiling` package, `math.integer` and `re.prefixmatch()`; it removes the `sre_*` modules. The curriculum teaches these as current features with "New in 3.15" markers, and the coverage check requires them (the `lazy` keyword, `frozendict`, `sentinel`, `math.integer`, `profiling`).
* Python's real error message for a list used as a key is `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')`; the sample shows it because outputs are produced by running, not typed.
* Windows installs Python with the **Python install manager** (`py install 3.15`); the setup page and the runner setting use it.
* Testing shaped the design: a fixed time limit can't separate O(n²) from O(n) on every laptop, so speed checks compare against a reference on the same machine (`assert_fast_enough`); and examples run under two hash seeds catch output that depends on set order.

## Customising

* **Rename** the course: `title` in `course.json` and the brand text in the templates.
* **Change scope or pace**: edit the phase files; `spec/02` shows the dependencies and which lesson owns which reference target (keep `tools/coverage.json` in step).
* **Add local flavour**: ask Claude to adapt examples and datasets to your country (the style guide allows it as long as examples stay clear to everyone).

## What this kit is not

It isn't the 199 finished lessons. Claude writes those module by module from these specs; `spec/11` keeps the sessions consistent. Nothing in the kit needs API keys or network access.
