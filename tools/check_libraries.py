"""Check that every pinned library imports and works on this Python.

  python tools/check_libraries.py                 # all pins in tools/requirements-dev.txt
  python tools/check_libraries.py --skip-missing  # while building: skip libraries not installed
  python tools/check_libraries.py -j 8 torch      # only checks whose title contains "torch"

Each check runs in its own process, so one broken library cannot hide another. The checks
also pin down the API generation the lessons must use (pandas 3, DuckDB 2, MCP 2, ...):
if a check fails after a version bump, the matching lessons need the same change.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pins import ROOT, read_pins

DEV_REQUIREMENTS = ROOT / "tools" / "requirements-dev.txt"

IMPORTS = {  # distribution -> import name
    "pytest": "pytest", "pytest-cov": "pytest_cov", "hypothesis": "hypothesis", "ruff": "ruff",
    "mypy": "mypy", "pre-commit": "pre_commit",
    "numpy": "numpy", "pandas": "pandas", "pyarrow": "pyarrow", "polars": "polars", "duckdb": "duckdb",
    "matplotlib": "matplotlib", "seaborn": "seaborn", "plotly": "plotly", "altair": "altair",
    "scipy": "scipy", "statsmodels": "statsmodels", "scikit-learn": "sklearn", "jupyterlab": "jupyterlab",
    "requests": "requests", "httpx": "httpx", "beautifulsoup4": "bs4", "lxml": "lxml",
    "pydantic": "pydantic", "sqlalchemy": "sqlalchemy", "pandera": "pandera", "pyyaml": "yaml",
    "python-dotenv": "dotenv", "rich": "rich",
    "xgboost": "xgboost", "lightgbm": "lightgbm", "shap": "shap", "optuna": "optuna",
    "imbalanced-learn": "imblearn", "umap-learn": "umap", "mlflow": "mlflow",
    "torch": "torch", "torchvision": "torchvision", "transformers": "transformers", "datasets": "datasets",
    "tokenizers": "tokenizers", "tiktoken": "tiktoken", "sentence-transformers": "sentence_transformers",
    "faiss-cpu": "faiss", "bm25s": "bm25s", "anthropic": "anthropic", "openai": "openai", "mcp": "mcp",
    "fastapi": "fastapi", "uvicorn": "uvicorn", "streamlit": "streamlit", "gradio": "gradio",
    "skops": "skops", "onnx": "onnx", "skl2onnx": "skl2onnx", "river": "river", "locust": "locust",
    "dvc": "dvc",
    "prophet": "prophet", "opencv-python": "cv2", "gymnasium": "gymnasium", "networkx": "networkx",
    "geopandas": "geopandas", "shapely": "shapely", "pyspark": "pyspark",
}
CLI_ONLY = {"ruff", "locust"}  # checked by running them: ruff is a binary, locust patches sockets on import

CHECKS: dict[str, tuple[list[str], str]] = {}


def check(title: str, needs: str):
    def register(fn):
        CHECKS[title] = (needs.split(), textwrap.dedent(fn.__doc__))
        return fn
    return register


@check("pandas 3 and NumPy 2 semantics", "pandas numpy")
def _():
    """
    import numpy as np, pandas as pd
    s = pd.Series(["a", "b"])
    assert str(s.dtype) == "str", s.dtype                    # strings get the str dtype by default
    assert not hasattr(pd.DataFrame, "applymap") and not hasattr(pd.DataFrame, "append")
    df = pd.DataFrame({"k": ["x", "y", "x"], "v": [1, 2, 3]})
    column = df["v"]; column.iloc[0] = 99                    # Copy-on-Write: df itself is unchanged
    assert df.loc[0, "v"] == 1
    assert df.groupby("k")["v"].sum().to_dict() == {"x": 4, "y": 2}
    assert np.random.default_rng(0).integers(0, 10, 3).shape == (3,)
    assert not hasattr(np, "float_")                         # NumPy 2 removed the old aliases
    """


@check("Polars, DuckDB 2 and PyArrow", "polars duckdb pyarrow pandas")
def _():
    """
    import pathlib, tempfile
    import duckdb, pandas as pd, polars as pl, pyarrow as pa
    out = (pl.LazyFrame({"k": ["a", "b", "a"], "v": [1, 2, 3]})
           .group_by("k").agg(pl.col("v").sum()).sort("k").collect())
    assert out["v"].to_list() == [4, 2]
    path = pathlib.Path(tempfile.mkdtemp()) / "t.parquet"; out.write_parquet(path)
    assert duckdb.sql(f"select sum(v) from read_parquet('{path}')").fetchall() == [(6,)]
    df = pd.DataFrame({"v": [1, 2]})
    assert duckdb.sql("select sum(v) as s from df").df()["s"].tolist() == [3]
    assert not hasattr(duckdb.sql("select 1"), "fetchone")  # DuckDB 2: relations re-run, no fetchone()
    assert duckdb.connect().execute("select 2").fetchone() == (2,)
    assert pa.table({"a": [1]}).num_rows == 1
    """


@check("charts: Matplotlib, seaborn, Plotly, Altair", "matplotlib seaborn plotly altair")
def _():
    """
    import io, matplotlib
    matplotlib.use("Agg")
    import altair as alt, matplotlib.pyplot as plt, pandas as pd, plotly.express as px, seaborn as sns
    df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 3], "g": ["a", "b", "a"]})
    fig, ax = plt.subplots(); sns.barplot(df, x="g", y="y", ax=ax)
    buf = io.BytesIO(); fig.savefig(buf, format="png"); assert buf.getvalue()[:4] == b"\\x89PNG"
    assert "<div" in px.line(df, x="x", y="y").to_html(include_plotlyjs=False)
    assert '"mark"' in alt.Chart(df).mark_line().encode(x="x", y="y").to_json()
    """


@check("SciPy and statsmodels", "scipy statsmodels")
def _():
    """
    import numpy as np, pandas as pd, scipy.stats as st, statsmodels.formula.api as smf
    rng = np.random.default_rng(1)
    assert st.ks_2samp(rng.normal(size=200), rng.normal(size=200)).pvalue > 0.01
    df = pd.DataFrame({"x": np.arange(50.0)}); df["y"] = 2 * df.x + 1 + rng.normal(scale=0.1, size=50)
    assert abs(smf.ols("y ~ x", data=df).fit().params["x"] - 2) < 0.01
    """


@check("scikit-learn, skops, ONNX export and the ONNX reference runtime", "sklearn skops skl2onnx onnx")
def _():
    """
    import pathlib, tempfile
    import numpy as np, onnx, skops.io as sio
    from onnx.reference import ReferenceEvaluator
    from skl2onnx import to_onnx
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X, y = load_iris(return_X_y=True); X = X.astype(np.float32)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X, y)
    path = pathlib.Path(tempfile.mkdtemp()) / "model.skops"
    sio.dump(model, path)                                    # no pickle: types are checked on load
    back = sio.load(path, trusted=sio.get_untrusted_types(file=path))
    assert (back.predict(X) == model.predict(X)).all()
    onx = to_onnx(model, X[:1], options={"zipmap": False}); onnx.checker.check_model(onx)
    labels = ReferenceEvaluator(onx).run(None, {"X": X})[0]
    assert (labels == model.predict(X)).mean() > 0.99
    """


@check("XGBoost, LightGBM, SHAP, Optuna, imbalanced-learn, UMAP", "xgboost lightgbm shap optuna imblearn umap")
def _():
    """
    import lightgbm as lgb, optuna, shap, umap, xgboost as xgb
    from imblearn.over_sampling import SMOTE
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=300, n_features=8, weights=[0.85], random_state=0)
    m = xgb.XGBClassifier(n_estimators=20, max_depth=3, early_stopping_rounds=5, eval_metric="logloss")
    m.fit(X[:200], y[:200], eval_set=[(X[200:], y[200:])], verbose=False)
    lgb.LGBMClassifier(n_estimators=20, verbose=-1).fit(X, y, callbacks=[lgb.log_evaluation(0)])
    assert shap.TreeExplainer(m)(X[:10]).values.shape == (10, 8)
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(); study.optimize(lambda t: (t.suggest_float("x", -2, 2) - 1) ** 2, n_trials=15)
    Xr, yr = SMOTE(random_state=0).fit_resample(X, y); assert (yr == 1).sum() == (yr == 0).sum()
    assert umap.UMAP(n_neighbors=10, random_state=0).fit_transform(X[:100]).shape == (100, 2)
    """


@check("MLflow 3 tracking and model logging", "mlflow sklearn")
def _():
    """
    import inspect, tempfile, mlflow, mlflow.sklearn
    from sklearn.linear_model import LinearRegression
    mlflow.set_tracking_uri(f"sqlite:///{tempfile.mkdtemp()}/mlflow.db")
    assert "name" in inspect.signature(mlflow.sklearn.log_model).parameters   # MLflow 3: name=, not artifact_path=
    with mlflow.start_run():
        mlflow.log_param("alpha", 0.1); mlflow.log_metric("rmse", 1.5)
        info = mlflow.sklearn.log_model(LinearRegression().fit([[0], [1]], [0, 1]), name="model")
    assert round(float(mlflow.sklearn.load_model(info.model_uri).predict([[2]])[0]), 6) == 2.0
    """


@check("PyTorch and torchvision on the CPU", "torch torchvision")
def _():
    """
    import pickle, tempfile, torch
    from torchvision.transforms import v2
    torch.manual_seed(0)
    net = torch.nn.Sequential(torch.nn.Linear(4, 8), torch.nn.ReLU(), torch.nn.Linear(8, 1))
    opt = torch.optim.AdamW(net.parameters(), lr=0.01)
    x, y = torch.randn(64, 4), torch.randn(64, 1)
    for _ in range(5):
        opt.zero_grad(); torch.nn.functional.mse_loss(net(x), y).backward(); opt.step()
    img = torch.randint(0, 256, (3, 32, 32), dtype=torch.uint8)
    out = v2.Compose([v2.RandomResizedCrop(16), v2.ToDtype(torch.float32, scale=True)])(img)
    assert out.shape == (3, 16, 16) and out.dtype == torch.float32
    class Box: pass
    path = tempfile.mktemp(suffix=".pt"); torch.save({"box": Box()}, path)
    try:
        torch.load(path)                                     # weights_only=True is the default
        raise SystemExit("torch.load accepted an arbitrary object")
    except pickle.UnpicklingError:
        pass
    torch.save(net.state_dict(), path); net.load_state_dict(torch.load(path))
    """


@check("transformers 5, tokenizers, datasets, sentence-transformers (offline)",
       "transformers tokenizers datasets sentence_transformers torch")
def _():
    """
    import pathlib, tempfile, torch, transformers
    from datasets import Dataset
    from sentence_transformers import SentenceTransformer, models as st_models
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers
    from transformers import AutoModel, BertConfig, BertModel, PreTrainedTokenizerFast
    assert not hasattr(transformers, "TFAutoModel")          # transformers 5 is PyTorch-only
    folder = pathlib.Path(tempfile.mkdtemp())
    tok = Tokenizer(models.WordPiece(unk_token="[UNK]")); tok.pre_tokenizer = pre_tokenizers.Whitespace()
    special = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
    tok.train_from_iterator(["the cat sat", "the dog ran", "a cat ran"] * 20,
                            trainers.WordPieceTrainer(vocab_size=60, special_tokens=special))
    fast = PreTrainedTokenizerFast(tokenizer_object=tok, unk_token="[UNK]", pad_token="[PAD]",
                                   cls_token="[CLS]", sep_token="[SEP]", mask_token="[MASK]")
    config = BertConfig(vocab_size=fast.vocab_size, hidden_size=32, num_hidden_layers=1,
                        num_attention_heads=2, intermediate_size=37)
    BertModel(config).save_pretrained(folder); fast.save_pretrained(folder)
    model = AutoModel.from_pretrained(folder, dtype=torch.float16)   # dtype=, not torch_dtype=
    assert next(model.parameters()).dtype == torch.float16
    ds = Dataset.from_dict({"text": ["the cat", "a dog"]}).map(lambda b: fast(b["text"]), batched=True)
    assert "input_ids" in ds.column_names
    st = SentenceTransformer(modules=[st_models.Transformer(str(folder)), st_models.Pooling(32, "mean")])
    assert st.encode(["the cat sat"]).shape == (1, 32)
    """


@check("FAISS and bm25s retrieval", "faiss bm25s")
def _():
    """
    import bm25s, faiss, numpy as np
    xb = np.random.default_rng(0).random((100, 16), dtype=np.float32)
    index = faiss.IndexFlatL2(16); index.add(xb)
    _, ids = index.search(xb[:3], 2); assert (ids[:, 0] == [0, 1, 2]).all()
    corpus = ["the cat sat on the mat", "dogs chase cats", "python is a language"]
    retriever = bm25s.BM25(); retriever.index(bm25s.tokenize(corpus, show_progress=False), show_progress=False)
    docs, _ = retriever.retrieve(bm25s.tokenize(["python language"], show_progress=False), k=1, show_progress=False)
    assert int(docs[0, 0]) == 2
    """


@check("Anthropic and OpenAI SDKs, MCP 2 server", "anthropic openai mcp")
def _():
    """
    import asyncio, anthropic, openai
    from mcp.server.mcpserver import MCPServer               # MCP 2: FastMCP was renamed MCPServer
    a, o = anthropic.Anthropic(api_key="test"), openai.OpenAI(api_key="test")
    assert callable(a.messages.create) and callable(o.responses.create)
    server = MCPServer("demo")
    @server.tool()
    def add(a: int, b: int) -> int:
        "Add two integers."
        return a + b
    tools = asyncio.run(server.list_tools())
    assert [t.name for t in tools] == ["add"] and tools[0].input_schema["required"] == ["a", "b"]
    """


@check("FastAPI lifespan and TestClient", "fastapi httpx pydantic")
def _():
    """
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from pydantic import BaseModel
    state = {}
    @asynccontextmanager
    async def lifespan(app):
        state["model"] = "loaded"; yield; state.clear()
    app = FastAPI(lifespan=lifespan)
    class Item(BaseModel):
        x: float
    @app.post("/predict")
    def predict(item: Item):
        return {"y": item.x * 2, "model": state["model"]}
    with TestClient(app) as client:
        assert client.post("/predict", json={"x": 2}).json() == {"y": 4.0, "model": "loaded"}
        assert client.post("/predict", json={"x": "a"}).status_code == 422
    """


@check("Streamlit AppTest and Gradio Blocks", "streamlit gradio")
def _():
    """
    import gradio as gr
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_string("import streamlit as st\\nn = st.number_input('n', value=2)\\nst.write(n * 2)").run()
    assert not at.exception and "4" in at.markdown[0].value
    with gr.Blocks():
        box, out = gr.Textbox(), gr.Textbox(); box.submit(lambda s: s.upper(), box, out)
    """


@check("pydantic 2, SQLAlchemy 2, pandera, httpx, Beautiful Soup, PyYAML, dotenv, rich",
       "pydantic sqlalchemy pandera httpx bs4 lxml yaml dotenv rich")
def _():
    """
    import io, pathlib, tempfile
    import httpx, pandas as pd, pandera.pandas as pa, yaml
    from bs4 import BeautifulSoup
    from dotenv import dotenv_values
    from pydantic import BaseModel, field_validator
    from rich.console import Console
    from sqlalchemy import String, create_engine, select
    from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
    class User(BaseModel):
        name: str
        @field_validator("name")
        @classmethod
        def strip(cls, v): return v.strip()
    assert User.model_validate({"name": " ada "}).model_dump() == {"name": "ada"}
    class Base(DeclarativeBase): pass
    class Row(Base):
        __tablename__ = "rows"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(20))
    engine = create_engine("sqlite://"); Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Row(name="a")); session.commit()
        assert session.scalars(select(Row.name)).all() == ["a"]
    pa.DataFrameSchema({"x": pa.Column(int, pa.Check.ge(0))}).validate(pd.DataFrame({"x": [1]}))
    client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"ok": True})))
    assert client.get("https://example.test").json() == {"ok": True}
    assert BeautifulSoup("<p class='a'>hi</p>", "lxml").select_one("p.a").text == "hi"
    assert yaml.safe_load("a: 1") == {"a": 1}
    env = pathlib.Path(tempfile.mkdtemp()) / ".env"; env.write_text("KEY=value\\n")
    assert dotenv_values(env) == {"KEY": "value"}
    Console(file=io.StringIO()).print("[bold]ok[/]")
    """


@check("pytest 9 (native TOML config), pytest-cov, Hypothesis, mypy, ruff, pre-commit",
       "pytest pytest_cov hypothesis mypy pre_commit")
def _():
    """
    import pathlib, subprocess, sys, tempfile
    folder = pathlib.Path(tempfile.mkdtemp())
    (folder / "calc.py").write_text("def add(a: int, b: int) -> int:\\n    return a + b\\n")
    (folder / "check_calc.py").write_text(
        "from hypothesis import given, strategies as st\\nfrom calc import add\\n\\n\\n"
        "@given(st.integers(), st.integers())\\ndef check_add(a: int, b: int) -> None:\\n"
        "    assert add(a, b) == add(b, a)\\n")
    (folder / "pyproject.toml").write_text(  # [tool.pytest] is read only if it finds check_*.py
        '[tool.pytest]\\npython_files = ["check_*.py"]\\npython_functions = ["check_*"]\\n')
    def run(*args):
        done = subprocess.run([sys.executable, "-m", *args], cwd=folder, capture_output=True, text=True)
        assert done.returncode == 0, " ".join(args) + "\\n" + done.stdout + done.stderr
        return done.stdout
    assert "1 passed" in run("pytest", "-p", "no:cacheprovider", "--cov=calc")
    run("mypy", "--strict", "calc.py", "check_calc.py")
    run("ruff", "check", "calc.py"); run("ruff", "format", "--check", "calc.py")
    run("pre_commit", "--version")
    """


@check("Jupyter runs a notebook on this Python", "nbformat nbclient ipykernel")
def _():
    """
    import sys, nbformat
    from nbclient import NotebookClient
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("import sys; print(sys.version_info[:2])")])
    NotebookClient(nb, timeout=120, kernel_name="python3").execute()
    assert str(tuple(sys.version_info[:2])) in nb.cells[0].outputs[0]["text"]
    """


@check("DVC and Locust command lines", "dvc locust")
def _():
    """
    import subprocess, sys
    for module in ("dvc", "locust"):
        done = subprocess.run([sys.executable, "-m", module, "--version"], capture_output=True, text=True)
        assert done.returncode == 0, module + done.stdout + done.stderr
    """


@check("River streaming drift detection", "river numpy")
def _():
    """
    import numpy as np
    from river import drift
    rng = np.random.default_rng(0)
    stream = np.concatenate([rng.normal(0, 1, 1000), rng.normal(2, 1, 1000)])
    detector, first = drift.ADWIN(), None
    for i, x in enumerate(stream):
        detector.update(float(x))
        if detector.drift_detected and first is None:
            first = i
    assert first is not None and 1000 <= first < 1100, first
    """


@check("OpenCV, Gymnasium, NetworkX, GeoPandas and Shapely", "cv2 gymnasium networkx geopandas shapely")
def _():
    """
    import cv2, geopandas as gpd, gymnasium as gym, networkx as nx, numpy as np
    from shapely.geometry import Point
    img = np.zeros((32, 32, 3), np.uint8); cv2.circle(img, (16, 16), 8, (255, 255, 255), -1)
    assert cv2.imencode(".png", cv2.GaussianBlur(img, (5, 5), 0))[0]
    env = gym.make("CartPole-v1"); obs, info = env.reset(seed=0)
    assert len(env.step(env.action_space.sample())) == 5     # obs, reward, terminated, truncated, info
    assert nx.shortest_path(nx.Graph([(1, 2), (2, 3), (1, 3), (3, 4)]), 1, 4) == [1, 3, 4]
    gdf = gpd.GeoDataFrame({"n": [1, 2]}, geometry=[Point(0, 0), Point(1, 1)], crs="EPSG:4326")
    assert gdf.to_crs("EPSG:3857").buffer(10).area.gt(0).all()
    """


@check("Prophet fit and forecast", "prophet")
def _():
    """
    import logging, numpy as np, pandas as pd
    logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
    from prophet import Prophet
    ds = pd.date_range("2026-01-01", periods=90, freq="D")
    y = 10 + 0.1 * np.arange(90) + np.sin(np.arange(90) * 2 * np.pi / 7)
    model = Prophet(daily_seasonality=False).fit(pd.DataFrame({"ds": ds, "y": y}))
    assert len(model.predict(model.make_future_dataframe(periods=7))) == 97
    """


@check("PySpark local session with a Python UDF", "pyspark java")
def _():
    """
    import os, sys
    os.environ["PYSPARK_PYTHON"] = sys.executable            # workers must run the same Python
    from pyspark.sql import SparkSession, functions as F
    spark = (SparkSession.builder.master("local[1]").appName("check")
             .config("spark.ui.enabled", "false").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    df = spark.createDataFrame([("a", 1), ("b", 2), ("a", 3)], ["k", "v"])
    assert sorted(tuple(r) for r in df.groupBy("k").agg(F.sum("v")).collect()) == [("a", 4), ("b", 2)]
    plus_one = F.udf(lambda x: x + 1, "int")
    assert [r[0] for r in df.select(plus_one("v")).collect()] == [2, 3, 4]
    spark.stop()
    """


def available(name: str) -> bool:
    return shutil.which(name) is not None if name == "java" else importlib.util.find_spec(name) is not None


def import_script(dists: list[str]) -> str:
    lines = ["import importlib, importlib.metadata as md, subprocess, sys", "bad = []"]
    for dist in dists:
        if dist in CLI_ONLY:
            lines.append(f"r = subprocess.run([sys.executable, '-m', {IMPORTS[dist]!r}, '--version'], capture_output=True)\n"
                         f"bad += [] if r.returncode == 0 else [{dist!r}]")
        else:
            lines.append(f"try:\n    importlib.import_module({IMPORTS[dist]!r})\n"
                         f"except Exception as err:\n    bad.append(f'{dist} ({{type(err).__name__}}: {{err}})')")
    lines.append("assert not bad, 'failed: ' + ', '.join(bad)")
    return "\n".join(lines)


def run(title: str, code: str, timeout: int) -> tuple[str, bool, str, float]:
    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as cwd:
        try:
            done = subprocess.run([sys.executable, "-c", code], cwd=cwd, capture_output=True,
                                  text=True, timeout=timeout, check=False)
            ok, out = done.returncode == 0, done.stdout + done.stderr
        except subprocess.TimeoutExpired:
            ok, out = False, f"timed out after {timeout} s"
    return title, ok, out.strip(), time.perf_counter() - start


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("only", nargs="*", help="run only checks whose title contains one of these words")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--skip-missing", action="store_true", help="skip checks whose libraries are absent")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args(argv)

    pinned = sorted(read_pins(DEV_REQUIREMENTS))
    unknown = [d for d in pinned if d not in IMPORTS]
    stale = [d for d in IMPORTS if d not in pinned]
    if unknown or stale:
        print(f"IMPORTS is out of step with {DEV_REQUIREMENTS.name}: add {unknown}, remove {stale}")
        return 1
    present = [d for d in pinned if available(IMPORTS[d])]  # find_spec does not import
    missing = sorted(set(pinned) - set(present))
    if missing and not args.skip_missing:
        print(f"not installed: {', '.join(missing)} (install {DEV_REQUIREMENTS.relative_to(ROOT)}, "
              "or pass --skip-missing)")
        return 1
    tasks = {f"import {len(present)} pinned libraries": import_script(present)}
    skipped = []
    for title, (needs, code) in CHECKS.items():
        if all(available(n) for n in needs):
            tasks[title] = code
        elif args.skip_missing:
            skipped.append(title)
        else:
            tasks[title] = f"raise SystemExit('needs: {' '.join(n for n in needs if not available(n))}')"
    if args.only:
        tasks = {t: c for t, c in tasks.items() if any(w.lower() in t.lower() for w in args.only)}

    print(f"Python {sys.version.split()[0]}: {len(tasks)} checks"
          + (f", {len(skipped)} skipped (libraries not installed)" if skipped else ""), flush=True)
    failed = 0
    with cf.ThreadPoolExecutor(args.jobs) as pool:
        for title, ok, out, secs in pool.map(lambda kv: run(*kv, args.timeout), tasks.items()):
            failed += not ok
            print(f"[{'PASS' if ok else 'FAIL'}] {title} ({secs:.0f} s)", flush=True)
            if not ok:
                print(textwrap.indent(out[-3000:], "    "))
    print("all checks passed" if not failed else f"{failed} checks failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
