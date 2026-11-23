# 01 · Course blueprint

## 1. Identity

| | |
|---|---|
| **Title** | Python for AI: Zero to Job-Ready |
| **Tagline** | Write real Python from lesson one. Finish with deployed AI projects and interview confidence. |
| **Promise** | By the end, the learner can design, build, test, deploy and explain data and AI systems in Python, and has a public portfolio that proves it. |
| **Format** | Self-paced course website (static, works offline) that doubles as a reference. Learners run every example and exercise **on their own computer**: verified code with its real output, pytest-graded exercise packs, in-page quizzes, notebooks for exploration and local projects for engineering skills |
| **Size** | Orientation + 6 phases · 28 modules · 199 lessons · 6 portfolio projects · capstone · about 430 hours |
| **Prerequisites** | None for Python. School-level algebra. University calculus, linear algebra and probability help but are re-taught in code (M14) |

## 2. Learner persona

**Primary persona: a CS (AI) undergraduate, Year 1–3.** They are studying for a computer-science degree with an AI specialisation and want an internship or graduate role in AI, ML or data. Python is expected in their courses but often taught thinly.

| Entry profile | Description | Path |
|---|---|---|
| A · New to programming | Has never written code, or only school-level Scratch/HTML | Full track from M00 |
| B · Knows another language | Did C, C++ or Java in Year 1 and knows loops and arrays, but not Python idioms | Placement quiz → usually starts at M03, skims M01–M02 |
| C · Knows basic Python | Has done a Python course or notebooks; weak on engineering, DSA and ML depth | Placement → starts at M07 or M11; must still pass the Phase 1–2 checkpoints |

**Constraints:** a laptop with 8 GB RAM and no GPU; sometimes a phone; 8–15 hours a week alongside coursework; unreliable or metered internet at times; English may be a second language.

**Motivations:** get an internship, build a portfolio, understand the AI tools everyone talks about, pass technical interviews.

**Fears:** "I'm not a math person", "everyone else already knows this", "tutorial hell: I can follow along but can't build alone". The course answers these with small wins, the math taught through code, and many independent "Make" tasks.

## 3. Program outcomes

By the end of the course the learner can:

| # | Outcome | Evidence |
|---|---|---|
| PO1 | Write clean, idiomatic, tested Python (functions, OOP, iterators, typing) | M01–M08 exercises, P1–P2 projects |
| PO2 | Solve algorithmic problems with appropriate data structures and explain their complexity | M09 practice set, timed assessment |
| PO3 | Work like a professional engineer: Git, environments, packaging, testing, linting, CI, code review | M10, P2 package with CI |
| PO4 | Acquire, clean, analyse and visualise data with SQL, NumPy, pandas and Matplotlib/Seaborn, and communicate insights | M11–M15, P3 analytics report |
| PO5 | Apply probability, statistics, linear algebra and calculus in code to reason about models | M14 exercises |
| PO6 | Build, tune, evaluate and explain classical ML models with scikit-learn, avoiding leakage and bias | M16–M19, P4 model + model card |
| PO7 | Implement neural networks from scratch and train deep models with PyTorch | M20–M21 |
| PO8 | Build LLM applications (prompting, structured output, tools, RAG, evaluation, safety) | M22–M23, P5 RAG assistant |
| PO9 | Ship models as tested, containerised, monitored services with CI/CD | M24–M25, P6 deployed service |
| PO10 | Present themselves for jobs: portfolio, resume, interviews (coding, ML, system design, behavioural) | M26, capstone, mock interviews |

## 4. Competency framework

Each competency has three levels. Modules move learners up a level; projects provide the evidence.

