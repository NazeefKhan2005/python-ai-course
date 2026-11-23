# Phase 3 · Data Science Stack

**Goal:** acquire, clean, analyse, visualise and reason statistically about real data, end to end, with NumPy, pandas, Matplotlib/Seaborn, SciPy and SQL.
**Modules:** M11–M15 · 38 lessons · ~61 h · **Portfolio project P3:** end-to-end analytics report (`spec/09`) · **Phase exam `p3-exam`:** 25 questions + 3 data tasks (pandas, SQL, statistics), 100 minutes.

**Phase teaching notes**
* **Data files** come from `tools/make_datasets.py` (synthetic, seeded) in `site/data/`; see `spec/03` §9. Examples embed small files with `<script type="text/x-file" data-name="sales.csv">` or link a download from `site/data/`; exercise packs include the files their tests read, so code says `pd.read_csv("sales.csv")` relative to the pack folder.
* **First-use downloads:** Exact outputs depend on library versions: lessons are verified with `site/downloads/requirements-core.txt`, and the first lesson of each library module tells the learner to install it.
* **pandas 3 rules (the course is verified with pandas 3.1):** Copy-on-Write is the only mode, so chained assignment (`df[df.x > 0]["y"] = 1`) never updates `df`; teach `df.loc[mask, "y"] = 1`. Strings default to the `str` dtype. Never teach `inplace=True`, `DataFrame.append` or `applymap` (use `concat` and `DataFrame.map`). Check every pandas API against the 3.x docs.
* **Grading data work:** compare DataFrames with `pandas.testing.assert_frame_equal(actual, expected)` (add `check_dtype=False` only when dtypes may legitimately differ) or check specific values; check plots through the `Axes` the function returns (titles, labels, number of artists; `spec/05` §4 rule 8), never through pixels.
* `np.random.default_rng(seed)` only. Never `np.random.seed`.

---

## M11 · NumPy
`m11-numpy` · 8 lessons · ~11 h · Needs M06

**Why it matters at work:** NumPy is the language of numerical Python. pandas, scikit-learn, PyTorch tensors and image data all follow its array model. Vectorised thinking means 100× faster code.

