from datetime import datetime, timezone, timedelta
from app.github import RepoData
from app.features import build_features

def _commit(days_ago, author):
    d = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return {"date": d, "author": author}

def test_bus_factor_and_recency():
    # one dominant author over 2 others
    commits = [_commit(400, "a") for _ in range(8)] + [_commit(410, "b"), _commit(420, "c")]
    data = RepoData(owner="o", repo="r", commits=commits, contributors=[], meta={})
    f, _ = build_features(data)
    assert f.bus_factor == 1.0            # 'a' alone is >=50%
    assert f.contributor_count == 3.0
    assert f.days_since_last_commit >= 395

def test_alive_velocity():
    commits = [_commit(i, "a") for i in range(0, 80, 2)]  # frequent, recent
    data = RepoData(owner="o", repo="r", commits=commits, contributors=[], meta={})
    f, _ = build_features(data)
    assert f.velocity_ratio > 0.5
