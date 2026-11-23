# Build and publish the course with Claude Code

This guide takes the kit to a live course at `https://<your-github-name>.github.io/<repository>/`. Claude Code writes the course on your computer, one stage or one module per session, following `CLAUDE.md` and `spec/11`. GitHub checks every push again and publishes the site.

The commands are for **macOS on Apple silicon**. [On Windows or Linux](#on-windows-or-linux) lists the differences.

It is a long build: roughly 60 sessions. The site can go live after the second one, and every push after that updates it.

## 1. Install the tools

You need:

* **A Claude plan that includes Claude Code** (Pro, Max, Team or Enterprise) or a Claude Console account. A plan with higher usage limits suits a build this long.
* **A GitHub account.** The free plan is enough if the repository is public: GitHub Pages on GitHub Free needs a public repository, and GitHub Actions is free for public repositories.
* **macOS 15 or later.** Two pinned libraries, FAISS and OpenCV, publish macOS packages only for macOS 15 and later.
* **About 5 GB of free disk space.** The pinned libraries are about 0.7 GB to download on a Mac.

Install [Homebrew](https://brew.sh) if you don't have it, then:

```bash
brew install git gh node                        # Git, the GitHub CLI, Node.js (22.12 or later)
brew install --cask google-chrome temurin@21    # Chrome for the browser checks, Java 21 for PySpark
```

Install **Python 3.15** with the macOS installer from [python.org](https://www.python.org/downloads/macos/) (3.15.2 or later), then check it:

```bash
python3.15 --version
```

Install **Claude Code** and sign in to GitHub:

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version        # if "claude" isn't found, open a new terminal window first
gh auth login
```

## 2. Create the project folder

```bash
mkdir -p ~/Projects && cd ~/Projects
unzip ~/Downloads/python-ai-course-kit-v5.zip
mv python-ai-course-kit python-ai-course
cd python-ai-course
```

The folder holds `CLAUDE.md`, `README.md`, this guide, `spec/` and a hidden `.claude/` folder (Command-Shift-. shows hidden files in Finder) with the project's Claude Code permission rules, skills and reviewer agent. Keep this layout: Claude Code reads `CLAUDE.md` and `.claude/` from the folder you start it in.

## 3. Run a session

Start every session in the project folder. Once Stage 0 has created `.venv`, activate it first, so that `python` means the course's Python 3.15:

```bash
cd ~/Projects/python-ai-course
source .venv/bin/activate
claude
```

The first time, Claude Code asks whether you trust this folder. Say yes: the allow rules in `.claude/settings.json` apply only in trusted folders.

Type `/` to see the project's commands:

| Command | What it does |
|---|---|
| `/stage 0` … `/stage 9` | Runs one stage of `spec/11`. Stage 5, the module loop, is `/build-module` |
| `/build-module m05` | Plans module M05 and waits for your OK, then builds it lesson by lesson, runs the checks and commits |
| `/end-phase 2` | Builds a finished phase's exam, portfolio project page and recap |
| `/review-module m07` | A strict reviewer in a fresh context reports problems by severity; then tell Claude which ones to fix |
| `/wrap-up` | Rebuilds, runs the checks, updates `BUILD_LOG.md` and commits |
| `/fix-ci` | Finds and fixes the cause of a failing check, on your Mac or on GitHub |
| `/deploy` | Creates the GitHub repository and turns on Pages the first time, pushes, watches the run and gives you the address |

Habits that keep a long build on track:

* **One stage or module per session.** End with `/wrap-up`, then `/clear` (or quit) before the next one. `BUILD_LOG.md` carries the state from one session to the next.
* **Read the plan.** `/build-module` stops after planning. Correct the plan if you need to, then say OK.
* **Let it run to the end (optional).** After you approve a plan, `/goal` keeps Claude working until a condition holds; a separate model checks the condition after every turn. For example: `/goal every lesson of m05 is built and committed, python tools/ci.py --partial ends with "CI passed", and BUILD_LOG.md names the next step, or stop after 60 turns`
* **Look at the pages.** `open site/index.html` opens the course from disk in your browser.
* **Approvals.** Claude Code asks you before it pushes, creates the repository, or edits `spec/`, `CLAUDE.md`, the requirements files or the workflows. It is blocked from hand-editing generated files (`manifest.js`, `search-index.js`, `api-index.html`, the vendored assets), which `tools/build.py` writes. Shift+Tab switches the permission mode, including plan mode, in which Claude reads and plans without editing.
* **If Claude goes in circles,** run `/clear` and start the step again with a sharper prompt. Nothing is lost: the work is committed and `BUILD_LOG.md` says where things stand.

## 4. The build, in order

| Session | Command | Result |
|---|---|---|
| 1 | `/stage 0` | The kit committed as unzipped, the repository layout, `BUILD_LOG.md`, and `.venv` with every pinned library. Then quit, run `source .venv/bin/activate` and start `claude` again |
| 2 | `/stage 1` | The tested platform from `spec/04` and `spec/08` and the sample lesson; `python tools/ci.py --partial` green, with 51 browser checks |
| 3 | `/deploy` | The first publication: the home page, the setup page and the sample lesson |
| 4–5 | `/stage 2`, then `/stage 3` | The datasets; the syllabus, glossary and certificate pages |
| 6–7 | `/stage 4` | M00 and M01, in two sessions. Look at them with Show set to each option before going on |
| then | `/build-module m02` … `m25`, then `m27` | One module per session, two for M09 and M12. `/end-phase N` after M06, M10, M15, M19 and M23; `/review-module` every three or four modules; `/deploy` whenever you want the site updated |
| then | `/stage 6 m12` … | The notebooks, one module per session: M12, M13, M16, M18, M19, M21, M22, M23 |
| then | `/stage 7`, then `/end-phase 6` | M26 Career Launchpad and the career pages; then Phase 6's exam and project |
| then | `/stage 8` | The capstone, then the electives, one per session |
| last | `/stage 9` | The release: the full checks, a release report, `CHANGELOG.md` and the release run on GitHub |

## 5. Publish on GitHub Pages

`/deploy` does this for you. To do it by hand:

1. Create the repository, public and empty: `gh repo create python-ai-course --public --source . --remote origin` (or on github.com, without a README).
2. Turn on Pages: in the repository, **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Push: `git push -u origin main`.
4. Watch the **Actions** tab ("Check and publish the course"). When the run is green, the course is at `https://<your-github-name>.github.io/python-ai-course/`.

From then on, every push to `main` checks the course and republishes it. The workflow (`.github/workflows/site.yml`) installs Python 3.15, the pinned libraries (with the CPU build of PyTorch), Node and the browser-check tools, runs `python tools/ci.py --partial`, and deploys `site/` only if every check passed. `--partial` checks every page that exists in full, and reports course-wide coverage that isn't built yet as pending. Pull requests are checked but not deployed.

For the release (Stage 9), run the workflow by hand with **release** ticked (Actions → Check and publish the course → Run workflow), or `gh workflow run site.yml -f release=true`. That runs the full check, which needs every course-wide coverage target.

Worth knowing:

* **Your Mac produces the outputs; GitHub's Linux runner checks them again.** An example that prints something platform-dependent, such as the last digits of a float or a path, fails on GitHub. `/fix-ci` makes it print the same everywhere (`spec/06` §8), which also protects learners on Windows and Linux.
* The first run installs every library and takes the longest; later runs reuse pip's cache.
* A Pages site can be up to 1 GB, and a deployment must finish within 10 minutes. The course stays far below both.

## 6. Optional: Claude on GitHub

`/install-github-app` in Claude Code installs the Claude GitHub App and a workflow, so that you can mention `@claude` in an issue or pull request ("@claude the m12 check fails on GitHub, please fix it"). You need admin access to the repository; the command stores an API key or a subscription token as a repository secret for you.

## 7. When something goes wrong

| Symptom | Fix |
|---|---|
| `claude: command not found` | Open a new terminal window. If that doesn't help, see [Troubleshoot installation](https://code.claude.com/docs/en/troubleshoot-install) |
| `python --version` in a session isn't 3.15 | The session started without `source .venv/bin/activate`. Claude falls back to `.venv/bin/python`, but quit and restart to be safe |
| pip can't install faiss-cpu or opencv-python | macOS is older than 15: update macOS |
| The PySpark library check fails | Java is missing: `brew install --cask temurin@21`, then open a new terminal window |
| "Chrome not found" in the browser checks | Install Google Chrome, or set `CHROME_PATH` to its executable. `python tools/ci.py --partial --no-browser` skips the browser checks for a quick run |
| Green on your Mac, red on GitHub | `/fix-ci` |
| The deploy job fails with "Get Pages site failed" or "Not Found" | Pages isn't on: Settings → Pages → Source: GitHub Actions, then run the workflow again |
| "Branch is not allowed to deploy to github-pages" | Deploy from `main`, or allow the branch in Settings → Environments → github-pages |

## On Windows or Linux

* **Windows:** build inside WSL 2 with Ubuntu 24.04 and follow the Linux notes. Every pinned library installs there, and it matches GitHub's runner. Natively, FAISS has no Windows packages.
* **Linux:** use a distribution with glibc 2.39 or later, such as Ubuntu 24.04 (orjson, which Gradio needs, has Python 3.15 packages only for those). Install Claude Code with the same `curl` command, and Python 3.15, Node 22.12 or later, Chrome and Java 17 or later from your distribution or the projects' sites. Without an NVIDIA GPU, Stage 0 installs the pinned PyTorch from PyTorch's CPU-only index first, which saves about 4 GB.

Sources: Claude Code documentation: [quickstart](https://code.claude.com/docs/en/quickstart), [skills](https://code.claude.com/docs/en/skills), [permissions](https://code.claude.com/docs/en/permissions), [subagents](https://code.claude.com/docs/en/sub-agents), [/goal](https://code.claude.com/docs/en/goal), [GitHub Actions](https://code.claude.com/docs/en/github-actions). GitHub documentation: [publishing with GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [about GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages), [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).