**Outcomes:** create and inspect arrays; index with slices, masks and fancy indexing; vectorise with broadcasting; aggregate along axes; reshape and stack; do linear algebra; simulate with seeded random generators.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m11-l01** `l01-numpy-arrays` Why NumPy: arrays vs lists | `ndarray`, `dtype`, `shape`, `ndim`; creation (`array`, `zeros`, `ones`, `full`, `arange`, `linspace`, `eye`); vectorisation speed demo; memory layout intuition | ◆ dtypes, `astype`, `nbytes`, creation functions ▲ strides and views | **E1** `make_grid(rows, cols) -> np.ndarray`, a multiplication table without loops (rules: forbid `for`). **E2** `celsius_to_fahrenheit(arr)`, vectorised |
| **m11-l02** `l02-indexing-slicing` Indexing & slicing | Basic and negative indexing, slices as **views**, `.copy()`, boolean masks, fancy indexing, `np.where` | ◆ boolean and fancy indexing, `np.where`, views vs copies ▲ `np.ix_` | **E1** `clip_outliers(x, low, high)` (no `np.clip`: use masks). **E2** `replace_negatives(a, value)`, returning a new array and leaving the input unchanged. **E3** `select_rows(X, y, label)` |
| **m11-l03** `l03-broadcasting` Vectorised math & broadcasting | ufuncs, element-wise operations, broadcasting rules (align from the right), `np.newaxis`, replacing loops | ◆ ufuncs, the broadcasting rules in full, `out=` ▲ `np.einsum` | **E1** `standardize(X)`, column z-scores. **E2** `pairwise_distances(A, B)` with no loops (rules: forbid `for`). **E3** `softmax(z)`, numerically stable for large values |
| **m11-l04** `l04-aggregations-axes` Aggregations & axes | `sum/mean/std/min/max/argmax` with `axis` and `keepdims`, `cumsum`, `sort`/`argsort`, `unique(return_counts=True)`, `percentile`, `nan*` functions | ◆ `axis` and `keepdims`, `nan`-aware functions, cumulative operations ▲ numerically stable `logsumexp` | **E1** `column_stats(X) -> dict[str, np.ndarray]`. **E2** `top_k_indices(x, k)` (largest first). **E3** `normalize_rows(X)` (rows sum to 1; zero rows stay zero) |
| **m11-l05** `l05-reshaping` Reshaping & combining | `reshape`, `ravel`, `T`/`swapaxes`, `stack`/`hstack`/`vstack`/`concatenate`, `split`, `expand_dims`/`squeeze`; images as `(H, W, C)` arrays | ◆ `reshape(-1)`, `concatenate`/`stack`/`split`, `transpose`, `np.newaxis` ▲ C vs Fortran order | **E1** `to_batches(X, batch_size) -> list[np.ndarray]`. **E2** `to_grayscale(img)` with luminance weights → `(H, W)`. **E3** `tile_images(images, cols)` |
| **m11-l06** `l06-linear-algebra` Linear algebra | `@`/`dot`/`matmul`, `inv` vs `solve`, determinant, norms, eigen-decomposition, SVD, `lstsq`; linking to linear regression | ◆ `@`, `np.linalg` (`solve`, `inv`, `det`, `eig`, `svd`, `norm`, `lstsq`) ▲ conditioning | **E1** `solve_system(A, b)`. **E2** `fit_line(x, y) -> tuple[float, float]` (slope, intercept) via `lstsq`. **E3** `cosine_similarity_matrix(X)` |
| **m11-l07** `l07-random-simulation` Random numbers & simulation | `default_rng(seed)`, distributions (`normal`, `uniform`, `integers`, `choice`, `permutation`), reproducibility, Monte Carlo, vectorised simulation | ◆ `Generator` methods, seeds and reproducibility, sampling without replacement ▲ `SeedSequence` and parallel streams | **E1** `estimate_pi(n, seed) -> float` (within 0.05 for n = 100 000). **E2** `dice_counts(n_rolls, seed) -> np.ndarray`. **E3** `train_test_indices(n, test_frac, seed)` (disjoint, complete, reproducible) |
| **m11-l08** `l08-numpy-reference` NumPy reference | The 40 NumPy functions and 20 array methods used most, grouped by task | ◆ every top-level function by family (creation, manipulation, maths and ufuncs, logic, sorting and searching, statistics, set operations, I/O, constants and dtypes), every `ndarray` method and attribute, every `Generator` method, `numpy.linalg` ▲ `np.lib.stride_tricks`, structured dtypes · **Ref:** `module:numpy` `class:numpy.ndarray` `class:numpy.random.Generator` `module:numpy.linalg` | **Reference drills** (each a small function built on a less common tool): **E1** `moving_average` with `sliding_window_view`. **E2** `rank_items` with `argsort`/`searchsorted`. **E3** `histogram_table` with `np.histogram`. **E4** `pairwise_dot` with `einsum` |

**Module project (`m11-project`):** *Image filters*: grayscale, brightness, box blur (convolution with slicing), Sobel edges and threshold on small images (`data/images.npz`); results displayed with `plt.imshow`. Graded by array checks against reference outputs.
**Checkpoint (`m11-checkpoint`, 14 Q).**
**Interview corner:** what broadcasting is · view vs copy · why NumPy is fast · what `axis=0` means.
**Misconceptions:** slices copy; `a * b` is matrix multiplication; `np.random.seed` is the modern way.

---

## M12 · pandas
`m12-pandas` · 10 lessons · ~17 h · Needs M11

**Why it matters at work:** most analyst and data scientist time goes on loading, cleaning, joining and aggregating tables. pandas fluency is tested in nearly every DS interview and take-home.

