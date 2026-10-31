#!/usr/bin/env python3
"""Validate data/seed_repos.csv against Task-3 requirements.

Exit 0 + printed summary on pass.
Exit 1 on any violation with explanation.
"""
import sys
import pandas as pd
from app.schemas import FEATURE_ORDER

REQUIRED_ROWS = 100
REQUIRED_PER_CLASS = 15
TRAINING_MODES = {"alive", "completed", "abandoned", "burned_out", "pivoted"}

def main():
    path = "data/seed_repos.csv"
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"FAIL: {path} not found", file=sys.stderr)
        sys.exit(1)

    violations = []

    # (a) Every FEATURE_ORDER column present
    missing_cols = [c for c in FEATURE_ORDER if c not in df.columns]
    if missing_cols:
        violations.append(f"Missing FEATURE_ORDER columns: {missing_cols}")

    # (b) Row count >= 100
    if len(df) < REQUIRED_ROWS:
        violations.append(f"Row count {len(df)} < required {REQUIRED_ROWS}")

    # (c) Each training mode >= 15 rows
    counts = df["death_mode"].value_counts().to_dict()
    for mode in TRAINING_MODES:
        n = counts.get(mode, 0)
        if n < REQUIRED_PER_CLASS:
            violations.append(f"Class '{mode}' has {n} rows < required {REQUIRED_PER_CLASS}")

    # (d) No NaN/empty in FEATURE_ORDER columns (only check present cols)
    present_feat_cols = [c for c in FEATURE_ORDER if c in df.columns]
    if present_feat_cols:
        nan_cols = df[present_feat_cols].columns[df[present_feat_cols].isnull().any()].tolist()
        if nan_cols:
            violations.append(f"NaN values in feature columns: {nan_cols}")

    # (e) death_mode only in training modes (no 'insufficient_history' etc.)
    bad_modes = set(df["death_mode"].unique()) - TRAINING_MODES
    if bad_modes:
        violations.append(f"Non-training death_mode values found: {bad_modes}")

    # (f) No duplicate feature vectors (redirect-aliased repos produce byte-identical rows)
    if present_feat_cols:
        dup_mask = df.duplicated(subset=FEATURE_ORDER)
        if dup_mask.any():
            violations.append(
                f"Duplicate feature vectors ({int(dup_mask.sum())} rows): "
                f"{df[dup_mask]['owner_repo'].tolist()}"
            )

    if violations:
        print("FAIL — seed validation violations:")
        for v in violations:
            print(f"  • {v}")
        sys.exit(1)

    # Print summary
    print("PASS — seed_repos.csv is valid")
    print(f"  Total rows: {len(df)}")
    print(f"  Per-class distribution:")
    for mode in sorted(TRAINING_MODES):
        n = counts.get(mode, 0)
        print(f"    {mode:15s}: {n}")
    print(f"  Feature columns: {len(present_feat_cols)}/{len(FEATURE_ORDER)} ({present_feat_cols[0]}..{present_feat_cols[-1]})")
    sys.exit(0)


if __name__ == "__main__":
    main()
