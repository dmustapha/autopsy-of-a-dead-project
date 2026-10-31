"""P5 grounding registers: cross-field digit-smuggle must be rejected.

The grounding guarantee is that the LLM eulogy may contain NO numeric value
absent from the SEMANTIC numbers of the evidence block. The old check built
its allowed-set from arbitrary 2+-digit runs, which let stray digits sliced
out of dates ("2021-03-02" -> 2021/03/02) and the confidence percentage
("80%") whitelist unrelated false claims.

These tests pin the registers: ATTACK1/2/3 must fall back to the template,
and a legitimately grounded eulogy must still pass through untouched.
"""
from app.schemas import Features, Verdict, RepoMeta
from app import narrator


def _fixture():
    f = Features(days_since_last_commit=800, commit_cadence_decay=-3.0, lifespan_days=530,
                 contributor_count=2, bus_factor=1, velocity_ratio=0.04)
    v = Verdict(mode="abandoned", confidence=0.8, probs={"abandoned": 0.8}, engine="tabpfn")
    m = RepoMeta(stars=10, created_at="2021-03-02", last_commit_at="2022-08-14")
    return f, v, m


def _fake_llm(monkeypatch, content: str):
    class FakeResp:
        class C:
            class M:
                pass
            message = M()
        choices = [C()]
    FakeResp.choices[0].message.content = content
    monkeypatch.setattr(narrator, "_client", lambda: type("X", (), {
        "chat": type("Y", (), {"completions": type("Z", (), {
            "create": staticmethod(lambda **k: FakeResp())})()})()})())


def test_attack1_confidence_pct_cannot_ground_star_lie(monkeypatch):
    # evidence has "confidence 80%" -> token 80; real stars = 10.
    f, v, m = _fixture()
    _fake_llm(monkeypatch, "A cold vigil for a repo of 80 stars, now silent.")
    out = narrator.narrate("o", "r", v, f, m)
    assert "80 stars" not in out                 # smuggle rejected
    assert "without the language model" in out   # templated fallback fired


def test_attack2_lifespan_cannot_ground_contributor_lie(monkeypatch):
    # evidence has "Lifespan (days): 530"; real contributors = 2.
    f, v, m = _fixture()
    _fake_llm(monkeypatch, "Mourned by its 530 contributors in the dark.")
    out = narrator.narrate("o", "r", v, f, m)
    assert "530 contributors" not in out
    assert "without the language model" in out


def test_attack3_date_year_cannot_ground_days_lie(monkeypatch):
    # evidence has "Born: 2021-03-02"; nothing says it survived 2021 days.
    f, v, m = _fixture()
    _fake_llm(monkeypatch, "It survived 2021 days before the final commit.")
    out = narrator.narrate("o", "r", v, f, m)
    assert "2021 days" not in out
    assert "without the language model" in out


def test_legit_grounded_eulogy_still_passes(monkeypatch):
    # Every number here is a REAL semantic value: 800 days, 530-day lifespan, 10 stars.
    f, v, m = _fixture()
    legit = ("Here rests a project that drew breath for 530 days, then fell quiet "
             "800 days ago. Only 10 stars kept vigil over its 2 contributors; its "
             "bus factor of 1 foretold the silence. Confidence in this verdict: high.")
    _fake_llm(monkeypatch, legit)
    out = narrator.narrate("o", "r", v, f, m)
    assert out == legit                           # grounded -> passed through untouched
    assert "without the language model" not in out