**Outcomes:** load and save data with correct types; select and filter precisely; clean messy data; transform with vectorised operations and method chaining; group, aggregate, pivot and merge; work with time series; know when to reach for Polars or DuckDB.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m12-l01** `l01-series-dataframes` Series & DataFrames | Creating them; index and columns; dtypes; `head/info/describe/shape`; selecting columns; **pandas 3 notes** (Copy-on-Write, `str` dtype) | ◆ `Index` objects, nullable and string dtypes, Copy-on-Write (pandas 3) ▲ `MultiIndex` preview | **E1** `make_frame(records: list[dict]) -> pd.DataFrame` with a given column order and index. **E2** `profile(df) -> dict` (rows, columns, missing per column) |
| **m12-l02** `l02-io` Loading & saving data | `read_csv` options (`sep`, `usecols`, `dtype`, `parse_dates`, `na_values`), `read_json`, `to_csv`, **Parquet** (PyArrow, in `requirements-core.txt`), Excel (local), encodings | ◆ `read_csv` options (`dtype`, `parse_dates`, `usecols`, `chunksize`), Parquet, Excel ▲ Arrow-backed dtypes | **E1** `load_sales(path) -> pd.DataFrame` with correct dtypes and parsed dates (tests check `df.dtypes`). **E2** `csv_to_parquet(src, dst)`, round-trip equal |
| **m12-l03** `l03-selecting-filtering` Selecting & filtering | `[]`, `loc`, `iloc`, boolean masks, `isin`, `between`, `query`, `.str.contains`; why chained assignment fails under Copy-on-Write | ◆ `.loc`/`.iloc`/`.at`/`.iat`, `query`, `isin`, `between` ▲ chained assignment under Copy-on-Write | **E1** `high_value_orders(df, threshold)`. **E2** `orders_between(df, start, end)` (inclusive dates). **E3** `flag_vip(df) -> pd.DataFrame` using `loc` (a new column, original untouched) |
| **m12-l04** `l04-cleaning` Cleaning data | Missing values (`isna`, `fillna`, `dropna`, `interpolate`), duplicates, `to_numeric(errors="coerce")`, `to_datetime`, `.str` cleaning, `category`, mapping inconsistent labels, outliers | ◆ the `.str` accessor, `fillna`/`dropna`/`interpolate`, duplicates, outliers ▲ the categorical dtype | **E1** `clean_customers(df) -> pd.DataFrame` (6 specific fixes); graded with `assert_frame_equal` against the expected clean frame |
| **m12-l05** `l05-transforming` Transforming columns | `assign`, vectorised arithmetic, `np.where`/`np.select`, `map`/`replace`, why to avoid `apply`, `cut`/`qcut`, method chaining with `pipe` | ◆ `assign`, `map`, `apply` (and when not to), `pipe`, the `.dt` accessor ▲ speed of vectorised string methods | **E1** `add_features(df)` (unit price, size bucket, weekend flag). **E2** `age_band(ages: pd.Series) -> pd.Series` (an ordered categorical) |
| **m12-l06** `l06-groupby-agg` Grouping & aggregation | `groupby` + `agg` (named aggregations), `transform`, `filter`, `pivot_table`, `crosstab`, `value_counts(normalize=True)` | ◆ named aggregations, `transform`, `filter`, `pivot_table` ▲ `observed=` with categoricals | **E1** `revenue_by_category(df)`. **E2** `top_product_per_region(df)`. **E3** `share_of_total(df)` using `transform` |
| **m12-l07** `l07-merging-joining` Combining datasets | `merge` (inner/left/right/outer), keys, suffixes, `validate=`, `indicator=True`, `concat`; how bad joins duplicate rows | ◆ `merge(validate=, indicator=)`, `concat`, `join` ▲ `merge_asof` | **E1** `orders_with_customers(orders, customers)` (`validate="many_to_one"`). **E2** `unmatched_orders(orders, customers)` via `indicator` |
| **m12-l08** `l08-reshape-time-series` Reshaping & time series | `melt`, `pivot`, `stack`/`unstack`; datetime index, `resample`, `rolling`, `shift`/`diff`/`pct_change`, time zones | ◆ `melt`, `pivot`, `stack`/`unstack`, `resample`, `rolling`, time zones ▲ `MultiIndex` in full | **E1** `monthly_revenue(df) -> pd.Series`. **E2** `rolling_7d_mean(daily)`. **E3** `wide_to_long(df)` |
| **m12-l09** `l09-performance-alternatives` Performance, Polars & DuckDB | Vectorisation vs loops, memory (dtypes, `category`), chunked reading; **Polars** expressions and lazy frames; **DuckDB** SQL directly on DataFrames | ◆ Polars expressions and lazy frames, DuckDB on DataFrames ▲ DataFrame memory profiling | **E1** speed up a row-loop to vectorised code (relative speed test). **E2** `duckdb_top_products(df, n)` with SQL. **E3** `polars_monthly(df)` returning the same numbers as pandas |
| **m12-l10** `l10-pandas-reference` pandas reference | The 50 DataFrame/Series operations used most, grouped by task | ◆ every `DataFrame`, `Series` and `Index` method and attribute, every `.str` and `.dt` accessor method, every `GroupBy` method, every top-level function ▲ extension dtypes, options (`pd.set_option`), deprecations in pandas 3 · **Ref:** `module:pandas` `class:pandas.DataFrame` `class:pandas.Series` `class:pandas.Index` and the `.str`, `.dt` and `GroupBy` expr targets in `tools/coverage.json` | **Reference drills:** **E1** `top_n_per_group` (`nlargest` + `groupby`). **E2** `explode_tags` (`str.split` + `explode`). **E3** `month_over_month` (`pct_change`, `resample`). **E4** `safe_merge` (`validate=`, `indicator=`) |

