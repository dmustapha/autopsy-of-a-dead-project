from app.schemas import Features, Verdict, RepoMeta
from app import narrator


def test_grounding_rejects_fabricated_numbers(monkeypatch):
    f = Features(days_since_last_commit=800, commit_cadence_decay=-3.0, lifespan_days=530,
                 contributor_count=2, bus_factor=1, velocity_ratio=0.04)
    v = Verdict(mode="abandoned", confidence=0.8, probs={"abandoned": 0.8}, engine="tabpfn")
    m = RepoMeta(stars=10, created_at="2021-03-02", last_commit_at="2022-08-14")

    class FakeResp:
        class C:
            class M:
                content = "It had 99999 commits across 12345 years."  # fabricated
            message = M()
        choices = [C()]
    monkeypatch.setattr(narrator, "_client", lambda: type("X", (), {
        "chat": type("Y", (), {"completions": type("Z", (), {"create": staticmethod(lambda **k: FakeResp())})()})()})())
    out = narrator.narrate("o", "r", v, f, m)
    assert "99999" not in out        # grounding check forced the templated fallback
