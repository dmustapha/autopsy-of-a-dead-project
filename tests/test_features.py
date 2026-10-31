import math
from datetime import datetime, timezone, timedelta
from app.github import RepoData
from app.features import build_features, NO_RELEASE_RECENCY
from app.schemas import FEATURE_ORDER

def _commit(days_ago, author, message="chore: update"):
    d = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return {"date": d, "author": author, "message": message}

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


# ---- Tier B: richer feature vector ----

def _repo(meta):
    commits = [_commit(400, "a"), _commit(500, "a"), _commit(600, "b")]
    return RepoData(owner="o", repo="r", commits=commits, contributors=[], meta=meta)

def test_tier_b_archived_and_releases():
    f, m = build_features(_repo({
        "is_archived": True, "release_count": 3, "last_release_at": "2020-01-01",
        "open_issues_count": 5, "closed_issues_count": 15}))
    assert f.is_archived_flag == 1.0
    assert f.has_releases == 1.0
    assert f.release_recency_days > 1000          # old release -> stale
    assert abs(f.open_issue_ratio - 0.25) < 1e-6  # 5 / (5+15)
    assert m.release_count == 3 and m.open_issues_count == 5

def test_tier_b_no_releases_sentinel():
    f, _ = build_features(_repo({"release_count": 0, "open_issues_count": 0,
                                 "closed_issues_count": 0}))
    assert f.has_releases == 0.0
    assert f.release_recency_days == NO_RELEASE_RECENCY  # BOUNDED no-release sentinel (5406, not 9999)
    assert NO_RELEASE_RECENCY == 5406.0           # pin the documented constant
    assert f.open_issue_ratio == 0.0              # no issues -> 0, not a crash


def test_tier_b_partial_issue_counts_impute():
    # EITHER count missing -> impute from seed median, never fabricate an extreme
    # 1.0/0.0 ratio from half the data. Here closed is absent (partial fetch fail).
    f, _ = build_features(_repo({"release_count": 2, "last_release_at": "2022-01-01",
                                 "open_issues_count": 7, "closed_issues_count": None}))
    # 7 open with closed unknown would fabricate 1.0; imputation must avoid that.
    assert f.open_issue_ratio != 1.0
    assert 0.0 <= f.open_issue_ratio <= 1.0

def test_tier_b_missing_meta_imputes_not_crash():
    # Signals absent (None) -> seed-median impute, never 0, never crash.
    f, m = build_features(_repo({}))
    assert f.is_archived_flag == 0.0              # absent archived -> not archived
    assert f.release_recency_days >= 0.0          # imputed from seed median
    assert m.release_count is None               # honest: not fetched


# ---- Tier C: log-popularity / topics / readme / flags / language-freq ----

def _repo_c(meta, readme=None):
    commits = [_commit(400, "a"), _commit(500, "a"), _commit(600, "b")]
    return RepoData(owner="o", repo="r", commits=commits, contributors=[], meta=meta, readme=readme)

def test_build_features_emits_full_enriched_vector():
    readme = "x" * 300
    meta = {
        "stars": 100, "forks_count": 10, "watchers_count": 50,
        "topics": ["a", "b"], "size": 200,
        "has_wiki": True, "has_pages": False, "fork": False,
        "license_present": True, "description": "x",
    }
    f, _ = build_features(_repo_c(meta, readme=readme))

    assert f.log_stars == round(math.log1p(100), 4)
    assert f.log_forks == round(math.log1p(10), 4)
    assert f.log_watchers == round(math.log1p(50), 4)
    assert f.topics_count == 2.0
    assert f.readme_size == 300.0
    assert f.description_present == 1.0
    assert f.license_present == 1.0
    assert f.has_wiki == 1.0
    assert f.has_pages == 0.0
    assert f.is_fork == 0.0
    # primary_language_freq: seed has no primary_language col yet -> honest 0.0 (guard fires)
    assert isinstance(f.primary_language_freq, float)

    # Full vector has no None entries
    vector = [getattr(f, k) for k in FEATURE_ORDER]
    assert len(vector) == len(FEATURE_ORDER)
    assert all(v is not None for v in vector)


def test_enriched_features_empty_inputs_are_zero_not_crash():
    # No topics/license/description, readme=None -> honest 0.0, never crash
    f, _ = build_features(_repo_c({}, readme=None))
    assert f.topics_count == 0.0
    assert f.readme_size == 0.0
    assert f.description_present == 0.0
    assert f.license_present == 0.0
    # Full vector still full-length, no None entries
    vector = [getattr(f, k) for k in FEATURE_ORDER]
    assert len(vector) == len(FEATURE_ORDER)
    assert all(v is not None for v in vector)
