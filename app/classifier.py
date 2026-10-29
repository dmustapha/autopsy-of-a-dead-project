from __future__ import annotations
import os, functools
import numpy as np
import pandas as pd
from .schemas import Features, Verdict, FEATURE_ORDER

SEED_PATH = os.environ.get("SEED_PATH", "data/seed_repos.csv")


@functools.lru_cache(maxsize=1)
def _seed() -> pd.DataFrame:
    return pd.read_csv(SEED_PATH)


def classify(f: Features) -> Verdict:
    seed = _seed()
    X_train, y_train = seed[FEATURE_ORDER], seed["death_mode"]
    row = [[getattr(f, k) for k in FEATURE_ORDER]]
    X_test = pd.DataFrame(row, columns=FEATURE_ORDER)
    try:
        from tabpfn_client import TabPFNClassifier, set_access_token
        token = os.environ.get("TABPFN_TOKEN")
        if not token:
            raise RuntimeError("TABPFN_TOKEN unset")   # → labeled rules fallback (I3), never a silent fake-tabpfn
        set_access_token(token)                        # authenticate the hosted client BEFORE fit (0.1.6 requires it)
        clf = TabPFNClassifier()
        clf.fit(X_train, y_train)
        proba = clf.predict_proba(X_test)[0]
        classes = list(clf.classes_)
        idx = int(proba.argmax())
        return Verdict(
            mode=classes[idx],
            confidence=float(proba[idx]),
            probs={c: float(p) for c, p in zip(classes, proba)},
            engine="tabpfn",
        )
    except Exception:
        return _forensic_rules(f)


def _forensic_rules(f: Features) -> Verdict:
    # transparent heuristic fallback — ALWAYS labeled engine="rules"
    if f.days_since_last_commit > 365 and f.velocity_ratio < 0.1:
        mode = "abandoned"
    elif f.commit_cadence_decay < -2 and f.bus_factor == 1:
        mode = "burned_out"
    elif f.lifespan_days < 120 and f.velocity_ratio < 0.2:
        mode = "pivoted"
    elif f.velocity_ratio >= 0.8:
        mode = "alive"
    else:
        mode = _nearest_mode(f)        # 1-NN over the seed corpus (II.26) — never a hard-coded "completed"
    return Verdict(mode=mode, confidence=0.4, probs={mode: 0.4}, engine="rules")


def _nearest_mode(f) -> str:
    # 1-NN on standardized seed features — the fallback still reflects the labeled corpus (honest, labeled rules)
    seed = _seed()
    X = seed[FEATURE_ORDER].to_numpy(dtype=float)
    mu, sd = X.mean(0), X.std(0) + 1e-9
    q = (np.array([getattr(f, k) for k in FEATURE_ORDER], dtype=float) - mu) / sd
    Xs = (X - mu) / sd
    i = int(np.argmin(((Xs - q) ** 2).sum(1)))
    return str(seed["death_mode"].iloc[i])
