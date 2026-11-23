# Phase 0 · Orientation

**Goal:** the learner understands how the course works, has a working local setup and a GitHub portfolio repository, knows the AI career landscape, and has habits for learning to code (reading errors, asking good questions, using AI tutors responsibly).
**Modules:** M00 only · ~6 h · ends with a **placement quiz** that recommends a starting module (`spec/01` §6).

How to read these files: each lesson row gives the **file slug**; the **Essential** content every learner must master; the **Extra & advanced** content that makes the lesson a complete reference, with its **reference targets** (`Ref:`, checked by `tools/check_coverage.py`, `spec/06` §4); and the **graded exercises** (local pytest packs) as `signature → behaviour`. Claude writes starters, tests, hints and quizzes from these following `spec/05`. Unless noted, every lesson also has verified examples the learner runs locally (PRIMM), a 3–5 question end-of-lesson quiz, a recap and the "On the job" callout (`spec/06`).

---

## M00 · Start Here: Learn, Set Up, Use This Course
`m00-start-here` · 5 lessons · ~6 h · Needs: none

**Why it matters at work:** professionals spend more time reading errors, setting up environments and using Git than writing new code. Starting with these habits prevents months of friction.

**Outcomes.** The learner can:
1. run the course's code on their own computer, check exercises with pytest, read the feedback, record progress with completion codes, and explain the hint/solution/mastery rules;
2. describe the main AI/data job roles and choose a target role;
3. install Python 3.15, VS Code and uv, then create and run a project in a virtual environment;
4. use Git and GitHub to commit, push and open a pull request;
5. read a traceback, ask a good debugging question, and use an AI assistant as a tutor rather than a solution machine.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m00-l01** `l01-how-this-course-works` How this course works | Course map and phases; anatomy of a lesson; the PRIMM routine; reading a lesson (level markers, the Show filter, callouts, verified outputs); copying and downloading code; exercise packs, pytest and completion codes; hints and the solution rules; progress, mastery, badges; time planning; where progress is stored and how to export it | ◆ keyboard shortcuts, how progress is stored, working offline ▲ how the course verifies every output (the tools in `spec/04`) | **E1** `greet(name: str) -> str` → `"Hello, <name>! Welcome to Python for AI."` (exactly; the first-ever exercise, with a fully guided walkthrough). Quiz on course mechanics |
| **m00-l02** `l02-python-ai-careers` Python, AI and the jobs you're aiming for | What Data Analysts, Data Scientists, ML Engineers, AI/LLM Engineers and MLOps Engineers do day to day; the tools each uses; why Python dominates AI; reading a job description; how the modules map to roles; picking a target role and track | ◆ adjacent roles (data engineer, research engineer), reading salary data critically | No code exercise. **Self-assessment** (saved locally): rate yourself on the `spec/01` competencies. Quiz: match tasks to roles |
| **m00-l03** `l03-local-setup` Set up your machine | Install Python 3.15 (Windows: the Python install manager, `py install 3.15`; macOS: python.org; Linux: `uv python install 3.15`), VS Code with the Python and Jupyter extensions; terminal basics (`cd`, `ls`/`dir`, `mkdir`, paths); virtual environments: what and why; installing the course's pinned tools from `requirements-tools.txt` (and the later phase files, `site/setup.html` §6); `uv init`, `uv add numpy`, `uv run main.py`; running a notebook in VS Code; the course's **Runner** setting (`python`, `python3`, `py` or `uv`) that rewrites every command on the site; Windows, macOS and Linux notes in tabs; troubleshooting (PATH, "python not found", corporate/campus proxies) | ◆ `uv` workflow (`uv python install`, `uv run`), PATH explained, several Python versions side by side (`py list`) ▲ WSL on Windows, conda compared | **Checklist** (self-report, saved): Python version shown, virtual environment created, the first exercise pack ran under pytest, a notebook ran. Quiz: what a venv is for; which command adds a package |
| **m00-l04** `l04-git-github-basics` Git & GitHub from day one | Repositories, commits, staging, `.gitignore`, branches, remotes, push and pull; GitHub account, SSH or HTTPS auth, PRs, README.md in Markdown; creating `python-ai-portfolio`; the GitHub Education student benefits (link only); commit message style | ◆ `git log`/`diff`/`restore`, SSH keys, `.gitattributes` ▲ rebase vs merge (preview of M10-L06) | **Parsons problem**: put the commands for "create repo → first commit → push" in order. Quiz: `git add` vs `git commit`; what `.gitignore` is for; why never commit `.env` |
| **m00-l05** `l05-learn-like-an-engineer` Learn like an engineer | Deliberate practice; reading a traceback bottom-up; the debugging loop (reproduce → isolate → hypothesise → test); rubber-duck debugging; reading official docs; good questions (minimal example, expected vs actual); spaced repetition and notes; the course AI-use policy and tutor prompts ("don't give me the answer; ask me a guiding question"); academic integrity in your university | ◆ reading official docs (library API pages, the Python docs' structure) ▲ minimal reproducible examples for bug reports | **E1** (debug) `average(numbers)` contains a `NameError` and a `ZeroDivisionError` on empty input; fix both. Spec: return `0.0` for an empty list. **Quiz**: read three tracebacks and name the line and the cause |

**Placement quiz (`m00-placement`)**: 20 questions in increasing difficulty: Python basics → data structures → functions → OOP → NumPy/pandas basics → ML concepts. The result page recommends a starting module and lists checkpoint quizzes the learner may take to unlock skipped modules.

**Interview corner:** "Walk me through how you debug a problem you've never seen." "How do you use AI tools in your workflow?" (Introduces the ideas of honesty and verification.)

**Misconceptions to tackle:** "Errors mean I'm bad at this" (errors are information). "I should memorise everything" (learn to look things up). "AI can do it for me" (you must be able to explain and debug it).

**Notes:** keep the setup lesson OS-neutral with tabs. Give links to official installers only. Nothing runs in the browser, so setup is the gate to the whole course: give a troubleshooting table and a "get unstuck" checklist; say so to reduce anxiety.
