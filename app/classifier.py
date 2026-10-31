from __future__ import annotations
import os, functools
import numpy as np
import pandas as pd
from .schemas import Features, Verdict, FEATURE_ORDER

SEED_PATH = os.environ.get("SEED_PATH", "data/seed_repos.csv")


@functools.lru_cache(maxsize=1)
def _seed() -> pd.DataFrame:
    df = pd.read_csv(SEED_PATH)
    # Forward-compat: fill any FEATURE_ORDER columns not yet in the seed with 0.0.
    # Task 3 adds Tier-C columns; until then the 1-NN / TabPFN still operate on
    # the existing columns and treat the new ones as neutral (0.0 = honest empty).
    for col in FEATURE_ORDER:
        if col not in df.columns:
            df[col] = 0.0
    return df


TIE_ZONE = 0.25   # max(probs) - 2nd-max below this = the adjudicator's window


@functools.lru_cache(maxsize=1)
def _tabpfn_clf():
    # LOCAL open-weight TabPFN — on-device inference, NO hosted Prior Labs 503 dependency.
    # In-context learning: load the pretrained weights once and fit() = hand it the seed as
    # context; every predict is then a fast forward pass. Cached so the ~GB model loads once
    # per process (the startup prewarm warms it). Disable in tests via TABPFN_DISABLE=1.
    if os.environ.get("TABPFN_DISABLE") == "1":
        raise RuntimeError("TabPFN disabled (test mode) -> labeled rules fallback")
    from tabpfn import TabPFNClassifier
    seed = _seed()
    clf = TabPFNClassifier()
    clf.fit(seed[FEATURE_ORDER], seed["death_mode"])
    return clf


def classify(f: Features, hint: dict | None = None) -> Verdict:
    row = [[getattr(f, k) for k in FEATURE_ORDER]]
    X_test = pd.DataFrame(row, columns=FEATURE_ORDER)
    try:
        clf = _tabpfn_clf()
        proba = clf.predict_proba(X_test)[0]
        classes = list(clf.classes_)
        probs = {c: float(p) for c, p in zip(classes, proba)}
        idx = int(proba.argmax())
        return _adjudicate(classes[idx], float(proba[idx]), probs, hint)
    except Exception:
        return _adjudicate_rules(_forensic_rules(f), hint)   # labeled rules fallback (I3)


_VALID_MODES = {"abandoned", "pivoted", "completed", "burned_out", "alive", "insufficient_history"}


def _adjudicate_rules(v: Verdict, hint: dict | None) -> Verdict:
    # When TabPFN is down, rules is a CRUDE heuristic. A HIGH-confidence LLM reading of the
    # repo's own death-note (commit messages / README) is stronger evidence than the
    # heuristic, so it may override — labeled engine="rules+llm" (honest about what ran).
    # Offline/low/medium hint => rules stands unchanged. Agreement => no relabel.
    if hint and not hint.get("llm_offline") and hint.get("hint_confidence") == "high":
        h = hint.get("classification_hint")
        if h in _VALID_MODES and h != v.mode:
            return Verdict(mode=h, confidence=0.5, probs={h: 0.5}, engine="rules+llm")
    return v


def _adjudicate(mode: str, confidence: float, probs: dict[str, float], hint: dict | None) -> Verdict:
    # LLM-as-adjudicator: only in the tie-zone, only on a HIGH-confidence hint that is
    # already one of TabPFN's top-2 modes. Otherwise TabPFN's argmax stands (engine="tabpfn").
    # Honesty invariant: offline/low-confidence hint => no tie-break, no engine relabel.
    if hint and hint.get("hint_confidence") == "high":
        ranked = sorted(probs.values(), reverse=True)
        gap = ranked[0] - ranked[1] if len(ranked) >= 2 else 1.0
        top2 = {c for c, _ in sorted(probs.items(), key=lambda kv: kv[1], reverse=True)[:2]}
        h = hint.get("classification_hint")
        if gap < TIE_ZONE and h in top2:
            return Verdict(mode=h, confidence=probs[h], probs=probs, engine="tabpfn+llm")
    return Verdict(mode=mode, confidence=confidence, probs=probs, engine="tabpfn")


def _forensic_rules(f: Features) -> Verdict:
    # transparent heuristic fallback — ALWAYS labeled engine="rules"
    # Tier B: an archived repo that went quiet is a deliberate end-of-life — lean
    # completed (shipped & sealed) if it ever cut releases, else abandoned.
    if f.is_archived_flag >= 1.0 and f.days_since_last_commit > 180 and f.velocity_ratio < 0.1:
        mode = "completed" if f.has_releases >= 1.0 else "abandoned"
    elif f.days_since_last_commit > 365 and f.velocity_ratio < 0.1:
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


def nearest_cohort(f, k: int = 5) -> dict:
    # k-NN over the SAME standardized seed corpus as _nearest_mode — "died like N of k similar repos".
    # Pure corpus lookup (no API, no model); honest — it reports what the labeled seed actually holds.
    seed = _seed()
    X = seed[FEATURE_ORDER].to_numpy(dtype=float)
    k = max(1, min(k, len(seed)))
    mu, sd = X.mean(0), X.std(0) + 1e-9
    q = (np.array([getattr(f, kk) for kk in FEATURE_ORDER], dtype=float) - mu) / sd
    Xs = (X - mu) / sd
    idx = np.argsort(((Xs - q) ** 2).sum(1))[:k]
    modes = [str(m) for m in seed["death_mode"].iloc[idx].tolist()]
    neighbors = [str(r) for r in seed["owner_repo"].iloc[idx].tolist()]
    dominant = max(set(modes), key=modes.count)
    return {"dominant_mode": dominant, "cohort_size": int(k),
            "matching": modes.count(dominant), "neighbors": neighbors}
