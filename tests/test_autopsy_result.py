"""
Task 6 — project_summary field wired through AutopsyResult.

Tests:
  1. Schema is backward-safe: old cached shape (no project_summary) still validates.
  2. Schema accepts the new field.
  3. _project_summary helper: NOT confidence-gated; offline → None; empty → None.
"""
import pytest
from app.schemas import AutopsyResult, RepoMeta, Features, Verdict


# ---------------------------------------------------------------------------
# Minimal fixtures — enough to construct AutopsyResult without a real run.
# ---------------------------------------------------------------------------

def _meta() -> RepoMeta:
    return RepoMeta()


def _features() -> Features:
    return Features(
        days_since_last_commit=365,
        commit_cadence_decay=0.1,
        lifespan_days=700,
        contributor_count=1,
        bus_factor=1,
        velocity_ratio=0.05,
    )


def _verdict() -> Verdict:
    return Verdict(mode="abandoned", confidence=0.9, probs={"abandoned": 0.9}, engine="rules")


def _base_kwargs() -> dict:
    return dict(
        owner="acme",
        repo="old-thing",
        meta=_meta(),
        features=_features(),
        verdict=_verdict(),
        narration="It died quietly.",
        certificate_id="abc123",
    )


# ---------------------------------------------------------------------------
# 1. Backward-safe: old shape (no project_summary) still validates.
# ---------------------------------------------------------------------------

def test_autopsy_result_old_shape_no_project_summary():
    result = AutopsyResult(**_base_kwargs())
    assert result.project_summary is None


# ---------------------------------------------------------------------------
# 2. New field accepted.
# ---------------------------------------------------------------------------

def test_autopsy_result_accepts_project_summary():
    result = AutopsyResult(**_base_kwargs(), project_summary="A bundler.")
    assert result.project_summary == "A bundler."


# ---------------------------------------------------------------------------
# 3. _project_summary helper behaviour — import directly from main.
# ---------------------------------------------------------------------------

from app.main import _project_summary  # noqa: E402  (import after schema tests pass)


def test_project_summary_live_low_confidence_not_gated():
    """NOT confidence-gated: low hint still returns the summary."""
    hint = {"llm_offline": False, "project_summary": "X", "hint_confidence": "low"}
    assert _project_summary(hint) == "X"


def test_project_summary_live_medium_confidence():
    hint = {"llm_offline": False, "project_summary": "A build tool.", "hint_confidence": "medium"}
    assert _project_summary(hint) == "A build tool."


def test_project_summary_offline_returns_none():
    hint = {"llm_offline": True, "project_summary": "X"}
    assert _project_summary(hint) is None


def test_project_summary_empty_string_returns_none():
    hint = {"llm_offline": False, "project_summary": ""}
    assert _project_summary(hint) is None


def test_project_summary_whitespace_returns_none():
    hint = {"llm_offline": False, "project_summary": "   "}
    assert _project_summary(hint) is None


def test_project_summary_missing_key_returns_none():
    hint = {"llm_offline": False}
    assert _project_summary(hint) is None


def test_project_summary_none_key_returns_none():
    hint = {"llm_offline": False, "project_summary": None}
    assert _project_summary(hint) is None
