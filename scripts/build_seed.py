#!/usr/bin/env python3
"""Build data/seed_repos.csv from scripts/seed_list.txt using the SAME feature extractor as production.
Usage: python scripts/build_seed.py  (requires GITHUB_TOKEN recommended for rate limit)."""
import asyncio, csv, sys
from app.github import fetch_repo
from app.features import build_features
from app.schemas import FEATURE_ORDER

async def one(owner_repo: str):
    owner, repo = owner_repo.split("/", 1)
    data = await fetch_repo(owner, repo)
    feats, _ = build_features(data)
    return {k: getattr(feats, k) for k in FEATURE_ORDER}

async def main():
    rows = []
    for line in open("scripts/seed_list.txt"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        slug, mode, note = [p.strip() for p in line.split(",", 2)]
        try:
            feats = await one(slug)
            rows.append({"owner_repo": slug, **feats, "death_mode": mode, "note": note})
            print(f"ok  {slug} -> {mode}")
        except Exception as e:
            print(f"ERR {slug}: {e}", file=sys.stderr)
    cols = ["owner_repo", *FEATURE_ORDER, "death_mode", "note"]
    with open("data/seed_repos.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"\nwrote {len(rows)} rows to data/seed_repos.csv")
    # quick LOO separability check
    try:
        import pandas as pd
        from tabpfn_client import TabPFNClassifier
        df = pd.read_csv("data/seed_repos.csv")
        correct = 0
        for i in range(len(df)):
            tr = df.drop(i); te = df.iloc[[i]]
            clf = TabPFNClassifier(); clf.fit(tr[FEATURE_ORDER], tr["death_mode"])
            pred = clf.predict(te[FEATURE_ORDER])[0]
            correct += int(pred == te["death_mode"].iloc[0])
        print(f"LOO accuracy: {correct}/{len(df)} = {correct/len(df):.0%}")
    except Exception as e:
        print(f"(LOO check skipped: {e})")

if __name__ == "__main__":
    asyncio.run(main())
