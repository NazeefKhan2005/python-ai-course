# 10 · Career readiness

Content source for **M26 Career Launchpad**, the **interview corner** in every lesson, the **mock-interview simulator** and the `site/career/` pages. Facts about salaries, companies and hiring markets change and differ by country, so lessons teach learners **how to research their own market** and never state numbers as universal.

## 1. Role profiles and skills matrix

| Role | Day to day | Core tools | Must-have evidence |
|---|---|---|---|
| **Data Analyst** | Answer business questions, dashboards, A/B readouts | SQL, pandas, visualisation/BI, statistics, Excel | P3 report; SQL fluency (windows, CTEs); clear charts |
| **Data Scientist** | Experiments, predictive models, insight → decision | Python, statistics, scikit-learn, SQL, communication | P3 + P4; A/B test reasoning; a model card |
| **ML Engineer** | Productionise models: pipelines, serving, monitoring | Python, scikit-learn/PyTorch, Docker, CI/CD, cloud, MLOps | P4 + P6; clean, tested code; system design |
| **AI / LLM Engineer** | Build LLM features: RAG, tools, evals, guardrails | Python, LLM APIs, vector search, evaluation, FastAPI | P5 (RAG) + P6; an eval harness; safety awareness |
| **MLOps / Platform** | Tooling for training, deployment, observability | CI/CD, containers, orchestration, monitoring | P6; infrastructure-as-code basics |
| **Research Engineer / Scientist** | Novel methods, papers, large-scale training | Deep learning, maths, PyTorch, experimentation | Usually needs a postgraduate degree and publications; the course is a foundation |

Entry routes for students: internships, graduate programmes, research assistantships, open-source contributions, Kaggle/competitions, freelance analytics for student societies and NGOs.

## 2. Reading a job description

Split it into **must-have** vs **nice-to-have**; map each line to evidence you have (a project, a course module, an exercise); apply when you meet about 60–70% of the must-haves; tailor the CV's top third to the role's top three requirements; note keywords for ATS (applicant tracking systems) honestly. Never claim skills you can't discuss in depth.

## 3. Portfolio and GitHub

* **Pin 4–6 repositories:** P3, P4, P5, P6, the capstone, and `textkit`. Each has the `spec/09` §10 README, a demo and results.
* **Profile README:** a 2-line pitch, target role, 3 flagship projects with one-line results, and contact.
* **Quality signals recruiters notice in 30 seconds:** a clear README top section, a live demo or video, green CI badges, tests, sensible commit history, no secrets, no notebooks full of errors.
* **Write about your work:** one short article per flagship project (problem, approach, result, what you learned). Writing is a differentiator.

## 4. CV and LinkedIn

