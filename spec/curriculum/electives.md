# Electives (outline)

Electives are built **after** the core course. Each is 4–6 lessons (about 8–12 h) and follows the same anatomy and exercise rules. IDs: `e1`…`e7`; folders `electives/e1-time-series/` and so on. Lesson IDs: `e1-l01` (add electives to `manifest.js` as modules with ids `e1`…; `check_site.py` accepts `mNN`, so extend its pattern when you add them).

## E1 · Time Series Forecasting (L/N) · needs M16
1. Time series data: stationarity, seasonality, decomposition (`statsmodels`, in `requirements-core.txt`). 2. Baselines (naive, seasonal naive) and metrics (MAE, MAPE pitfalls, MASE). 3. ARIMA/SARIMA with `statsmodels`. 4. Feature-based ML forecasting (lags, rolling features, calendar features) with gradient boosting. 5. Backtesting (rolling-origin evaluation) and avoiding leakage. 6. Notebook: Prophet (`requirements-electives.txt`; silence `cmdstanpy`'s INFO log in verified examples), statsforecast as an overview (`spec/02` §5.1), plus a forecasting project.
*Exercises:* `seasonal_naive(y, season)`, `make_lag_features(df, lags)`, `rolling_origin_splits(n, initial, horizon)`, `mase(y_true, y_pred, y_train, season)`.

## E2 · Computer Vision with OpenCV (L/N) · needs M11, M21
1. Images as arrays; colour spaces. 2. Filtering, edges, morphology (`opencv-python`, in `requirements-electives.txt`). 3. Contours, shapes and simple object measurement. 4. Feature detection and matching (ORB). 5. Notebook: detection/segmentation with pretrained models; evaluation (IoU, mAP basics).
*Exercises:* `iou(box_a, box_b)`, `non_max_suppression(boxes, scores, thr)`, `count_objects(binary_img)`.

## E3 · Reinforcement Learning Basics (L/N) · needs M20
1. MDPs, rewards, returns, policies. 2. Dynamic programming (value iteration) on a grid world. 3. Monte Carlo and TD learning. 4. **Q-learning from scratch** on a grid world (pure Python + NumPy). 5. Notebook: Gymnasium environments (`reset()` returns `(obs, info)`, `step()` returns 5 values with `terminated` and `truncated`), DQN overview; RL in LLM training (RLHF/RLAIF concepts).
*Exercises:* `value_iteration(P, R, gamma)`, `epsilon_greedy(Q, state, eps, rng)`, `q_update(Q, s, a, r, s2, alpha, gamma)`.

## E4 · Big Data with PySpark, Polars & DuckDB (L/N/W) · needs M12, M25
1. When data doesn't fit in memory: the options. 2. Polars lazy queries and streaming. 3. DuckDB on Parquet and partitioned data. 4. PySpark DataFrames and Spark SQL (notebook; `requirements-electives.txt`, Java 17 or later; start Spark from the activated environment, because its workers must run the same Python minor version; pandas API on Spark warns that it does not fully support pandas 3 yet). 5. Distributed ML and data-lake concepts (Delta/Iceberg overview).
*Exercises (pytest):* rewrite pandas pipelines as Polars lazy queries; DuckDB SQL over Parquet; partition-pruning quiz.

## E5 · Graphs & Network Science (L) · needs M09, M12
1. Graphs with `networkx` (in `requirements-electives.txt`). 2. Centrality (degree, betweenness, PageRank). 3. Community detection. 4. Link prediction basics. 5. Graph ML overview (node embeddings, GNN concepts).
*Exercises:* `pagerank(adj, d, iters)` from scratch vs networkx; `top_influencers(G, k)`.

## E6 · Recommender Systems Deep Dive (L/N) · needs M18
1. Problem framing and implicit vs explicit feedback. 2. Collaborative filtering (user/item kNN). 3. Matrix factorisation with ALS/SGD from scratch. 4. Ranking metrics (precision@k, MAP, NDCG). 5. Two-tower retrieval and re-ranking (concepts; notebook). 6. Evaluation pitfalls and cold start.
*Exercises:* `ndcg_at_k(ranked, relevant, k)`, `als_step(R, U, V, lam)`, `train_test_split_by_time(ratings, cutoff)`.

## E7 · Geospatial Data Science (L/N) · needs M12, M13
1. Coordinates, CRS and projections. 2. `shapely` geometry operations. 3. `geopandas` (in `requirements-electives.txt`): spatial joins, buffers, dissolve. 4. Maps with Matplotlib (static), plus interactive maps in a notebook. 5. Geospatial features for ML (distances, clusters, H3 concept).
*Exercises:* `haversine_km(a, b)`, `points_in_polygon(points, polygon)`, `nearest_store(customers, stores)`.
