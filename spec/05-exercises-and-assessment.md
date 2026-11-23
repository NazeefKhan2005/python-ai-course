# 05 · Exercises & assessment

Everything here runs on the learner's computer. Exercises are **pytest packs**; quizzes are answered in the page. Every example in §11 passed `tools/check_content.py` (solution passes, starter fails, every mutant caught, quiz answers verified by running the code).

## 1. Assessment map

| Component | Graded by | Where |
|---|---|---|
| Examples (PRIMM) | Not graded: predict, run, try-it prompts | Every teaching section |
| Code exercise (`function`, `fix`, `refactor`) | pytest file in the pack | 2–4 per lesson |
| Program exercise (`program`) | pytest runs the script with `run_program(path, stdin=...)` and checks what it prints | M01–M02, CLI lessons |
| Data / plot / SQL / model exercise | pytest: values, frames, `Axes` inspection, query rows on two databases, metric thresholds on a held-out split | P3–P5 |
| Write-the-tests (`write_tests`) | the learner's tests must pass on the real code and fail on every mutant (`check_tests`) | M04, M10, M25 |
| Warm-up / end-of-lesson quiz | In the page (mcq, multi, predict, short, order) | Every lesson |
| Module checkpoint | In-page quiz (12–20 Q) + optional checkpoint pack | `modules/mNN-…/checkpoint.html` |
| Phase exam | Timed in-page quiz + timed exam pack (no hints) | `exams/pN-exam.html` |
| Projects & capstone | Rubric (self-assessment + optional peer/AI review) and the project's own test suite | `projects/…` |
| Checklists / self-assessments | Saved checkboxes (no score) | M00, M26, project submission |

## 2. Exercise markup

An exercise is an `article.exercise` inside `section.exercises`. The page renders the starter (and, collapsed, the tests) read-only with Download buttons, the pytest command for the learner's runner, the completion-code box, the hint ladder and the gated solution. Nothing executes in the page. Example from `spec/07`:

````html
<article class="exercise" id="m03-l04-e1" data-kind="function" data-file="e1_word_freq.py">
  <h3>Exercise 1 · Word frequencies</h3>
  <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
  <div class="exercise-task">
    <p>Write <code>word_freq(text)</code> that returns a dictionary mapping each word to the number of times it appears. Treat upper and lower case as the same word, and split on any whitespace.</p>
    <script type="text/x-pycon">
    >>> from e1_word_freq import word_freq
    >>> word_freq("the cat the hat")
    {'the': 2, 'cat': 1, 'hat': 1}
    </script>
  </div>
  <script type="text/x-python" data-role="starter">
  def word_freq(text):
      """Return a dict mapping each lower-case word in text to its count."""
      counts = {}
      # your code here
      return counts


  if __name__ == "__main__":
      print(word_freq("the cat the hat"))
  </script>
  <script type="text/x-python" data-role="tests">
  from e1_word_freq import word_freq


  def test_counts_repeated_words():
      assert word_freq("the cat the hat") == {"the": 2, "cat": 1, "hat": 1}


  def test_treats_upper_and_lower_case_as_one_word():
      assert word_freq("Data data DATA") == {"data": 3}


  def test_empty_text_gives_an_empty_dict():
      assert word_freq("") == {}


  def test_returns_a_dict_instead_of_printing():
      assert isinstance(word_freq("a b"), dict), "end with: return counts"


  def test_splits_on_any_whitespace():
      assert word_freq("  spaced   out\nwords  ") == {"spaced": 1, "out": 1, "words": 1}
  </script>
  <script type="text/x-python" data-role="solution">
  def word_freq(text):
      """Return a dict mapping each lower-case word in text to its count."""
      counts = {}
      for word in text.lower().split():
          counts[word] = counts.get(word, 0) + 1
      return counts


  if __name__ == "__main__":
      print(word_freq("the cat the hat"))
  </script>
  <ol class="hints">
    <li>Loop over the words one at a time: <code>text.lower().split()</code> gives you a list of lower-case words.</li>
    <li><code>split()</code> with no arguments splits on any run of spaces, tabs or newlines.</li>
    <li>For each word: <code>counts[word] = counts.get(word, 0) + 1</code>.</li>
  </ol>
</article>
````

