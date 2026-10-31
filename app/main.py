from __future__ import annotations
import os, hashlib, asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .schemas import AutopsyRequest, AutopsyResult
from .validators import parse_repo_url, BadRepoURL
from .github import fetch_repo, RepoError
from .features import build_features
from .classifier import classify, _seed, nearest_cohort
from .narrator import narrate
from .extractor import extract_death_note
from .cache import cache
from .ratelimit import rate_limit

load_dotenv()
app = FastAPI(title="Autopsy of a Dead Project")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

EXAMPLES = [
    {"repo": os.environ.get("EX_ABANDONED", "bower/bower"), "death_mode": "abandoned"},
    {"repo": os.environ.get("EX_BURNED", "sindresorhus/caprine"), "death_mode": "burned_out"},
    {"repo": os.environ.get("EX_ALIVE", "fastapi/fastapi"), "death_mode": "alive"},
]


def _cert_id(owner: str, repo: str) -> str:
    return hashlib.sha256(f"{owner}/{repo}".encode()).hexdigest()[:6]


def _adjudicate_evidence(data) -> dict:
    # Tier A: run the LLM adjudicator over commit messages + README. Honesty invariant —
    # offline/parse-fail returns the labeled "none" guard (llm_offline=True); callers must
    # NOT tie-break or populate death_note from an offline hint.
    messages = [c.get("message", "") for c in data.commits[:20]]
    return extract_death_note(messages, data.readme)


def _narration_engine(narration: str) -> str:
    # Honest narration badge: the REAL model + provider that wrote the eulogy, derived from env.
    # Never hard-code a model the deploy isn't using (the whole thesis is honest engine labels).
    if "without the language model" in narration:
        return "templated · LLM offline"
    model = os.environ.get("LLM_MODEL", "gemma2:2b")
    base = os.environ.get("LLM_BASE_URL", "")
    if "0g.ai" in base:
        prov = "0G Compute"
    elif "11434" in base or "localhost" in base:
        prov = "Ollama (local)"
    elif "groq" in base:
        prov = "Groq"
    else:
        prov = "open-weight"
    return f"{model} · {prov}"


def _death_note(hint: dict) -> str | None:
    # Only a live hint with at least MEDIUM confidence AND a quote earns a death_note.
    # A low/none-confidence quote is too weak to become a certificate finding — it would
    # read as fabricated authority. Never fabricated; offline -> None.
    # (Distinct from the classifier adjudicator, which stays HIGH-only for an override.)
    if hint.get("llm_offline"):
        return None
    if hint.get("hint_confidence") not in ("high", "medium"):
        return None
    quote = (hint.get("evidence_quote") or "").strip()
    return quote or None


def _project_summary(hint: dict) -> str | None:
    # Factual "what this project was" line from the adjudicator. Honest empty on offline.
    # NOT confidence-gated: unlike _death_note, a factual summary is valid even for a
    # 'none'/'low' hint (an alive repo still has a real description).
    if hint.get("llm_offline"):
        return None
    summary = (hint.get("project_summary") or "").strip()
    return summary or None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "examples": EXAMPLES})


@app.get("/examples")
async def examples():
    return EXAMPLES


@app.get("/healthz")
async def healthz():
    seed_rows = len(_seed())
    reachable = bool(os.environ.get("TABPFN_TOKEN"))
    return {"ok": True, "seed_rows": seed_rows, "tabpfn_reachable": reachable}


@app.post("/autopsy", response_model=AutopsyResult)
async def autopsy(req: AutopsyRequest, request: Request):
    rate_limit(request)
    try:
        owner, repo = parse_repo_url(req.repo_url)
    except BadRepoURL as e:
        raise HTTPException(status_code=422, detail=f"That doesn't look like a GitHub grave. {e}")
    cached = cache.get(owner, repo)
    if cached:
        return cached
    try:
        data = await fetch_repo(owner, repo)
    except RepoError as e:
        msg = {
            "not_found": "Couldn't exhume this grave - is the repository public?",
            "empty": "No body to examine - this repo has almost no history.",
            "rate_limited": "The gatekeeper (GitHub) is rate-limiting us. Try again shortly.",
        }.get(e.kind, "The exhumation failed unexpectedly.")
        raise HTTPException(status_code=422, detail=msg)
    try:
        features, meta = build_features(data)
    except ValueError:
        raise HTTPException(status_code=422, detail="No body to examine - too little commit history.")
    # Blocking calls (LLM HTTP + torch) run in a threadpool so the single event loop
    # stays responsive (healthz/other requests) during a ~16-30s narration.
    hint = await asyncio.to_thread(_adjudicate_evidence, data)
    verdict = await asyncio.to_thread(classify, features, hint)
    death_note = _death_note(hint)
    narration = await asyncio.to_thread(narrate, owner, repo, verdict, features, meta, hint.get("evidence_quote", ""))
    result = AutopsyResult(owner=owner, repo=repo, meta=meta, features=features,
                           verdict=verdict, narration=narration, narration_engine=_narration_engine(narration),
                           certificate_id=_cert_id(owner, repo),
                           death_note=death_note, project_summary=_project_summary(hint),
                           llm_hint=hint, cohort=nearest_cohort(features))
    cache.set(owner, repo, result)
    return result


async def _prewarm_one(ex: dict) -> None:
    try:
        owner, repo = parse_repo_url(ex["repo"])
        if not cache.get(owner, repo):
            data = await fetch_repo(owner, repo)
            feats, meta = build_features(data)
            hint = await asyncio.to_thread(_adjudicate_evidence, data)
            v = await asyncio.to_thread(classify, feats, hint)
            n = await asyncio.to_thread(narrate, owner, repo, v, feats, meta, hint.get("evidence_quote", ""))
            cache.set(owner, repo, AutopsyResult(owner=owner, repo=repo, meta=meta,
                      features=feats, verdict=v, narration=n, narration_engine=_narration_engine(n),
                      certificate_id=_cert_id(owner, repo),
                      death_note=_death_note(hint), project_summary=_project_summary(hint),
                      llm_hint=hint, cohort=nearest_cohort(feats)))
    except Exception:
        pass  # pre-warm is best-effort; never blocks startup


async def _prewarm() -> None:
    for ex in EXAMPLES:
        await _prewarm_one(ex)


@app.on_event("startup")
async def _schedule_prewarm():
    # Fire-and-forget: pre-warm the examples in the background so a slow/failing
    # upstream (TabPFN, GitHub) can NEVER block the server from accepting traffic.
    import asyncio
    asyncio.create_task(_prewarm())


@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "The crypt is sealed - an unexpected error occurred."})
