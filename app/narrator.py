from __future__ import annotations
import os, re
from openai import OpenAI
from .schemas import Features, Verdict, RepoMeta

SYSTEM = (
    "You are a forensic coroner for software projects. Write a 120-200 word coroner's report / "
    "eulogy. Spooky, literary, Dia-de-los-Muertos reverence - but EVERY factual claim must come "
    "from the provided evidence. Never mock the maintainer; hold a vigil, do not ridicule. "
    "CRITICAL: write in pure literary PROSE and do NOT quote any specific numbers, dates, counts, "
    "percentages, or years - those already live in the evidence table beside your report. Evoke "
    "the story of the life and death (silence, abandonment, the last breath), never the statistics. "
    "Output ONLY the eulogy prose, no headings or labels."
)


def _client() -> OpenAI:
    # FINAL STACK (ADR-005b / ARCH PART III.1): narration = Gemma (open weights) via Ollama, keyless.
    # base_url -> Ollama's OpenAI-compatible endpoint; api_key is a placeholder Ollama ignores.
    # 0G / Groq remain fallbacks only (swap LLM_BASE_URL/LLM_MODEL/LLM_API_KEY in .env).
    return OpenAI(
        base_url=os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.environ.get("LLM_API_KEY") or os.environ.get("GROQ_API_KEY") or "ollama",
    )


def _evidence(owner, repo, v: Verdict, f: Features, m: RepoMeta, evidence_quote: str = "") -> str:
    ev = (
        f"Repo: {owner}/{repo}\nBorn: {m.created_at}\nLast seen: {m.last_commit_at}\n"
        f"Verdict: {v.mode} (confidence {v.confidence:.0%})\n"
        f"Days idle: {int(f.days_since_last_commit)}\n"
        f"Cadence decay: {f.commit_cadence_decay}\nLifespan (days): {int(f.lifespan_days)}\n"
        f"Contributors: {int(f.contributor_count)}\nBus factor: {int(f.bus_factor)}\n"
        f"Velocity ratio: {f.velocity_ratio}\nStars: {m.stars}\nArchived: {m.is_archived}"
    )
    # Tier B metric lines. Only surfaced when a real count exists (None => not
    # fetched => omitted, never printed as 0), so the grounding gate only ever
    # binds a number the evidence actually holds.
    if m.release_count is not None:
        ev += f"\nReleases: {m.release_count}"
    if m.open_issues_count is not None:
        ev += f"\nOpen issues: {m.open_issues_count}"
    if evidence_quote:
        # Verbatim quote from the adjudicator (commit messages / README). It is prose,
        # not a metric, so it cannot smuggle a number past the grounding gate.
        ev += f"\nText evidence: {evidence_quote}"
    return ev


# Metric nouns a eulogy may attach a number to -> canonical evidence metric.
# Binding a text number to its metric closes cross-field digit-smuggle: a value
# that is real for one field ("530-day lifespan") can no longer ground a lie about
# another ("530 contributors").
_METRIC_NOUNS = {
    "stars": "stars", "star": "stars",
    "contributors": "contributors", "contributor": "contributors",
    "maintainers": "contributors", "maintainer": "contributors",
    "days": "days", "day": "days",
    # "commit"/"commits" tracked with an EMPTY binding: the evidence has no "Commits: N"
    # line, so any "N commits" claim fails the binding gate (N can't be in an empty set)
    # and is rejected. The evidence labels were renamed ("Days idle", "Cadence decay")
    # so the word "commit" never appears in a label — otherwise the staleness value would
    # bind to "commits" and ground a fabricated commit count (the honesty hole we closed).
    "commits": "commits", "commit": "commits",
    # Tier B nouns — bind to the "Releases:" / "Open issues:" evidence lines so a
    # eulogy that legitimately cites them isn't rejected as ungrounded.
    "releases": "releases", "release": "releases",
    "issues": "issues", "issue": "issues",
}


def _norm_nums(s: str) -> str:
    # Normalize numeric FORMATTING so legitimately grounded prose isn't false-rejected:
    #  - strip thousands separators: "22,010" -> "22010" (matches the plain evidence int)
    #  - collapse yyyy-mm-dd to its YEAR: "2012-09-07" -> "2012", so a birth-year mention
    #    ("born in 2012") stays groundable while stray month/day runs (09, 07) don't leak in.
    s = s.replace(",", "")
    s = re.sub(r"(\d{4})-\d{2}-\d{2}", r"\1", s)
    return s