**Module project (`m12-project`):** *Data cleaning challenge* on `data/food_delivery_messy.csv`. Clean it (types, duplicates, inconsistent labels, impossible values), then answer 6 business questions as a `dict`. Graded with frame checks and numeric tolerance.
**Checkpoint (`m12-checkpoint`, 18 Q).**
**Interview corner:** `merge` vs `join` vs `concat` · `apply` vs vectorised · `groupby().transform` vs `agg` · strategies for missing data · Copy-on-Write in one sentence.
**Misconceptions:** `df2 = df` copies; `inplace=True` is faster; `apply` is vectorised.

---

## M13 · Data Visualization & EDA
`m13-visualization-eda` · 7 lessons · ~11 h · Needs M12

**Why it matters at work:** analysis only counts when someone understands it. Clear charts and a disciplined EDA find data problems early and persuade stakeholders.

**Outcomes:** build charts with Matplotlib's object-oriented API; choose the right chart and avoid misleading ones; use Seaborn for statistical plots; run a structured EDA; write and present a data story.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m13-l01** `l01-matplotlib-basics` Matplotlib fundamentals | `fig, ax = plt.subplots()`; line, bar, scatter, histogram, box plot; titles, labels, legends, ticks, annotations; subplots; saving | ◆ the Figure/Axes model, `subplots`, styles, saving (dpi, formats) ▲ the Artist hierarchy | **E1** `plot_monthly_sales(df) -> Axes`: title, axis labels, 12 points (tests inspect the returned `Axes`; `spec/05` §11.5). **E2** `compare_regions(df) -> Figure`: 2×2 subplots, shared y-axis |
| **m13-l02** `l02-choosing-charts` Choosing the right chart | Chart purposes (comparison, distribution, relationship, composition, trend); perception ranking; colour-blind-safe palettes; misleading charts (truncated axes, dual axes, 3-D); accessible charts (alt text, direct labels) | ◆ chart-choice matrix, sequential/diverging/categorical colour ▲ perceptual uniformity | **E1** fix a misleading bar chart (`ax.get_ylim()[0] == 0`, labels present). Quiz: 6 "critique this chart" questions with images |
| **m13-l03** `l03-seaborn` Seaborn statistical plots | (`data-pip="seaborn"`) `histplot/kdeplot`, `boxplot/violinplot`, `scatterplot/regplot`, `heatmap`, `pairplot`, `FacetGrid`, themes | ◆ figure-level vs axes-level functions, `hue`, `FacetGrid` ▲ the seaborn objects interface | **E1** `correlation_heatmap(df) -> Axes`, annotated, diverging palette centred at 0 (tests check the collection type and the annotations) |
| **m13-l04** `l04-eda-workflow` The EDA workflow | Questions first; data overview; univariate → bivariate → multivariate; missingness; outliers; correlation is not causation; an EDA checklist and report template | ◆ profiling checklists, correlation pitfalls ▲ Simpson's paradox | **E1** `eda_answers(df) -> dict`: 8 graded answers about `data/student_performance.csv` (numeric tolerance) |
| **m13-l05** `l05-interactive-viz` Interactive charts & dashboards | When interactivity helps; Plotly Express and Altair basics; dashboard thinking (Streamlit comes in M24). Interactive charts run in a **notebook** | ◆ Plotly Express, saving HTML ▲ dashboards (Streamlit preview) | Notebook `m13-l05-interactive-viz.ipynb` with self-checks. Quiz on choosing static vs interactive |
| **m13-l06** `l06-data-storytelling` Data storytelling | From findings to narrative; annotating the key insight; executive summaries; structuring a report; presenting to non-technical people | ◆ annotations, titles that state the finding ▲ accessible charts (colour-blind palettes, alt text) | **E1** `annotate_peak(ax, x, y, text)` (tests check the annotation). **Rubric** (self-assessed) for a one-page story about a provided chart |
| **m13-l07** `l07-matplotlib-reference` Matplotlib reference | The 30 `Axes` methods behind most charts, grouped (plotting, labels, limits and scales, ticks, legends, annotation) | ◆ every `pyplot` function, every `Axes` and `Figure` method ▲ artists, transforms, `rcParams` · **Ref:** `module:matplotlib.pyplot` `class:matplotlib.axes.Axes` `class:matplotlib.figure.Figure` | **Reference drills** graded by inspecting the returned `Axes` (`spec/05` §11.5): **E1** twin y-axes. **E2** log scale with formatted ticks. **E3** annotated bar labels (`bar_label`). **E4** a shared-axis subplot grid |