| Competency | Foundation | Practitioner | Job-ready |
|---|---|---|---|
| Python programming | Writes correct scripts with functions and core data structures | Uses OOP, iterators, decorators and typing idiomatically | Writes clean, tested, typed, documented modules others can use |
| Problem solving & DSA | Traces and debugs code | Applies hashing, two pointers, recursion and BFS/DFS | Solves medium interview problems in about 30 minutes and explains Big-O |
| Software engineering | Uses Git and a virtual environment | Writes pytest suites, uses ruff and mypy, makes PRs | Ships a package with CI, reviews code, structures projects |
| Data wrangling & analysis | Loads and filters data | Cleans, joins, groups and reshapes; writes SQL with joins | Builds reproducible analyses and SQL with windows/CTEs |
| Visualisation & communication | Makes basic charts | Picks the right chart; runs an EDA | Tells a data story to non-technical people |
| Math & stats for ML | Computes summary statistics | Uses gradients, probability and tests in code | Explains models' maths in interviews; designs A/B tests |
| Machine learning | Trains a model with scikit-learn | Builds leak-proof pipelines; tunes and evaluates properly | Chooses, explains and audits models; writes model cards |
| Deep learning & GenAI | Explains neurons and backprop | Trains CNNs/RNNs in PyTorch; implements attention | Builds evaluated RAG/agent apps; fine-tunes with Hugging Face |
| MLOps & deployment | Saves and loads models | Serves models with FastAPI and Docker | Adds CI/CD, tracking and drift monitoring |
| Professional skills | Writes READMEs | Uses AI assistants responsibly; collaborates in Git | Interviews well; has a portfolio of deployed projects |

## 5. Structure at a glance

| Phase | Modules | Lessons | Hours* | Phase outcome | Portfolio project |
|---|---|---|---|---|---|
| P0 Orientation | M00 | 5 | 6 | Set up, learn how to learn, Git basics | Portfolio repository created |
| P1 Python Foundations | M01–M06 | 40 | 50.5 | Write correct, readable Python programs | P1 · CLI Expense Tracker |
| P2 Intermediate Python & Engineering | M07–M10 | 34 | 54.5 | Write professional Python; pass coding interviews | P2 · `textkit` package with CI |
| P3 Data Science Stack | M11–M15 | 38 | 61 | Analyse real data end to end | P3 · Analytics report |
| P4 Machine Learning | M16–M19 | 29 | 47 | Build and audit ML models | P4 · Churn model + model card |
| P5 Deep Learning & GenAI | M20–M23 | 28 | 53 | Build neural nets and LLM apps | P5 · RAG assistant or image classifier |
| P6 Production & Career | M24–M27 | 25 | 40 | Ship ML services; get hired | P6 · Deployed, monitored ML service |
| Capstone | | | ~50 | End-to-end AI product | Capstone |

\*Whole lesson pages and exercises. The essentials-only path through the lessons takes about 60 % of this. Portfolio projects add about 70 hours, so the total is about **430 hours**.

## 6. Learning paths

* **Full track (profile A):** everything in order. About 34 weeks at 12 h/week, or two university semesters.
* **Fast track (profiles B/C):** the M00 placement quiz recommends a start module. Skipped modules are unlocked by passing their checkpoint quiz (≥ 80%). Saves 30–60 hours.
* **Intensive (holiday) plan:** 20 hours a week for 20 weeks.
* **Role tracks.** After Phase 3 the learner may choose an emphasis. All tracks finish M26 and the capstone.

| Track | Must-do depth | Lighter touch | Suggested electives |
|---|---|---|---|
| Data Analyst | M12, M13, M15, M14 L03–L05, M19 L03 | M20–M21, M24–M25 | E1 Time series, E7 Geospatial |
| Data Scientist | M14, M16–M19, M13 | M21, M25 | E1, E6 Recommenders |
| ML Engineer | M10, M17–M18, M21, M24–M25 | M15 L05 | E4 Big data, E2 Vision |
| AI / LLM Engineer | M20, M22, M23, M24, M25 | M13 L05, M18 L08 | E3 RL basics |

## 7. Pedagogy (what every lesson does and why)

1. **PRIMM for code.** For each worked example the learner **P**redicts the output (examples can hide it until revealed), **R**uns it on their own computer, **I**nvestigates with guided questions, **M**odifies it, then **M**akes something new (the graded exercise). This builds code-reading before code-writing and beats copy-paste learning.
2. **Worked → faded → independent.** A fully worked example first, then a partly completed one (the starter file in the exercise pack), then an independent exercise. This manages cognitive load for beginners.
3. **Retrieval and spacing.** Each lesson from M02 onwards opens with a 1–2 question warm-up on earlier lessons. Checkpoint quizzes mix in questions from older modules.
4. **Mastery, not seat time.** A module is "mastered" at ≥ 80% of required exercises and ≥ 80% on its checkpoint. Learners can always retry.
5. **Productive struggle with a hint ladder.** Hint 1 is conceptual, hint 2 strategic, hint 3 nearly the answer. The solution is behind a confirmation ("you learn most after a real attempt") and viewing it is recorded.
6. **Immediate, kind, specific feedback.** pytest shows what was expected and what happened; assertion messages explain the rule in plain English. Edge-case tests reward careful thinking, and a completion code printed by pytest records the pass on the lesson page.
7. **Authentic tasks.** Datasets and briefs look like real work (orders, churn, logs, support tickets). Every module ends in something portfolio-shaped.
8. **Metacognition.** Recaps, "explain it like an interview" questions, and a short reflection prompt per module ("what confused you; what would you tell a friend").
9. **Interleaving.** Projects and DSA practice mix earlier skills on purpose.
10. **Complete, layered content.** Every lesson teaches its topic completely but marks each part **Essential**, **Extra info** or **Advanced**, so a beginner can take the essential path and come back later; the reference tables make each lesson a lasting reference (`spec/06` §3–4).
11. **Inclusive by default.** Short sentences, jargon defined on first use, a glossary, diverse names and contexts, small downloads, and no reliance on colour alone.

