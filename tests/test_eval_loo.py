"""
Smoke test for scripts/eval_loo.py.

Run under TABPFN_DISABLE=1 (conftest sets it) so the heavy TabPFN LOO is skipped.
Asserts:
  - output JSON has keys: tabpfn_loo, onenn_loo, n, tabpfn_beats_1nn
  - onenn_loo is a float (not None)
  - n equals the number of rows in data/seed_repos.csv
"""
import importlib
import json
import os
import sys
from pathlib import Path
import pandas as pd


SEED_PATH = Path(__file__).parent.parent / "data" / "seed_repos.csv"


def test_eval_loo_reports_both_models(capsys):
    # Ensure TABPFN_DISABLE is set (conftest already does this, belt-and-suspenders)
    assert os.environ.get("TABPFN_DISABLE") == "1", "conftest must set TABPFN_DISABLE=1"

    # Import (or re-import) the module freshly
    if "scripts.eval_loo" in sys.modules:
        del sys.modules["scripts.eval_loo"]
    import scripts.eval_loo as eval_loo

    result = eval_loo.main()

    # main() must return the dict
    assert isinstance(result, dict), f"main() should return a dict, got {type(result)}"

    # Required keys
    for key in ("tabpfn_loo", "onenn_loo", "n", "tabpfn_beats_1nn"):
        assert key in result, f"Missing key: {key}"

    # Under TABPFN_DISABLE, tabpfn_loo must be None
    assert result["tabpfn_loo"] is None, (
        f"Expected tabpfn_loo=None under TABPFN_DISABLE, got {result['tabpfn_loo']}"
    )

    # 1-NN LOO must always be computed
    assert isinstance(result["onenn_loo"], float), (
        f"onenn_loo must be a float, got {result['onenn_loo']!r}"
    )
    assert 0.0 <= result["onenn_loo"] <= 1.0, (
        f"onenn_loo out of range: {result['onenn_loo']}"
    )

    # n must equal seed row count
    expected_n = len(pd.read_csv(SEED_PATH))
    assert result["n"] == expected_n, (
        f"n mismatch: got {result['n']}, expected {expected_n}"
    )
