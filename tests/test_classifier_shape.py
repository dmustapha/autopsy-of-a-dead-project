from app.schemas import Features
from app.classifier import _forensic_rules


def test_fallback_labeled_and_valid():
    f = Features(days_since_last_commit=900, commit_cadence_decay=-3.0, lifespan_days=700,
                 contributor_count=4, bus_factor=2, velocity_ratio=0.0)
    v = _forensic_rules(f)
    assert v.engine == "rules"
    assert v.mode in {"abandoned", "pivoted", "completed", "burned_out", "alive"}
    assert 0.0 <= v.confidence <= 1.0