| Attribute / child | Meaning |
|---|---|
| `id="mNN-lNN-eN"` | Permanent id; numbered from 1 without gaps |
| `data-kind` | `function` (default), `program`, `fix` (starter contains bugs), `refactor` (behaviour + speed or style rules), `write_tests` |
| `data-file="eN_<name>.py"` | The learner's file; tests live in `test_eN_<name>.py` |
| `data-optional` | Optional stretch (★★★): not needed for mastery |
| `data-requires="pandas sklearn"` | Libraries the tests import (CI skips with `--skip-missing` only when told to) |
| `p.ex-meta` | Difficulty (★), points, AI policy ("AI help: hints only", `spec/01` §8) |
| `div.exercise-task` | The task: inputs, outputs, edge cases, constraints; an `x-pycon` example (run against the solution by the checker) |
| `script[data-role=starter]` | What the learner starts from |
| `script[data-role=tests]` | The pytest file (shown to the learner: tests are part of the spec) |
| `script[data-role=solution]` + `data-notes` | One good solution and why (complexity, trade-offs) |
| `script[data-role=target]`, `script[type=application/json][data-role=mutants]` | `write_tests` only: the correct code under test, and `{"description of the bug": "buggy source"}` |
| `script[type=text/x-file][data-name]` | A data file shipped in the pack |
| `ol.hints` | 2–3 hints, revealed one at a time |

## 3. The pack

`tools/export_exercises.py` builds `site/downloads/mNN-lNN.zip` (and `all-exercises.zip`) from the page, so the page is the single source of truth:

```text
m03-l04/
  README.md              lesson link, how to run, the exercise list
  pack.json              {"lesson", "title", "python", "exercises": [{"id", "title", "file", "tests", "optional"}]}
  conftest.py            the course pytest plugin (import path + completion codes)
  course_helpers.py      run_program, assert_fast_enough, assert_no_syntax, check_tests
  course_mocks.py        MockLLM, HashEmbedder, FakeResponse, fake_get
  e1_word_freq.py        starter          test_e1_word_freq.py      tests
  e2_invert.py           starter          test_e2_invert.py         tests
  …                      data files from x-file blocks
```

For `write_tests` the pack holds the target `eN_x.py`, the learner's `test_eN_x.py` (starter), `eN_x_mutants.json` and the checker `test_eN_x_check.py`, which calls `check_tests`. Packs never contain solutions.

**Completion codes.** After any pytest run in the pack, the plugin prints one line per exercise: `PASSED  code 5F2A-91C3` when every test in its file ran and passed (no deselection, failure, error or skip), otherwise how many tests are not passing yet. The code is FNV-1a 32-bit of `"pyai:" + exercise id`; the page computes the same and records `{status: "passed", verified: true}`. "I can't run pytest: mark as done" records `{status: "done", verified: false}`. The code is a progress record, not an anti-cheating device.

## 4. Writing tests (rules)

1. **At least 4 test functions** (parametrized cases count once). Cover the happy path, edge cases (empty, one item, duplicates, negatives, zero, case, whitespace, unicode, large input) and "doesn't change its input" where relevant.
2. **One behaviour per test**, named so the learner knows what to fix (`test_keys_are_lower_case_and_words_unchanged`). No shared mutable state between tests; use fixtures for data.
3. **Messages that teach**: pytest already shows both values; add `assert …, "end with: return counts"` only when it teaches more.
4. **Guard against hard-coding** with a second data set (another database, another split, many generated pairs). The learner can read the tests, so make them about behaviour, not about one answer.
5. **Floats, arrays and frames**: `pytest.approx`, `numpy.testing.assert_allclose`, `pandas.testing.assert_frame_equal`/`assert_series_equal`. Never `==` on floats.
6. **Speed**: `assert_fast_enough(learner_fn, reference_fn, *args, factor=10)` compares with a reference on the learner's own machine (fixed time limits fail on slow laptops). Choose inputs where the naive approach is ≥ 50× slower but still finishes in a few seconds (`spec/07` E4: 40 001 characters; the `s.count` approach fails, two linear passes pass).
7. **ML thresholds**: the tests build the held-out split themselves (seeded) and set the threshold from the reference solution's score minus a margin; check that the classic mistake (no scaling, leakage, wrong metric) fails.
8. **Plots**: call `matplotlib.use("Agg")` at the top of the test file, inspect the returned `Axes` (title, labels, `get_lines()`, patches, collections), `plt.close("all")` in a fixture. Never compare pixels.
9. **SQL**: the learner sets `QUERY`; tests build in-memory SQLite databases (fixtures), compare exact rows and column names, and run the query on a second database.
10. **Method rules** (when the method is the learning goal): `assert_no_syntax("eN_x.py", nodes=(ast.For,), calls=("sorted",))`. Use sparingly.
11. **Programs**: `run_program("eN_x.py", stdin="63\n3\n10\n")` returns everything printed; compare the meaningful line(s), not the prompts.
12. **Write-the-tests**: 3–4 mutants, each a realistic bug that one specific test would catch, described in words the learner understands ("forgets the 400-year exception"). The starter is a weak test file that passes on the target; the solution is a strong one.
13. **Starters** import cleanly, keep the signature and docstring, contain `# your code here`, `...` or `raise NotImplementedError`, and **fail at least one test** (`check_content.py` proves it). Type hints from M04-L04 on.
14. **Solutions** are idiomatic and use only what has been taught; `data-notes` explains the key idea and complexity.
15. **Budget**: one exercise's tests run in under 15 s on a laptop (most under 1 s). **Never** use the network, unseeded randomness or the current date; LLM and HTTP calls use `course_mocks`.

