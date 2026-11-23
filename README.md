# Python for AI: Zero to Job-Ready

This repository holds **Python for AI: Zero to Job-Ready**, an HTML course that takes a Computer Science (AI) undergraduate from their first line of Python to job-ready work in data, machine-learning and AI roles.

The course is a static site in `site/`: plain HTML, one stylesheet and one script, with no backend, so it works from disk and on GitHub Pages. No code runs in the browser. Each example shows the output that real Python printed for it, learners run the code on their own computer, and exercises come as pytest packs that print a completion code when every test passes.

Claude Code builds the course from the specification in [`spec/`](spec/), one stage or module per session, following [`CLAUDE.md`](CLAUDE.md). [`BUILD_LOG.md`](BUILD_LOG.md) says where the build stands and what comes next; [`DECISIONS.md`](DECISIONS.md) records the decisions taken along the way.

## Set up

You need Python 3.15, Node.js 22.12 or later and Google Chrome (for the browser checks), and Java 17 or later (for PySpark). From the repository root:

```bash
python3.15 -m venv .venv
source .venv/bin/activate
python -m pip install -r tools/requirements-dev.txt
npm install --no-save puppeteer-core@25 axe-core@4.14.1
```

`tools/requirements-dev.txt` installs all 65 libraries the course pins, from the six phase files in `site/downloads/`. On macOS, XGBoost and LightGBM also need the OpenMP runtime from Homebrew (`brew install libomp`). On Linux without an NVIDIA GPU, first install the pinned `torch` and `torchvision` from PyTorch's CPU-only index: it saves about 4 GB.

## Build and check

```bash
python tools/build.py           # regenerate the manifest, search index, API index and exercise packs
python tools/ci.py --partial    # every check, while the course is being built
python tools/ci.py              # the release check: all course-wide coverage must be complete
```

`python tools/ci.py --partial --no-browser` skips the headless-Chrome checks for a quicker run. GitHub runs the same checks on every push to `main` and publishes `site/` with GitHub Pages when they pass.

To read the course, open `site/index.html` in your browser.

## More

* [`BUILD-AND-DEPLOY.md`](BUILD-AND-DEPLOY.md): the owner's guide, from installing the tools to the course on GitHub Pages
* [`spec/`](spec/): the course specification. The build plan is [`spec/11-build-plan-and-prompts.md`](spec/11-build-plan-and-prompts.md) and the done-checks are [`spec/12-qa-checklist.md`](spec/12-qa-checklist.md)
* [`CLAUDE.md`](CLAUDE.md): the project's decisions, rules and repository layout
