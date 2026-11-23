# 03 · Technical architecture

## 1. The model in one paragraph

The course is a **static website that runs no Python**. Each page shows code, the exact output that real Python 3.15 printed for it, and the command to run it. Learners copy or download the code and run it in their own terminal, editor or notebook, as they will at work. Exercises are **pytest packs** (zip files) that learners run locally; when a test file passes, the course's pytest plugin prints a **completion code** that the learner pastes into the page to record the pass. Quizzes are the only interactive check inside the page. A build step on the author's side (`tools/build.py`) generates the manifest, the search index, the API index and the packs; a verification suite (`tools/ci.py`) runs every example, session, exercise and quiz answer with real Python, checks the reference coverage, and drives the pages in headless Chrome.

Why this design: it teaches the real workflow (editor + terminal + tests) from day one; it works offline and from `file://`; pages stay light (no 30 MB runtime download); and outputs can be trusted because they are produced by running the code, never typed.

## 2. Repository and site layout

See `CLAUDE.md` §5 for the tree. Key points:

| Path | Role | Edited by |
|---|---|---|
| `course.json` | Course metadata, phases, modules, lessons (`planned: true` for lessons not written yet) | author |
| `site/modules/mNN-slug/lNN-slug.html` | Lesson pages (the content) | author |
| `site/index.html`, `site/setup.html`, other top-level pages | Home (dashboard, settings), setup guide, syllabus, glossary, career, exams | author |
| `site/assets/js/course.js`, `site/assets/css/course.css` | The platform (`spec/04`, `spec/08`) | author, rarely |
| `site/assets/vendor/prism.bundle.js` | Syntax highlighting (Prism 1.30.0, manual mode), built by `tools/vendor/build_prism.py` | generated once |
| `site/assets/js/manifest.js`, `search-index.js`, `site/api-index.html`, `site/downloads/*.zip` | Derived data | `tools/build.py` only |
| `templates/` | Page shell and lesson template | author |
| `tools/` | Build, checks, learner helpers, tests | author |

Generated files are committed so that the site works straight from a clone or a zip. CI fails if they are stale (`build.py --check`).

## 3. How a page works in the browser