def _numbers(s: str) -> set[str]:
    # Semantic metric values (incl. the birth year). Percentages (confidence 80%) are a
    # smuggle vector -- they inject a stray run that could ground an unrelated claim -- so
    # strip them. The binding gate (below) is the real protection for metric-noun claims.
    s = _norm_nums(s)
    s = re.sub(r"\d+%", " ", s)
    return set(t for t in re.findall(r"\b\d+\b", s) if len(t) >= 2)


def _metric_values(ev: str) -> dict[str, set[str]]:
    # Map each canonical metric -> the value(s) the evidence binds to it,
    # parsed from "Label: N" / "Lifespan (days): 530" lines.
    out: dict[str, set[str]] = {}
    for label, num in re.findall(r"([A-Za-z][A-Za-z ()]*?):\s*(\d+)", ev):
        for word in re.findall(r"[a-z]+", label.lower()):
            canon = _METRIC_NOUNS.get(word)
            if canon:
                out.setdefault(canon, set()).add(num)
    return out


def _grounded(text: str, ev: str) -> bool:
    allowed = _numbers(ev)
    text = _norm_nums(text)   # same formatting normalization as the evidence side
    # 1) value gate: every 2+-digit value in the eulogy must exist in evidence.
    for num in re.findall(r"\b\d+\b", text):
        if len(num) >= 2 and num not in allowed:
            return False
    # 2) binding gate: if the eulogy attaches a number to a metric noun
    #    ("530 contributors"), that value must be the one evidence binds to
    #    that metric -- not merely present somewhere in evidence.
    bindings = _metric_values(ev)
    for num, noun in re.findall(r"(\d+)\s+([A-Za-z]+)", text):
        if len(num) < 2:
            continue
        canon = _METRIC_NOUNS.get(noun.lower())
        if canon and num not in bindings.get(canon, set()):
            return False
    return True


def narrate(owner, repo, v: Verdict, f: Features, m: RepoMeta, evidence_quote: str = "") -> str:
    ev = _evidence(owner, repo, v, f, m, evidence_quote)
    try:
        client = _client()
        model = os.environ.get("LLM_MODEL", "gemma2:2b")
        # Reasoning models (e.g. 0G deepseek-v4-flash) spend tokens on a hidden reasoning
        # pass before emitting content; a 320 budget truncates the eulogy or returns EMPTY
        # content. LLM_MAX_TOKENS lets the deploy raise it (>=400 for reasoning models) while
        # keeping Gemma's small default. An empty/too-short reply is never accepted as a real
        # eulogy (an empty string trivially "grounds" — the honesty hole we close here).
        max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "320"))
        for attempt in range(2):
            extra = "" if attempt == 0 else "\nUse ONLY numbers that appear in the evidence."
            resp = client.chat.completions.create(
                model=model, temperature=0.7, max_tokens=max_tokens,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": f"Evidence:\n{ev}{extra}\n\nWrite the coroner's report."}])
            text = (resp.choices[0].message.content or "").strip()
            if len(text) >= 40 and _grounded(text, ev):
                return text
        return _template(owner, repo, v, m)
    except Exception:
        return _template(owner, repo, v, m)


def _template(owner, repo, v: Verdict, m: RepoMeta) -> str:
    if v.mode == "alive":
        return (f"Still beating: {owner}/{repo}, last seen {m.last_commit_at}. "
                f"The examination finds no cause of death; the vital signs hold. "
                f"(Generated without the language model.)")
    if v.mode == "insufficient_history":
        return (f"{owner}/{repo}, last seen {m.last_commit_at}. "
                f"The history is too short for a finding; this is a preliminary note, not a cause of death. "
                f"(Generated without the language model.)")
    return (f"Here lies {owner}/{repo}, last seen {m.last_commit_at}. "
            f"The forensic examination records a cause of death of '{v.mode}'. "
            f"It is remembered, not mocked. (Generated without the language model.)")
