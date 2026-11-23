"""Helpers the exercise tests use. Read it if you are curious; you don't need to edit it."""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

__all__ = ["assert_fast_enough", "assert_no_syntax", "check_tests", "run_program"]


def run_program(path, stdin: str = "", args=(), timeout: float = 10) -> str:
    """Run a Python script like you would in a terminal and return everything it printed."""
    path = Path(path).resolve()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "NO_COLOR": "1"}
    try:
        result = subprocess.run([sys.executable, str(path), *map(str, args)], input=stdin, text=True,
                                capture_output=True, timeout=timeout, cwd=path.parent, env=env, check=False)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{path.name} was still running after {timeout} s "
                             "(is it waiting for more input, or stuck in a loop?)") from None
    if result.returncode != 0:
        raise AssertionError(f"{path.name} stopped with exit status {result.returncode}.\n"
                             f"--- it printed ---\n{result.stdout}\n--- errors ---\n{result.stderr}")
    return result.stdout


def _best_time(func, args, repeat: int) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        best = min(best, time.perf_counter() - start)
    return best


def assert_fast_enough(func, baseline, *args, factor: float = 10.0, repeat: int = 3) -> None:
    """Fail if func(*args) is more than `factor` times slower than baseline(*args).

    Speed is compared with a reference solution on the same machine, so a slow laptop
    doesn't fail a good solution (fixed time limits do).
    """
    mine = _best_time(func, args, repeat)
    reference = max(_best_time(baseline, args, repeat), 1e-4)
    assert mine <= factor * reference, (
        f"{func.__name__} took {mine * 1000:.1f} ms; the reference takes {reference * 1000:.1f} ms. "
        f"Look for repeated work inside a loop (allowed: up to {factor:g}x slower).")


def assert_no_syntax(path, nodes=(), calls=()) -> None:
    """Fail if the file uses any of the given AST node types (e.g. ast.For) or calls (e.g. "sorted", ".sort")."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if nodes and isinstance(node, tuple(nodes)):
            raise AssertionError(f"line {node.lineno}: this exercise asks you not to use {type(node).__name__}")
        if calls and isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else "." + func.attr if isinstance(func, ast.Attribute) else None
            if name in calls:
                raise AssertionError(f"line {node.lineno}: this exercise asks you not to call {name.lstrip('.')}()")


def _pytest(folder: Path, test_file: str) -> int:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", test_file],
                          cwd=folder, capture_output=True, text=True, env=env, timeout=60, check=False).returncode


def check_tests(test_file, module: str, mutants) -> None:
    """Check *your* tests: they must pass on the correct code and fail on every buggy version.

    mutants: {"description of the bug": "buggy source of the module", ...} or a JSON file name.
    """
    test_path = Path(test_file).resolve()
    here = test_path.parent
    if isinstance(mutants, (str, Path)):
        mutants = json.loads((here / mutants).read_text(encoding="utf-8"))
    correct = (here / f"{module}.py").read_text(encoding="utf-8")

    def run_with(source: str) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copy(test_path, folder / test_path.name)
            (folder / f"{module}.py").write_text(source, encoding="utf-8")
            return _pytest(folder, test_path.name)

    status = run_with(correct)
    assert status != 5, f"{test_path.name} has no tests yet: write functions whose names start with test_"
    assert status == 0, f"{test_path.name} fails on the CORRECT code; fix the tests first (run pytest {test_path.name})"
    missed = [bug for bug, source in mutants.items() if run_with(source) == 0]
    assert not missed, "Your tests did not catch these bugs:\n" + "\n".join(f"  - {bug}" for bug in missed)