## 5. Helpers shipped in every pack

| Helper | Use |
|---|---|
| `run_program(path, stdin="", args=(), timeout=10)` | Run a script like a terminal does; returns its output; fails with the script's errors shown |
| `assert_fast_enough(fn, reference, *args, factor=10, repeat=3)` | Relative speed check (best of `repeat`) |
| `assert_no_syntax(path, nodes=(), calls=())` | Forbid syntax (`ast.For`) or calls (`"sorted"`, `".sort"`) |
| `check_tests(test_file, module, mutants)` | Run the learner's tests on the real module (must pass) and on each mutant (must fail) |
| `MockLLM(replies)` | `.complete(messages, **options)` returns scripted replies (a list, or a function of the messages) and records `.calls` |
| `HashEmbedder(dim=64)` | `.embed(text)` → a deterministic unit-length bag-of-words vector (lexical, not semantic: say so in lessons) |
| `FakeResponse`, `fake_get(routes)` | Canned HTTP responses with `.status_code`, `.json()`, `.text`, `.raise_for_status()` |

Plus everything pytest offers: fixtures (`tmp_path`, `monkeypatch`, `capsys`), `pytest.raises`, `pytest.warns`, `pytest.approx`, `parametrize`.

## 6. Hints, solutions and feedback

* **Hint ladder**: (1) the concept or strategy, (2) the tool or next step, (3) nearly the line. Revealed one at a time; the count is saved.
* **Solution gate**: the solution sits in a collapsed panel behind a confirmation ("You learn most from the solution after a real attempt… Show it anyway?"). Viewing it is recorded (`solutionViewed`).
* **Feedback** comes from pytest itself: the failing assertion, both values, and the test's message. Write messages in plain English that point to the rule, never "Wrong!".

## 7. Mastery, scoring and badges

| Status | Meaning | Credit |
|---|---|---|
| `passed` (verified) | Completion code recorded, solution not viewed before | 100 % |
| `passed`, solution viewed first | Completion code recorded after viewing the solution | 50 % |
| `done` (not verified) | Self-reported | 50 % |

* **Module mastered** = ≥ 80 % of the module's non-optional exercise credit **and** checkpoint ≥ 80 % (retries allowed).
* **Phase complete** = every module mastered + phase exam ≥ 70 % + project rubric ≥ "Proficient" on every row.
* **Course score** weights: exercises 30 %, checkpoints 15 %, phase exams 15 %, projects 25 %, capstone 15 %.
* **Badges** (dashboard): one per phase ("Python Foundations", "Pythonista Engineer", "Data Wrangler", "ML Practitioner", "Deep Learning & GenAI Builder", "Production-Ready"), plus "Interview Ready" (M09 exercises + timed assessment ≥ 70 %) and "Capstone Shipped".

## 8. Quiz spec (`quiz-spec` JSON)

```json
{"id": "mNN-lNN-quiz", "questions": [ … ]}
```

The section's `id` equals the spec's `id`: `mNN-lNN-quiz` (end of lesson) or `mNN-lNN-warmup` (opening retrieval questions).

