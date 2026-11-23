# 11 · Build plan & prompts

Ten stages. Each stage says what to read, what "done" means, and gives a prompt to paste. One stage (or one module) per session; `BUILD_LOG.md` carries the state between sessions.

**In Claude Code** the prompts in this file are also project skills in `.claude/skills/`, so a session starts with one command: `/stage N` (Stages 0–4 and 6–9), `/build-module mNN` (Stage 5), `/end-phase N`, `/review-module mNN` (the critic pass), `/wrap-up` (end of session), `/fix-ci` (if something breaks) and `/deploy` (GitHub Pages). The skills follow this file, so a change here changes them too. `BUILD-AND-DEPLOY.md` is the owner's step-by-step guide.

## Session routine (every session)

**Start-of-session prompt** (paste first in each new session):
```text
Read CLAUDE.md, BUILD_LOG.md (current state + next step) and course.json.
Summarise in 5 lines where the build stands and what this session should do.
Then continue with the next step unless I say otherwise.
```

**End-of-session prompt:**
```text
Run python tools/build.py, then python tools/ci.py --partial. Fix anything red.
Update BUILD_LOG.md (current state, what was done, check results, open issues,
next step) and list the files you created or changed.
```

**If something breaks:**
```text
The checks failed (output below). Find the root cause, fix it with the smallest
change that respects the contracts (CLAUDE.md rule 12, spec/03 §4, spec/05 §3),
re-run the checks and explain what was wrong in two sentences.
<paste output>
```

---

## Stage 0 · Bootstrap the repository

**Reads:** `CLAUDE.md`, `README.md`. **Done when:** the repository has the layout of `CLAUDE.md` §5 (empty folders where needed), `BUILD_LOG.md` and `DECISIONS.md` exist, `git` is initialised on branch `main` with a `.gitignore` (`.venv/`, `__pycache__/`, `.ruff_cache/`, `.mypy_cache/`, `node_modules/`, `.env`, `.claude/settings.local.json`), the first commit holds the kit exactly as unzipped, and `.venv` has Python 3.15 with every pinned library.
```text
Stage 0: initialise git on branch main (if it isn't already) and commit the kit
exactly as it is ("Add the build kit"). Then create the repository layout from
CLAUDE.md §5, BUILD_LOG.md with a "Current state / Next step" block,
DECISIONS.md and .gitignore, and rewrite README.md as a short README for the
course repository (what it is, how to run the checks, links to
BUILD-AND-DEPLOY.md and spec/). Create a Python 3.15 virtual environment in
.venv. Copy tools/requirements-dev.txt and the six
site/downloads/requirements-*.txt files from spec/04 §23, then install
tools/requirements-dev.txt (under 1 GB on macOS; about 8 GB on Linux with
PyTorch's CUDA libraries, so without an NVIDIA GPU install the pinned torch and
torchvision from PyTorch's CPU-only index first). PySpark needs Java 17 or
later. Commit.
```

## Stage 1 · The platform (tested code from spec/04 and spec/08)

**Reads:** `spec/03`, `spec/04`, `spec/08`. **Done when:** every file in `spec/04` (and the CSS from `spec/08` §8) is in place byte for byte, the Prism bundle is built and the fonts copied, the sample lesson from `spec/07` and `examples/spec05-examples.html` (`spec/04` §22.4) are in place, and `python tools/ci.py --partial` is green (40 unit tests, 22 library checks, ruff clean, 0 site problems, 6 coverage targets complete, every example/exercise/quiz verified including the 6 pattern exercises, 51 browser checks with 0 axe-core accessibility problems).
```text
Stage 1: copy every file from spec/04 (sections 1-26) and the CSS from spec/08 §8
to their paths, exactly. Build the Prism bundle and copy the fonts (spec/04 §21). Put the sample
lesson from spec/07 §4 in place. Run python tools/build.py, then
python tools/ci.py --partial. Report the summary line of every step. Do not
"improve" the code in this stage: if something fails, report it with the output.
```

## Stage 2 · Datasets

**Reads:** `spec/03` §9, the data needs in the phase files. **Done when:** `tools/make_datasets.py` generates every dataset with fixed seeds into `site/data/`, each ≤ 2 MB, documented in `site/data/README.md` (columns, rows, licence), with a unit test that the generator is deterministic.
```text
Stage 2: list every dataset the phase files need (name, columns, rows, which
lessons use it). Write tools/make_datasets.py (NumPy, seeded) to generate them,
site/data/README.md, and a test that two runs produce identical bytes. Keep each
file under 2 MB; prefer realistic, global, fictional data (spec/06 §11).
```

