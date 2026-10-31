from app.schemas import Features, FEATURE_ORDER
from app.classifier import _forensic_rules, _adjudicate


def test_fallback_labeled_and_valid():
    f = Features(days_since_last_commit=900, commit_cadence_decay=-3.0, lifespan_days=700,
                 contributor_count=4, bus_factor=2, velocity_ratio=0.0)
    v = _forensic_rules(f)
    assert v.engine == "rules"
    assert v.mode in {"abandoned", "pivoted", "completed", "burned_out", "alive"}
    assert 0.0 <= v.confidence <= 1.0


# ---- Tier B: feature vector shape + archived rule branch ----

def test_feature_order_includes_tier_b():
    for col in ("is_archived_flag", "release_recency_days", "has_releases", "open_issue_ratio"):
        assert col in FEATURE_ORDER
    # Every FEATURE_ORDER key must be constructible as a Features field.
    f = Features(days_since_last_commit=0, commit_cadence_decay=0, lifespan_days=0,
                 contributor_count=0, bus_factor=0, velocity_ratio=0)  # all Tier-B default 0.0
    for k in FEATURE_ORDER:
        assert isinstance(getattr(f, k), float)

def test_archived_with_releases_leans_completed():
    f = Features(days_since_last_commit=400, commit_cadence_decay=-0.2, lifespan_days=2000,
                 contributor_count=5, bus_factor=2, velocity_ratio=0.0,
                 is_archived_flag=1.0, has_releases=1.0)
    v = _forensic_rules(f)
    assert v.engine == "rules"
    assert v.mode == "completed"


# ---- Tier A adjudicator (TabPFN path only) ----

_TIE = {"abandoned": 0.45, "pivoted": 0.40, "completed": 0.15}   # gap 0.05 < 0.25
_CLEAR = {"abandoned": 0.80, "pivoted": 0.15, "completed": 0.05}  # gap 0.65


def test_tiezone_high_confidence_hint_overrides():
    hint = {"classification_hint": "pivoted", "hint_confidence": "high", "llm_offline": False}
    v = _adjudicate("abandoned", 0.45, _TIE, hint)
    assert v.mode == "pivoted"
    assert v.engine == "tabpfn+llm"
    assert v.confidence == _TIE["pivoted"]


def test_clear_winner_never_overridden():
    hint = {"classification_hint": "pivoted", "hint_confidence": "high", "llm_offline": False}
    v = _adjudicate("abandoned", 0.80, _CLEAR, hint)
    assert v.mode == "abandoned"
    assert v.engine == "tabpfn"


def test_offline_hint_no_tiebreak():
    hint = {"classification_hint": "none", "hint_confidence": "low", "llm_offline": True}
    v = _adjudicate("abandoned", 0.45, _TIE, hint)
    assert v.mode == "abandoned"
    assert v.engine == "tabpfn"


def test_hint_outside_top2_ignored():
    hint = {"classification_hint": "completed", "hint_confidence": "high", "llm_offline": False}
    v = _adjudicate("abandoned", 0.45, _TIE, hint)   # 'completed' is 3rd, not top-2
    assert v.mode == "abandoned"
    assert v.engine == "tabpfn"


def test_no_hint_keeps_tabpfn():
    v = _adjudicate("abandoned", 0.45, _TIE, None)
    assert v.engine == "tabpfn"


def test_medium_confidence_hint_in_tiezone_does_not_override():
    # Adjudicator override stays HIGH-only. A medium-confidence hint, even in the
    # tie-zone and in top-2, must NOT flip the verdict (engine stays "tabpfn").
    hint = {"classification_hint": "pivoted", "hint_confidence": "medium", "llm_offline": False}
    v = _adjudicate("abandoned", 0.45, _TIE, hint)
    assert v.mode == "abandoned"
    assert v.engine == "tabpfn"