| `type` | Fields | Checked by |
|---|---|---|
| `mcq` | `prompt`, `options` (HTML), `answer` (index), `explanations` (one per option) **or** `explanation` | Index equality |
| `multi` | `prompt`, `options`, `answer` (list of indexes), `explanation` | Set equality |
| `predict` | `prompt`, `code`, `answer` (exact output), `explanation` | Normalised text; **`check_content.py` runs `code` and verifies `answer`** |
| `short` | `prompt`, `accept` (case-insensitive) and/or `accept_regex` (must work in JavaScript too), `explanation` | Match |
| `order` | `prompt`, `items` (3+, **in the correct order**), `explanation` | Order (shown shuffled, keyboard-accessible ↑/↓) |

Good questions test understanding, not trivia; every distractor reflects a real misconception and every explanation teaches. 4–8 questions per lesson quiz (prefix extra/advanced questions with "Extra:" or "Advanced:"), 1–2 per warm-up; predict code ≤ 8 lines with unambiguous output.

## 9. Checkpoints and exams

* **Module checkpoint** (`modules/mNN-…/checkpoint.html`, id `mNN-checkpoint`): 12–20 quiz questions, about 70 % this module and 30 % retrieval; 2–4 predict questions; optionally a checkpoint pack (`downloads/mNN-checkpoint.zip`) with 1–2 coding tasks graded like exercises. Retries allowed; the best score counts.
* **Phase exam** (`exams/pN-exam.html`, `<section class="exam" data-exam-id="p1-exam" data-minutes="90">`, built in Stage 5): a start screen with the rules → a countdown timer (announced every 10 minutes and in the last 5) → the quiz part in the page with answers hidden until submission → the coding part as a timed exam pack (`downloads/pN-exam.zip`, no hints; its completion codes are pasted into the exam page before time runs out) → the score is saved under `progress.exams[id]` with a timestamp. One scored attempt per 24 hours; practice attempts are unlimited.
* **Timed coding assessment** (M26-L04): 3 problems from the M09 bank as a pack, 60 minutes, AI policy "none".

## 10. Rubrics and checklists (components built in Stage 5)

```html
<section class="rubric" id="p1-project-rubric">
  <script type="application/json" class="rubric-spec">
  {"id": "p1-project-rubric", "levels": ["Beginning", "Developing", "Proficient", "Exemplary"],
   "criteria": [{"name": "Functionality", "weight": 30, "descriptors": ["…", "…", "…", "…"]}]}
  </script>
</section>
```

Rendered as an accessible table with one radio group per criterion (`fieldset` + `legend`); the weighted score and a "ready to submit?" message appear; saved under `progress.rubrics[id]`. Descriptors are observable ("tests cover the happy path and 3+ edge cases"), never vague. Each project page also offers a review prompt for an AI assistant (`spec/09` §8).

Checklists: `<section class="checklist" id="m00-l03-setup-checklist">` with JSON `{"id", "items": ["Python 3.15 installed: python --version shows 3.15.x", …]}` → checkboxes saved under `progress.checklists[id]`.

## 11. Validated examples

Each is the pattern to copy for its exercise type. All passed `check_content.py`: the solution passes, the starter fails, and (write-the-tests) the reference tests catch all three mutants while the starter tests catch none.

### 11.1 Program exercise (M01): a script graded through `run_program`