## Stage 3 · Site shell pages

**Reads:** `spec/01`, `spec/02`, `spec/08`. **Done when:** `syllabus.html` (rendered from the manifest: phases, modules, lessons, hours, projects), `glossary.html` (terms with `dfn` ids, linked from lessons), `certificate.html` (completion summary from progress) and `site/data/README.md` link check pass `check_site.py`.
```text
Stage 3: build syllabus.html, glossary.html and certificate.html from
templates/page-shell.html (spec/03 §4). Render lists from window.COURSE where
possible (small additions to course.js with tests in smoke_pages.mjs). Run the
checks.
```

## Stage 4 · Vertical slice: M00 + M01 (then the owner reviews)

**Reads:** the M00–M01 sections of `phase-0-orientation.md` and `phase-1-foundations.md`, `spec/05`, `spec/06`, `spec/07`. **Done when:** both modules are complete to the definition of done (`CLAUDE.md` §8), including **M01-L07 (language reference)** with every `kw:` row and the functions/types/constants part of `module:builtins`, and the owner has reviewed one lesson in each Show mode.
```text
Stage 4: build M00 and M01 following CLAUDE.md §7. Plan first (sections with
levels, reference targets, examples, exercises with signatures and edge cases,
data files, minutes) and wait for my OK. For M01-L07 start from
python tools/api_skeleton.py module:builtins and write the kw: rows for
every keyword and soft keyword. Then build, run the checks, and tell me which
pages to review.
```

## Stage 5 · The module loop (M02 → M27, one module per session)

**Reads (each session):** `CLAUDE.md`, the module's section of its phase file, `spec/06`, `spec/07`, `spec/05` §2–§5, and `spec/02` §4 for its reference targets.

**Module prompt** (change the ID each time):
```text
Build module <M05> following CLAUDE.md §7.
1) Plan first: for each lesson list its sections with levels (essential, then
   extra, then advanced), its reference targets and the row groups you will use,
   the examples (which ones predict-first, which end in an error on purpose),
   exercises (signatures, key edge cases, kind), data files and minutes for the
   essentials path and the whole page. Wait for my OK.
2) Build each lesson: reference rows first (tools/api_skeleton.py), then the
   teaching sections, then code -> check_content.py --update-outputs -> read the
   outputs -> prose. Run python tools/check_coverage.py --partial and
   check_content.py on the lesson before moving on.
3) Build the module project brief and the checkpoint page (12-20 questions,
   ~30 % retrieval from earlier modules; optional checkpoint pack).
4) Add the lessons to course.json, run tools/build.py, update the glossary and
   BUILD_LOG.md, run tools/ci.py --partial, and report.
```

**At the end of each phase:**
```text
Phase <N> is complete. Build the phase exam page (spec/05 §9: timed in-page quiz
+ exam pack; if this is the first exam, implement the .exam component in
course.js with smoke tests first), the portfolio project page for p<N>-project
from spec/09 (implement the .rubric and .checklist components first if they don't
exist yet), and a "Phase N recap" on the dashboard. Run all checks and update
BUILD_LOG.md.
```

**Critic pass** (high value, every 3–4 modules):
```text
Act as a strict reviewer who did not write these lessons. Review module <M07>
against spec/06 (§3 levels, §4 coverage, §15 self-review), spec/05 §4 and spec/12.
Read each lesson with Show set to "Essentials" and to "Everything". Look for: concepts used
before they are taught, dishonest levels (essential content marked extra, or the
reverse), reference rows that are vague or wrong, weak tests, hints that give the
answer away, misconception-free distractors, inaccessible markup, outdated APIs.
List issues by severity with file and line, then fix the top ones.
```

## Stage 6 · Notebooks (N lessons)

**Reads:** `spec/03` §9, the notebook rows in the phase files (M12, M13, M16, M18, M19, M21, M22, M23). **Done when:** every notebook runs top to bottom locally on a CPU with the pinned requirements (you run it with `jupyter nbconvert --execute`) and ends with passing self-checks.
```text
Stage 6: create the notebooks for module <M21> per spec/03 §9: an environment
check cell (Python and library versions), sections mirroring the lessons, TODO
exercise cells, assert-based self-checks, CPU-sized defaults with a note on how
to scale up on a GPU. Use only permissively licensed data (state the licence).
Link each from its lesson with a download link. Execute every notebook with
nbconvert and report the results.
```

## Stage 7 · Career pages and the simulator

