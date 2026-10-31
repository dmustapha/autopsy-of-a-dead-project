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


def _mock_llm(monkeypatch, content):
    class FakeResp:
        class C:
            class M: ...
            message = M()
        choices = [C()]
    FakeResp.C.M.content = content
    monkeypatch.setattr(narrator, "_client", lambda: type("X", (), {
        "chat": type("Y", (), {"completions": type("Z", (), {
            "create": staticmethod(lambda **k: FakeResp())})()})()})())


def test_grounding_accepts_tier_b_nouns(monkeypatch):
    # A eulogy that cites the NEW metric nouns with VALUES the evidence binds must pass.
    f = Features(days_since_last_commit=800, commit_cadence_decay=-3.0, lifespan_days=530,
                 contributor_count=2, bus_factor=1, velocity_ratio=0.04)
    v = Verdict(mode="abandoned", confidence=0.8, probs={"abandoned": 0.8}, engine="tabpfn")
    m = RepoMeta(stars=10, created_at="2021-03-02", last_commit_at="2022-08-14",
                 release_count=12, open_issues_count=34)
    _mock_llm(monkeypatch, "It cut 12 releases and left 34 issues open before falling silent.")
    out = narrator.narrate("o", "r", v, f, m)
    assert "12 releases" in out and "34 issues" in out   # grounded, not rejected


def test_grounding_rejects_wrong_tier_b_binding(monkeypatch):
    # Right value, wrong metric: 12 is releases, not issues -> binding gate rejects.
    f = Features(days_since_last_commit=800, commit_cadence_decay=-3.0, lifespan_days=530,
                 contributor_count=2, bus_factor=1, velocity_ratio=0.04)
    v = Verdict(mode="abandoned", confidence=0.8, probs={"abandoned": 0.8}, engine="tabpfn")
    m = RepoMeta(stars=10, created_at="2021-03-02", last_commit_at="2022-08-14",
                 release_count=12, open_issues_count=34)
    _mock_llm(monkeypatch, "It left 12 issues open at the end.")  # 12 is releases, not issues
    out = narrator.narrate("o", "r", v, f, m)
    assert "12 issues" not in out        # binding gate forced the templated fallback


def test_grounding_rejects_fabricated_commit_count(monkeypatch):
    # "commits" has an EMPTY binding (no "Commits: N" evidence line). A fabricated
    # "<N> commits" claim where N == days_since_last_commit (800) must NOT ground off
    # the staleness value — the binding gate rejects it (closes the digit-smuggle hole).
    f = Features(days_since_last_commit=800, commit_cadence_decay=-3.0, lifespan_days=530,
                 contributor_count=2, bus_factor=1, velocity_ratio=0.04)
    v = Verdict(mode="abandoned", confidence=0.8, probs={"abandoned": 0.8}, engine="tabpfn")
    m = RepoMeta(stars=10, created_at="2021-03-02", last_commit_at="2022-08-14")
    _mock_llm(monkeypatch, "After 800 commits it fell silent.")  # 800 is days-idle, not commits
    out = narrator.narrate("o", "r", v, f, m)
    assert "800 commits" not in out      # rejected -> templated fallback


def test_grounding_accepts_real_days_contributors_releases(monkeypatch):
    # Legitimate "<N> days" / "<N> contributors" / "<N> releases" citations still pass,
    # each bound to the value evidence actually holds for that metric.
    f = Features(days_since_last_commit=800, commit_cadence_decay=-3.0, lifespan_days=530,
                 contributor_count=47, bus_factor=1, velocity_ratio=0.04)
    v = Verdict(mode="abandoned", confidence=0.8, probs={"abandoned": 0.8}, engine="tabpfn")
    m = RepoMeta(stars=10, created_at="2021-03-02", last_commit_at="2022-08-14",
                 release_count=12)
    _mock_llm(monkeypatch, "Idle 800 days, built by 47 contributors across 12 releases.")
    out = narrator.narrate("o", "r", v, f, m)
    assert "800 days" in out and "47 contributors" in out and "12 releases" in out
