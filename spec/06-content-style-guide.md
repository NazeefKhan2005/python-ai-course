# 06 · Content style guide

How to write a lesson. `spec/07` is the worked example and the quality bar; `spec/03` §4 is the markup contract.

## 1. Voice and tone

* **A calm, expert mentor sitting next to the learner.** Second person ("you"), active voice, present tense.
* **Plain international English** (CEFR B2). Short sentences (aim for ≤ 20 words), one idea per paragraph, no idioms or culture-bound jokes. Define every term the first time it appears with `<dfn id="term-…">` and add it to the glossary.
* **Encouraging but honest.** Errors are information. Never write "simply", "just", "obviously", "easy" or "trivial".
* **Concrete before abstract:** show a small example, then name the concept, then generalise.
* **Respect for time:** no filler, no motivational padding. Every paragraph explains, shows or asks.

## 2. Lesson anatomy (in this order)

| # | Block | Markup | Notes |
|---|---|---|---|
| 1 | Breadcrumb, title, meta | `p.breadcrumb`, one `h1`, `ul.lesson-meta` | Meta: "Essentials N min · whole page about N h", level, linked prerequisites, Python version |
| 2 | Outcomes | `section.outcomes` | 3–6 measurable "You'll be able to…" items |
| 3 | Run the code yourself | `section.run-locally` | The standard paragraph, the run command, the pack link (`data-pack`) |
| 4 | Warm-up (from M02 on) | `section.quiz#mNN-lNN-warmup` | 1–2 retrieval questions on earlier lessons |
| 5 | Teaching sections | `section[id][data-level]` with `h2`, optional `h3` subsections | Essential sections first, in teaching order; then extra; then advanced (§3) |
| 6 | Reference | `section.api-reference[data-api-targets]` | Complete tables for the lesson's reference targets (§4). Lessons without targets may skip it |
| 7 | Exercises | `section.exercises` with `article.exercise` | 2–4 graded exercises, easy → hard, + optional ★★★ challenge (`spec/05`) |
| 8 | Quiz | `section.quiz#mNN-lNN-quiz` | 4–8 questions, distractors from real misconceptions; mark extra/advanced questions in the prompt ("Advanced:") |
| 9 | Summary | `section.summary` | Level-marked recap bullets, "On the job" and "Interview" callouts, 2–4 links to official docs |
| 10 | Completion + pager | `div.lesson-complete`, `nav.pager` | Always last |

`course.js` adds the breadcrumb, the learner's progress band, the legend ("How to read this page"), the "On this page" navigation, anchors, badges and the command under each example; don't write them by hand (no "Run: …" lines either: the run bar shows the command). Reading-only lessons (rare, e.g. M00-L02) omit 6–7.

## 3. Levels: what is essential, extra or advanced

Every block of teaching carries one of three markers. The learner chooses how much to see with **Show** (Everything / Core / Essentials).

| Level | Badge | Put here | Test |
|---|---|---|---|
| `essential` | ● Essential | What the learner needs to continue the course and do this lesson's required exercises | "Would a junior developer be stuck without this in their first month?" |
| `extra` | ◆ Extra info | Useful depth: variants, less common methods, conveniences, history, related tools, performance notes | "Useful soon, but a beginner can skip it today and come back" |
| `advanced` | ▲ Advanced | Internals, edge cases, rarely used APIs, surprising semantics, interview deep-dives | "Matters for experts, debugging oddities or senior interviews" |

Rules (enforced where possible by `check_site.py`):

1. **Every teaching section has a level.** Paragraphs, list items, figures, callouts and table rows inherit it, or set their own.
2. **A child is never more essential than its parent.** An `advanced` paragraph inside an `extra` section is fine; an `essential` paragraph inside an `extra` section is an error. So: essential material lives in essential sections.
3. **The essentials-only path stands alone.** Read the page with Show set to Essentials before you finish it: it must still make sense, and every required (non-optional) exercise must be solvable from essential content plus earlier lessons. Optional ★★★ challenges may draw on extra content.
4. **Mark honestly, not generously.** On a typical page about 40–60 % of the words are essential. If everything is essential, nothing is.
5. **Order inside the page**: essential sections first, in the order you teach them; then extra sections; then advanced ones. Within a section, an extra or advanced subsection or paragraph may follow the essential text it deepens.
6. **Reference rows get levels too**, so Show → Essentials turns each reference table into a cheat sheet (and essential names are highlighted even when everything shows): mark as essential the 20–30 % of names a beginner uses weekly.

