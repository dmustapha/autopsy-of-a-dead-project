from __future__ import annotations
import os, json
from .narrator import _client

# Tier A — LLM-as-adjudicator evidence extraction.
# Reuses narrator._client() (Ollama OpenAI-compat / 0G / Groq via same env).
# STRICT JSON only. Offline / parse-fail -> honest "none" guard, NEVER raises,
# NEVER fabricates a signal (honesty invariant).

SYSTEM = (
    "You are a forensic triage assistant for dead software projects. You read the LAST commit "
    "messages and the README of a repository and extract ONLY what is literally present. "
    "Never invent. Return STRICT JSON with exactly these keys: "
    '{"death_signals": [up to 4 verbatim short quotes that hint why the project stopped], '
    '"classification_hint": one of "abandoned"|"pivoted"|"completed"|"burned_out"|"none", '
    '"hint_confidence": one of "high"|"medium"|"low", '
    '"evidence_quote": a single short verbatim quote that best supports the hint, or "", '
    '"project_summary": a single factual line describing what this project was or did, '
    'STRICTLY from the README/description — no invention; use "" if nothing supports it}. '
    "If nothing supports a hint, use classification_hint=\"none\" and hint_confidence=\"low\"."
)

_OFFLINE = {
    "classification_hint": "none",
    "hint_confidence": "low",
    "death_signals": [],
    "evidence_quote": "",
    "project_summary": "",
    "llm_offline": True,
}

_VALID_HINTS = {"abandoned", "pivoted", "completed", "burned_out", "none"}
_VALID_CONF = {"high", "medium", "low"}


def _normalize(raw: dict) -> dict:
    # Coerce the model's JSON into the strict shape; anything off-spec degrades to the
    # honest defaults for that field (never fabricates, never raises).
    hint = raw.get("classification_hint")
    conf = raw.get("hint_confidence")
    signals = raw.get("death_signals")
    quote = raw.get("evidence_quote")
    summary = raw.get("project_summary")
    return {
        "classification_hint": hint if hint in _VALID_HINTS else "none",
        "hint_confidence": conf if conf in _VALID_CONF else "low",
        "death_signals": [str(s)[:200] for s in signals][:4] if isinstance(signals, list) else [],
        "evidence_quote": str(quote)[:200] if isinstance(quote, str) else "",
        "project_summary": str(summary)[:300] if isinstance(summary, str) else "",
        "llm_offline": False,
    }


def extract_death_note(messages: list[str], readme: str | None) -> dict:
    # Optional Tier-A LLM adjudicator. On a resource-tight deploy its extra LLM round-trip
    # doubles autopsy latency for a hint the TabPFN classifier does not require; skip it when
    # EXTRACTOR_LLM_DISABLE=1 (returns the labeled-offline hint — same as a failed call).
    if os.environ.get("EXTRACTOR_LLM_DISABLE") == "1":
        return dict(_OFFLINE)
    msg_block = "\n".join(f"- {m}" for m in messages[:20] if m)
    readme_block = (readme or "")[:2000]
    user = (
        f"Last commit messages:\n{msg_block or '(none)'}\n\n"
        f"README (excerpt):\n{readme_block or '(none)'}\n\n"
        "Return the STRICT JSON object."
    )
    try:
        client = _client()
        model = os.environ.get("LLM_MODEL", "gemma2:2b")
        resp = client.chat.completions.create(
            model=model, temperature=0, max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "400")),
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": user}])
        raw = json.loads((resp.choices[0].message.content or "").strip())
        if not isinstance(raw, dict):
            return dict(_OFFLINE)
        return _normalize(raw)
    except Exception:
        return dict(_OFFLINE)
