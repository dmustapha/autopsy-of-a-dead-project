from app.main import _death_note


def _hint(conf, quote="we are shutting this down", offline=False):
    return {"hint_confidence": conf, "evidence_quote": quote, "llm_offline": offline,
            "classification_hint": "abandoned", "death_signals": []}


def test_offline_hint_yields_no_death_note():
    assert _death_note(_hint("high", offline=True)) is None


def test_low_confidence_quote_is_not_a_certificate_finding():
    # A low/none-confidence quote must NOT become a death_note (reads as fabricated authority).
    assert _death_note(_hint("low")) is None
    assert _death_note(_hint("none")) is None


def test_high_and_medium_confidence_quotes_pass_through():
    assert _death_note(_hint("high")) == "we are shutting this down"
    assert _death_note(_hint("medium")) == "we are shutting this down"


def test_high_confidence_but_empty_quote_is_none():
    assert _death_note(_hint("high", quote="")) is None