````html
<section id="program-exercise">
<article class="exercise" id="m01-l03-e1" data-kind="program" data-file="e1_split_bill.py">
  <h3>Exercise 1 · Split the bill</h3>
  <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
  <div class="exercise-task">
    <p>Read three lines: the total bill, the number of people and the tip percentage. Print each person's share with two decimals, exactly like this: <code>Each person pays 23.10</code></p>
  </div>
  <script type="text/x-python" data-role="starter">
  total = float(input("Total bill: "))
  # read the number of people and the tip percentage the same way
  # work out each person's share, then print it
  </script>
  <script type="text/x-python" data-role="tests">
  import pytest
  from course_helpers import run_program

  CASES = [
      ("63\n3\n10\n", "Each person pays 23.10"),
      ("50\n1\n0\n", "Each person pays 50.00"),
      ("100\n3\n0\n", "Each person pays 33.33"),
      ("45.5\n2\n15\n", "Each person pays 26.16"),
      ("0\n4\n20\n", "Each person pays 0.00"),
  ]


  @pytest.mark.parametrize("typed, expected", CASES)
  def test_prints_each_share(typed, expected):
      printed = run_program("e1_split_bill.py", stdin=typed)
      last_line = printed.strip().splitlines()[-1]
      assert last_line.endswith(expected), f"typed {typed!r}: expected a line ending {expected!r}, got {last_line!r}"
  </script>
  <script type="text/x-python" data-role="solution">
  total = float(input("Total bill: "))
  people = int(input("People: "))
  tip = float(input("Tip %: "))
  share = total * (1 + tip / 100) / people
  print(f"Each person pays {share:.2f}")
  </script>
  <ol class="hints">
    <li>Read each line with <code>input()</code> and convert it: <code>float</code> for money and percentages, <code>int</code> for people.</li>
    <li>The total including the tip is <code>total * (1 + tip / 100)</code>.</li>
    <li>Print with two decimals: <code>print(f"Each person pays {share:.2f}")</code>.</li>
  </ol>
</article>
</section>
````

### 11.2 Data exercise (M12): pandas, fixtures, Copy-on-Write-safe

````html
<section id="data-exercise">
<article class="exercise" id="m12-l06-e1" data-kind="function" data-file="e1_revenue.py" data-requires="pandas">
  <h3>Exercise 1 · Revenue by category</h3>
  <p class="ex-meta">★★☆ · 15 points · AI help: explain only</p>
  <div class="exercise-task">
    <p>Write <code>revenue_by_category(df)</code> that returns a Series of total revenue (<code>units × unit_price</code>) per category, largest first, named <code>"revenue"</code>. Don't change <code>df</code>.</p>
  </div>
  <script type="text/x-python" data-role="starter">
  import pandas as pd


  def revenue_by_category(df: pd.DataFrame) -> pd.Series:
      """Total revenue (units x unit_price) per category, largest first."""
      ...
  </script>
  <script type="text/x-python" data-role="tests">
  import pandas as pd
  import pytest
  from pandas.testing import assert_frame_equal

  from e1_revenue import revenue_by_category


  @pytest.fixture
  def orders():
      return pd.DataFrame({
          "category": ["books", "games", "books", "music", "games", "books"],
          "units": [2, 1, 1, 3, 2, 5],
          "unit_price": [12.5, 60.0, 8.0, 9.99, 55.0, 10.0],
      })


  def test_correct_totals(orders):
      assert revenue_by_category(orders).to_dict() == pytest.approx({"games": 170.0, "books": 83.0, "music": 29.97})


  def test_largest_first(orders):
      assert list(revenue_by_category(orders).index) == ["games", "books", "music"], "finish with sort_values(ascending=False)"


  def test_named_revenue(orders):
      assert revenue_by_category(orders).name == "revenue"


  def test_leaves_the_input_unchanged(orders):
      before = orders.copy()
      revenue_by_category(orders)
      assert_frame_equal(orders, before)


  def test_zero_units_and_one_category():
      df = pd.DataFrame({"category": ["x", "x"], "units": [0, 3], "unit_price": [9.0, 1.5]})
      assert revenue_by_category(df).to_dict() == pytest.approx({"x": 4.5})
  </script>
  <script type="text/x-python" data-role="solution">
  import pandas as pd


  def revenue_by_category(df: pd.DataFrame) -> pd.Series:
      """Total revenue (units x unit_price) per category, largest first."""
      revenue = df["units"] * df["unit_price"]
      return revenue.groupby(df["category"]).sum().sort_values(ascending=False).rename("revenue")
  </script>
  <ol class="hints">
    <li>Multiply the two columns to get a revenue Series: <code>df["units"] * df["unit_price"]</code>.</li>
    <li>Group that Series by the category column and sum: <code>revenue.groupby(df["category"]).sum()</code>.</li>
    <li>Chain <code>.sort_values(ascending=False).rename("revenue")</code>.</li>
  </ol>
</article>
</section>
````

### 11.3 Model exercise (M16): the held-out split lives in the tests