* **Format:** one page for students; a single column; a standard font; no photos, graphs or skill bars (ATS can't read them); PDF export; file name `Firstname-Lastname-CV.pdf`.
* **Sections:** contact + links · summary (2 lines, tailored) · skills (grouped: languages, ML/DS, tools) · projects (3–4, each 2–3 bullets) · experience · education (with relevant modules) · achievements.
* **Bullet formula:** *action verb + what you built/did + how + measurable result.*
  * Weak: "Worked on a churn model using Python."
  * Strong: "Built a leak-proof churn pipeline (scikit-learn, LightGBM) that identifies 61% of churners in the top 10% riskiest customers (vs 23% baseline); shipped as a Dockerised FastAPI service with CI and drift monitoring."
  * Weak: "Made a chatbot." → Strong: "Built a RAG assistant over 120 policy documents with hybrid retrieval and citations; raised recall@5 from 0.64 to 0.86 through chunking and reranking ablations; evaluated with a 40-question test set and 12 prompt-injection cases."
* **LinkedIn:** headline = target role + core stack ("Aspiring ML Engineer | Python · scikit-learn · PyTorch · FastAPI"); an "About" section in 3 short paragraphs; Featured = demos; ask for recommendations from project partners or lecturers.

## 5. Job-search plan (12 weeks) and networking

| Weeks | Focus |
|---|---|
| 1–2 | Target roles and companies list (30+), CV v1, GitHub clean-up, LinkedIn |
| 3–4 | 5 tailored applications a week; 2 informational chats a week; daily DSA (30 min) |
| 5–8 | Applications continue; mock interviews weekly (coding, ML, behavioural); polish the capstone |
| 9–12 | Interview loops; follow-ups; reflect and iterate on CV/targeting from response rates |

Track applications in a simple tracker (the career page offers a downloadable CSV template: company, role, link, date, status, contact, next step).
**Networking message template (adapt, keep it short):** "Hi <name>, I'm a CS (AI) student building ML projects (recently: <one-line project + result>). I noticed you work on <team/topic> at <company>. Could I ask you two quick questions about how your team <does X>? A 15-minute chat or a reply here would help a lot. Thank you!"

## 6. Code-review checklist (projects and peer review)

Correctness and edge cases · tests exist and fail when the code breaks · names explain intent · functions do one thing · no duplicated logic · errors handled with useful messages · no secrets/PII · dependencies pinned/locked · README explains run/test/deploy · performance hot spots measured · data leakage impossible by construction (pipelines) · reproducible (seeds, configs) · accessible UI (if any) · AI-usage disclosure.

## 7. The coding-interview method

**Clarify** (inputs, outputs, constraints, edge cases) → **examples** (including tricky ones) → **approach** (brute force first, then improve; say the complexity) → **code** (clean, talk while writing) → **test** (walk through the examples and edge cases; fix calmly) → **analyse** (time/space; trade-offs). Practise thinking aloud; silence reads as being stuck.

## 8. Question banks

Format: **question**, then *what a strong answer covers*. Lessons draw their interview corners from these. Checkpoints and the M26 quizzes randomise from them.

### 8.1 Python
1. **Mutable vs immutable types; why it matters.** Lists/dicts/sets vs int/str/tuple; aliasing; dict keys must be hashable; default-argument bug.
2. **`is` vs `==`.** Identity vs equality; small-int/str interning is an implementation detail; use `is` for `None`.
3. **How does a dict work?** Hash table, probing, average O(1), insertion order since 3.7, the `__hash__`/`__eq__` contract.
4. **List vs tuple vs set vs dict, by operation cost.** Membership O(n) vs O(1); tuples immutable and hashable; when to use each.
5. **Generators vs lists.** Lazy evaluation, memory, single pass, `yield`, pipelines, `itertools`.
6. **What is a decorator? Write one.** A higher-order function, `functools.wraps`, decorators with arguments, real uses.
7. **Context managers.** `__enter__/__exit__`, exception handling, `contextlib.contextmanager`, resource safety.
8. **`*args` / `**kwargs`, keyword-only and positional-only parameters.** Syntax, use cases, API design.
9. **The GIL; threads vs processes vs asyncio.** CPU- vs I/O-bound; free-threaded builds (3.13+, supported since 3.14); when each fits.
10. **Shallow vs deep copy.** Nested objects; `copy.deepcopy`; pandas/NumPy views.
11. **How are exceptions best used?** Specific excepts; EAFP; custom exceptions; never a bare `except`; chaining.
12. **Dataclasses vs NamedTuple vs dict vs pydantic.** Mutability, validation, typing, performance.
13. **What happens when you `import` a module?** `sys.modules` cache, search path, executing module code once, circular imports.
14. **Type hints: are they enforced?** No (except by tools such as pydantic); mypy/pyright; why teams use them.
15. **`__slots__`, memory, and when it helps.** Many small objects; trade-offs.
16. **Explain list comprehensions vs `map`/`filter`.** Readability, speed, laziness of generator expressions.
17. **How would you speed up slow Python code?** Measure (cProfile) → algorithm → data structures → vectorise → cache → compiled extensions.
18. **What's new in recent Python versions that you use?** Pattern matching, `X | Y` types, generics syntax, t-strings (3.14), free-threading, lazy imports (3.15): mention one you've really used.

### 8.2 DSA pattern map (M09)

| Pattern | Signals in the problem | Template problems |
|---|---|---|
| Hash map / set | "seen before", counts, pairs summing to k, grouping | two-sum, group anagrams, longest consecutive, subarray sum = k |
| Two pointers | sorted input, pairs, palindromes, in-place | two-sum sorted, remove duplicates, container with most water |
| Sliding window | contiguous subarray/substring with a constraint | longest unique substring, max window sum, min window |
| Prefix sums | many range-sum queries, subarray sums | range sums, subarray sum = k |
| Stack / monotonic stack | brackets, "next greater", undo | valid parentheses, daily temperatures, RPN |
| Heap | top-k, k-way merge, scheduling, running median | top-k frequent, merge k lists, median stream |
| BFS / DFS | grids, graphs, shortest unweighted path, components | islands, word ladder, clone graph |
| Topological sort | prerequisites, ordering with dependencies | course schedule |
| Binary search | sorted data, "minimum feasible value" | search insert, rotated array, capacity to ship |
| Backtracking | all combinations/permutations, constraints | subsets, permutations, combination sum, N-queens |
| Dynamic programming | optimal value with overlapping subproblems | coin change, LIS, edit distance, knapsack |
| Union-find | dynamic connectivity, grouping | number of provinces, redundant connection |

### 8.3 SQL
1. Top N per group (window `ROW_NUMBER`/`DENSE_RANK` + filter in a CTE). 2. Second-highest value (`DENSE_RANK` or `OFFSET`; handle ties and NULL). 3. Running totals and moving averages (window frames). 4. Month-over-month growth (`LAG`). 5. `INNER` vs `LEFT` join and the NULLs it creates; anti-join to find missing rows. 6. `WHERE` vs `HAVING`. 7. Duplicates: find and delete safely. 8. Retention/cohort query (first-order month, activity month). 9. Indexes: what they speed up, what they cost. 10. SQL injection and parameterised queries.

### 8.4 Statistics and probability
1. **Explain a p-value to a non-statistician.** The probability of data this extreme if the null hypothesis is true; not the probability that the null is true; significance vs size.
2. **Design an A/B test.** Hypothesis, metric (+ guardrails), randomisation unit, sample size and power, duration, peeking, novelty effects.
3. **Base-rate (Bayes) puzzle.** Work through prior × likelihood; false positives dominate when prevalence is low.
4. **Central limit theorem and why it matters.** Sampling distributions, CIs, the assumptions.
5. **Confidence interval meaning.** The procedure's coverage, not a probability about this one interval.
6. **Correlation vs causation; confounders.** Examples; experiments; causal diagrams (high level).
7. **Type I vs Type II errors; precision/recall analogy.** Trade-offs, costs.
8. **Bootstrap.** Resampling with replacement; when it helps.
9. **Multiple comparisons.** Inflated false positives; corrections (Bonferroni, FDR).
10. **Simpson's paradox.** Aggregation reverses trends; stratify.

### 8.5 Machine learning
1. **The bias–variance trade-off.** Under/over-fitting, complexity, regularisation, more data, learning curves.
2. **Precision vs recall; when to prefer each.** Costs of FP/FN with examples; thresholds; PR-AUC for imbalance.
3. **ROC-AUC vs PR-AUC.** Imbalance sensitivity; what each measures.
4. **Data leakage: give three examples.** Target leakage, preprocessing before the split, temporal leakage; prevention with pipelines and time splits.
5. **Why cross-validate? Which scheme when?** k-fold, stratified, group, time series; nested CV for tuning.
6. **L1 vs L2 regularisation.** Sparsity vs shrinkage; geometry; when to use each.
7. **How does a decision tree split? Why do forests help?** Impurity decrease; bagging + feature randomness reduce variance.
8. **Gradient boosting vs random forest.** Sequential residual fitting vs parallel averaging; tuning; overfitting behaviour.
9. **Handling class imbalance.** Metrics, class weights, resampling, thresholds, calibration.
10. **Feature scaling: which models need it?** Distance- and gradient-based models do; tree-based models don't.
11. **How does k-means work; its limits?** Lloyd's algorithm, k-means++, spherical clusters, choosing k.
12. **PCA: what and when?** Variance directions, compression, visualisation, not feature importance.
13. **How do you know a model is good enough to ship?** Baseline, business metric, CIs, slices, fairness, latency/cost, monitoring plan.
14. **Your model is great offline but bad in production: why?** Training–serving skew, drift, leakage, feedback loops, label delay.
15. **Explain a model's prediction to a customer.** Local explanations, caveats, actionable reasons.
16. **Fairness metrics and trade-offs.** Demographic parity vs equal opportunity; context; documentation.

### 8.6 Deep learning
1. **Explain backpropagation.** Chain rule on the computational graph; gradients flowing backwards; caching activations.
2. **Vanishing/exploding gradients and the fixes.** ReLU, initialisation, normalisation, residuals, clipping.
3. **Batch norm vs layer norm.** Over the batch vs over the features; why transformers use layer norm.
4. **Dropout: train vs inference.** Inverted dropout, scaling, regularisation effect.
5. **CNN intuition.** Local receptive fields, weight sharing, translation equivariance, pooling.
6. **Transfer learning strategy.** Freeze vs fine-tune, learning rates, data size, domain shift.
7. **Adam vs SGD.** Adaptive moments; generalisation folklore; schedules; weight decay (AdamW).
8. **Training loss is NaN: what do you check?** Learning rate, data (NaN/inf), loss stability (log of 0), mixed precision, gradient clipping.
9. **Overfitting in deep nets.** Augmentation, regularisation, early stopping, more data, smaller model.
10. **GPU out-of-memory: fixes.** Batch size, mixed precision, gradient accumulation, checkpointing, freeing tensors.

### 8.7 LLMs and generative AI
1. **Explain attention / transformers.** Q, K, V; scaled dot product; multi-head; positional information; why it parallelises.
2. **Tokenisation's impact.** Cost, context limits, multilingual fairness, rare words.
3. **Temperature, top-k, top-p.** Sampling vs determinism; task-dependent settings.
4. **Prompting vs RAG vs fine-tuning: how to choose.** Knowledge freshness, behaviour vs knowledge, cost, data, evaluation.
5. **Design a RAG system.** Chunking, embeddings, hybrid search, reranking, citations, "I don't know", evaluation, refresh.
6. **How do you evaluate an LLM feature?** Test sets, task metrics, retrieval metrics, human review, LLM-as-judge with calibration, regression suites.
7. **Prompt injection: what and how to mitigate.** Direct/indirect; least privilege for tools; separating instructions from data; output filtering; human confirmation; monitoring. No silver bullet.
8. **Hallucinations: causes and mitigations.** Retrieval grounding, citations, constrained outputs, abstention, verification.
9. **Structured outputs and tool use.** Schemas, validation, retries, idempotent tools, step budgets.
10. **When not to build an agent.** Deterministic workflows, cost, reliability, latency, auditability.
11. **Cost and latency optimisation.** Caching, smaller models, batching, prompt trimming, streaming.
12. **Privacy and security for LLM apps.** PII handling, data retention, secrets, access control.

### 8.8 ML system design scenarios (use the M26-L06 framework)
1. Recommendations for an online bookstore (candidate generation + ranking; cold start; metrics; feedback loops).
2. Real-time card-fraud detection (latency, imbalance, features with time windows, human review, drift).
3. Search ranking for a recipe site (retrieval + learning-to-rank; offline/online metrics).
4. A support-ticket triage assistant (classification + RAG + escalation; evaluation; safety).
5. ETA prediction for food delivery (features, data freshness, monitoring, fairness across regions).
6. Demand forecasting for a grocery chain (hierarchies, seasonality, backtesting, retraining cadence).

**Answer skeleton:** clarify goals and constraints → define success metrics (offline + online + guardrails) → data sources and labels → features → model choices (baseline first) → evaluation → serving architecture (batch vs real time, latency budget) → monitoring and retraining → risks (privacy, fairness, abuse) → iteration plan.

### 8.9 Behavioural (STAR: Situation, Task, Action, Result)
1. Tell me about a project you're proud of. 2. A bug that took you long to find. 3. A time you disagreed with a teammate. 4. When you had to learn something fast. 5. A failure and what changed after it. 6. Juggling deadlines. 7. Explaining something technical to a non-technical person. 8. Receiving tough feedback. 9. Taking initiative without being asked. 10. Why this role/company?
Build a **story bank** of 6–8 STAR stories from course projects and life; each story should flex to several questions. Quantify results; say "I", not only "we"; end with what you learned.

## 9. Take-home assignment playbook

Read the brief twice and list the assumptions · time-box (and say so) · start with a baseline end to end, then improve · tests for the core logic · README first: how to run, decisions, trade-offs, what you'd do with more time · clean commit history · no over-engineering · verify that it runs from a fresh clone · if you used AI tools and it's allowed, say how.

## 10. Questions to ask; offers and negotiation basics

**Ask:** what success looks like in 6 months; how the team ships models (review, CI, monitoring); mentoring; the biggest current challenge; how they measure model impact.
**Offers:** get it in writing; compare total compensation, learning and mentorship; research typical pay **for your country and level** from reliable local sources; negotiate politely with evidence; never accept on the spot under pressure.

## 11. Mock-interview simulator (component spec, built in Stage 5)

`site/career/mock-interview.html`: choose a category (Python, DSA, SQL, statistics, ML, DL, LLM, system design, behavioural) and a length (15/30/45 minutes) → it draws random questions from these banks (JSON in the page) → a timer per question → the learner answers aloud or in a text box → "Reveal key points" shows the coverage list → the learner self-scores 0–3 per key point → it's saved under `progress.quizzes["mock-<date>"]`, and a weak-topics summary links to the relevant lessons. Coding questions (Python, DSA, SQL) come with a timed exercise pack in `site/downloads/` that the learner runs locally with pytest; the completion code it prints is recorded like any exercise. Optional: a "practise with an AI interviewer" prompt to copy:

```text
You are interviewing me for a junior <role> position. Ask one question at a
time from <category>. Wait for my answer, then give feedback: what was strong,
what was missing, and a model answer in under 120 words. Increase difficulty
gradually. Do not answer for me.
```

## 12. Keep growing (M26-L08)

A 12-week post-course plan: pick a specialisation elective → one paper a fortnight (with a 1-page summary) → one Kaggle competition or open-source contribution → one public write-up a month → mentor a newer learner (teaching consolidates mastery). Avoid tutorial hell: every new topic ends in something built and published.
