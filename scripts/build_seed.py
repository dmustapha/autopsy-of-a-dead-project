#!/usr/bin/env python3
"""Build data/seed_repos.csv from scripts/seed_list.txt using the SAME feature extractor as production.

Two-pass build (RULING R1):
  Pass 1 — fetch each repo via fetch_repo + build_features (the PROD path); capture
            meta.primary_language so the CSV gets a raw `primary_language` column.
            primary_language_freq will be 0.0 in this pass (the column doesn't exist yet).
  Pass 2 — reuse app.features._language_freq() pointed at the just-written file to
            back-fill primary_language_freq for every row (train==serve: identical function).

Usage: python scripts/build_seed.py  (requires GITHUB_TOKEN for rate-limit headroom)
"""
import asyncio
import csv
import os
import sys

from app.github import fetch_repo
from app.features import build_features
from app.schemas import FEATURE_ORDER

# CSV columns: FEATURE_ORDER includes primary_language_freq; we also store the raw
# primary_language string so _language_freq() can compute frequencies post-pass.
COLS = ["owner_repo", *FEATURE_ORDER, "primary_language", "death_mode", "note"]

CSV_PATH = "data/seed_repos.csv"


async def fetch_one(owner_repo: str) -> tuple[dict, str | None]:
    """Return (feat_dict, primary_language). Raises on fetch failure."""
    owner, repo = owner_repo.split("/", 1)
    data = await fetch_repo(owner, repo)
    feats, meta = build_features(data)
    feat_dict = {k: getattr(feats, k) for k in FEATURE_ORDER}
    return feat_dict, meta.primary_language


async def main():
    # ---- PASS 1: fetch all repos, write CSV with primary_language column ----
    rows = []
    for line in open("scripts/seed_list.txt"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        slug, mode, note = [p.strip() for p in line.split(",", 2)]
        try:
            feat_dict, primary_language = await fetch_one(slug)
            rows.append({
                "owner_repo": slug,
                **feat_dict,
                "primary_language": primary_language,
                "death_mode": mode,
                "note": note,
            })
            print(f"ok  {slug} -> {mode}")
        except Exception as e:
            print(f"ERR {slug}: {e}", file=sys.stderr)

    # Write CSV after pass 1 (primary_language_freq values are 0.0 from the guard)
    with open(CSV_PATH, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nPass 1: wrote {len(rows)} rows to {CSV_PATH}")

    # ---- PASS 2: back-fill primary_language_freq using the serve function ----
    # The CSV now has a primary_language column, so _language_freq() will return
    # a real frequency map. We reuse the IDENTICAL function used at serve time.
    import app.features as F
    F._language_freq.cache_clear()
    # Point at the just-written file (default SEED_PATH already points here, but be explicit)
    os.environ["SEED_PATH"] = CSV_PATH
    F._language_freq.cache_clear()

    freq_map = F._language_freq()
    filled = 0
    for row in rows:
        new_freq = float(freq_map.get(row["primary_language"], 0.0))
        if new_freq != row["primary_language_freq"]:
            filled += 1
        row["primary_language_freq"] = new_freq

    # Rewrite CSV with corrected primary_language_freq
    with open(CSV_PATH, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"Pass 2: back-filled primary_language_freq for {filled} rows")
    print(f"  Language freq map has {len(freq_map)} entries: {dict(list(freq_map.items())[:5])} ...")
    print(f"\nTotal rows written: {len(rows)}")


if __name__ == "__main__":
    asyncio.run(main())