## 8. AI-assistant policy for learners

Learners will use AI assistants at work, so the course teaches responsible use instead of pretending they don't exist. Every exercise shows its policy in its `p.ex-meta` line ("AI help: hints only"; the policy names below are used in the curriculum and project files as `ai_policy`).

| Policy | Meaning | Default where |
|---|---|---|
| `none` | Practise like an interview: no AI, no searching for solutions | Interview challenges, timed exams |
| `hints-only` | You may ask an AI to explain an error or a concept, but not for code that solves the task | P1–P2 exercises |
| `explain` | You may ask an AI to explain and review your code; write the code yourself | P3–P4 exercises |
| `pair` | AI pair-programming allowed. Disclose it in an "AI usage" section of the README and be able to explain every line | Portfolio projects P3+ and the capstone |

M00-L05 teaches good "tutor prompts" (for example "Don't give me the answer; ask me a question that helps me find the bug") and why over-reliance hurts in interviews.

## 9. The job-readiness thread

Every module includes these, so career preparation isn't left until the end:

* **"On the job" callout:** where this skill appears in real roles and tools.
* **Interview corner:** 1–3 typical questions with model answers (`spec/10` has the banks).
* **Portfolio artifact:** each phase ends in a GitHub-ready project with a README, tests and a demo (`spec/09`).
* **Professional habits from day one:** Git commits for every project, a README for everything, code review checklists from Phase 2.
* **Career milestones:** P1 the GitHub profile is set up; P2 the first CV draft; P3 the first data portfolio piece is public; P4 a Kaggle-style notebook; P5 an AI demo deployed; P6 a mock interview loop, applications plan and capstone presentation.

## 10. Assessment overview (details in `spec/05`)

| Layer | What | Weight in course score |
|---|---|---|
| Formative | Running the examples, warm-ups, end-of-lesson quizzes | 0% (practice) |
| Exercises | Code exercises graded by pytest on the learner's machine (completion codes) | 30% |
| Module checkpoints | 12–20 mixed questions per module | 15% |
| Phase exams | Timed, no hints, mixed questions and coding | 15% |
| Portfolio projects | Rubric-scored (self-assessment + optional peer/AI review) | 25% |
| Capstone | Rubric-scored, with a demo video and write-up | 15% |

**Completion** requires every module mastered, all six portfolio projects at least "Proficient" on every rubric row, and the capstone submitted. The certificate page is self-issued and printable, and clearly says it is not an accredited qualification.

## 11. Accessibility and inclusion

* WCAG 2.2 AA (see `spec/08`); keyboard-only use is fully supported, including quizzes, search and the Show filter.
* Readable on a phone: lessons work at 360 px wide. Coding is best on a laptop, and the course says so politely.
* Low bandwidth: Python downloads once (about 10 MB core, plus packages on first use) and is cached. Lessons say up front when a big package (scikit-learn, about 30 MB) will load.
* Plain English (CEFR B2), with idioms avoided and terms defined on first use and in the glossary.
* Examples use diverse names and global contexts and avoid stereotypes. Currency and units are generic or labelled.

## 12. How we know the course works

Watch these (locally, or with opt-in feedback if the owner adds it): exercise first-try pass rates (aim for 40–70%; outside that range the exercise is too easy or too hard), hint usage, the most-failed tests (often a bad test or an unclear prompt), time per lesson against the estimate, module drop-off, and learner reflections. Review every module after the first cohort.