**Checkpoint (`m13-checkpoint`, 12 Q).** The Phase 3 project includes an EDA report.
**Interview corner:** "Which chart would you use for X and why?" · "You see a correlation between A and B: what next?" · "How do you communicate uncertainty?"
**Misconceptions:** pie charts for many categories; more colours mean more insight; correlation implies causation.

---

## M14 · Math & Statistics for ML (in code)
`m14-math-stats` · 7 lessons · ~12 h · Needs M11

**Why it matters at work:** interviews and model debugging need the maths behind ML: gradients, probability, distributions, hypothesis tests, linear algebra and entropy. Teaching it **in code** makes it concrete for learners who fear the formulas.

**Outcomes:** reason geometrically about vectors and matrices; compute derivatives and gradients numerically and run gradient descent; apply probability and Bayes; work with distributions, sampling, confidence intervals and the bootstrap; run and interpret hypothesis tests and A/B tests; derive PCA via SVD; compute entropy and cross-entropy.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m14-l01** `l01-vectors-matrices` Vectors & matrices as geometry | Magnitude and direction, dot product and cosine similarity, projection, matrices as transformations (plots), the meaning of matrix multiplication; embeddings preview | ◆ dot product as similarity, projections ▲ distances in high dimensions | **E1** `project(u, v)`. **E2** `angle_between(u, v) -> float` (degrees). **E3** `rotation_matrix(theta) -> np.ndarray` |
| **m14-l02** `l02-calculus-gradients` Calculus for ML | Derivatives as slopes, central differences, partial derivatives and gradients, the chain rule, gradient descent in 1-D and 2-D (with plots), learning-rate effects | ◆ numerical gradients, the chain rule in code ▲ automatic differentiation preview | **E1** `numerical_derivative(f, x, h=1e-5)`. **E2** `numerical_gradient(f, x) -> np.ndarray`. **E3** `gradient_descent(grad, x0, lr, steps) -> np.ndarray` (path) |
| **m14-l03** `l03-probability` Probability foundations | Events, conditional probability, independence, **Bayes' theorem with base rates** (spam and diagnostic-test examples), random variables, expectation and variance; simulation to check intuition | ◆ conditional probability, Bayes, the `statistics` module (`mean`, `median`, `stdev`, `NormalDist`, `correlation`, `linear_regression`) ▲ `NormalDist` arithmetic · **Ref:** `module:statistics` | **E1** `posterior(prior, sensitivity, specificity) -> float`. **E2** `birthday_probability(n_people, trials, seed) -> float` (simulation within tolerance of the exact value) |
| **m14-l04** `l04-distributions-sampling` Distributions & sampling | Bernoulli, binomial, Poisson, normal, uniform, exponential; PMF/PDF/CDF with `scipy.stats`; the central limit theorem by simulation; standard error; confidence intervals; the bootstrap | ◆ the `random` module in full (seeds, weighted `choices`, `sample`, `shuffle`, distributions), the bootstrap ▲ `random` vs `secrets` vs NumPy generators · **Ref:** `module:random` | **E1** `bootstrap_ci(data, stat, n_boot, alpha, seed) -> tuple[float, float]`. **E2** `zscore_outliers(x, threshold=3.0) -> np.ndarray` |
| **m14-l05** `l05-hypothesis-testing` Hypothesis testing & A/B tests | Null and alternative hypotheses; what a p-value is and isn't; t-tests, chi-square; effect sizes; power and sample size; multiple testing; A/B test design; practical vs statistical significance | ◆ p-values, confidence intervals, power ▲ multiple-testing corrections | **E1** `ab_test(conv_a, n_a, conv_b, n_b) -> dict` (two-proportion z-test: `p_value`, `lift`; checked against statsmodels). **E2** `welch_t(a, b) -> tuple[float, float]` (matches `scipy.stats.ttest_ind(equal_var=False)`) |
| **m14-l06** `l06-pca-svd` PCA & SVD from scratch | The covariance matrix, eigenvectors as directions of variance, SVD, explained variance, centring → SVD → projection, reconstruction; comparison with `sklearn.decomposition.PCA` | ◆ variance explained, reconstruction error ▲ numerical details of the SVD | **E1** `pca(X, k) -> tuple[np.ndarray, np.ndarray]` (projection, explained ratio); tests are sign-agnostic |
| **m14-l07** `l07-information-theory` Information theory for ML | Entropy, cross-entropy, KL divergence, log-loss; why classifiers minimise cross-entropy; log-sum-exp stability | ◆ entropy, cross-entropy, KL divergence ▲ mutual information | **E1** `entropy(p)`. **E2** `cross_entropy(y_true, y_prob, eps=1e-12)`. **E3** `kl_divergence(p, q)`. **E4** `logsumexp(x)` (stable for x = 1000) |

