# Phase 6 · Production & Career

**Goal:** ship models as tested, containerised, monitored services with CI/CD, and get hired: portfolio, CV, interview loops, system design.
**Modules:** M24–M27 · 25 lessons · ~40 h · **Portfolio project P6:** deployed, monitored ML service · **Capstone** afterwards (`spec/09`) · **Phase exam `p6-exam`:** an ML system design write-up (rubric) + a 60-minute timed coding assessment.

**Phase teaching notes**
* Everything runs on the learner's machine. Pure-Python parts (pydantic models, request handlers, drift statistics, config validation, async code) are graded with pytest; servers, Docker and cloud deployment are **workflow tasks** checked by project rubrics.
* FastAPI exercises call the app with FastAPI's `TestClient` inside pytest (in `requirements-production.txt`), so no server needs to be running.
* Cloud providers, free tiers and prices change often. Lessons explain how to **check** current options, avoid promising specific free tiers, and use placeholders.

---

## M24 · APIs, Apps & Deployment
`m24-deployment` · 6 lessons · ~10 h · Needs M10, M17

**Why it matters at work:** a model creates value only when other systems and people can use it. ML engineers are expected to ship an API, a demo and a container.

**Outcomes:** design clean HTTP APIs for ML; build FastAPI services with pydantic validation; serve models safely (loading, versioning, health checks); build quick demos with Streamlit or Gradio; containerise with Docker; deploy to a cloud platform with secrets handled correctly.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises / tasks |
|---|---|---|---|
| **m24-l01** `l01-api-design` HTTP & API design for ML | Resources, methods, status codes, idempotency, versioning, pagination, error formats, OpenAPI; latency budgets | ◆ methods and status codes, REST design ▲ idempotency | **E1** `validate_request(payload: dict) -> tuple[bool, list[str]]`. Quiz: pick status codes for 6 scenarios |
| **m24-l02** `l02-fastapi` FastAPI essentials | Path and query parameters, pydantic request/response models, dependency injection, error handling, async endpoints, auto docs; testing with `TestClient` (local) | ◆ path, query and body parameters, pydantic models, dependencies ▲ async endpoints | **E1** pydantic `PredictRequest`/`PredictResponse` models with validators. **E2** `predict_endpoint(req, model)`, the endpoint function called directly. Local task: run it with Uvicorn and open `/docs` |
| **m24-l03** `l03-serving-models` Serving models | Persistence (joblib/pickle **security risks**; skops files loaded with explicit trusted types; ONNX export with skl2onnx, checked with ONNX's reference runtime `onnx.reference`; ONNX Runtime as the production runtime, overview until it installs on 3.15: `spec/02` §5.1), loading at startup (lifespan), input validation, batch vs online inference, model version in responses, health and readiness endpoints | ◆ loading a model once, batching ▲ model versions in an API | **E1** `predict_handler(payload, model, version) -> dict` with input validation and error mapping. Quiz: pickle safety |
| **m24-l04** `l04-demo-apps` Demo apps with Streamlit & Gradio | When to use which; widgets, state, caching; Hugging Face Spaces deployment | ◆ Streamlit and Gradio basics ▲ caching in Streamlit | Local task: a Gradio or Streamlit demo of the P4 model. Quiz on caching and state |
| **m24-l05** `l05-docker` Docker for data scientists | Images vs containers, Dockerfile best practices (slim base, layer caching, non-root user, uv in Docker, `.dockerignore`), `docker compose` (API + database), image size | ◆ Dockerfile instructions, layers, `.dockerignore` ▲ multi-stage builds | **Review exercise:** find 6 problems in a Dockerfile (multi-select with explanations). Local task: containerise the FastAPI service |
| **m24-l06** `l06-cloud-deployment` Cloud deployment | Options (managed platforms, HF Spaces, serverless, the big three in outline), environment variables and secrets, logs, costs (how to check, not promises), CI deploy, HTTPS and domains | ◆ PaaS vs containers vs serverless ▲ secrets management | Local task: deploy the container; the README has the URL and a health-check badge |

**Module project:** folded into P6 (the API + Docker + demo part).
**Checkpoint (`m24-checkpoint`, 14 Q).**
**Interview corner:** design an API for a fraud model · scaling inference (batching, caching, autoscaling) · Docker basics · how to manage secrets.
**Misconceptions:** pickle files are safe to load from anywhere; `localhost` inside a container is the host; one endpoint per model version is unnecessary.

---

## M25 · MLOps & Production ML
`m25-mlops` · 7 lessons · ~11 h · Needs M24

**Why it matters at work:** models decay as data changes. Companies need reproducible pipelines, tracked experiments, tested ML code, automated deployments, monitoring and a plan for retraining.

**Outcomes:** explain the production ML lifecycle and its failure modes; build reproducible, configurable pipelines; track experiments and manage model versions; test data and models; set up CI/CD for ML; detect drift; reason about scaling and concurrency.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises / tasks |
|---|---|---|---|
| **m25-l01** `l01-ml-lifecycle` The ML lifecycle in production | Training–serving skew, hidden technical debt, batch vs real-time systems, MLOps maturity levels, roles and handoffs | ◆ stages, roles, failure modes ▲ ML technical debt | Quiz on case studies (8 Q). **E1** `detect_skew(train_stats, serving_stats, tol) -> list[str]` |
| **m25-l02** `l02-reproducible-pipelines` Reproducible pipelines & configuration | Config files + pydantic validation, pipeline stages, data and model versioning (DVC concepts), artifact stores, seeds | ◆ configuration files, CLI entry points ▲ data versioning | **E1** `load_config(yaml_text) -> TrainConfig` (pyyaml + pydantic; clear errors) |
| **m25-l03** `l03-tracking-registry` Experiment tracking & model registry | MLflow tracking and registry (local), params/metrics/artifacts, aliases and promotion rules | ◆ MLflow tracking and registry ▲ model lineage | **E1** `select_champion(runs, metric, min_gain) -> str \| None` |
| **m25-l04** `l04-testing-ml` Testing ML systems | Data validation tests, behavioural model tests (invariance, directional, minimum functionality), pipeline tests with pytest, golden datasets | ◆ data tests and model tests ▲ behavioural testing | **E1** (`write_tests`) for a feature function (mutants: off-by-one window, wrong fill, leakage). **E2** `invariance_test(model, X, perturb, tol) -> float` |
| **m25-l05** `l05-ci-cd-ml` CI/CD for ML | GitHub Actions: test → train → evaluate → **gate on metrics** → build the image → deploy; scheduled retraining; model cards in CI | ◆ CI for ML, model gates ▲ canary releases | Quiz: read a workflow (8 Q). Local task (P6): a metric gate in CI |
| **m25-l06** `l06-monitoring-drift` Monitoring & drift | What to monitor (latency, errors, data quality, drift, delayed-label performance); **PSI**, KS test, categorical drift; alert thresholds; retraining triggers; streaming drift detectors with River (ADWIN, Page-Hinkley); monitoring tools such as Evidently as overview (`spec/02` §5.1) | ◆ drift statistics (PSI, KS) ▲ concept vs data drift | **E1** `psi(expected, actual, bins=10) -> float`. **E2** `ks_drift(ref, cur, alpha) -> bool`. **E3** `drift_report(ref_df, cur_df) -> pd.DataFrame` |
| **m25-l07** `l07-scaling-concurrency` Scaling & concurrency | CPU-bound vs I/O-bound work; threads, processes, **asyncio** (first taught in M08-L08); `concurrent.futures`; free-threaded Python; vectorisation; Polars/DuckDB for larger data; Spark (hands-on in E4) and Ray (overview, `spec/02` §5.1) | ◆ processes for CPU-bound work, async I/O at scale (builds on M08-L08) ▲ free-threaded Python | **E1** `fetch_all(urls, fetch) -> list` with `asyncio.gather` and a concurrency limit (`Semaphore`); tests use a fake async fetch and check timing. **E2** `chunked_mean(path, column, chunksize) -> float` |

**Phase 6 portfolio project (`p6-project`):** deployed, monitored ML service (`spec/09`). **Checkpoint (`m25-checkpoint`, 14 Q).**
**Interview corner:** training–serving skew · how to detect drift · design a retraining pipeline · asyncio vs threads vs processes.
**Misconceptions:** a model is done when deployed; drift always means retrain; asyncio makes CPU-bound code faster.

---

## M26 · Career Launchpad
`m26-career` · 8 lessons · ~12 h · Needs: start any time after Phase 2; finish before the capstone

**Why it matters:** skills only turn into offers when they're visible and well communicated. This module turns course evidence into a job search. Detailed content and question banks are in `spec/10`.

**Outcomes:** choose target roles and read job descriptions critically; present a strong GitHub portfolio; write an ATS-friendly CV and LinkedIn profile with impact bullets; prepare for coding, ML/stats/SQL, system design and behavioural interviews; handle take-home assignments; plan continuous learning.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded / evaluative activities |
|---|---|---|---|
| **m26-l01** `l01-job-market-roles` The AI job market & roles | Role profiles and skills matrices, reading job descriptions (must-have vs nice-to-have), internships and graduate programmes, choosing targets, a T-shaped profile | ◆ comparing roles ▲ negotiating offers | Quiz: classify JD requirements. **Self-assessment** against the `spec/01` competencies (saved) |
| **m26-l02** `l02-portfolio-github` Portfolio & GitHub | What recruiters scan in 30 seconds; choosing 3–5 projects; a README template; pinned repos; demos and videos; writing about projects; open-source contributions | ◆ README quality, pinned repositories ▲ open-source contributions | **Rubric** self-check of the portfolio repository (`spec/09` README template) |
| **m26-l03** `l03-resume-linkedin` CV & LinkedIn | ATS-friendly format, impact bullets (action + what + measurable result), tailoring, the projects section, LinkedIn headline and about section, networking messages | ◆ ATS-friendly CVs ▲ portfolios for career changers | **Exercise:** rewrite 5 weak bullets; self-check with the rubric; optional AI-review prompt (policy `explain`) |
| **m26-l04** `l04-coding-interviews` Coding interviews | Online assessments vs live coding, the interview method, thinking aloud, testing your own code, complexity, a pattern map (M09) | ◆ the patterns map, timing yourself ▲ live-coding etiquette | **Timed assessment** (`exams/coding-assessment.html`): 3 problems, 60 minutes, `ai_policy: none` |
| **m26-l05** `l05-ml-stats-sql-interviews` ML, statistics & SQL interviews | Theory question styles, explaining trade-offs, case questions, live SQL | ◆ classic ML, statistics and SQL questions ▲ case studies | **Randomised quiz** from the `spec/10` bank (40 Q pool, 15 per attempt) |
| **m26-l06** `l06-ml-system-design` ML system design interviews | The framework (clarify → objectives and metrics → data → features → model → evaluation → serving → monitoring → iteration); worked examples (recommendations, fraud detection, search ranking, RAG assistant) | ◆ a design template ▲ discussing trade-offs | **Design exercise** with a model answer and a self-scoring rubric (structured form, saved) |
| **m26-l07** `l07-takehome-behavioral` Take-homes & behavioural interviews | Take-home strategy (scope, assumptions, tests, README, time-boxing); STAR stories; a story bank; questions to ask; offers and negotiation basics | ◆ STAR stories ▲ scoping a take-home | **STAR builder** (structured form, saved). **Take-home simulation** brief (4 hours, rubric) |
| **m26-l08** `l08-keep-growing` Keep growing | A learning plan after the course; reading papers; Kaggle; communities; certifications (optional); avoiding tutorial hell; teaching others | ◆ a learning plan ▲ reading papers | **Plan builder:** a 12-week plan saved as Markdown to download |

**Interview corner:** this whole module. **Checkpoint:** none (activities instead). **Capstone** follows (`spec/09`).

---

## M27 · Standard Library Atlas (reference module)
`m27-stdlib-atlas` · 4 lessons · ~7 h · Needs M06 · Open it any time after Phase 1; learners use it as a reference for the rest of their careers.

**Why it matters at work:** "there's a module for that" saves days. Knowing what the standard library offers (and what it doesn't) is the difference between writing 200 lines and importing one function.

**Outcomes:** find the right standard-library module for a task; read its documentation quickly; use dates and time zones, exact decimal arithmetic, archives and persistence correctly and safely.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m27-l01** `l01-stdlib-atlas` The standard library atlas | How the standard library is organised (the documentation's categories); the 30 modules every Python developer uses; how to read a module's docs page | ◆ one row for **every** public module: purpose, level marker, platform notes, and where the course teaches it ▲ modules removed in 3.13 (PEP 594) and 3.15 (`sre_*`) and what replaced them; new in 3.15: `profiling`, `math.integer`; platform-only modules · **Ref:** a `module:` row for every module in `sys.stdlib_module_names` (minus the exclusions in `tools/coverage.json`) | **E1** `modules_used(source: str) -> set[str]` lists the top-level modules a program imports (`ast`). **E2** `classify(modules) -> dict[str, list[str]]` splits them into standard library and third-party with `sys.stdlib_module_names` |
| **m27-l02** `l02-dates-times` Dates, times & time zones | `date`, `datetime`, `timedelta`; aware vs naive; `zoneinfo.ZoneInfo`; ISO 8601 with `fromisoformat`/`isoformat`; `strftime`/`strptime` | ◆ every method of the five `datetime` classes; the `time` module's clocks (`time`, `monotonic`, `perf_counter`, `sleep`) ▲ DST gaps and folds (`fold`), `time.time_ns`, leap seconds; `utcnow()` is deprecated (use `datetime.now(datetime.UTC)`), and since 3.15 `strptime` rejects `%d` without a year · **Ref:** `module:datetime` `class:datetime.date` `class:datetime.datetime` `class:datetime.time` `class:datetime.timedelta` `class:datetime.timezone` `module:zoneinfo` `module:time` | **E1** `business_days_between(start, end) -> int`. **E2** `to_utc(local: str, tz: str) -> datetime` across a DST change. **E3** `parse_log_time(line: str) -> datetime` |
| **m27-l03** `l03-exact-numbers` Exact numbers: decimal & fractions | Why `0.1 + 0.2 != 0.3`; `Decimal` for money (build from strings, `quantize`, rounding modes); `Fraction` | ◆ every `decimal` context setting, signals and traps; `Fraction.limit_denominator` ▲ the `numbers` tower, performance of `Decimal` · **Ref:** `module:decimal` `module:fractions` | **E1** `split_bill(total: str, people: int) -> list[Decimal]` whose parts add up exactly. **E2** `best_fraction(x: float, max_denominator: int) -> Fraction` |
| **m27-l04** `l04-archives-persistence` Archives & persistence | Reading and writing zip archives and gzip files; `pickle` and why you never unpickle untrusted data | ◆ every `zipfile` class and method, `gzip` options, pickle protocols, `shelve`/`dbm` and `tarfile` with extraction filters (3.12+) ▲ `__reduce__`, `copyreg`, restricting `Unpickler.find_class` · **Ref:** `module:zipfile` `module:gzip` `module:pickle` | **E1** `zip_folder(folder, out) -> list[str]` with a deterministic order. **E2** `read_jsonl_gz(path) -> list[dict]`. **E3** `safe_load(path)` allows only listed classes |

**Module checkpoint (`m27-checkpoint`):** 15 "which module would you use?" questions plus 5 predict-the-output questions on dates and decimals.
