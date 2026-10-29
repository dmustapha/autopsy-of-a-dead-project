from __future__ import annotations
import os, hashlib
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .schemas import AutopsyRequest, AutopsyResult
from .validators import parse_repo_url, BadRepoURL
from .github import fetch_repo, RepoError
from .features import build_features
from .classifier import classify, _seed
from .narrator import narrate
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
    verdict = classify(features)
    narration = narrate(owner, repo, verdict, features, meta)
    result = AutopsyResult(owner=owner, repo=repo, meta=meta, features=features,
                           verdict=verdict, narration=narration, certificate_id=_cert_id(owner, repo))
    cache.set(owner, repo, result)
    return result


async def _prewarm_one(ex: dict) -> None:
    try:
        owner, repo = parse_repo_url(ex["repo"])
        if not cache.get(owner, repo):
            data = await fetch_repo(owner, repo)
            feats, meta = build_features(data)
            v = classify(feats)
            n = narrate(owner, repo, v, feats, meta)
            cache.set(owner, repo, AutopsyResult(owner=owner, repo=repo, meta=meta,
                      features=feats, verdict=v, narration=n, certificate_id=_cert_id(owner, repo)))
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