* **Scripts**: three classic `defer` scripts in this order: `prism.bundle.js`, `manifest.js` (`window.COURSE = {...};`), `course.js`. No ES modules and no `fetch`, so pages work from `file://`. `search-index.js` (`window.SEARCH_INDEX = [...]`) is loaded on demand, by inserting a `<script>` tag the first time the learner focuses the search box.
* **First paint**: a tiny inline script in `<head>` applies the saved theme, text size and reading depth before the page renders (no flash).
* **What `course.js` does on load**, in order: theme toggle, menu button and keyboard shortcuts; search box; the **Show** switch; the reading-settings panel (Show, text size, theme, shortcuts on/off); course navigation from the manifest (phases, modules, lesson status); level badges and callout titles; run cells and code panels (highlighting, Copy, Download, the command in the learner's runner, outputs, predict-then-reveal); on lesson pages the breadcrumb and the learner's progress band; the "How to read this page" legend; heading and row anchors; exercise panels; quizzes; lesson completion; previous/next cards; the continue card, course map and settings on the home page; the "On this page" navigation (a rail beside the content from 75rem, a collapsible block below); the reading-progress line, the current section in the rail and the saved reading position; applying the saved depth; revealing the target of a `#link` (switching the depth to Everything if the target is hidden). The look of each part is in `spec/08`.
* **Progress store**: `localStorage["pyai.progress.v1"]` = `{version: 1, lessons, exercises, quizzes, exams, rubrics, checklists, settings}`. Every access is wrapped in `try/catch` (private windows, full storage). Settings: `theme`, `text` (`s`/`l`; standard when absent), `depth` (`all`/`core`/`essential`), `runner` (`python`/`python3`/`py`/`uv`), `shortcuts` (`false` turns single-key shortcuts off), `resume` (`{lesson, section, title, at}`: where the learner was last reading, saved quietly as they scroll).
* **Without JavaScript** the text, headings and tables are readable; code panels, badges and quizzes need JavaScript (stated on the setup page).

## 4. The page contract (authoring markup)

Pages are **strict HTML**: every non-void element is closed explicitly (`</p>`, `</li>`, `</td>`), attributes are not duplicated, indentation uses spaces. `tools/pagekit.py` parses this into a tree with exact source offsets; the checks and the build rely on it.

### 4.1 Body and page types

`<body data-page="lesson|home|setup|reference|project|exam" data-lesson-id="mNN-lNN" data-root="../../">`. `data-root` is the relative path to `site/` (`""` at the top level). Generated pages also carry `data-generated` (excluded from the search index).

### 4.2 Lesson sections

Direct children of `<main>` are sections with an `id`:

| Section | Purpose | Level |
|---|---|---|
| `section.outcomes` | "What you'll be able to do" | none |
| `section.run-locally` | How to run this lesson's code; the pack link `<a data-pack href="../../downloads/mNN-lNN.zip" download>` | none |
| content sections | Teaching, one topic each, `h2` + optional `h3` subsections | **required** `data-level` |
| `section.api-reference[data-api-targets]` | Reference tables (§4.6) | rows carry levels |
| `section.exercises` | `article.exercise` items | none |
| `section.quiz#mNN-lNN-quiz` | End-of-lesson quiz | none |
| `section.summary` | Recap, "On the job", interview corner, further reading | items may carry levels |

### 4.3 Level markers and the Show filter

`data-level="essential|extra|advanced"` on sections, subsections, paragraphs, list items, callouts, figures and table rows. Elements inherit their ancestor's level; a child may be less essential than its parent, never more (`check_site.py` enforces it). The header's **Show** control sets `html[data-depth]`:

| Show | Hides | Use |
|---|---|---|
| Everything (`all`) | nothing | reading the whole topic, reference lookups |
| Core (`core`) | `advanced` | a solid first pass |
| Essentials (`essential`) | `extra` and `advanced` | beginners; revision; cheat-sheet view of reference tables (printing with it gives a paper cheat sheet) |

CSS does the hiding (`html[data-depth=…] [data-level=…] {display: none}`), so it is instant and works for any element. A note under the legend says how many marked parts are hidden, with a "Show everything" button.

### 4.4 Kind markers

`<aside class="callout" data-kind="…">` with an optional `<p class="callout-title">`. Kinds: `tip`, `pitfall` (rendered "Common mistake"), `version` (needs `data-version`), `interview`, `job` ("On the job"), `hood` ("Under the hood"), `try` ("Try it yourself"), `deprecated`, `performance`, `security`, `note`. Inline version markers: `<span class="version" data-version="3.9" data-change="added|changed|deprecated|removed"></span>` (rendered "New in 3.9", "Changed in 3.7", …).

### 4.5 Code blocks

All code is stored verbatim in `<script>` elements (no HTML escaping needed; `</script` must not appear inside). Types:

| Script type | Meaning | Verified by `check_content.py` |
|---|---|---|
| `text/x-python` | Python source. In `figure.example` it is the example; elsewhere a standalone snippet. `data-file="name.py"` names the download | always compiled; run when its figure has an `x-output` |
| `text/x-output` | The exact output (stdout and stderr interleaved, as a terminal shows it) | compared with two real runs |
| `text/x-stdin` | What the learner types when `input()` asks; the run echoes it like a terminal | fed to the run |
| `text/x-file` + `data-name` | A data file created next to the example before it runs | used by the run |
| `text/x-pycon` | An interactive session (`>>>` lines and results) | doctest, twice |
| `text/x-shell` | Terminal commands with tokens `{python}`, `{pytest}`, `{pip}` replaced by the learner's runner | tokens validated |
| `text/x-code` + `data-lang` | Other code (JSON, SQL, YAML, TOML, bash, Dockerfile, HTML) shown with highlighting | not run |
| `application/json` + `class="quiz-spec"` | A quiz | schema + predict answers run |

`figure.example` attributes: `data-predict` (output hidden until the learner reveals it), `data-raises="KeyError"` (the run must end with that exception; the output ends with `Traceback (most recent call last):`, a line `  ...`, then the exception line, as doctest does), `data-exit="2"`, `data-args="--name Ada"`, `data-output="sample"` (random or timing output: must run, not compared), `data-match="ellipsis"` (doctest `...` wildcards, for memory addresses), `data-requires="numpy pandas"`, `data-python="3.16"` (only checked by that Python or newer: for features newer than the course's Python), `data-timeout="120"`.

**Indentation rule** (identical in `pagekit.dedent` and `course.js`): if the line holding `</script>` contains only spaces, its width is the base indent removed from every line; otherwise the common indent is removed. Blank lines at the start and end are dropped and trailing spaces trimmed. So outputs whose every line starts with spaces survive intact.

### 4.6 Reference sections

```html
<section class="api-reference" id="reference" data-api-targets="class:dict expr:dict_keys=type({}.keys())">
  <table class="api-table"><caption>…</caption><thead>…</thead><tbody>
    <tr id="api-dict-get" data-api="dict.get" data-level="essential"><td><code>d.get(k, default=None)</code></td><td>…</td><td>…</td></tr>
```

* **Targets**: `class:NAME` (built-in or dotted path; the alias is the last component), `module:NAME` (alias = full module path), `expr:ALIAS=EXPRESSION` (the type of an expression, for views and accessors). Explicit aliases: `class:Counter=collections.Counter`.
* **Rows**: `data-api` lists one or more names (`dict.__eq__ dict.__ne__`); the row `id` is `api-` + the first name with dots as dashes; every row has a level. Other namespaces: `kw:yield` (keywords), `module:json` (standard-library atlas), and free rows `syntax:…`, `concept:…` that are not checked against an object. Rows for names newer than the checking Python carry `data-version`.

### 4.7 Exercises and quizzes

Markup, pack layout, tests and completion codes are specified in `spec/05`. The page shows the starter (and, collapsed, the tests) read-only with Download buttons, the pytest command, the completion-code box, hints one at a time and the solution behind a confirmation.

## 5. Running code on the learner's computer

* **Setup** (`site/setup.html`, M00-L03): Python 3.15 (Windows: the Python install manager, `py install 3.15`; macOS: python.org installer; Linux: distribution packages or `uv python install 3.15`), an editor, a virtual environment, `requirements-tools.txt` (pytest and the code-quality tools), then one requirements file per phase as the learner reaches it (`requirements-core`, `-ml`, `-deep-learning`, `-production`, `-electives`), installed into the same environment in that order.
* **Runner setting**: every command on every page is written with tokens and rendered for the learner's choice: `python` → `python -m pytest`, `python3` → `python3 -m pytest`, `py` → `py -m pytest`, `uv` → `uv run python`, `uv run --with pytest pytest`, `uv pip`.
* **Packs**: `site/downloads/mNN-lNN.zip` → folder `mNN-lNN/` with `README.md`, `pack.json`, `conftest.py` (the course plugin), `course_helpers.py`, `course_mocks.py`, the starters `eN_*.py`, their tests `test_eN_*.py` and any data files. `all-exercises.zip` bundles every pack. Packs never contain solutions.
* **Completion codes**: the plugin prints, for every test file that fully passed (no deselection, no failures, no skips), `fnv1a32("pyai:" + exercise_id)` formatted `XXXX-XXXX`. `course.js` computes the same value to verify a pasted code. It proves the learner ran the tests, not that they couldn't cheat; it is a progress record, not an exam lock.

## 6. The build (`tools/build.py`)

| Output | From |
|---|---|
| `site/assets/js/manifest.js` | `course.json` + each lesson page: description, exercises (id, title, optional), quiz id, pack path |
| `site/assets/js/search-index.js` | every page: titles, `h2`/`h3` with ids, reference rows (code text, names, description), `<dfn id>` terms, exercises; with each entry's level |
| `site/api-index.html` | every reference row, grouped by target, A–Z (from `templates/page-shell.html`) |
| `site/downloads/*.zip` | `tools/export_exercises.py`: deterministic zips (sorted entries, fixed timestamps) |

`python tools/build.py --check` exits non-zero if any output differs from the committed file.

## 7. Verification

| Tool | Checks |
|---|---|
| `check_site.py` | strict structure; head (charset, viewport, title, description), the three scripts in order with `defer`; ids unique and valid; one `h1`, no skipped levels; links and `#anchors` (planned lessons allowed); images' `alt`; levels valid and monotonic; content sections have levels and ids; callout kinds; version markers; reference rows (inside `api-reference`, id rule, level, no `TODO`); tables have captions and header scopes; script types and their placement; shell tokens; exercise ids/files/roles/hints and numbering; quiz id; lesson pages present in `course.json` |
| `check_content.py` | compiles every `x-python`; runs every example twice (`PYTHONHASHSEED` 0 and 1, so set-order dependence is caught) in a temporary folder through a small harness (stderr merged into stdout, `input()` echoed, tracebacks reduced to the doctest form, `MPLBACKEND=Agg`, `NO_COLOR`) and compares with the page; runs every `x-pycon` with doctest (sessions inside an exercise run against its solution); runs every exercise's tests against its solution (must pass) and its starter (must fail), and for `write_tests` against every mutant; validates quizzes and runs predict-question code. `--update-outputs` rewrites outputs from the real run; `--skip-missing` skips blocks whose `data-requires` libraries are absent; `-j N` runs in parallel |
| `check_coverage.py` | resolves every declared target in the running Python; requires a row for every **required name**: for modules, `__all__` (or the public non-module names); for classes, their own public attributes and special methods (minus `ignore_dunders` in `tools/coverage.json`) plus those inherited from helper bases (not from built-ins or from other targets); every row must name something that exists; exclusions need a reason and go stale loudly. Course-wide: `required_targets` declared somewhere, every keyword used in verified code and documented with a `kw:` row, every AST node type used in verified code, every public standard-library module in the atlas. `--partial` reports unbuilt course-wide items as pending |
| `check_libraries.py` | every pinned library imports on the running Python (in its own process); 21 functional checks exercise each library the way the lessons use it and fix the API generation (`spec/06` §9). `--skip-missing` skips libraries that are not installed |
| `check_pins.py` | (network, not in `ci.py`) for each pin, the newest release on PyPI that installs on the course's Python; `--strict` fails when a pin can move up. Run weekly by `.github/workflows/pins.yml` |
| `tools/tests/` | unit tests for all of the above, the packs and the learner helpers; they also enforce that every pin has a library check and sits in exactly one learner file linked from the setup page |
| `smoke_pages.mjs` | headless Chrome over `file://`: rendering, highlighting, badges, legend, fonts, the on-this-page rail and its current section, the reading-progress line and saved reading position, depth filter (including reference rows and deep links into hidden content), reading settings, shortcuts and their off switch, predict-then-reveal, hints, solution gate, completion codes (JS = Python), quiz of every type, search, theme, continue card, course map, runner setting, API index, mobile layout, 24 px targets, no console errors; axe-core's WCAG 2.2 A/AA rules on every page type in both themes and on the lesson at phone width (0 problems) |
| `ci.py` | runs them in order: unit tests, library checks, ruff on `tools/`, `build.py --check`, site, coverage, content, the spec/05 patterns, the browser. The GitHub workflow runs `ci.py` on Python 3.15 with every pinned library, then deploys `site/` |

## 8. Search and the API index

Search is client-side over `SEARCH_INDEX`: every query word must appear in the entry; matches on a reference name (`dict.get`, `.get`), the start of a title and API rows rank highest; essentials get a small boost. `/` focuses the box (unless the learner turned single-key shortcuts off); arrow keys and Enter navigate. Results link to `#anchors`, which reveal hidden content (§3). The API index is the A–Z view of the same rows.

## 9. Data and notebooks

* Datasets in `site/data/` are synthetic or properly licensed, ≤ 2 MB each, generated by `tools/make_datasets.py` with fixed seeds; `site/data/README.md` documents columns and licences.
* Small examples embed their data in `x-file` blocks; exercises put data in the pack (`x-file` inside the `article.exercise`).
* Notebooks (`site/notebooks/`) are downloaded and run locally; they start with an environment check (Python and library versions) and end with self-check `assert` cells. GPU is never required for graded work.

## 10. Budgets

* `course.js` + `course.css` + `prism.bundle.js` together under 160 KB uncompressed (152 KB, 43 KB gzipped, when the kit was assembled).
* Fonts: self-hosted, split by `unicode-range`; a lesson loads at most three files (87 KB), cached across pages.
* A lesson page under 400 KB of HTML; the search index is loaded only when used.
* Every example runs in under 10 s on a laptop (`data-timeout` for the rare exception); every exercise's tests in under 15 s.

## 11. Security and privacy

* Learner text never reaches `innerHTML`; course content in `innerHTML` (quiz prompts, hints) is authored, trusted HTML.
* No third-party scripts, analytics or font services; the fonts are files in `site/assets/fonts/`. No network requests at all (except links the learner clicks).
* Examples and exercises never need keys or network: HTTP and LLM calls use `course_mocks` in tests; lessons show how to use a real key from an environment variable.
