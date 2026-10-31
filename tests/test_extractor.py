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
