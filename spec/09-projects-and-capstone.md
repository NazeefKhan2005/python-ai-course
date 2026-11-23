# 09 · Projects & capstone

Projects turn exercises into evidence a recruiter can see. Each phase ends with a **portfolio project** in the learner's own GitHub repository, assessed with a rubric (`spec/05` §10). The **capstone** is an end-to-end AI product. Every project page in `site/projects/` contains: the brief, requirements, milestones, the rubric component, a submission checklist and a review prompt.

## 1. Rules for every portfolio project

* **Its own repository** (or a folder in `python-ai-portfolio`) with: `README.md` (template in §10), `src/` or a notebook with a clear structure, `tests/`, `pyproject.toml` (uv), `.gitignore`, a licence (MIT recommended), and a meaningful commit history (no single "final" commit).
* **From P2 on:** CI on GitHub Actions (tests + ruff), type hints, and a status badge.
* **From P3 on:** a demo (a live URL, a GIF or a 2-minute video) and a "Results" section with numbers.
* **An "AI usage" section:** what assistants were used for (allowed by the project's policy, usually `pair`) and what the learner verified. Undisclosed AI-written code fails the integrity row.
* **Data:** synthetic or properly licensed, never personal data. Keys go in `.env` (git-ignored), with a `.env.example` committed.

**Rubric levels** (all projects): **Beginning** (missing or broken) · **Developing** (partly meets Proficient) · **Proficient** (meets the descriptor) · **Exemplary** (exceeds it as described). Passing a project means at least Proficient on **every** row.

---

## 2. P1 · CLI Expense Tracker (after M06) · ~10 h · `ai_policy: hints-only`

**Brief:** Build `spent`, a command-line tool to record expenses and see where money goes.
**Must:** `spent add 12.50 food "lunch" [--date 2026-03-01]`, `spent list [--month 2026-03] [--category food]`, `spent summary --month 2026-03` (totals per category, sorted, with a percentage), `spent export out.csv`; data stored as JSON in the user's home folder (`pathlib`); validation with clear errors (negative amounts, bad dates, unknown commands); exit codes; at least 10 pytest tests.
**Should:** budgets per category with warnings; `spent undo`; colourised output (optional `rich`).
**Could:** monthly bar chart in the terminal; import from CSV.
**Milestones:** (1) data model and storage, (2) `add`/`list`, (3) `summary`/`export`, (4) errors and tests, (5) README with a demo GIF.

| Criterion (weight) | Proficient | Exemplary |
|---|---|---|
| Functionality (30) | All "must" commands work as specified, including edge cases | Plus 2+ "should" features, robust to corrupted data files |
| Code quality (20) | Small functions, clear names, no globals, PEP 8 | Modules split by responsibility; docstrings; type hints |
| Errors and UX (15) | Helpful messages, correct exit codes, no tracebacks for user mistakes | `--help` is excellent; consistent output formatting |
| Testing (20) | 10+ tests covering happy paths and 3+ edge cases | Uses `tmp_path` fixtures; tests the CLI end to end |
| README and Git (15) | Install, usage examples, demo; 8+ meaningful commits | Design notes and limitations section |

## 3. P2 · `textkit`: a tested, typed Python package with CI (after M10) · ~12 h · `ai_policy: explain`

**Brief:** Package the text tools from M05 (tokenize, n-grams, bag-of-words, similarity, slugify, keyword extraction) as a reusable library other people could `pip install`.
**Must:** `src/textkit/` layout, `pyproject.toml` built with uv; full type hints (mypy `--strict` clean); ruff clean; pytest with ≥ 90% line coverage (pytest-cov); GitHub Actions running on 3.14 and 3.15; a published **TestPyPI** release; docstrings on the public API; a CHANGELOG and semantic version `0.1.0`.
**Should:** property-based tests (Hypothesis, local); docs site (MkDocs); pre-commit hooks.
**Could:** a CLI entry point (`textkit stats file.txt`); a benchmark script.

| Criterion (weight) | Proficient | Exemplary |
|---|---|---|
| API design (20) | Clear, consistent function names and signatures; no surprising side effects | Thoughtful defaults, input validation, documented complexity |
| Tests and coverage (25) | ≥ 90% coverage; edge cases; parametrised tests | Property-based tests; mutation-style thinking in the README |
| Types and lint (15) | mypy strict and ruff pass in CI | `py.typed` marker; typed public API documented |
| Packaging and release (20) | Builds; installs from TestPyPI in a fresh env | Versioning policy; automated release workflow |
| Docs and Git workflow (20) | README with usage; PR-based history; CHANGELOG | Docs site; contribution guide; issue templates |

## 4. P3 · End-to-end analytics report (after M15) · ~14 h · `ai_policy: pair` (disclosed)

**Brief:** A (fictional) food-delivery company asks: *"Why did repeat orders fall last quarter, and what should we do?"* Use the course's synthetic datasets (orders in SQLite, customers in CSV, a mock promotions API) and produce a decision-ready report.
**Must:** ingestion (SQL with joins and a window function, plus paginated API calls via the mock client) → cleaning (documented decisions) → analysis (cohort/repeat-rate analysis, one statistical test with an effect size) → 5–7 well-designed charts → a **two-page executive summary** with recommendations → a reproducible notebook or script (`uv run`), plus data-validation checks (pydantic or pandera).
**Should:** a Streamlit page with filters; an A/B test design for one recommendation.
**Could:** a Polars or DuckDB version of the heaviest step, with timing.

| Criterion (weight) | Proficient | Exemplary |
|---|---|---|
| Question and framing (10) | Restates the business question; defines metrics | Hypotheses written before the analysis; limitations noted |
| Data work (25) | Correct joins (validated), cleaning documented, reproducible | Tests for data assumptions; idempotent pipeline |
| Analysis and statistics (25) | Correct cohort maths; a test with an effect size and its interpretation | Sensitivity checks; confidence intervals throughout |
| Visualisation (20) | Right chart types; labelled; accessible colours; one insight per chart | Annotated storytelling; consistent style |
| Communication (20) | Executive summary a manager could act on | Clear recommendations with expected impact and risks |

## 5. P4 · Churn prediction with a model card (after M19) · ~15 h · `ai_policy: pair`

**Brief:** Predict which telecom customers will churn next month (`telco_churn.csv`, synthetic) so the retention team can call the top 10% riskiest.
**Must:** baseline → leak-proof `Pipeline` → at least 3 model families compared with CV → tuned final model → evaluation on a held-out test set with **business-relevant metrics** (precision@top-10%, recall, PR-AUC) and a cost-based threshold → interpretation (permutation importance, PDP for the top 3 features) → error analysis by segment → a fairness check across a sensitive attribute (`age_band`) → a **model card** → a saved pipeline (skops or joblib, with a note on pickle safety).
**Should:** calibration; MLflow tracking; a simple Gradio demo.
**Could:** SHAP local explanations (notebook); a monitoring plan.

| Criterion (weight) | Proficient | Exemplary |
|---|---|---|
| Methodology (25) | Correct splits, no leakage, CV comparisons, baseline beaten | Nested CV or repeated CV; leakage tests in code |
| Modelling (20) | 3+ families, tuned sensibly, choice justified | Calibration; well-argued trade-offs (speed, interpretability) |
| Evaluation (20) | Business metrics + threshold choice explained | Cost curves; confidence intervals on key metrics |
| Responsible AI (20) | Error analysis + fairness check + model card | Mitigation tried and evaluated; limits stated honestly |
| Engineering (15) | Clean repo, tests for features, saved pipeline, README | CI running training smoke tests; a reproducible environment |

## 6. P5 · RAG assistant **or** image classifier app (after M23) · ~16 h · `ai_policy: pair`

**Option A: RAG assistant.** Q&A over the fictional company handbook (`site/data/docs/`) or a documentation set the learner may legally use.
**Must:** ingestion and chunking with metadata; embeddings (a real embedding model run locally with sentence-transformers, or a hosted API with the key in `.env`); a vector index (FAISS; another vector store only if it installs on the course's Python, `spec/02` §5.1); hybrid retrieval (BM25 + vectors); answers with **citations**; refusal when the answer isn't in the sources; an **evaluation set of 30+ questions** with retrieval metrics (recall@k, MRR) and answer metrics (token-F1 or a rubric-based judge with documented caveats); a prompt-injection test set (10+ cases) with results; a simple UI (Gradio or Streamlit); a cost and latency table.

**Option B: image classifier app.** Transfer learning on a small, permissively licensed image dataset.
**Must:** train/val/test split, augmentation, fine-tuned backbone, a confusion matrix, per-class metrics, error analysis with misclassified examples, a model card, a Gradio demo on Hugging Face Spaces, and inference latency on CPU.

| Criterion (weight) | Proficient | Exemplary |
|---|---|---|
| System design (20) | Clear architecture diagram; sensible components | Alternatives considered with trade-offs |
| Quality evaluation (30) | A real evaluation set and metrics, reported honestly | Ablations (chunk size, k, reranking / augmentations, backbones) |
| Safety and robustness (20) | Injection tests or failure analysis; handles "don't know" | Mitigations measured before and after |
| Engineering (15) | Clean code, config, tests for the core logic | CI, caching, cost/latency optimisations |
| Demo and docs (15) | A working demo and a README with results | A 2-minute video walkthrough |

## 7. P6 · A deployed, monitored ML service (after M25) · ~15 h · `ai_policy: pair`

**Brief:** Ship the P4 model (or the P5 classifier) as a production-style service.
**Must:** FastAPI with pydantic request/response models, `/predict`, `/health` and `/version`; input validation and error mapping; a Dockerfile (slim, non-root, layer-cached); tests (unit + API via `TestClient`); GitHub Actions: test → build image → **gate on a metric threshold** → deploy to a cloud platform; structured logging; a **drift report** comparing a "current" batch with the training data (PSI/KS), run on a schedule; a runbook in the README (how to roll back, how to retrain).
**Should:** a load test (Locust, in `requirements-production.txt`) with latency percentiles; MLflow model registry; a demo UI.
**Could:** canary or shadow deployment design; alerting.

| Criterion (weight) | Proficient | Exemplary |
|---|---|---|
| API and code (20) | Validated, versioned endpoints; typed; tested | Clear error taxonomy; OpenAPI examples |
| Containerisation (15) | Builds reproducibly; non-root; reasonable size | Multi-stage build; image scanning |
| CI/CD (25) | Automated tests, metric gate and deploy | Environments (staging → prod); a rollback path |
| Monitoring (25) | Drift report on a schedule; logs; a health check | Alert thresholds justified; a dashboard |
| Operations docs (15) | Runbook: deploy, roll back, retrain | Cost estimate; SLOs |

---

## 8. Capstone · End-to-end AI product (after M26) · ~50 h · `ai_policy: pair` (disclosed)

**Goal:** prove job readiness with one substantial, original product the learner can talk about for 30 minutes in an interview.

**Choose one track** (or propose your own with the same depth):
1. **Predictive product:** e.g. demand forecasting for a fictional retailer (E1 skills) with an API and dashboard.
2. **LLM product:** e.g. a support-ticket triage assistant: classification + RAG + tool use + evaluation + guardrails.
3. **Vision product:** e.g. a defect detector for synthetic product images, with active-learning ideas.
4. **Data product:** e.g. a recommendation service for a fictional bookstore, with offline and online metrics.

**Phases and milestones**

| Week | Milestone | Evidence |
|---|---|---|
| 1 | Proposal (1 page): user, problem, success metrics, data, risks, scope cut-lines | Approved against the proposal checklist |
| 2 | Data pipeline + EDA + baseline | Notebook/script, data tests, baseline metric |
| 3 | Model or system iteration 1 + evaluation harness | Evaluation report with ≥ 2 variants |
| 4 | Product: API/UI, CI, deployment | A live URL, a green CI badge |
| 5 | Hardening: monitoring, safety/fairness, docs, demo video, presentation | Final repository + a 5-minute video + a 10-slide deck |

**Capstone rubric** (weights): Problem framing and impact (10) · Data and pipeline quality (15) · Modelling and evaluation rigour (20) · Engineering and deployment (20) · Responsible AI, safety and privacy (10) · Documentation and README (10) · Demo and communication (15). Proficient on every row is required; Exemplary on 3+ rows earns a distinction note on the certificate page.

**Presentation guide:** problem → users → approach → results (with honest limits) → architecture → what you'd do next. Practise answering "why this model?", "what failed?", "how would it scale?" and "what does it cost?"

## 9. Mini-projects (end of each module)

Listed in each module's curriculum entry. They're graded on the learner's machine (a pytest pack and/or a rubric), take 1–3 hours, and the best ones can be polished into extra portfolio pieces.

## 10. README template (every project)

```markdown
# <Project name>: <one-line value proposition>
![CI](<badge>) · [Live demo](<url>) · [2-min video](<url>)

## Problem
Who has it, why it matters, how success is measured.

## Results
Key numbers (with a baseline), one chart or screenshot.

## How it works
Architecture diagram + 5-8 bullet walkthrough.

## Run it
uv sync · uv run … · environment variables (.env.example)

## Tests & quality
How to run the tests; coverage; CI.

## Data
Source, licence, size, known issues.

## Limitations & next steps
Honest list.

## AI usage
What I used AI assistants for, and what I verified myself.

## About me
One line + LinkedIn/portfolio link.
```

## 11. Review protocol

1. **Self-review** with the rubric (the `.rubric` component saves it) and the submission checklist (`.checklist`: README sections, CI green, demo link, no secrets, licence).
2. **Peer review** (optional): swap repositories with a study partner and use the `spec/10` §6 code-review checklist.
3. **AI review** (optional, policy `explain`): paste into an assistant:

```text
Act as a senior engineer reviewing a junior's portfolio project for a job
application. Here is the rubric: <paste rubric>. Here is the README and the
key files: <paste>. For each rubric row, give the level you'd award, the
evidence you used, and the single most valuable improvement. Don't rewrite my
code; point to lines and explain. Finish with 3 interview questions you would
ask me about this project.
```
