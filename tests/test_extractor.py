from app import extractor


def test_offline_returns_labeled_none_guard(monkeypatch):
    # No live LLM -> _client() call raises -> honest guard, never fabricated, never raises.
    def boom():
        raise RuntimeError("Ollama offline")
    monkeypatch.setattr(extractor, "_client", boom)
    out = extractor.extract_death_note(["giving up on this", "final commit"], "A README.")
    assert out["llm_offline"] is True
    assert out["classification_hint"] == "none"
    assert out["hint_confidence"] == "low"
    assert out["death_signals"] == []
    assert out["evidence_quote"] == ""


def test_parse_failure_degrades_to_guard(monkeypatch):
    # Non-JSON content -> json.loads fails -> same honest guard (no raise).
    class FakeResp:
        class C:
            class M:
                content = "not json at all"
            message = M()
        choices = [C()]
    monkeypatch.setattr(extractor, "_client", lambda: type("X", (), {
        "chat": type("Y", (), {"completions": type("Z", (), {
            "create": staticmethod(lambda **k: FakeResp())})()})()})())
    out = extractor.extract_death_note(["m"], None)
    assert out["llm_offline"] is True
    assert out["classification_hint"] == "none"


def test_valid_json_is_normalized(monkeypatch):
    import json
    payload = {"death_signals": ["pivoting to v2", "no time"],
               "classification_hint": "pivoted", "hint_confidence": "high",
               "evidence_quote": "we are pivoting to v2"}

    class FakeResp:
        class C:
            class M:
                content = json.dumps(payload)
            message = M()
        choices = [C()]
    monkeypatch.setattr(extractor, "_client", lambda: type("X", (), {
        "chat": type("Y", (), {"completions": type("Z", (), {
            "create": staticmethod(lambda **k: FakeResp())})()})()})())
    out = extractor.extract_death_note(["m"], "r")
    assert out["llm_offline"] is False
    assert out["classification_hint"] == "pivoted"
    assert out["hint_confidence"] == "high"
    assert out["evidence_quote"] == "we are pivoting to v2"


def test_offline_returns_empty_project_summary(monkeypatch):
    # EXTRACTOR_LLM_DISABLE=1 -> _OFFLINE dict -> project_summary="" + llm_offline=True.
    monkeypatch.setenv("EXTRACTOR_LLM_DISABLE", "1")
    out = extractor.extract_death_note(["some commit"], "Some README.")
    assert out["project_summary"] == ""
    assert out["llm_offline"] is True


def test_garbage_json_yields_empty_summary_no_fabrication(monkeypatch):
    import json

    monkeypatch.delenv("EXTRACTOR_LLM_DISABLE", raising=False)

    def make_fake_client(content):
        class FakeResp:
            class C:
                class M:
                    pass
                message = M()
            choices = [C()]
        FakeResp.choices[0].message.content = content
        return type("X", (), {"chat": type("Y", (), {"completions": type("Z", (), {
            "create": staticmethod(lambda **k: FakeResp())})()})()})()

    # Case (a): non-JSON text -> except path -> _OFFLINE -> project_summary=""
    monkeypatch.setattr(extractor, "_client", lambda: make_fake_client("not json at all"))
    out = extractor.extract_death_note(["m"], None)
    assert out["project_summary"] == ""
    assert out["classification_hint"] == "none"
    assert out["hint_confidence"] == "low"

    # Case (b): empty dict {} -> _normalize -> project_summary="" (raw.get returns None, not str)
    monkeypatch.setattr(extractor, "_client", lambda: make_fake_client(json.dumps({})))
    out = extractor.extract_death_note(["m"], None)
    assert out["project_summary"] == ""
    assert out["classification_hint"] == "none"
    assert out["hint_confidence"] == "low"

    # Case (c): project_summary is a non-string (int) -> _normalize -> project_summary=""
    monkeypatch.setattr(extractor, "_client", lambda: make_fake_client(
        json.dumps({"project_summary": 42, "classification_hint": "abandoned",
                    "hint_confidence": "high", "death_signals": [], "evidence_quote": ""})))
    out = extractor.extract_death_note(["m"], None)
    assert out["project_summary"] == ""


def test_valid_json_includes_normalized_summary(monkeypatch):
    import json

    monkeypatch.delenv("EXTRACTOR_LLM_DISABLE", raising=False)
    short_summary = "A CLI bundler for JS."
    long_summary = "X" * 350  # exceeds 300 char limit

    def make_fake_client(payload):
        class FakeResp:
            class C:
                class M:
                    pass
                message = M()
            choices = [C()]
        FakeResp.choices[0].message.content = json.dumps(payload)
        return type("X", (), {"chat": type("Y", (), {"completions": type("Z", (), {
            "create": staticmethod(lambda **k: FakeResp())})()})()})()

    # Short summary passes through as-is
    monkeypatch.setattr(extractor, "_client", lambda: make_fake_client({
        "project_summary": short_summary, "classification_hint": "completed",
        "hint_confidence": "high", "death_signals": [], "evidence_quote": "done"}))
    out = extractor.extract_death_note(["m"], "r")
    assert out["project_summary"] == short_summary
    assert out["llm_offline"] is False

    # Long summary is truncated to 300 chars
    monkeypatch.setattr(extractor, "_client", lambda: make_fake_client({
        "project_summary": long_summary, "classification_hint": "none",
        "hint_confidence": "low", "death_signals": [], "evidence_quote": ""}))
    out = extractor.extract_death_note(["m"], "r")
    assert out["project_summary"] == long_summary[:300]
    assert len(out["project_summary"]) == 300