## 4. Complete coverage and the reference section

"The lesson covers everything available on the topic" has a precise meaning in this course:

1. **Concepts:** everything in the curriculum's Essential and "Extra & advanced" columns for the lesson, at the level shown there (◆ extra, ▲ advanced).
2. **API surface:** for each **reference target** the curriculum assigns to the lesson (`Ref:` in the phase file; the full map is `spec/02` §4), one reference row for every required public name, checked by `tools/check_coverage.py` against the real object in Python 3.15:
   * a **class**: its constructor, every public method and attribute, and every special method it defines (operators, `len`, iteration, `repr`, hashing, generics…), plus those inherited from helper base classes;
   * a **module**: every name in `__all__` (or every public non-module name);
   * **course-wide**: every keyword (`kw:` rows, M01-L07), every public standard-library module (`module:` rows, M27-L01), and every piece of syntax (every AST node type appears in at least one verified example somewhere in the course).
3. **Behaviour:** every method you list is described correctly, including the edge case people get wrong (what it returns, whether it changes the object, what it raises).

**Writing reference tables**

* Start from `python tools/api_skeleton.py <target>`: it prints one draft row per required name with its real signature and the first docstring line, marked `TODO`. Then edit: group related names into one row (`data-api="dict.__eq__ dict.__ne__"`), write every description in course voice, set each row's level, delete every `TODO`.
* Columns: **Code** (how you write it: `d.get(k, default=None)`, `k in d`, `len(d)`; operators shown as operators, not dunder calls) · **What it does** (one sentence, returns/raises) · **Notes** (pitfalls, versions, complexity, "see section X"). Group rows under captions by task ("Creating", "Reading", "Changing", "Views"…).
* Order rows by task, then by importance; never alphabetically unless the table is an index.
* Use `syntax:…` rows for syntax that belongs to the topic (literals, comprehensions, unpacking) and `concept:…` rows for related names that aren't attributes of a target (for example a name added after the course's Python version, with `data-version`).
* A name may be left out only through an **exclusion with a reason** in `tools/coverage.json` (for example an internal hook that has no user-facing meaning). Exclusions are rare and reviewed.
* Teaching sections link to rows (`#api-dict-get`) and rows point back to sections ("see Merge dictionaries").

## 5. Kind markers (callouts)

`<aside class="callout" data-kind="…">`, optionally with `<p class="callout-title">` and its own `data-level`.

| Kind | Rendered as | Use for |
|---|---|---|
| `tip` | Tip | A better or faster way |
| `pitfall` | Common mistake | A frequent error: the message, the cause, the fix |
| `version` | Version note · Python 3.x | Behaviour that changed, or a newer feature (needs `data-version`) |
| `interview` | Interview | A question as interviewers phrase it, with a strong 80–150-word answer |
| `job` | On the job | Where this appears in real roles and tools (2–4 sentences) |
| `hood` | Under the hood | The mechanism, once the surface is understood |
| `try` | Try it yourself | A modification to run locally and what to look for (the "Investigate/Modify" of PRIMM) |
| `deprecated` | Deprecated | Old APIs still seen in code, and their replacement |
| `performance` | Performance | Costs, complexity, measured trade-offs |
| `security` | Security | Data loss, injection, secrets, unsafe deserialisation |
| `note` | Note | Anything else that is useful but secondary |

Callouts hold side information; never put the main explanation of an essential idea in one. Every lesson has at least one `pitfall`, one `job` and one `interview` callout. Inline version markers: `<span class="version" data-version="3.9" data-change="added"></span>`.

## 6. Budgets

| Item | Target |
|---|---|
| Essentials path | 30–60 minutes including the required exercises (state it in the meta) |
| Whole page | Up to about 3 hours for big reference lessons; state the honest total |
| Examples | 4–20 per page; each ≤ 25 lines, one new idea, prints something meaningful, runs in < 2 s (`data-timeout` only for model training) |
| Exercises | 2–4 required + an optional challenge |
| Paragraph | ≤ 5 sentences |
| Code line | ≤ 88 characters |

## 7. Explaining well (PRIMM, locally)

* **Predict → Run → Investigate → Modify → Make.** Put `data-predict` on 1–3 key examples per page so the output stays hidden until revealed. Ask the learner to run examples themselves; follow important ones with a `try` callout ("change `0` to `None` and run it again: what happens?").
* **Contrast pairs** for common mistakes (`d[key]` vs `d.get(key)`), ideally as one example that ends in the real error (`data-raises`).
* **Mental models** used once, then dropped (a dictionary is a coat check).
* **Name the pattern** ("the counting pattern"), so it transfers.
* **Interleave review**: reuse earlier lessons ("you met `enumerate` in M02-L03") and link to them.

