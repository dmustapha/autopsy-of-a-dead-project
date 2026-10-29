from __future__ import annotations
from datetime import datetime, timezone
from collections import Counter
import numpy as np
from .github import RepoData
from .schemas import Features, RepoMeta

def _parse(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except ValueError:
        return None

def _now() -> datetime:
    return datetime.now(timezone.utc)

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

    feats = Features(
        days_since_last_commit=float(days_since_last),
        commit_cadence_decay=round(slope, 3),
        lifespan_days=float(lifespan_days),
        contributor_count=contributor_count,
        bus_factor=bus_factor,
        velocity_ratio=round(velocity_ratio, 3),
    )
    meta = RepoMeta(
        stars=data.meta.get("stars", 0),
        primary_language=data.meta.get("primary_language"),
        created_at=data.meta.get("created_at"),
        last_commit_at=last.date().isoformat(),
        is_archived=data.meta.get("is_archived", False),
    )
    return feats, meta
