"""Self-falsification: feed each honesty CLAIM a lie, assert the system refuses it.
A green suite that cannot go red proves nothing. These are the essay's load-bearing claims.
(conftest sets TABPFN_DISABLE=1 → classify() runs the labeled rules fallback.)"""
from app.schemas import Features, Verdict, RepoMeta
from app import classifier, narrator

def _f():
    return Features(days_since_last_commit=900, commit_cadence_decay=-3.0, lifespan_days=700,
                    contributor_count=1, bus_factor=1, velocity_ratio=0.0)

def test_claim_engine_badge_is_honest_on_fallback():
    """CLAIM: 'every verdict carries an honest engine badge.' LIE: a fallback that pretends tabpfn ran.
    With TabPFN unavailable, classify() MUST stamp engine in {rules, rules+llm} — never 'tabpfn'."""
    v = classifier.classify(_f(), hint=None)
    assert v.engine.startswith("rules"), f"fallback mislabeled as {v.engine!r} — decorative integration"
    assert "tabpfn" not in v.engine, "a rules fallback must NOT claim tabpfn (fake-tabpfn = lost category)"

def test_claim_grounding_rejects_fabricated_number():
    """CLAIM: 'the narrator never emits an ungrounded number.' LIE: a eulogy citing 99999 not in evidence."""
    ev = "commits: 10\nissues: 5\ndays since last commit: 900"
    liar = "This repository logged 99999 commits before its quiet death."
    assert narrator._grounded(liar, ev) is False, "ungrounded 99999 slipped past the grounding guard"

def test_claim_grounded_number_is_accepted():
    """Control: a number that IS in the evidence must be accepted (guard isn't vacuously rejecting all)."""
    ev = "commits: 10\nissues: 5\ndays since last commit: 900"
    honest = "After 900 days of silence, the last of 10 commits had long gone cold."
    assert narrator._grounded(honest, ev) is True, "grounding wrongly rejected a grounded eulogy"