````html
<section id="model-exercise">
<article class="exercise" id="m16-l02-e1" data-kind="function" data-file="e1_knn.py" data-requires="sklearn">
  <h3>Exercise 1 · A k-NN pipeline that generalises</h3>
  <p class="ex-meta">★★☆ · 15 points · AI help: explain only</p>
  <div class="exercise-task">
    <p>Write <code>make_knn(k)</code> returning an <em>unfitted</em> scikit-learn <code>Pipeline</code> that scales the features, then classifies with k-NN. The tests train it on the wine data and score it on a split you never see.</p>
  </div>
  <script type="text/x-python" data-role="starter">
  from sklearn.neighbors import KNeighborsClassifier
  from sklearn.pipeline import Pipeline


  def make_knn(k: int) -> Pipeline:
      """Scale the features, then classify with k-NN. Return it unfitted."""
      return Pipeline([("knn", KNeighborsClassifier(n_neighbors=k))])
  </script>
  <script type="text/x-python" data-role="tests">
  from sklearn.datasets import load_wine
  from sklearn.dummy import DummyClassifier
  from sklearn.model_selection import train_test_split
  from sklearn.pipeline import Pipeline
  from sklearn.preprocessing import MinMaxScaler, StandardScaler

  from e1_knn import make_knn


  def split(seed):
      X, y = load_wine(return_X_y=True)
      return train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)


  def test_returns_an_unfitted_pipeline():
      model = make_knn(5)
      assert isinstance(model, Pipeline)
      assert not hasattr(model[-1], "classes_"), "return the pipeline without calling fit"


  def test_uses_k():
      assert make_knn(7)[-1].n_neighbors == 7


  def test_scales_the_features_first():
      assert isinstance(make_knn(5)[0], (StandardScaler, MinMaxScaler)), "k-NN compares distances: put a scaler first"


  def test_beats_the_majority_baseline_by_20_points():
      Xtr, Xte, ytr, yte = split(7)
      baseline = DummyClassifier().fit(Xtr, ytr).score(Xte, yte)
      assert make_knn(5).fit(Xtr, ytr).score(Xte, yte) >= baseline + 0.20


  def test_generalises_to_a_split_you_never_saw():
      Xtr, Xte, ytr, yte = split(11)
      accuracy = make_knn(5).fit(Xtr, ytr).score(Xte, yte)
      assert accuracy >= 0.90, f"accuracy on unseen data is {accuracy:.2f}; did you scale the features?"
  </script>
  <script type="text/x-python" data-role="solution">
  from sklearn.neighbors import KNeighborsClassifier
  from sklearn.pipeline import Pipeline
  from sklearn.preprocessing import StandardScaler


  def make_knn(k: int) -> Pipeline:
      """Scale the features, then classify with k-NN. Return it unfitted."""
      return Pipeline([("scale", StandardScaler()), ("knn", KNeighborsClassifier(n_neighbors=k))])
  </script>
  <ol class="hints">
    <li>A Pipeline is a list of named steps: <code>Pipeline([("scale", ...), ("knn", ...)])</code>.</li>
    <li>Use <code>StandardScaler()</code> for the first step.</li>
    <li>Return the pipeline without calling <code>fit</code>: the tests fit it.</li>
  </ol>
</article>
</section>
````

### 11.4 SQL exercise (M15): two databases prove nothing is hard-coded

