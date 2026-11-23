# Phase 4 · Machine Learning

**Goal:** frame ML problems, then build, tune, evaluate, interpret and audit classical models with scikit-learn, understanding the maths well enough to implement the key algorithms from scratch.
**Modules:** M16–M19 · 29 lessons · ~47 h · **Portfolio project P4:** churn prediction with a model card (`spec/09`) · **Phase exam `p4-exam`:** 25 questions + 2 modelling tasks (an exam pack whose tests score the model on a held-out split they build themselves), 100 minutes.

**Phase teaching notes**
* **Data:** scikit-learn's bundled datasets (`load_iris`, `load_wine`, `load_breast_cancer`, `load_diabetes`, `load_digits`) work offline. **Never** use `fetch_*` loaders: they download at runtime. Synthetic tables come from `site/data/` (`telco_churn.csv`, `transactions_fraud.csv`, `ratings.csv` …).
* **Graded models:** `setup` gives the learner **training data only**. Test code builds the held-out data itself (same seeded split), so the learner can't see it, and checks a metric threshold. Set thresholds from the reference solution's score minus a margin (`spec/05` §4.7), and keep training under about 10 s on a laptop CPU.
* "From scratch" means NumPy only, compared with scikit-learn's results to a tolerance.
* Every exercise sets `random_state`/seeds. Rule of thumb in every lesson: **fit on train, transform test.**

---

## M16 · Machine Learning Foundations
`m16-ml-foundations` · 7 lessons · ~12 h · Needs M12, M14

**Why it matters at work:** most ML failures come from bad framing, missing baselines, wrong metrics and leakage, not from algorithm choice. This module builds those instincts.