**Checkpoint (`m14-checkpoint`, 16 Q).**
**Interview corner:** "Explain a p-value to a product manager." · a base-rate (Bayes) puzzle · "Explain gradient descent." · "What does PCA do?" · "Why use cross-entropy instead of accuracy as a loss?"
**Misconceptions:** p = 0.03 means a 97% chance the effect is real; a larger sample always means a bigger effect; PCA picks the most predictive features.

---

## M15 · Data Acquisition: SQL, APIs & Scraping
`m15-sql-apis` · 6 lessons · ~10 h · Needs M12

**Why it matters at work:** data lives in databases and behind APIs. SQL is the most-tested data skill in analyst and data-science interviews, and safe data access (no injection, no leaked keys) is non-negotiable.

**Outcomes:** write SQL from basic queries to joins, CTEs and window functions; use SQL safely from Python; consume REST APIs robustly (pagination, retries, auth); scrape responsibly; validate data at the boundaries with pydantic.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m15-l01** `l01-sql-fundamentals` SQL fundamentals | The relational model; `SELECT/WHERE/ORDER BY/LIMIT`; aggregates; `GROUP BY`/`HAVING`; `NULL` logic; SQLite (`sqlite3` is in the standard library: nothing to install) | ◆ `CASE`, `COALESCE`, string and date functions in SQLite ▲ `EXPLAIN QUERY PLAN` | SQL exercises: the learner sets `QUERY = """…"""`; tests run it on in-memory SQLite databases and compare `conn.execute(QUERY).fetchall()` with the expected rows (`spec/05` §11.4). **E1** `top_customers` · **E2** `monthly_order_counts` · **E3** `categories_over_threshold` (`HAVING`) |
| **m15-l02** `l02-sql-advanced` Joins, CTEs & window functions | Inner/left joins, self-joins, subqueries, CTEs (`WITH`), `ROW_NUMBER/RANK/DENSE_RANK`, running totals, `LAG`; classic interview queries | ◆ window frames, `RANK`/`DENSE_RANK`, recursive CTEs ▲ indexes and their costs | **E1** `second_highest_salary` · **E2** `top_n_per_group` · **E3** `running_total` · **E4** `month_over_month_growth` |
| **m15-l03** `l03-python-databases` Python + databases | `sqlite3` API (connect, execute, parameters, transactions, `executemany`), **SQL injection and parameterised queries**, `pd.read_sql`/`to_sql`, SQLAlchemy 2 overview, DuckDB for analytics | ◆ the `sqlite3` API in full (parameters, `executemany`, `row_factory`, transactions, `backup`), SQLAlchemy overview ▲ SQL injection and parameterisation · **Ref:** `module:sqlite3` | **E1** `insert_users(conn, users)`. **E2** `find_user(conn, name)`, parameterised; a test tries `"x'; DROP TABLE users; --"` and checks the table survives |
| **m15-l04** `l04-web-apis` Working with web APIs | HTTP methods, status codes, headers, REST conventions, JSON, query parameters, pagination, rate limits, retries with backoff, API keys in environment variables; `httpx`/`requests` locally; `course_mocks.fake_get` so tests never touch the network | ◆ `urllib.parse` (building and quoting URLs), `urllib.request`, `httpx`/`requests`, retries and rate limits ▲ pagination styles, async HTTP · **Ref:** `module:urllib.parse` `module:urllib.request` | **E1** `fetch_all_pages(client) -> list` against a `MockAPIClient` (in `setup`) with page tokens. **E2** `get_with_retry(client, url, retries, backoff)` using an injected `sleep` |
| **m15-l05** `l05-web-scraping` Web scraping responsibly | HTML/DOM basics, BeautifulSoup with CSS selectors, tables via `pd.read_html` (lxml, in `requirements-core.txt`), `robots.txt`, terms of service and law, rate limiting, preferring APIs | ◆ `robots.txt`, `html.parser` and BeautifulSoup ▲ legal and ethical limits | **E1** `parse_products(html) -> list[dict]` on provided HTML. **E2** `table_to_frame(html) -> pd.DataFrame` |
| **m15-l06** `l06-formats-validation` Data formats & validation | CSV vs JSON vs Parquet vs Arrow; schemas and data contracts; **pydantic v2** models and validators; quarantining bad records; pandera (local) | ◆ pydantic validation, JSON Schema, Parquet vs CSV ▲ schema evolution | **E1** `validate_records(records) -> tuple[list[Order], list[str]]` with a pydantic `Order` model (exact error summaries) |

**Phase 3 portfolio project (`p3-project`):** end-to-end analytics report (`spec/09`). **Checkpoint (`m15-checkpoint`, 15 Q)** and **phase exam `p3-exam`**.
**Interview corner:** write a query for the top N per group · `INNER` vs `LEFT JOIN` · how to prevent SQL injection · how to handle API pagination and rate limits.
**Misconceptions:** `WHERE` can filter aggregates; `NULL = NULL` is true; scraping anything public is always allowed.