````html
<section id="sql-exercise">
<article class="exercise" id="m15-l01-e1" data-kind="function" data-file="e1_top_customers.py">
  <h3>Exercise 1 · Top customers (SQL)</h3>
  <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
  <div class="exercise-task">
    <p>Set <code>QUERY</code> to SQL that returns the 3 customers who spent the most: columns <code>customer</code> and <code>total</code> (rounded to 2 decimals), highest first.</p>
  </div>
  <script type="text/x-python" data-role="starter">
  QUERY = """
  SELECT customer
  FROM orders
  """
  </script>
  <script type="text/x-python" data-role="tests">
  import sqlite3

  import pytest

  from e1_top_customers import QUERY

  ROWS = [("Aisyah", 120.0), ("Ben", 35.5), ("Aisyah", 60.0), ("Chen", 99.9), ("Ben", 10.0), ("Dev", 250.0)]


  def database(rows):
      conn = sqlite3.connect(":memory:")
      conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, customer TEXT, amount REAL)")
      conn.executemany("INSERT INTO orders (customer, amount) VALUES (?, ?)", rows)
      return conn


  @pytest.fixture
  def conn():
      return database(ROWS)


  def test_returns_the_top_three(conn):
      assert conn.execute(QUERY).fetchall() == [("Dev", 250.0), ("Aisyah", 180.0), ("Chen", 99.9)]


  def test_column_names(conn):
      assert [d[0] for d in conn.execute(QUERY).description] == ["customer", "total"], "name the sum with AS total"


  def test_does_not_change_the_data(conn):
      conn.execute(QUERY).fetchall()
      assert conn.execute("SELECT COUNT(*) FROM orders").fetchall() == [(6,)]


  def test_works_on_other_data():
      other = database([("Eve", 5), ("Eve", 5), ("Fay", 7), ("Gus", 1), ("Hal", 2)])
      assert other.execute(QUERY).fetchall() == [("Eve", 10.0), ("Fay", 7.0), ("Hal", 2.0)]
  </script>
  <script type="text/x-python" data-role="solution">
  QUERY = """
  SELECT customer, ROUND(SUM(amount), 2) AS total
  FROM orders
  GROUP BY customer
  ORDER BY total DESC
  LIMIT 3
  """
  </script>
  <ol class="hints">
    <li>Group the rows by customer and add up the amounts: <code>GROUP BY customer</code> with <code>SUM(amount)</code>.</li>
    <li>Sort with <code>ORDER BY total DESC</code> and keep three rows with <code>LIMIT 3</code>.</li>
    <li>Round in SQL: <code>ROUND(SUM(amount), 2) AS total</code>.</li>
  </ol>
</article>
</section>
````

### 11.5 Plot exercise (M13): inspect the Axes, not pixels

````html
<section id="plot-exercise">
<article class="exercise" id="m13-l01-e1" data-kind="function" data-file="e1_monthly_chart.py" data-requires="matplotlib pandas">
  <h3>Exercise 1 · Monthly sales chart</h3>
  <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
  <div class="exercise-task">
    <p>Write <code>plot_monthly_sales(df)</code>: a line chart of <code>sales</code> by <code>month</code> titled "Monthly sales", with axis labels "Month" and "Sales (units)". Return the <code>Axes</code>.</p>
  </div>
  <script type="text/x-python" data-role="starter">
  import matplotlib.pyplot as plt


  def plot_monthly_sales(df):
      """Line chart of sales by month with a title and axis labels. Return the Axes."""
      fig, ax = plt.subplots()
      # your code here
      return ax
  </script>
  <script type="text/x-python" data-role="tests">
  import matplotlib

  matplotlib.use("Agg")  # draw off-screen: no windows pop up during the tests
  import matplotlib.axes  # noqa: E402
  import matplotlib.pyplot as plt  # noqa: E402
  import pandas as pd  # noqa: E402
  import pytest  # noqa: E402

  from e1_monthly_chart import plot_monthly_sales  # noqa: E402

  SALES = [12, 15, 14, 18, 21, 25, 24, 22, 20, 19, 23, 30]


  @pytest.fixture
  def ax():
      axes = plot_monthly_sales(pd.DataFrame({"month": range(1, 13), "sales": SALES}))
      yield axes
      plt.close("all")


  def test_returns_an_axes(ax):
      assert isinstance(ax, matplotlib.axes.Axes), "create it with fig, ax = plt.subplots() and return ax"


  def test_title_and_labels(ax):
      assert ax.get_title() == "Monthly sales"
      assert (ax.get_xlabel(), ax.get_ylabel()) == ("Month", "Sales (units)")


  def test_one_line_with_twelve_points(ax):
      assert len(ax.get_lines()) == 1
      assert len(ax.get_lines()[0].get_xdata()) == 12


  def test_plots_the_sales_column(ax):
      assert list(ax.get_lines()[0].get_ydata()) == SALES, "plot the sales column on the y-axis"
  </script>
  <script type="text/x-python" data-role="solution">
  import matplotlib.pyplot as plt


  def plot_monthly_sales(df):
      """Line chart of sales by month with a title and axis labels. Return the Axes."""
      fig, ax = plt.subplots(figsize=(7, 3.5))
      ax.plot(df["month"], df["sales"], marker="o")
      ax.set_title("Monthly sales")
      ax.set_xlabel("Month")
      ax.set_ylabel("Sales (units)")
      ax.set_xticks(range(1, 13))
      return ax
  </script>
  <ol class="hints">
    <li>Start with <code>fig, ax = plt.subplots()</code> and draw with <code>ax.plot(x, y)</code>.</li>
    <li>Use <code>ax.set_title</code>, <code>ax.set_xlabel</code> and <code>ax.set_ylabel</code>.</li>
    <li><code>ax.plot(df["month"], df["sales"], marker="o")</code> draws one line with a dot per month.</li>
  </ol>
