"""
LOO evaluation: TabPFN LOO vs standardized 1-NN LOO on the same enriched features.

Outputs JSON: {"tabpfn_loo": float|null, "onenn_loo": float, "n": int, "tabpfn_beats_1nn": bool}

When TABPFN_DISABLE=1: skips TabPFN loop → tabpfn_loo=null, tabpfn_beats_1nn=false.

1-NN LOO uses IDENTICAL standardization as app/classifier.py::_nearest_mode:
  mu, sd = fold.mean(0), fold.std(0) + 1e-9
  query_std = (query - mu) / sd
  closest = argmin(sum_sq_distance)  → label

Both loops operate on the same FEATURE_ORDER and same df rows.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Project root on the path when run as a script
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from app.schemas import FEATURE_ORDER

SEED_CSV = _ROOT / "data" / "seed_repos.csv"


def _onenn_loo_predict(tr: np.ndarray, te: np.ndarray) -> int:
    """Return the 1-NN label index given training matrix tr and 1-row test te.

    Replicates app/classifier.py::_nearest_mode exactly:
      mu, sd = tr.mean(0), tr.std(0) + 1e-9
      Xs = (tr - mu) / sd  ;  q = (te - mu) / sd
      i = argmin(((Xs - q)**2).sum(1))
    """
    mu = tr.mean(0)
    sd = tr.std(0) + 1e-9
    Xs = (tr - mu) / sd
    q = (te - mu) / sd
    return int(np.argmin(((Xs - q) ** 2).sum(1)))


def main() -> dict:
    """Run LOO evaluation and return result dict (also printed as JSON)."""
    df = pd.read_csv(SEED_CSV)
    n = len(df)
    labels = df["death_mode"].to_numpy()
    X = df[FEATURE_ORDER].to_numpy(float)

    tabpfn_disable = os.environ.get("TABPFN_DISABLE", "0") == "1"

    # ── 1-NN LOO ──────────────────────────────────────────────────────────────
    onenn_correct = 0
    for i in range(n):
        tr_idx = [j for j in range(n) if j != i]
        tr_X = X[tr_idx]
        te_X = X[i : i + 1]  # shape (1, F)
        nn_idx = _onenn_loo_predict(tr_X, te_X)
        pred_label = labels[tr_idx[nn_idx]]
        if pred_label == labels[i]:
            onenn_correct += 1

    onenn_loo = onenn_correct / n

    # ── TabPFN LOO ─────────────────────────────────────────────────────────────
    tabpfn_loo = None
    if not tabpfn_disable:
        from tabpfn import TabPFNClassifier

        tabpfn_correct = 0
        tr_labels_list = [labels[[j for j in range(n) if j != i]] for i in range(n)]
        for i in range(n):
            tr_idx = [j for j in range(n) if j != i]
            tr_X = X[tr_idx]
            tr_y = labels[tr_idx]
            te_X = X[i : i + 1]

            clf = TabPFNClassifier()
            clf.fit(tr_X, tr_y)
            pred = clf.predict(te_X)[0]
            if pred == labels[i]:
                tabpfn_correct += 1

        tabpfn_loo = tabpfn_correct / n

    tabpfn_beats_1nn = (tabpfn_loo is not None) and (tabpfn_loo > onenn_loo)

    result = {
        "tabpfn_loo": tabpfn_loo,
        "onenn_loo": onenn_loo,
        "n": n,
        "tabpfn_beats_1nn": tabpfn_beats_1nn,
    }

    print(json.dumps(result))
    if tabpfn_loo is not None:
        winner = "TabPFN" if tabpfn_beats_1nn else "1-NN"
        print(
            f"TabPFN LOO: {tabpfn_loo:.4f}  |  1-NN LOO: {onenn_loo:.4f}  |  "
            f"n={n}  |  winner={winner}"
        )
    else:
        print(
            f"1-NN LOO: {onenn_loo:.4f}  |  n={n}  "
            f"(TabPFN disabled — set TABPFN_DISABLE=0 to run full eval)"
        )

    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
