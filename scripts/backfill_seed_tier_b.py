"""One-off backfill: ADD the 4 Tier-B feature columns to data/seed_repos.csv.

CRITICAL: this NEVER overwrites the existing 6 feature columns, death_mode, or
note — those are curated ground truth. It only APPENDS:
  is_archived_flag, release_recency_days, has_releases, open_issue_ratio
inserted after velocity_ratio, leaving death_mode,note last.

Fetches ONLY the new signals per repo (archived flag from repo meta, releases,
closed-issue count) — ~2 calls/repo. A repo that 404s now keeps its original row
and gets the seed-median sentinel for the new columns (noted on stderr).
"""
from __future__ import annotations
import asyncio, csv, os, sys, statistics
import httpx
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.github import _headers, _fetch_release_signals, _fetch_closed_issue_count, API
from app.features import NO_RELEASE_RECENCY
from datetime import datetime, timezone

CSV_PATH = os.environ.get("SEED_PATH", "data/seed_repos.csv")
NEW_COLS = ["is_archived_flag", "release_recency_days", "has_releases", "open_issue_ratio"]


async def fetch_signals(client: httpx.AsyncClient, owner: str, repo: str):
    """Return (archived, open_issues, release_count, last_release_at, closed_issues) or None on 404."""
    r = await client.get(f"{API}/repos/{owner}/{repo}")
    if r.status_code == 404:
        return None
    r.raise_for_status()
    meta = r.json()
    rc, last_rel = await _fetch_release_signals(client, owner, repo)
    closed = await _fetch_closed_issue_count(client, owner, repo)
    return (bool(meta.get("archived")), meta.get("open_issues_count"), rc, last_rel, closed)


def compute(sig) -> dict[str, float]:
    archived, openc, rc, last_rel, closedc = sig
    now = datetime.now(timezone.utc)
    is_archived_flag = 1.0 if archived else 0.0
    if rc is None:
        has_releases, release_recency = None, None            # impute later
    elif rc <= 0:
        has_releases, release_recency = 0.0, NO_RELEASE_RECENCY
    else:
        has_releases = 1.0
        if last_rel:
            d = datetime.fromisoformat(last_rel + "T00:00:00+00:00")
            release_recency = float((now - d).days)
        else:
            release_recency = NO_RELEASE_RECENCY
    if openc is None and closedc is None:
        open_issue_ratio = None                               # impute later
    else:
        o, total = (openc or 0), (openc or 0) + (closedc or 0)
        open_issue_ratio = round(o / total, 4) if total > 0 else 0.0
    return {"is_archived_flag": is_archived_flag, "release_recency_days": release_recency,
            "has_releases": has_releases, "open_issue_ratio": open_issue_ratio}


async def main():
    with open(CSV_PATH, newline="") as fh:
        rows = list(csv.DictReader(fh))
    orig_fields = list(rows[0].keys())
    assert not any(c in orig_fields for c in NEW_COLS), "new columns already present — refusing to re-run"

    computed, sentinels = [], []
    async with httpx.AsyncClient(timeout=15.0, headers=_headers(), follow_redirects=True) as client:
        for row in rows:
            owner, repo = row["owner_repo"].split("/", 1)
            try:
                sig = await fetch_signals(client, owner, repo)
            except Exception as e:
                sig = None
                print(f"  ! {owner}/{repo}: fetch error {e}", file=sys.stderr)
            if sig is None:
                computed.append({c: None for c in NEW_COLS})
                sentinels.append(row["owner_repo"])
            else:
                computed.append(compute(sig))
            print(f"  . {owner}/{repo}", file=sys.stderr)

    # Impute Nones (fetch-failed signals) from the median of successfully-fetched rows.
    for col in NEW_COLS:
        vals = [c[col] for c in computed if c[col] is not None]
        med = statistics.median(vals) if vals else 0.0
        for c in computed:
            if c[col] is None:
                c[col] = med

    # Rewrite: insert new cols after velocity_ratio, keep death_mode,note last.
    vi = orig_fields.index("velocity_ratio")
    new_fields = orig_fields[:vi + 1] + NEW_COLS + orig_fields[vi + 1:]
    with open(CSV_PATH, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=new_fields)
        w.writeheader()
        for row, extra in zip(rows, computed):
            row.update({k: round(float(v), 4) for k, v in extra.items()})
            w.writerow(row)

    print(f"\nDONE: {len(rows)} rows, +{len(NEW_COLS)} cols. Sentinel-imputed (404/fail): "
          f"{sentinels or 'none'}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