**Outcomes:** frame a business problem as an ML task (or decide ML isn't needed); train and evaluate models with scikit-learn's API; implement linear and logistic regression with gradient descent; choose and compute the right metrics; diagnose over- and under-fitting; use cross-validation correctly and spot leakage.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m16-l01** `l01-what-is-ml` What machine learning is | Supervised, unsupervised, self-supervised and reinforcement learning; features and labels; training vs inference; the ML workflow (frame → data → baseline → iterate → deploy → monitor); when **not** to use ML; the estimator API recap | ◆ supervised, unsupervised and reinforcement learning; the ML workflow ▲ no free lunch | **E1** `split_features_target(df, target) -> tuple[pd.DataFrame, pd.Series]`. Quiz: frame 6 business problems (task type, label, metric) |
| **m16-l02** `l02-first-model` Your first model | `train_test_split` (stratified, seeded), `DummyClassifier` baselines, k-NN on wine, `fit/predict/score`, reproducibility | ◆ the estimator API (`fit`/`predict`/`score`), train/test split ▲ `random_state` and reproducibility | **E1** `make_knn(k) -> Pipeline`: an *unfitted* scaler + k-NN pipeline; it must beat the majority baseline by ≥ 20 points and reach ≥ 0.90 on a held-out split built by the tests (the worked example in `spec/05` §11.3) |
| **m16-l03** `l03-linear-regression` Linear regression | Model and MSE loss, the normal equation, batch gradient descent from scratch, `LinearRegression`, interpreting coefficients, residual plots, assumptions | ◆ closed form vs gradient descent, R², residual plots ▲ multicollinearity | **E1** `LinearRegressionGD(lr, epochs)` with `fit/predict`; coefficients within 1e-2 of scikit-learn on scaled diabetes data. **E2** `r2(y_true, y_pred) -> float` |
| **m16-l04** `l04-logistic-regression` Logistic regression & classification | Sigmoid, the decision boundary, log-loss, probabilities vs labels, thresholds, multiclass (softmax/OvR), the `C` regularisation parameter | ◆ decision thresholds, `predict_proba` ▲ calibration | **E1** `sigmoid(z)`, stable for ±1000. **E2** `LogisticRegressionGD` reaching ≥ 0.95 accuracy on scaled breast-cancer data (held-out split) |
| **m16-l05** `l05-metrics` Evaluation metrics | MAE, MSE, RMSE, R²; accuracy, precision, recall, F1, the confusion matrix, ROC-AUC, PR-AUC, log-loss; choosing metrics by business cost; the imbalance trap | ◆ precision/recall/F1, ROC-AUC, PR-AUC, regression metrics ▲ choosing metrics for imbalanced data | **E1** `confusion_counts(y_true, y_pred) -> dict`. **E2** `precision_recall_f1(y_true, y_pred) -> tuple`. **E3** `best_threshold(y_true, proba, metric="f1") -> float` |
| **m16-l06** `l06-generalization` Overfitting, regularisation & bias–variance | Train vs test error, complexity curves, learning curves, Ridge/Lasso/ElasticNet, scaling before regularisation, early stopping (concept) | ◆ L1/L2, learning curves ▲ double descent (concept) | **E1** `choose_alpha(X, y, alphas, seed) -> float` (validation curve). **E2** `best_poly_degree(x, y, degrees, seed) -> int` |
| **m16-l07** `l07-cross-validation-leakage` Cross-validation & data leakage | k-fold, stratified, group k-fold, time-series split, nested CV preview; leakage types (target, train–test contamination, preprocessing, temporal) and how to detect them | ◆ k-fold, stratified, group and time-series splits; leakage patterns ▲ nested cross-validation | **E1** `kfold_indices(n, k, seed) -> list[tuple[np.ndarray, np.ndarray]]` (disjoint, complete). **E2** (debug) a leaky pipeline (scaler fitted before the split): fix it; tests compare CV scores and inspect the pipeline |

**Module project (`m16-project`):** *House-price baseline to model*: on `data/housing_small.csv`, build a baseline, linear, Ridge and a k-NN regressor, compare them with CV, and write 5 sentences of conclusions (rubric). Graded on RMSE on a held-out split.
**Checkpoint (`m16-checkpoint`, 16 Q).**
**Interview corner:** explain the bias–variance trade-off · precision vs recall with a real example · L1 vs L2 · three kinds of data leakage · why cross-validate.
**Misconceptions:** high train accuracy means a good model; accuracy works for imbalanced data; scaling the whole dataset before splitting is harmless.

---

## M17 · Feature Engineering & Pipelines
`m17-features-pipelines` · 7 lessons · ~10 h · Needs M16

**Why it matters at work:** in industry, features and leak-proof pipelines matter more than exotic models. scikit-learn `Pipeline`s are what get deployed.

**Outcomes:** scale and transform numeric features; encode categorical features (including unseen categories); impute missing values; compose `ColumnTransformer` + `Pipeline` (with custom transformers); engineer date, text and aggregate features; tune hyperparameters without peeking at the test set; handle imbalanced classes.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m17-l01** `l01-scaling-transforms` Scaling & transforms | `StandardScaler`, `MinMaxScaler`, `RobustScaler`, log/power transforms, which models need scaling, outliers | ◆ `StandardScaler`, `MinMaxScaler`, `RobustScaler`, log and power transforms ▲ `QuantileTransformer` | **E1** `scale_train_test(X_train, X_test) -> tuple` (fit on train only: a test checks that the test statistics differ). **E2** `log_skewed(df, cols)` |
| **m17-l02** `l02-encoding-categoricals` Encoding categorical features | One-hot (`handle_unknown="ignore"`), ordinal, `TargetEncoder` (cross-fitted, leakage risk), frequency encoding, high cardinality | ◆ one-hot, ordinal and target encoding ▲ the hashing trick | **E1** `encode_city(train, test) -> tuple[np.ndarray, np.ndarray]` surviving unseen cities. **E2** `frequency_encode(series) -> pd.Series` |
| **m17-l03** `l03-missing-data` Missing data | MCAR/MAR/MNAR intuition, `SimpleImputer`, missing-indicator features, `KNNImputer`, models with native NaN support (`HistGradientBoosting`) | ◆ `SimpleImputer`, `KNNImputer`, missing indicators ▲ MCAR/MAR/MNAR | **E1** `impute_and_flag(df, cols) -> pd.DataFrame` |
| **m17-l04** `l04-pipelines` Pipelines & ColumnTransformer | `Pipeline`, `ColumnTransformer`, `make_column_selector`, `set_output(transform="pandas")`, `FunctionTransformer`, custom transformers (`BaseEstimator` + `TransformerMixin`), leak-proof CV, saving with joblib/skops | ◆ `Pipeline`, `ColumnTransformer`, `set_output(transform="pandas")` ▲ custom transformers | **E1** `build_preprocessor(num_cols, cat_cols) -> ColumnTransformer` (tests transform new data: shape, no NaN, unseen categories). **E2** `ClipOutliers(lower_q, upper_q)`, a custom transformer that learns its bounds in `fit` |
| **m17-l05** `l05-feature-creation` Creating features | Domain ratios, interactions, polynomial features, datetime features (cyclical sin/cos), text features (`CountVectorizer`/`TfidfVectorizer`), group aggregates (with leakage care), feature selection | ◆ date parts, interactions, binning, text features ▲ feature selection | **E1** `datetime_features(df, col) -> pd.DataFrame`. **E2** `tfidf_top_terms(docs, k) -> list[str]` |
| **m17-l06** `l06-hyperparameter-tuning` Hyperparameter tuning | `GridSearchCV`, `RandomizedSearchCV`, successive halving, search spaces, `scoring`, `refit`, nested CV, Optuna (local), compute budgets, never tuning on the test set | ◆ grid, random and halving search ▲ Bayesian optimisation (concept) | **E1** `tune_knn(X, y, seed) -> dict` (best params within a given grid; ≥ threshold on the held-out split) |
| **m17-l07** `l07-imbalanced-data` Imbalanced data | `class_weight`, threshold tuning, resampling (imbalanced-learn, local), stratification, PR curves, cost-sensitive evaluation | ◆ class weights, resampling, threshold moving ▲ cost-sensitive evaluation | **E1** `fraud_pipeline(X, y) -> Pipeline` with recall ≥ 0.80 at precision ≥ 0.30 on the held-out split (`data/transactions_fraud.csv`). **E2** `threshold_for_recall(y, proba, target) -> float` |

**Module project (`m17-project`):** *Pipeline refactor*: turn a messy notebook-style script (global state, leakage, repeated code) into one `Pipeline`, prove there's no leakage with CV, and save it. Graded on the held-out score and the pipeline structure.
**Checkpoint (`m17-checkpoint`, 14 Q).**
**Interview corner:** why pipelines matter · target-encoding leakage · handling unseen categories in production · tuning without overfitting · metrics for 1% positive classes.
**Misconceptions:** more features are always better; impute with the test-set mean; class weights and resampling are interchangeable.

---

## M18 · ML Algorithms Toolkit
`m18-ml-algorithms` · 9 lessons · ~16 h · Needs M17

**Why it matters at work:** knowing how algorithms work (not just their API) lets you choose them well, debug them, and answer "how does X work?" in interviews.

**Outcomes:** implement k-NN, decision-tree splits, k-means and recommender similarity from scratch; use and tune random forests, gradient boosting (scikit-learn, XGBoost, LightGBM), SVMs and Naive Bayes; cluster and reduce dimensions; detect anomalies; pick an algorithm for a problem and justify it.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m18-l01** `l01-knn-distances` k-Nearest Neighbours & distances | Euclidean, Manhattan and cosine distances; vectorised k-NN; choosing k; scaling; the curse of dimensionality | ◆ distance metrics, why scaling matters ▲ the curse of dimensionality | **E1** `knn_predict(X_train, y_train, X_test, k) -> np.ndarray`, vectorised, matching `KNeighborsClassifier` |
| **m18-l02** `l02-decision-trees` Decision trees | Gini and entropy, searching for the best split, greedy growth, depth and pruning (`ccp_alpha`), `plot_tree`, importance pitfalls | ◆ impurity, pruning, `plot_tree` ▲ cost-complexity pruning | **E1** `gini(labels) -> float`. **E2** `best_split(x, y) -> tuple[float, float]` (threshold, impurity decrease) |
| **m18-l03** `l03-random-forests` Bagging & random forests | Bootstrap samples, variance reduction, feature subsampling, the OOB score, impurity vs permutation importance, extra trees | ◆ OOB score, feature importance ▲ permutation importance | **E1** `bootstrap_sample(X, y, seed)`. **E2** `rf_oob(X, y, seed) -> float` (≥ threshold) |
| **m18-l04** `l04-gradient-boosting` Gradient boosting | Fitting residuals, learning rate × trees × depth, `HistGradientBoosting`, **XGBoost and LightGBM** (in `requirements-ml.txt`), early stopping, native categorical support | ◆ `HistGradientBoosting`, XGBoost/LightGBM ▲ early-stopping internals | **E1** `boost_manually(X, y, n_rounds, lr) -> list` using depth-1 trees on residuals; it must beat the mean predictor by the target margin. **E2** `tuned_hgb(X, y, seed)` ≥ threshold |
| **m18-l05** `l05-svm-naive-bayes` SVMs & Naive Bayes | Maximum margin, kernels, `C` and `gamma`, scaling; Naive Bayes for text, Laplace smoothing; an end-to-end spam classifier with TF-IDF | ◆ kernels, `C`, `gamma`; Naive Bayes variants ▲ the dual form (concept) | **E1** `spam_classifier(texts, labels) -> Pipeline` with F1 ≥ threshold on held-out messages (`data/sms_small.csv`, synthetic). **E2** `laplace_prob(count, total, vocab_size, alpha=1.0)` |
| **m18-l06** `l06-clustering` Clustering | k-means (Lloyd's algorithm, vectorised), k-means++, elbow and silhouette, DBSCAN, hierarchical clustering; customer segmentation | ◆ k-means, DBSCAN, hierarchical clustering, silhouette ▲ Gaussian mixtures | **E1** `kmeans(X, k, seed, iters=100) -> tuple[centroids, labels]` (tests use `adjusted_rand_score` on blobs, so label order doesn't matter). **E2** `best_k_by_silhouette(X, ks, seed) -> int` |
| **m18-l07** `l07-dimensionality-reduction` Dimensionality reduction & embeddings | PCA for compression and visualisation, t-SNE/UMAP concepts (UMAP runs locally), visualising high-dimensional data, embeddings preview | ◆ PCA, t-SNE, UMAP ▲ embeddings for similarity search | **E1** `n_components_for_variance(X, target=0.95) -> int`. **E2** `plot_pca_2d(X, y) -> Axes` (tests inspect the returned `Axes`) |
| **m18-l08** `l08-anomaly-recsys` Anomaly detection & recommenders | z-score/IQR, `IsolationForest`, `LocalOutlierFactor`; recommenders: popularity, item–item cosine similarity, matrix factorisation (SVD) on ratings | ◆ `IsolationForest`, LOF, collaborative filtering ▲ matrix factorisation | **E1** `iqr_outliers(x) -> np.ndarray`. **E2** `item_similarity(R) -> np.ndarray`. **E3** `recommend(user_ratings, sim, k) -> list[int]` (excludes items already rated) |
| **m18-l09** `l09-sklearn-reference` scikit-learn reference | The estimator API in one table; which estimator to try for which problem; the 25 utilities used most | ◆ every public class and function in `preprocessing`, `model_selection`, `metrics`, `pipeline`, `compose`, `impute`, `linear_model`, `ensemble`, `tree`, `neighbors`, `svm`, `cluster`, `decomposition`; `BaseEstimator` methods ▲ `set_output`, metadata routing, estimator tags · **Ref:** `class:sklearn.base.BaseEstimator` and the 13 `module:sklearn.*` targets in `tools/coverage.json` | **Reference drills:** **E1** `make_preprocessor(df)` with `make_column_selector`. **E2** `pick_metric(task)` returning a scorer string that `cross_val_score` accepts. **E3** `tune(model, grid)` with `HalvingGridSearchCV` (explicit enable import) |

**Checkpoint (`m18-checkpoint`, 18 Q).**
**Interview corner:** random forest vs gradient boosting · how k-means works and fails · the kernel trick in plain words · the "naive" assumption · which algorithm for tabular data and why.
**Misconceptions:** deep learning beats boosting on every table; k-means finds any cluster shape; feature importance means causation.

---

## M19 · Evaluation, Interpretability & Responsible AI
`m19-evaluation-responsible-ai` · 6 lessons · ~9 h · Needs M18

**Why it matters at work:** models affect people. Companies expect ML practitioners to quantify uncertainty, explain predictions, find where models fail, check fairness, protect privacy and keep experiments reproducible. Regulators increasingly require it.

**Outcomes:** evaluate with confidence intervals and calibration; explain models globally and locally; run slice-based error analysis; compute and discuss fairness metrics; apply privacy and documentation practices (model cards, datasheets); track experiments reproducibly.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m19-l01** `l01-robust-evaluation` Beyond a single score | Validation strategy design, bootstrap confidence intervals for metrics, comparing models fairly (CV variance, paired comparisons), calibration (reliability curves, `CalibratedClassifierCV`), cost-based evaluation | ◆ confidence intervals for metrics, slicing ▲ comparing models statistically | **E1** `metric_ci(y_true, y_pred, metric, n_boot, seed) -> tuple`. **E2** `expected_calibration_error(y_true, proba, bins=10) -> float` |
| **m19-l02** `l02-interpretability` Interpretability | Global vs local; coefficients (with scaling caveats), permutation importance, partial dependence and ICE (`sklearn.inspection`), SHAP concepts (notebook), correlated-feature pitfalls | ◆ permutation importance, partial dependence, SHAP ▲ limits of explanations | **E1** `permutation_importance_manual(model, X, y, metric, seed, repeats=5) -> np.ndarray`, close to scikit-learn's |
| **m19-l03** `l03-error-analysis` Error analysis | Slice-based evaluation, confusion analysis, error buckets, finding label and data issues, prioritising fixes, data-centric AI | ◆ confusion analysis, error slices ▲ label noise | **E1** `performance_by_segment(df, segment, y_true, y_pred) -> pd.DataFrame`. **E2** `worst_segments(report, min_size, n) -> list[str]` |
| **m19-l04** `l04-fairness-bias` Fairness & bias | Sources of bias (historical, sampling, measurement, labelling); demographic parity, equal opportunity, equalised odds; why metrics can conflict; mitigations and their limits; documenting decisions | ◆ fairness metrics ▲ impossibility results | **E1** `demographic_parity_difference(y_pred, group) -> float`. **E2** `equal_opportunity_difference(y_true, y_pred, group) -> float` (checked on synthetic data with a known gap) |
| **m19-l05** `l05-responsible-ai` Responsible AI, privacy & governance | PII and data minimisation, pseudonymisation; regulation landscape (GDPR principles; the EU AI Act's risk-based approach, **verify current obligations when building**; your country's data-protection law); model cards and datasheets; human oversight; security; environmental cost | ◆ privacy, model cards, regulation overview ▲ differential privacy (concept) | **E1** `pseudonymize(df, cols, salt) -> pd.DataFrame` (salted hashes, stable across calls). **E2** `redact_pii(text) -> str` (emails, phone patterns). **Rubric:** write a model card for the P4 model |
| **m19-l06** `l06-experiment-tracking` Reproducibility & experiment tracking | Seeds and determinism, config files, versioning data and models, **MLflow** tracking (notebook/local), comparing runs | ◆ seeds, environment capture, MLflow ▲ data versioning | **E1** `ExperimentLog` class: `log(params, metrics)`, `best(metric, mode)` and `to_frame()` |

**Phase 4 portfolio project (`p4-project`):** churn prediction with a model card (`spec/09`). **Checkpoint (`m19-checkpoint`, 14 Q)** and **phase exam `p4-exam`**.
**Interview corner:** explain this model's prediction to a customer · two fairness metrics and their trade-off · what calibration means and when it matters · how you'd debug a model that fails for one region.
**Misconceptions:** removing the sensitive column removes bias; a good overall AUC means good for every group; interpretability equals causality.