## 8. Outputs are produced, never typed

* Write the code, then run `python tools/check_content.py <page> --update-outputs`. Read every output it wrote; if it surprises you, the code or the text is wrong.
* Non-determinism is a bug in an example: seed random generators, sort sets before printing, avoid timings and memory addresses. When variation is the point, use `data-output="sample"` (labelled "Sample output") or `data-match="ellipsis"`.
* Errors are part of the output: end the example on purpose with `data-raises` and explain the message.
* Library output (DataFrames, arrays, model reprs) depends on versions: the pinned `requirements-*.txt` are the contract.
* Some pinned libraries print extra lines that would make a verified output differ between machines or runs. Switch them off in the example itself, so the learner sees the same output as the page: transformers progress bars (`transformers.utils.logging.disable_progress_bar()`), Prophet's `cmdstanpy` INFO lines (`logging.getLogger("cmdstanpy").setLevel(logging.ERROR)`), MLflow's INFO hint on import (environment variable `MLFLOW_DISABLE_AGENT_HINT=1`, set before `import mlflow`). Where that isn't possible, use `data-output="sample"` or `data-match="ellipsis"`.
* **Outputs must be the same on every operating system.** Outputs are produced on the author's computer, checked again on Linux by CI, and compared by learners on Windows, macOS and Linux. Print floating-point results of linear algebra, statistics and training rounded (`f"{x:.4f}"`, `round(x, 4)`, `np.set_printoptions(precision=4, suppress=True)`), because maths libraries differ in the last digits; don't print absolute paths, user names, `sys.platform` or anything else that names the machine. When CI's output differs from yours, fix the example and run `--update-outputs` again. Only output that really varies between machines, such as training metrics after many steps, becomes `data-output="sample"`, with a sentence saying the numbers vary slightly between computers.

## 9. Code style in lessons

* PEP 8, ruff-clean under the pinned ruff's default rules (ruff 0.16+ enables 413 rules; examples that show a mistake on purpose are the exception), f-strings, `pathlib`, meaningful names, no single letters except loop indexes and maths (`X`, `y`, `i`).
* Type hints and Google-style docstrings from **M04-L04** on, in starters, solutions and examples.
* Imports at the top; aliases `np`, `pd`, `plt`, `sns`, `nn`, `F`.
* **Modern APIs only**, written for the pinned major versions. `tools/check_libraries.py` exercises most of these, so a pin bump that changes one usually shows up there first:

  | Library (pinned) | Write | Not (older generations, still common in tutorials) |
  |---|---|---|
  | pandas 3.1 | Copy-on-Write is the only mode (assign the result; chained assignment never changes the original); strings get the `str` dtype; `DataFrame.map` | `inplace=True`, `df.append`, `applymap`, the `mode.copy_on_write` option |
  | NumPy 2.5 | `np.random.default_rng(seed)`; `np.float64` | `np.random.seed`, the removed aliases `np.float_`, `np.NaN` |
  | DuckDB 2.0 | `duckdb.sql(q).fetchall()`, `.df()`, `.pl()`; `con.execute(q).fetchone()` on a connection | `duckdb.sql(q).fetchone()`: relations re-run on every call and have no `fetchone()` |
  | scikit-learn 1.9 | `Pipeline`, `ColumnTransformer`, `set_output(transform="pandas")`; skops for model files | pickling untrusted models |
  | PyTorch 2.15 | `torch.load(path)` for state dicts (`weights_only=True` is the default); `torchvision.transforms.v2` | `torch.load` of whole pickled objects; `transforms` v1 |
  | transformers 5.24 | PyTorch classes; `from_pretrained(..., dtype=torch.float16)` | `TF*`/`Flax*` classes (removed), `torch_dtype=` (deprecated) |
  | MLflow 3.18 | `mlflow.sklearn.log_model(model, name="model")` | `artifact_path=` (deprecated) |
  | MCP Python SDK 2.3 | `from mcp.server.mcpserver import MCPServer`; `@server.tool()`; `tool.input_schema` | `FastMCP` (renamed; importing `mcp.server.fastmcp` fails with a pointer to the migration guide), `inputSchema` |
  | FastAPI 0.165 | `FastAPI(lifespan=...)` to load models once; `TestClient` as a context manager | `@app.on_event("startup")` (deprecated) |
  | pydantic 2.14 | `model_validate`, `model_dump`, `field_validator`, `ConfigDict` | v1 `parse_obj`, `dict()`, `validator` |
  | SQLAlchemy 2.1 | `DeclarativeBase`, `Mapped[...]`, `mapped_column`, `session.scalars(select(...))` | `declarative_base()`, `session.query(...)` |
  | Gymnasium 1.4 | `obs, info = env.reset(seed=0)`; `obs, reward, terminated, truncated, info = env.step(a)` | gym's 4-value `step` and `done` |
  | pytest 9.2 | `[tool.pytest]` in `pyproject.toml` (native TOML) | — (`[tool.pytest.ini_options]` still works) |
  | ruff 0.17 | the default rule set (413 rules), narrowed or extended with `select`/`extend-select` | assuming only pyflakes and a few pycodestyle rules run by default |

  Also: `datetime.now(timezone.utc)`, and the OpenAI and Anthropic SDKs as `client.responses.create(...)` / `client.messages.create(...)` with the learner's own key.