**Reads:** `spec/10`, the M26 section of `phase-6-production-career.md`. **Done when:** M26 is complete, `site/career/` has the CV template, application tracker (CSV download), interview banks, the mock-interview simulator (with smoke tests for question drawing and scoring) and the timed coding assessment pack.
```text
Stage 7: build module M26 and the site/career pages from spec/10, including the
mock-interview simulator (spec/10 §11) and the timed coding assessment
(exams/coding-assessment.html + its pack: 3 problems from the M09 bank). Add
smoke tests for the simulator's logic (question drawing, timers, scoring). Run
all checks.
```

## Stage 8 · Capstone and electives

**Reads:** `spec/09` §8, `spec/curriculum/electives.md`.
```text
Stage 8: build projects/capstone.html (brief, tracks, milestones, proposal
checklist, rubric, presentation guide, submission checklist), then the electives
one per session in this order unless I say otherwise: E1, E6, E2, E3, E5, E7, E4.
```

## Stage 9 · QA and release

**Reads:** `spec/12`. **Done when:** `python tools/ci.py` (no `--partial`) is green, so every required target, every keyword, every AST node type and every standard-library module is covered; every item of the release checklist is ticked and recorded in `BUILD_LOG.md`; the release run of the publishing workflow (`release` ticked) is green and the site is deployed with GitHub Pages.
```text
Stage 9: run the full release checklist in spec/12, starting with
python tools/ci.py (no --partial). Produce a release report (checks, coverage
totals, browsers tested, accessibility results, performance numbers, known
issues), fix blockers, bump "version" in course.json and write CHANGELOG.md.
Then, after I confirm, push and run the release check on GitHub
(gh workflow run site.yml -f release=true, or Actions -> "Check and publish the
course" -> Run workflow with "release" ticked) and report the result and the
site's address. If GitHub Pages isn't on yet, follow /deploy first.
```

---

## Useful extra prompts

**Fill a reference table:**
```text
Lesson <m05-l01> owns class:str and module:string. Run tools/api_skeleton.py for
each, then turn the drafts into task-grouped tables (spec/06 §4): every name
described in course voice, levels set (about 25 % essential), related names
grouped, no TODO left. Run check_coverage.py --partial and check_site.py.
```

**Re-level a lesson:**
```text
Read <m08-l06> with Show set to "Essentials". Is it self-sufficient for the required
exercises? Is anything marked essential that a beginner can skip? Propose level
changes as a table (block, current, proposed, reason), apply them after my OK,
and run check_site.py.
```

**Add an exercise to an existing lesson:**
```text
Add a ★★ exercise to <m05-l04> that practises <named groups in regex>. Follow
spec/05 §2-§4 (≥ 4 tests, a second data set against hard-coding, 3 hints,
solution notes). Give it the next free id; don't renumber. Run
check_content.py on the lesson and tools/build.py.
```

**Refresh the library pins** (when the weekly `pins.yml` workflow fails, or before a release):
```text
Run python tools/check_pins.py. For each pin that can move up, read the
library's release notes for breaking changes, then move the pin (one library,
or one tightly coupled group such as torch + torchvision, per commit). Install,
run tools/check_libraries.py and tools/ci.py --partial. For every changed
output, run check_content.py --update-outputs and read the new output: explain
real behaviour changes in the lesson (a version callout if learners will meet
the old behaviour), and update spec/06 §9 if an API generation changed. Re-check
spec/02 §5.1: install each overview-only library with
uv pip install --dry-run --only-binary :all: <name>, and propose pinning any
that now installs. Log each bump in DECISIONS.md.
```

**Move to a new Python version** (yearly, after the main libraries support it):
```text
Python <3.16> is supported by every pinned library (check with
python tools/check_pins.py --python 3.16 and a dry-run install of
tools/requirements-dev.txt). Update CLAUDE.md §2, the workflows, course.json
"python", the setup page and requirements files. Run
tools/ci.py --partial with the new interpreter: list examples whose output
changed (check_content.py), new names that check_coverage.py now requires
(new methods, keywords, AST nodes), and data-python examples that now
run. Update the lessons, turning "coming in" notes into normal content where
appropriate, and log the decision in DECISIONS.md.
```

**Localise examples** (optional):
```text
Adapt the examples and datasets in module <M12> to <country/region> contexts
(names, places, currencies, fictional local businesses) without changing exercise
logic, IDs or difficulty. Re-run --update-outputs and read the new outputs.
```

**Claude Code:** these prompts are skills in `.claude/skills/` (see the top of this file). To add your own, create `.claude/skills/<name>/SKILL.md` with `name`, `description` and `disable-model-invocation: true` in its frontmatter and the prompt as its body; `$0`, `$1`… stand for the words typed after the command.
