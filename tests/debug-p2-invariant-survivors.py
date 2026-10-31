"""debug Phase 2 — INVARIANTS-survivor dispositions, each gated by a test.

Every survivor from INVARIANTS.md "Survivors from the A-G4 critical review" that is
mechanically checkable gets an assertion here so its disposition (CLEARED / HARDENED /
ACCEPTED) cannot silently regress. Feature-separability survivors are statistical and
ACCEPTED-by-design (reported honestly in the post, not code-fixable) — see DEBUG-REPORT.md.
"""
import inspect
import os
import re

from app import classifier, main, narrator
from app.schemas import Features


def _cases():
    return [
        Features(days_since_last_commit=900, commit_cadence_decay=-3, lifespan_days=700,
                 contributor_count=4, bus_factor=1, velocity_ratio=0.0),   # abandoned branch
        Features(days_since_last_commit=10, commit_cadence_decay=-5, lifespan_days=400,
                 contributor_count=1, bus_factor=1, velocity_ratio=0.3),   # burned_out branch
        Features(days_since_last_commit=5, commit_cadence_decay=0, lifespan_days=60,
                 contributor_count=2, bus_factor=1, velocity_ratio=0.1),   # pivoted branch
        Features(days_since_last_commit=1, commit_cadence_decay=1, lifespan_days=300,
                 contributor_count=10, bus_factor=3, velocity_ratio=0.9),  # alive branch
        Features(days_since_last_commit=200, commit_cadence_decay=0, lifespan_days=300,
                 contributor_count=3, bus_factor=2, velocity_ratio=0.5),   # else -> 1-NN
    ]


def test_rules_fallback_always_labeled():
    """HARDENED/CLEARED: every rules branch stamps engine='rules' — never a silent fake-tabpfn."""
    for c in _cases():
        v = classifier._forensic_rules(c)
        assert v.engine == "rules", f"engine leak on {c}: {v}"
        assert 0.0 <= v.confidence <= 1.0


def test_missing_token_degrades_to_labeled_rules(monkeypatch):
    """CLEARED (I2/I3): no TABPFN_TOKEN -> classify() returns engine='rules', never 'tabpfn'."""
    monkeypatch.delenv("TABPFN_TOKEN", raising=False)
    v = classifier.classify(_cases()[0])
    assert v.engine == "rules"


def test_healthz_is_token_presence_proxy_only():
    """ACCEPTED (documented): tabpfn_reachable is a token-presence proxy, not a model probe.
    The real proof is a live /autopsy returning engine=tabpfn (livetest), not /healthz."""
    src = inspect.getsource(main.healthz)
    assert "TABPFN_TOKEN" in src
    assert "predict" not in src and ".fit(" not in src  # not a real model round-trip


def test_classifier_references_no_missing_feature_fields():
    """CLEARED: every f.<field> a rule reads must exist on Features (a referenced-but-absent
    field is a silently-dead rule). Tier B legitimately added is_archived_flag/has_releases."""
    src = inspect.getsource(classifier)
    assert "total_commits" not in src          # never existed on Features
    referenced = set(re.findall(r"\bf\.([a-z_]+)\b", src))
    valid = set(Features.model_fields)
    assert referenced <= valid, f"rule reads missing field(s): {referenced - valid}"


def test_no_hardcoded_secrets_in_core_modules():
    """Phase 4 (I10): tokens come only from os.environ — no literal sk-/gsk_ secret in core."""
    from app import github
    for mod in (classifier, narrator, github, main):
        s = inspect.getsource(mod)
        assert not re.findall(r"sk-[A-Za-z0-9]{10,}|gsk_[A-Za-z0-9]{10,}", s)


def test_placeholder_api_key_is_harmless():
    """Phase 4: the openai client's placeholder api_key='ollama' + localhost base_url is
    a non-secret keyless-Gemma default, not a leaked credential."""
    src = inspect.getsource(narrator._client)
    assert '"ollama"' in src
    assert "localhost:11434" in src