* Comments explain **why**. Label steps in longer examples.
* Examples that are programs end with output; examples that define functions also call them.

## 10. Version notes

* The course is verified with **Python 3.15**, the latest stable release. Features added in recent versions (3.12–3.15: the `type` statement, t-strings, `except A, B:`, `lazy import`, `frozendict`, `sentinel`, unpacking in comprehensions, UTF-8 by default…) are taught as normal content with an inline `span.version` ("New in 3.15"), so learners on older systems know why something fails for them.
* Features of a future version (3.16) appear only as `version` callouts, with `data-python="3.16"` on their examples; CI verifies them once it runs that version.
* Older behaviour still common in the wild gets a `version` or `deprecated` callout ("before 3.7, dict order was not guaranteed").
* Library versions: say "pandas 3", "NumPy 2" where behaviour differs. Never state model names, prices, free tiers or "latest version" numbers as facts in lesson text; link to the official page.

## 11. Examples, names and data

* **Realistic, global and inclusive:** names from many cultures (Aisyah, Ben, Chen, Dev, Fatima, Kofi, Lucía, Mei, Omar, Priya, Tomás, Yuki…), mixed genders, everyday contexts (online shops, ride-hailing, clinics, universities, energy). Avoid stereotypes.
* **Fictional entities** only; no real personal data. Metric units, ISO dates, 24-hour times, a generic currency.
* Data comes from `site/data/` or inline `x-file` blocks; describe the columns before using them.

## 12. Maths, diagrams and images

* Maths: native **MathML** (`<math>`), supported by current browsers with no script, or plain Unicode for simple formulas. Always pair a formula with NumPy code and a plain-English sentence.
* Diagrams: inline SVG using CSS variables for colours (dark mode), `role="img"` and a `<title>`.
* Images: compressed, explicit `width`/`height`, meaningful `alt`; charts generated by code (saved by the example) rather than screenshots.

## 13. Accessibility in writing

* Descriptive link text. Never rely on colour alone. Headings form an outline (one `h1`, `h2` → `h3`).
* Tables: a `<caption>` and `th scope`. Code in prose uses `<code>`. Expand abbreviations on first use.

## 14. Avoid

* Anything that runs code in the browser; fake or hand-typed outputs; screenshots of code.
* Walls of text; more than one new idea per example; unexplained "magic" lines.
* Copying documentation text; reproducing copyrighted material.
* Outdated idioms: `%`-formatting in new code, `os.path` where `pathlib` fits, `np.random.seed`, `DataFrame.append`, `inplace=True`, `sklearn.cross_validation`, `torch.autograd.Variable`, `datetime.utcnow()`.
* Unsupported claims ("10× faster") without a measured example.
* Secrets, keys or tokens, even fake-looking ones.

## 15. Lesson self-review (before running the checks)

1. Set **Show** to **Essentials** and read the page top to bottom: does it teach everything the required exercises need?
2. Switch to **Everything**: is every curriculum item (Essential and Extra & advanced) present, and is every level honest?
3. Does every outcome map to an exercise or quiz question?
4. Can a beginner predict each `data-predict` example after reading the text above it?
5. Are reference descriptions correct, in course voice, and free of `TODO`? Do teaching sections link to the rows they explain?
6. Are the hints a ladder whose third rung unblocks without handing over the code?
7. Read it aloud: cut anything confusing, preachy or padded.
