from __future__ import annotations
import functools
import math
from datetime import datetime, timezone
from collections import Counter
import numpy as np
from .github import RepoData
from .schemas import Features, RepoMeta

# No-release sentinel: a project with zero releases is maximally stale on the
# release axis. Labeled, not fabricated — it says "no release signal", distinct
# from the seed-median impute used only when the SIGNAL itself failed to fetch.
#
# BOUNDED, not open-ended. The old 9999.0 was ~7.6× the max real release_recency
# in the seed corpus (max non-sentinel = 4325 days), so it blew out TabPFN's scale
# for this axis. We bound it to 1.25× that max real value — still unambiguously
# "more stale than any real release", but on-scale so it no longer distorts the
# standardized distance / posterior. `has_releases=0.0` remains the real flag for
# the no-release case; this value just keeps the axis sane.
#   SENTINEL = round(1.25 * 4325) = 5406
# If the seed's max real release_recency changes materially, recompute this.
NO_RELEASE_RECENCY = 5406.0

def _parse(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except ValueError:
        return None

def _now() -> datetime:
    return datetime.now(timezone.utc)


@functools.lru_cache(maxsize=1)
def _seed_medians() -> dict[str, float]:
    # Median of each Tier-B feature over the labeled seed corpus. Used to impute
    # when a signal fails to fetch (None) — honest (it's the corpus center), never 0.
    import os, pandas as pd
    path = os.environ.get("SEED_PATH", "data/seed_repos.csv")
    df = pd.read_csv(path)
    cols = ["is_archived_flag", "release_recency_days", "has_releases", "open_issue_ratio"]
    return {c: float(df[c].median()) for c in cols if c in df.columns}


@functools.lru_cache(maxsize=1)
def _language_freq() -> dict[str, float]:
    # Fraction of seed rows per primary_language — used to frequency-encode
    # a repo's language at serve time (train==serve: same function, same seed).
    # Guard: if the seed is missing/empty OR lacks the primary_language column
    # (Task 3 adds it), return {} so every lookup yields honest 0.0.
    import os, pandas as pd
    path = os.environ.get("SEED_PATH", "data/seed_repos.csv")
    try:
        df = pd.read_csv(path)
    except Exception:
        return {}
    if "primary_language" not in df.columns or df.empty:
        return {}
    counts = df["primary_language"].value_counts(normalize=True)
    return dict(counts)


def _tier_c(data: RepoData) -> dict[str, float]:
    meta = data.meta
    log_stars    = round(math.log1p(meta.get("stars") or 0), 4)
    log_forks    = round(math.log1p(meta.get("forks_count") or 0), 4)
    log_watchers = round(math.log1p(meta.get("watchers_count") or 0), 4)
    topics_count = float(len(meta.get("topics") or []))
    readme_size  = float(len(data.readme or ""))
    description_present = 1.0 if (meta.get("description") or "").strip() else 0.0
    license_present     = 1.0 if meta.get("license_present") else 0.0
    has_wiki  = 1.0 if meta.get("has_wiki") else 0.0
    has_pages = 1.0 if meta.get("has_pages") else 0.0
    is_fork   = 1.0 if meta.get("fork") else 0.0
    freq = _language_freq()
    primary_language_freq = float(freq.get(meta.get("primary_language"), 0.0))
    return {
        "log_stars": log_stars,
        "log_forks": log_forks,
        "log_watchers": log_watchers,
        "topics_count": topics_count,
        "readme_size": readme_size,
        "description_present": description_present,
        "license_present": license_present,
        "has_wiki": has_wiki,
        "has_pages": has_pages,
        "is_fork": is_fork,
        "primary_language_freq": primary_language_freq,
    }


def _median(col: str, default: float) -> float:
    try:
        return _seed_medians().get(col, default)
    except Exception:
        return default


def _tier_b(data: RepoData, now: datetime) -> dict[str, float]:
    # is_archived: already in meta (0 extra calls). Others from Tier-B fetchers.
    # Honesty invariant: a signal that failed to fetch (None) -> seed-median impute,
    # never coerced to 0. A signal that is legitimately absent (no releases) -> its
    # labeled sentinel. The two cases are kept distinct.
    meta = data.meta
    is_archived_flag = 1.0 if meta.get("is_archived") else 0.0

    rc = meta.get("release_count")
    if rc is None:                                   # fetch failed -> impute
        has_releases = _median("has_releases", 0.0)
        release_recency = _median("release_recency_days", NO_RELEASE_RECENCY)
    elif rc <= 0:                                    # genuinely no releases -> sentinel
        has_releases = 0.0
        release_recency = NO_RELEASE_RECENCY
    else:
        has_releases = 1.0
        last_rel = _parse((meta.get("last_release_at") or "") + "T00:00:00+00:00"
                          if meta.get("last_release_at") else None)
        release_recency = float((now - last_rel).days) if last_rel else NO_RELEASE_RECENCY

    # open_issue_ratio = open / (open + closed). Impute from the seed median if
    # EITHER count failed to fetch (None): a partial fetch (e.g. open known, closed
    # missing) would otherwise fabricate an extreme ratio (1.0 or 0.0) from half the
    # data — worse than honestly admitting the signal is incomplete.
    # KNOWN LIMITATION: this signal is weak/near-flat (~0.98) across abandoned /
    # completed / alive in the seed corpus, so it carries little discriminative power.
    # Kept (not dropped) to avoid re-backfill churn; treat it as a soft signal.
    openc, closedc = meta.get("open_issues_count"), meta.get("closed_issues_count")
    if openc is None or closedc is None:             # either failed -> impute
        open_issue_ratio = _median("open_issue_ratio", 0.0)
    else:
        o = openc or 0
        total = o + (closedc or 0)
        open_issue_ratio = round(o / total, 4) if total > 0 else 0.0

    return {
        "is_archived_flag": is_archived_flag,
        "release_recency_days": round(release_recency, 1),
        "has_releases": has_releases,
        "open_issue_ratio": open_issue_ratio,
    }

def build_features(data: RepoData) -> tuple[Features, RepoMeta]:
    dates = sorted(d for d in (_parse(c["date"]) for c in data.commits) if d)
    if len(dates) < 2:
        raise ValueError("insufficient_history")
    first, last = dates[0], dates[-1]
    now = _now()
    days_since_last = (now - last).days
    lifespan_days = max((last - first).days, 1)

    # monthly commit counts → OLS slope (commits/month per month) = cadence decay
    month_key = lambda d: d.year * 12 + d.month
    months = Counter(month_key(d) for d in dates)
    ordered = sorted(months.items())
    xs = np.array([m for m, _ in ordered], dtype=float)
    ys = np.array([c for _, c in ordered], dtype=float)
    if len(xs) >= 2 and xs.std() > 0:
        slope = float(np.polyfit(xs - xs.mean(), ys, 1)[0])
    else:
        slope = 0.0

    authors = Counter(c["author"] for c in data.commits)
    contributor_count = float(len(authors))
    total = sum(authors.values())
    # bus factor: smallest set of authors whose cumulative share >= 50%
    bus, acc = 0, 0
    for _, n in authors.most_common():
        acc += n
        bus += 1
        if acc / total >= 0.5:
            break
    bus_factor = float(bus)

    # velocity ratio: recent 90d rate vs lifetime rate
    window_start = now.timestamp() - 90 * 86400
    recent = sum(1 for d in dates if d.timestamp() >= window_start)
    lifetime_rate_per_90 = total / max(lifespan_days / 90.0, 1e-9)
    velocity_ratio = float(recent / lifetime_rate_per_90) if lifetime_rate_per_90 > 0 else 0.0

    tb = _tier_b(data, now)
    tc = _tier_c(data)
    feats = Features(
        days_since_last_commit=float(days_since_last),
        commit_cadence_decay=round(slope, 3),
        lifespan_days=float(lifespan_days),
        contributor_count=contributor_count,
        bus_factor=bus_factor,
        velocity_ratio=round(velocity_ratio, 3),
        **tb,
        **tc,
    )
    meta = RepoMeta(
        stars=data.meta.get("stars", 0),
        primary_language=data.meta.get("primary_language"),
        created_at=data.meta.get("created_at"),
        last_commit_at=last.date().isoformat(),
        is_archived=data.meta.get("is_archived", False),
        open_issues_count=data.meta.get("open_issues_count"),
        release_count=data.meta.get("release_count"),
        last_release_at=data.meta.get("last_release_at"),
    )
    return feats, meta
