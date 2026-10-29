from __future__ import annotations
import os, re
from openai import OpenAI
from .schemas import Features, Verdict, RepoMeta

SYSTEM = (
    "You are a forensic coroner for software projects. Write a 120-200 word coroner's report / "
    "eulogy. Spooky, literary, Dia-de-los-Muertos reverence - but EVERY factual claim must come "
    "from the provided evidence. Never invent numbers, dates, or contributors. Never mock the "
    "maintainer; hold a vigil, do not ridicule."
)


def _client() -> OpenAI:
    # FINAL STACK (ADR-005b / ARCH PART III.1): narration = Gemma (open weights) via Ollama, keyless.
    # base_url -> Ollama's OpenAI-compatible endpoint; api_key is a placeholder Ollama ignores.
    # 0G / Groq remain fallbacks only (swap LLM_BASE_URL/LLM_MODEL/LLM_API_KEY in .env).
    return OpenAI(
        base_url=os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.environ.get("LLM_API_KEY") or os.environ.get("GROQ_API_KEY") or "ollama",
    )


def _evidence(owner, repo, v: Verdict, f: Features, m: RepoMeta) -> str:
    return (
        f"Repo: {owner}/{repo}\nBorn: {m.created_at}\nLast seen: {m.last_commit_at}\n"
        f"Verdict: {v.mode} (confidence {v.confidence:.0%})\n"
        f"Days since last commit: {int(f.days_since_last_commit)}\n"
        f"Commit-cadence decay: {f.commit_cadence_decay}\nLifespan (days): {int(f.lifespan_days)}\n"
        f"Contributors: {int(f.contributor_count)}\nBus factor: {int(f.bus_factor)}\n"
        f"Velocity ratio: {f.velocity_ratio}\nStars: {m.stars}\nArchived: {m.is_archived}"
    )


def _numbers(s: str) -> set[str]:
    return set(re.findall(r"\d{2,}", s))


def narrate(owner, repo, v: Verdict, f: Features, m: RepoMeta) -> str:
    ev = _evidence(owner, repo, v, f, m)
    allowed = _numbers(ev)
    try:
        client = _client()
        model = os.environ.get("LLM_MODEL", "gemma2:2b")
        for attempt in range(2):
            extra = "" if attempt == 0 else "\nUse ONLY numbers that appear in the evidence."
            resp = client.chat.completions.create(
                model=model, temperature=0.7, max_tokens=320,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": f"Evidence:\n{ev}{extra}\n\nWrite the coroner's report."}])
            text = (resp.choices[0].message.content or "").strip()
            if _numbers(text) <= allowed:
                return text
        return _template(owner, repo, v, m)
    except Exception:
        return _template(owner, repo, v, m)


def _template(owner, repo, v: Verdict, m: RepoMeta) -> str:
    return (f"Here lies {owner}/{repo}, last seen {m.last_commit_at}. "
            f"The forensic examination records a cause of death of '{v.mode}'. "
            f"It is remembered, not mocked. (Generated without the language model.)")