</article>
</section>
````

### 11.6 Write-the-tests exercise (M04): mutation testing

````html
<section id="write-tests-exercise">
<article class="exercise" id="m04-l07-e1" data-kind="write_tests" data-file="e1_leap.py">
  <h3>Exercise 1 · Write tests that catch bugs</h3>
  <p class="ex-meta">★★☆ · 15 points · AI help: hints only</p>
  <div class="exercise-task">
    <p><code>e1_leap.py</code> contains a correct <code>is_leap_year(year)</code>. Write tests in <code>test_e1_leap.py</code> that pass on it and fail on each of three buggy versions we hide behind the scenes.</p>
  </div>
  <script type="text/x-python" data-role="target">
  def is_leap_year(year: int) -> bool:
      """Gregorian rule: every 4th year, except centuries, except every 400th year."""
      return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
  </script>
  <script type="text/x-python" data-role="starter">
  from e1_leap import is_leap_year


  def test_a_typical_leap_year():
      ...  # replace with an assert
  </script>
  <script type="text/x-python" data-role="solution">
  import pytest

  from e1_leap import is_leap_year


  @pytest.mark.parametrize("year, expected", [
      (2024, True),    # divisible by 4
      (2023, False),   # not divisible by 4
      (1900, False),   # century: not a leap year
      (2000, True),    # every 400th year is
  ])
  def test_gregorian_rule(year, expected):
      assert is_leap_year(year) is expected
  </script>
  <script type="application/json" data-role="mutants">
  {"treats every 4th year as a leap year (forgets centuries)": "def is_leap_year(year):\n    return year % 4 == 0\n",
   "forgets the 400-year exception": "def is_leap_year(year):\n    return year % 4 == 0 and year % 100 != 0\n",
   "says every year is a leap year": "def is_leap_year(year):\n    return True\n"}
  </script>
  <ol class="hints">
    <li>Each bug is wrong for one kind of year. Which years does each rule of the definition talk about?</li>
    <li>You need at least: an ordinary leap year, an ordinary non-leap year, a century, and a 400th year.</li>
    <li>Try 2024, 2023, 1900 and 2000.</li>
  </ol>
</article>
</section>
````

### 11.7 A quiz with every question type

````html
<section class="quiz" id="spec05-quiz">
  <h2>A quiz with every question type</h2>
  <script type="application/json" class="quiz-spec">
  {"id": "spec05-quiz", "questions": [
    {"type": "mcq", "prompt": "Which call reads a whole text file as one string?",
     "options": ["<code>Path('a.txt').read_text()</code>", "<code>Path('a.txt').read()</code>", "<code>open('a.txt').readlines()</code>"],
     "answer": 0, "explanations": ["Right.", "<code>Path</code> has no <code>read()</code> method.", "<code>readlines()</code> returns a list of lines."]},
    {"type": "multi", "prompt": "Which of these are immutable?", "options": ["<code>tuple</code>", "<code>list</code>", "<code>str</code>", "<code>dict</code>"],
     "answer": [0, 2], "explanation": "Tuples and strings can't be changed in place; lists and dicts can."},
    {"type": "predict", "prompt": "What does this print?", "code": "nums = [3, 1, 2]\nnums.sort()\nprint(nums[-1], len(nums))",
     "answer": "3 3", "explanation": "<code>sort()</code> sorts in place; the last item is now the largest."},
    {"type": "short", "prompt": "Which built-in returns the number of items in a list?", "accept": ["len", "len()"],
     "accept_regex": "^len(\\(\\))?$", "explanation": "<code>len(items)</code>."},
    {"type": "order", "prompt": "Put the debugging loop in order.", "items": ["Reproduce the bug", "Isolate where it happens", "Form a hypothesis", "Test the fix"],
     "explanation": "Reproduce, isolate, hypothesise, test."}
  ]}
  </script>
</section>
````
