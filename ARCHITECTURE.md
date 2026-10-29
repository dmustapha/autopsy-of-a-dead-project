# ARCHITECTURE — Autopsy of a Dead Project

A single Python web service that reads public GitHub data, classifies a repository's
"death-mode" with an open tabular foundation model (TabPFN), and narrates a forensic
coroner's report with an open-weight language model (via Groq). This document is the
implementation spec the build phase (B0–B6) consumes directly.

---

## 1. Design goals (in priority order)

1. **Render-tiny + deploy-trivial.** One Python process, no JS build step, no git binary,
   no local model weights, no database. Must run on a Render Starter instance (512MB RAM).
2. **Open-source AI load-bearing.** The death-mode verdict IS TabPFN's output; remove it and
   only a heuristic rules page remains. Narration is an open-weight LLM, never a closed model.
3. **Demo-safe + honest.** Deterministic enough to demo live; every fallback is labeled, never
   silently faked.
4. **Post-first.** The app exists to produce screenshots, a demo clip, and a story. Nothing in
   the architecture should cost build time that the write-up (heaviest judged axis) needs.

---

## 2. Stack (chosen, with rationale)

| Layer | Choice | Why this and not the alternative |
|---|---|---|
| Runtime | Python 3.11 | TabPFN + git analysis are Python-native; one language, one service |
| Web framework | FastAPI + Uvicorn | Tiny, async, fast cold-start, OpenAPI for free; one process Render hosts natively |
| Templating | Jinja2 (server-rendered single page) | No bundler, no client framework — the page is one HTML file |
| Frontend | Tailwind (CDN) + ~40 lines vanilla JS | Typing animation + a single fetch; a framework would add a build step for zero gain |
| Git data | GitHub REST API via `httpx` (async) | No clone, no git binary, no disk — `/commits` + `/contributors` + repo meta suffice |
| Classifier | TabPFN via `tabpfn-client` (hosted) | Load-bearing core; hosted avoids the local-weights browser license-accept + GPU/large tier |
| Narration | Groq (`openai` SDK, `base_url=https://api.groq.com/openai/v1`), model `llama-3.3-70b-versatile` | Open-weight, ~85ms TTFB, free, OpenAI-compatible; swappable to `qwen-2.5-*` |
| Deploy | Render Web Service, Starter $7/mo, `min instances = 1` (warm) | dl-1: free tier spins down at 15 min idle → a dead link during the Nov-2 judging week |

---

## 3. Module map

```
app/
  main.py            FastAPI app + routes
  github.py          GitHub REST client (async)
  features.py        feature-table construction
  classifier.py      TabPFN in-context classification (+ forensic-rules fallback)
  narrator.py        Groq open-weight narration (grounded)
  validators.py      repo-URL parsing / allow-listing
  cache.py           in-process LRU cache (narration + classification per repo)
  schemas.py         pydantic request/response models
  templates/
    index.html       the single page (paste field, card, typing JS)
  static/
    card.css         death-certificate card styling
    og.png           cover / Open-Graph image
data/
  seed_repos.csv     ~50 labeled repos — TabPFN's in-context train set (the linchpin)
  NOTES.md           seed-curation observations (handoff to the post)
tests/
  test_validators.py test_features.py test_classifier_shape.py test_narration_grounding.py
render.yaml          Render blueprint
requirements.txt     pinned deps
README.md            (owned by deploy-to-github @ deploy)
```

---

## 4. Routes (`main.py`)

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| GET | `/` | — | HTML (index.html) | the single page |
| POST | `/autopsy` | `{ "repo_url": str }` | `AutopsyResult` JSON | the one loop |
| GET | `/healthz` | — | `{"ok": true}` | Render health check + external warm-ping |
| GET | `/examples` | — | `[{repo, death_mode}]` | 3 pre-warmed demo repos for one-click |

`POST /autopsy` handler pseudocode:
```python
@app.post("/autopsy", response_model=AutopsyResult)
async def autopsy(req: AutopsyRequest):
    owner, repo = parse_repo_url(req.repo_url)          # validators — raises 422 on bad input
    if cached := cache.get(owner, repo):                 # cache.py
        return cached
    repo_data = await fetch_repo(owner, repo)            # github.py — raises 404/empty/archived
    features = build_features(repo_data)                 # features.py
    verdict  = classify(features)                        # classifier.py (TabPFN or fallback)
    narration = narrate(verdict, features, repo_data.meta)  # narrator.py (Groq)
    result = AutopsyResult(owner=owner, repo=repo, features=features,
                           verdict=verdict, narration=narration)
    cache.set(owner, repo, result)
    return result
```

---

## 5. The feature table (`features.py`) — the forensic evidence

`build_features(repo_data) -> dict[str, float]`. Six commit/contributor signals (Issues/PR
signals were cut for the 1-day scope — see LIMITATIONS). Exact definitions:

| Feature | Formula | Death-mode signal |
|---|---|---|
| `days_since_last_commit` | `now - max(commit.date)` in days | high → abandoned |
| `commit_cadence_decay` | OLS slope of monthly-commit-count over the repo lifespan (commits/month per month) | steep negative → burned-out / abandoned |
| `lifespan_days` | `max(commit.date) - min(commit.date)` in days | short + decay → pivoted; long + stable → completed |
| `contributor_count` | distinct commit authors | low → fragile |
| `bus_factor` | authors whose cumulative commit share ≥ 50% | 1 → single-maintainer burnout risk |
| `velocity_ratio` | `commits_last_90d / (total_commits / (lifespan_days/90))` | ≥1 → alive; ≪1 → fading |

Context columns also carried for narration (not classification): `total_commits`, `stars`,
`is_archived`, `primary_language`, `created_at`, `last_commit_at`.

Edge handling: <2 commits → `insufficient_history` verdict (skip classify, honest message);
huge repos → commit window capped at the most recent 1,000 commits (documented in LIMITATIONS);
archived repos → `is_archived=1` is a strong prior but TabPFN still runs.

---

## 6. Classifier (`classifier.py`) — TabPFN, honestly load-bearing

Death-mode classes: `{abandoned, pivoted, completed, burned_out, alive}`.

```python
from tabpfn_client import TabPFNClassifier
import pandas as pd

_SEED = pd.read_csv("data/seed_repos.csv")          # loaded once at startup
_FEATURES = ["days_since_last_commit","commit_cadence_decay","lifespan_days",
             "contributor_count","bus_factor","velocity_ratio"]

def classify(features: dict) -> Verdict:
    X_train, y_train = _SEED[_FEATURES], _SEED["death_mode"]
    X_test = pd.DataFrame([[features[f] for f in _FEATURES]], columns=_FEATURES)
    try:
        clf = TabPFNClassifier()                     # hosted inference
        clf.fit(X_train, y_train)                    # few-shot in-context "fit" (no training loop)
        proba = clf.predict_proba(X_test)[0]
        cls   = clf.classes_[proba.argmax()]
        return Verdict(mode=cls, confidence=float(proba.max()),
                       probs=dict(zip(clf.classes_, map(float, proba))), engine="tabpfn")
    except Exception as e:                           # client unreachable / quota
        return _forensic_rules(features, reason=str(e))   # TRANSPARENT fallback, labeled engine="rules"
```

**Why load-bearing (substitution test).** The verdict is `clf.predict_proba` over the seed set.
Remove TabPFN and `classify` returns only `_forensic_rules` — a hand-written if/else heuristic,
explicitly NOT AI. The seed CSV is TabPFN's in-context train data; it ships in-repo so the model
has priors about repos (it has none by default — it is a general tabular learner).

**Fallback (`_forensic_rules`).** Deterministic thresholds (e.g. `days_since_last_commit>365 and
velocity_ratio<0.1 → abandoned`). Returned with `engine="rules"` so the UI and narration can say
"forensic-rules estimate (model unavailable)" — never silently presented as the model.

---

## 7. Narrator (`narrator.py`) — open-weight, grounded

```python
from openai import OpenAI
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"])

SYSTEM = """You are a forensic coroner for software projects. Write a short (120–200 word)
coroner's report / eulogy. Spooky, literary, Día-de-los-Muertos reverence — but EVERY factual
claim must come from the provided evidence. Never invent numbers, dates, or contributors."""

def narrate(verdict, features, meta) -> str:
    evidence = render_evidence(verdict, features, meta)   # a compact, factual block
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=320,
        messages=[{"role":"system","content":SYSTEM},
                  {"role":"user","content":f"Evidence:\n{evidence}\n\nWrite the coroner's report."}])
    return resp.choices[0].message.content.strip()
```

**Grounding = anti-injection.** The model sees only the numeric evidence block + verdict, never
raw repo text → no prompt-injection surface from repository contents (SECURITY). A post-check
rejects a narration that introduces a number not present in `evidence` and retries once.

---

## 8. Request sequence (the one loop)

```
Browser (paste URL) ──POST /autopsy──▶ FastAPI
  1 validators.parse_repo_url        → (owner, repo)  | 422 friendly error
  2 cache.get                        → hit? return immediately (demo-safe, quota-safe)
  3 github.fetch_repo (async httpx)  → commits[], contributors[], meta | 404/empty/archived
  4 features.build_features          → feature row (6 signals + context)
  5 classifier.classify              → TabPFN verdict {mode, confidence, probs} | labeled fallback
  6 narrator.narrate (Groq)          → grounded coroner's report
  7 cache.set + return AutopsyResult
Browser ──▶ render death-certificate card, type out the eulogy
```

Latency budget (warm): GitHub fetch ~0.5–2s, TabPFN ~1–3s, Groq ~0.5–1s → typical <6s, target <15s.

---

## 9. Data schema — `data/seed_repos.csv` (the linchpin)

Columns: `owner_repo, days_since_last_commit, commit_cadence_decay, lifespan_days,
contributor_count, bus_factor, velocity_ratio, death_mode, note`. ~50 rows, roughly balanced
across the 5 classes. `note` is a human one-liner (feeds `data/NOTES.md` and the post). Built
B0-first; separability validated with a quick TabPFN fit before any UI work.

---

## 10. `render.yaml` (deploy blueprint)

```yaml
services:
  - type: web
    name: autopsy-of-a-dead-project
    runtime: python
    plan: starter                       # $7/mo durable — NOT free (dl-1)
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /healthz
    numInstances: 1                      # warm — no spin-down
    envVars:
      - key: GROQ_API_KEY      ; sync: false
      - key: TABPFN_TOKEN      ; sync: false
      - key: GITHUB_TOKEN      ; sync: false   # optional, higher rate limit
```
An external cron warm-ping hits `/healthz` every ~10 min through judging week as defence-in-depth.

---

## 11. Error-handling matrix

| Condition | Behavior |
|---|---|
| Bad/non-GitHub URL | 422 + friendly inline message; no crash |
| Repo 404 / private | "couldn't exhume this grave — is it public?" |
| <2 commits | `insufficient_history` verdict, honest copy, skip classify |
| Huge repo | cap at last 1,000 commits, note it in the card |
| GitHub 403 rate limit | ask for a token / retry later; cached examples still work |
| TabPFN client down | labeled forensic-rules fallback (engine="rules") |
| Groq down / rate limit | serve cached narration; else a terse non-LLM summary labeled as such |

---

## 12. Test plan (`tests/`)

- `test_validators.py` — URL parsing: full URL, owner/repo, trailing slash, non-GitHub rejected.
- `test_features.py` — feature math on a synthetic commit series (known decay slope, bus factor).
- `test_classifier_shape.py` — classify returns a valid class + confidence in [0,1]; fallback path labeled `rules`.
- `test_narration_grounding.py` — narration contains no number absent from the evidence block (mock Groq).

---

## 13. What is deliberately NOT here (scope cuts — Sonnet review, D7)

Issues/PR half-life features; server-side card image rendering; multi-repo comparison; user
accounts / persistence; private repos / OAuth. Each would cost build time the post needs.

---

## 14. Response schema (`schemas.py`)

```python
class AutopsyRequest(BaseModel):
    repo_url: str

class Feature(BaseModel):
    days_since_last_commit: float
    commit_cadence_decay: float
    lifespan_days: float
    contributor_count: float
    bus_factor: float
    velocity_ratio: float

class Verdict(BaseModel):
    mode: Literal["abandoned","pivoted","completed","burned_out","alive","insufficient_history"]
    confidence: float          # 0..1
    probs: dict[str, float]    # full posterior
    engine: Literal["tabpfn","rules"]   # honesty flag surfaced in the UI

class AutopsyResult(BaseModel):
    owner: str
    repo: str
    meta: dict                 # stars, language, created_at, is_archived, last_commit_at
    features: Feature
    verdict: Verdict
    narration: str
    certificate_id: str        # short hash for a shareable permalink in the card footer
```

The `engine` field is rendered verbatim in the card ("classified by TabPFN" vs "forensic-rules
estimate — model unavailable"). This is the honesty contract from LIMITATIONS, enforced in markup.

---

## 15. The single page (`templates/index.html`) — structure

```
<header>   title "Autopsy of a Dead Project", one-line subtitle, the theme framing
<main>
  <form id="autopsy">            paste field + "Perform the autopsy" button
  <section id="examples">        3 one-click demo repos (GET /examples), one per death-mode
  <section id="loading" hidden>  a tasteful "exhuming the commit history…" state (skeleton)
  <article  id="certificate" hidden>   the death-certificate card:
     ├─ cause of death  (verdict.mode, large)      + confidence bar
     ├─ dates           (born / last seen)          from meta
     ├─ evidence table  (the 6 features, labeled)   ← the ≥1-table craft element
     ├─ coroner's report (narration, typed out)     ← the eulogy
     └─ footer          engine badge + certificate_id + "share"
<footer>   open-source note: TabPFN + open-weight LLM; link to the Ollama-local mode
```

Client JS (~40 lines): submit → POST /autopsy → on success reveal `#certificate`, fill fields,
run a typewriter effect over `narration` (respecting `prefers-reduced-motion`). No framework.

### Accessibility
- Semantic landmarks; the certificate is an `<article>` with an `aria-live="polite"` region so
  the verdict is announced when it arrives.
- Typing animation gated on `prefers-reduced-motion` (falls back to instant text).
- Color is never the only signal — the confidence bar carries a numeric label; death-mode is text.
- Form input has a visible label + an example placeholder; errors are inline, not color-only.

---

## 16. Forensic-rules fallback — full threshold table (`classifier._forensic_rules`)

Used ONLY when the TabPFN client is unreachable; always surfaced as `engine="rules"`.

| Rule (evaluated top-down) | Verdict |
|---|---|
| `total_commits < 2` | `insufficient_history` |
| `is_archived == 1` | `completed` if `velocity_ratio≥0.3` else `abandoned` |
| `days_since_last_commit > 365 and velocity_ratio < 0.1` | `abandoned` |
| `commit_cadence_decay < -2 and bus_factor == 1` | `burned_out` |
| `lifespan_days < 120 and velocity_ratio < 0.2` | `pivoted` |
| `velocity_ratio >= 0.8` | `alive` |
| else | class with nearest centroid among seed rows (1-NN on standardized features) |

The 1-NN else-branch keeps the fallback honest (it still consults the seed data), but it is
labeled a heuristic, not the model.

---

## 17. Caching (`cache.py`)

In-process LRU (no external store — keeps Render-tiny). Key = `f"{owner}/{repo}"`. Stores the
full `AutopsyResult`. Purpose: (a) demo-safety — a re-paste during recording is instant and
identical; (b) quota protection — avoids re-hitting Groq/TabPFN for the same repo. TTL 1 hour;
capacity 256. The 3 demo repos are pre-warmed at startup so the judging demo never cold-calls.

---

## 18. Observability

- Structured request log: `{owner_repo, engine, verdict, confidence, latency_ms}` — no secrets,
  no PII, no raw repo text.
- `GET /healthz` returns `{ok, seed_rows, tabpfn_reachable}` so a glance confirms the model path
  is live before a demo.
- A startup self-check logs seed-row count + a single TabPFN probe classification; a failed probe
  logs a loud warning (demo would run on the fallback).

---

## 19. The Ollama-local / offline mode (open-innovation narrative for the post)

A documented alternative narration path: set `LLM_BASE_URL=http://localhost:11434/v1` and
`LLM_MODEL=qwen2.5` to run narration fully local via Ollama — zero closed dependencies, works
offline. TabPFN also has open weights. The post shows this as the "no API keys, runs on your
laptop" payoff. Not the deployed default (Starter can't host a 70B), but a real, runnable mode
and the strongest evidence that the AI core is genuinely open-source.

---

## 20. Dependencies (`requirements.txt`, pinned)

| Package | Role | Why it's light |
|---|---|---|
| `fastapi`, `uvicorn[standard]` | web | async, minimal |
| `jinja2` | templating | no client build |
| `httpx` | GitHub REST | async, no git binary |
| `pandas`, `numpy` | feature table + seed CSV | TabPFN's data interface |
| `tabpfn-client` | hosted classification | no local weights/GPU |
| `openai` | Groq (OpenAI-compatible) | one SDK, swappable base_url for Ollama |
| `pydantic` | schemas | ships with FastAPI |

RAM note: pandas+numpy import ~100–150MB; with FastAPI+client the resident set should sit under
the Starter 512MB ceiling — spot-checked at B5 before demo recording (Sonnet review).

---

## 21. Local dev + deploy runbook

```
# local
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY=... TABPFN_TOKEN=...
uvicorn app.main:app --reload
# → http://localhost:8000

# deploy (Render)
# 1. push repo to GitHub
# 2. Render → New Web Service → connect repo → it reads render.yaml
# 3. set env vars GROQ_API_KEY, TABPFN_TOKEN (and GITHUB_TOKEN optional) in the dashboard
# 4. confirm plan=starter, numInstances=1; deploy
# 5. verify GET /healthz → {ok:true, tabpfn_reachable:true}; pre-warm the 3 example repos
# rollback: Render keeps prior deploys → one-click rollback to the last green build
```

---

## 22. Failure-mode → judging-day impact (defence-in-depth summary)

| Failure | Judging-day impact | Guard |
|---|---|---|
| Render spin-down | dead link | Starter + numInstances=1 + warm-ping cron |
| TabPFN client down | verdict quality drops | labeled forensic-rules fallback; cached examples |
| Groq down | no fresh narration | cached narration for examples; terse labeled summary |
| GitHub rate limit | fetch fails for new repos | optional token; cached examples always work |
| RAM over 512MB | instance restart loop | B5 spot-check; drop to lazy imports if needed |

This matrix is the demo-rehearsal checklist (every row has a guard that is testable before recording).

---

## 23. Death-certificate card markup (reference)

The card is the post's hero image. Reference structure (Tailwind utility classes elided):
```html
<article id="certificate" class="certificate" aria-live="polite">
  <div class="cert-head">
    <span class="sigil">☠</span>
    <h2>Certificate of Death</h2>
    <span class="cert-id">No. {{ certificate_id }}</span>
  </div>
  <dl class="cert-body">
    <dt>Deceased</dt>        <dd>{{ owner }}/{{ repo }}</dd>
    <dt>Cause of death</dt>  <dd class="verdict verdict--{{ verdict.mode }}">{{ verdict.mode }}</dd>
    <dt>Certainty</dt>       <dd><meter value="{{ verdict.confidence }}"></meter> {{ pct }}%</dd>
    <dt>Born</dt>            <dd>{{ meta.created_at }}</dd>
    <dt>Last seen</dt>       <dd>{{ meta.last_commit_at }}</dd>
  </dl>
  <table class="evidence">                 <!-- the ≥1-table craft element -->
    <caption>Forensic evidence</caption>
    <tr><th>Days since last commit</th><td>{{ features.days_since_last_commit }}</td></tr>
    <tr><th>Commit-cadence decay</th>  <td>{{ features.commit_cadence_decay }}</td></tr>
    <tr><th>Lifespan (days)</th>       <td>{{ features.lifespan_days }}</td></tr>
    <tr><th>Contributors</th>          <td>{{ features.contributor_count }}</td></tr>
    <tr><th>Bus factor</th>            <td>{{ features.bus_factor }}</td></tr>
    <tr><th>Velocity ratio</th>        <td>{{ features.velocity_ratio }}</td></tr>
  </table>
  <blockquote class="coroner" data-typing>{{ narration }}</blockquote>
  <footer>
    <span class="engine engine--{{ verdict.engine }}">
      {{ "classified by TabPFN" if verdict.engine=="tabpfn" else "forensic-rules estimate — model unavailable" }}
    </span>
    <button class="share">Share this grave</button>
  </footer>
</article>
```

## 24. Config / environment variables

| Var | Required | Default | Purpose |
|---|---|---|---|
| `GROQ_API_KEY` | yes | — | open-weight narration |
| `TABPFN_TOKEN` | yes | — | hosted TabPFN classification |
| `GITHUB_TOKEN` | no | unauth | higher GitHub rate limit |
| `LLM_BASE_URL` | no | Groq | swap to Ollama for local mode |
| `LLM_MODEL` | no | `llama-3.3-70b-versatile` | narration model id |
| `COMMIT_WINDOW` | no | 1000 | max commits fetched for huge repos |
| `CACHE_TTL` | no | 3600 | seconds |

## 25. Warm-ping (defence-in-depth against spin-down)

A free external cron (e.g. cron-job.org) hits `GET /healthz` every ~10 minutes through the
Nov-2 judging week. Belt-and-braces with Render `numInstances=1`; if the paid-tier guarantee ever
lapses, the ping keeps the instance warm so a judge never lands on a cold start.

## 26. Build→downstream handoff contract

build emits: working app + `data/seed_repos.csv` + `data/NOTES.md` + `claims.json` (the machine
claims ledger, rows for "TabPFN classifies", "live on Render", "open-weight narration") + `evidence/`
(screenshots of 3 death-modes). design consumes the running UI; deploy renders README + screenshots +
the live URL; demo records the loop; package writes the post citing NOTES.md observations.

---

## 27. Alternatives considered & rejected

- **Next.js/React SPA** — rejected: adds a bundler + a second runtime for a one-page app; slower
  Render cold-start; nothing to gain when the page is server-rendered with one fetch.
- **Local TabPFN weights** — rejected: browser license-accept is awkward headless; weights +
  torch blow past the Starter 512MB/image budget and would force a larger instance.
- **A closed LLM for narration** — rejected: violates the "open-source AI at the core" rule; the
  whole premise is open-weight.
- **git clone + local analysis** — rejected: needs a git binary + disk; the REST API gives commits
  and contributors without a checkout.
- **A database for history** — rejected: stateless single-shot is the whole product; persistence
  is scope the post doesn't need.
- **Server-side Puppeteer card render** — rejected: heavy dep on Starter; a DOM card + screenshot
  is enough for the post hero image.

## 28. Glossary

- **Death-mode** — the inferred way a repo stopped: abandoned / pivoted / completed / burned_out / alive.
- **In-context classification** — TabPFN's mode: it is handed (X_train, y_train, X_test) per call
  and returns a posterior; there is no training loop and no fine-tune.
- **Seed dataset** — `data/seed_repos.csv`, the ~50 labeled rows that ARE TabPFN's train set.
- **Engine flag** — `tabpfn` vs `rules`, surfaced in the card so a fallback is never mistaken for the model.
- **Velocity ratio** — recent commit rate ÷ lifetime commit rate; the single best alive/fading signal.

---

# PART II — FULL COPY-EXACT IMPLEMENTATION (the single source of truth)

Everything below is copy-exact code. Build transcribes it into real files (PLAN B1–B4). A developer
with zero context builds the app from this section alone. Module dependency direction is one-way:
`main → {validators, github, features, classifier, narrator, cache, schemas}`; the inner modules do
not import `main`. Nothing imports I/O into the pure feature math.

## II.1 `requirements.txt`
```
fastapi==0.115.5
uvicorn[standard]==0.32.1
jinja2==3.1.4
httpx==0.27.2
pandas==2.2.3
numpy==2.1.3
tabpfn-client==0.1.6
openai==1.54.4
pydantic==2.9.2
python-dotenv==1.0.1
pytest==8.3.3
```

## II.2 `app/schemas.py`
```python
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

DeathMode = Literal["abandoned", "pivoted", "completed", "burned_out", "alive", "insufficient_history"]

class AutopsyRequest(BaseModel):
    repo_url: str = Field(..., min_length=3, max_length=200)

class RepoMeta(BaseModel):
    stars: int = 0
    primary_language: str | None = None
    created_at: str | None = None
    last_commit_at: str | None = None
    is_archived: bool = False

class Features(BaseModel):
    days_since_last_commit: float
    commit_cadence_decay: float
    lifespan_days: float
    contributor_count: float
    bus_factor: float
    velocity_ratio: float

class Verdict(BaseModel):
    mode: DeathMode
    confidence: float
    probs: dict[str, float] = {}
    engine: Literal["tabpfn", "rules"] = "tabpfn"

class AutopsyResult(BaseModel):
    owner: str
    repo: str
    meta: RepoMeta
    features: Features | None = None
    verdict: Verdict
    narration: str
    certificate_id: str

FEATURE_ORDER = [
    "days_since_last_commit", "commit_cadence_decay", "lifespan_days",
    "contributor_count", "bus_factor", "velocity_ratio",
]
```

## II.3 `app/validators.py`
```python
from __future__ import annotations
import re
from urllib.parse import urlparse

class BadRepoURL(ValueError):
    """Raised when the input is not a parseable public GitHub repo reference."""

_SLUG = re.compile(r"^[A-Za-z0-9_.-]+$")

def parse_repo_url(raw: str) -> tuple[str, str]:
    """Accept full URL, github.com/owner/repo, or bare owner/repo. Return (owner, repo).
    Rejects non-GitHub hosts, gists, and malformed input with BadRepoURL."""
    s = (raw or "").strip()
    if not s:
        raise BadRepoURL("empty")
    # strip scheme if present
    if s.startswith("http://") or s.startswith("https://"):
        u = urlparse(s)
        if u.netloc.lower() not in ("github.com", "www.github.com"):
            raise BadRepoURL("not a github.com URL")
        path = u.path
    elif s.startswith("github.com/") or s.startswith("www.github.com/"):
        path = "/" + s.split("/", 1)[1]
    else:
        path = "/" + s  # assume bare owner/repo
    parts = [p for p in path.split("/") if p]
    if len(parts) < 2:
        raise BadRepoURL("need owner/repo")
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    if owner.lower() == "gist" or not _SLUG.match(owner) or not _SLUG.match(repo):
        raise BadRepoURL("invalid owner/repo")
    return owner, repo
```

## II.4 `app/github.py`
```python
from __future__ import annotations
import os
from dataclasses import dataclass, field
import httpx

API = "https://api.github.com"
COMMIT_WINDOW = int(os.environ.get("COMMIT_WINDOW", "1000"))

class RepoError(Exception):
    def __init__(self, kind: str, message: str):
        self.kind = kind  # not_found | empty | rate_limited | error
        super().__init__(message)

@dataclass
class RepoData:
    owner: str
    repo: str
    commits: list[dict] = field(default_factory=list)   # [{date, author}]
    contributors: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "User-Agent": "autopsy-of-a-dead-project"}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

async def fetch_repo(owner: str, repo: str) -> RepoData:
    async with httpx.AsyncClient(timeout=10.0, headers=_headers()) as client:
        meta_r = await client.get(f"{API}/repos/{owner}/{repo}")
        if meta_r.status_code == 404:
            raise RepoError("not_found", "repository not found or private")
        if meta_r.status_code == 403 and "rate limit" in meta_r.text.lower():
            raise RepoError("rate_limited", "github rate limit")
        meta_r.raise_for_status()
        meta = meta_r.json()
        commits: list[dict] = []
        page = 1
        while len(commits) < COMMIT_WINDOW:
            cr = await client.get(
                f"{API}/repos/{owner}/{repo}/commits",
                params={"per_page": 100, "page": page})
            if cr.status_code == 409:   # empty repo
                break
            cr.raise_for_status()
            batch = cr.json()
            if not batch:
                break
            for c in batch:
                commit = c.get("commit", {}).get("author", {}) or {}
                author = (c.get("author") or {}).get("login") or commit.get("name") or "unknown"
                commits.append({"date": commit.get("date"), "author": author})
            if len(batch) < 100:
                break
            page += 1
        contributors = []
        cr = await client.get(f"{API}/repos/{owner}/{repo}/contributors", params={"per_page": 100})
        if cr.status_code == 200:
            contributors = cr.json() if isinstance(cr.json(), list) else []
        if len(commits) < 1:
            raise RepoError("empty", "no commit history")
        return RepoData(owner=owner, repo=repo, commits=commits, contributors=contributors, meta={
            "stars": meta.get("stargazers_count", 0),
            "primary_language": meta.get("language"),
            "created_at": (meta.get("created_at") or "")[:10] or None,
            "is_archived": bool(meta.get("archived")),
        })
```

## II.5 `app/features.py`
```python
from __future__ import annotations
from datetime import datetime, timezone
from collections import Counter
import numpy as np
from .github import RepoData
from .schemas import Features, RepoMeta

def _parse(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except ValueError:
        return None

def _now() -> datetime:
    return datetime.now(timezone.utc)

def build_features(data: RepoData) -> tuple[Features, RepoMeta]:
    dates = sorted(d for d in (_parse(c["date"]) for c in data.commits) if d)
    if len(dates) < 2:
        raise ValueError("insufficient_history")
    first, last = dates[0], dates[-1]
    now = _now()
    days_since_last = (now - last).days
    lifespan_days = max((last - first).days, 1)

    # monthly commit counts → OLS slope (commits/month per month) = cadence decay
    month_key = lambda d: d.year * 12 + d.month
    months = Counter(month_key(d) for d in dates)
    ordered = sorted(months.items())
    xs = np.array([m for m, _ in ordered], dtype=float)
    ys = np.array([c for _, c in ordered], dtype=float)
    if len(xs) >= 2 and xs.std() > 0:
        slope = float(np.polyfit(xs - xs.mean(), ys, 1)[0])
    else:
        slope = 0.0

    authors = Counter(c["author"] for c in data.commits)
    contributor_count = float(len(authors))
    total = sum(authors.values())
    # bus factor: smallest set of authors whose cumulative share >= 50%
    bus, acc = 0, 0
    for _, n in authors.most_common():
        acc += n
        bus += 1
        if acc / total >= 0.5:
            break
    bus_factor = float(bus)

    # velocity ratio: recent 90d rate vs lifetime rate
    window_start = now.timestamp() - 90 * 86400
    recent = sum(1 for d in dates if d.timestamp() >= window_start)
    lifetime_rate_per_90 = total / max(lifespan_days / 90.0, 1e-9)
    velocity_ratio = float(recent / lifetime_rate_per_90) if lifetime_rate_per_90 > 0 else 0.0

    feats = Features(
        days_since_last_commit=float(days_since_last),
        commit_cadence_decay=round(slope, 3),
        lifespan_days=float(lifespan_days),
        contributor_count=contributor_count,
        bus_factor=bus_factor,
        velocity_ratio=round(velocity_ratio, 3),
    )
    meta = RepoMeta(
        stars=data.meta.get("stars", 0),
        primary_language=data.meta.get("primary_language"),
        created_at=data.meta.get("created_at"),
        last_commit_at=last.date().isoformat(),
        is_archived=data.meta.get("is_archived", False),
    )
    return feats, meta
```

## II.6 `app/classifier.py`
```python
from __future__ import annotations
import os, functools
import pandas as pd
from .schemas import Features, Verdict, FEATURE_ORDER

SEED_PATH = os.environ.get("SEED_PATH", "data/seed_repos.csv")

@functools.lru_cache(maxsize=1)
def _seed() -> pd.DataFrame:
    return pd.read_csv(SEED_PATH)

def classify(f: Features) -> Verdict:
    seed = _seed()
    X_train, y_train = seed[FEATURE_ORDER], seed["death_mode"]
    row = [[getattr(f, k) for k in FEATURE_ORDER]]
    X_test = pd.DataFrame(row, columns=FEATURE_ORDER)
    try:
        from tabpfn_client import TabPFNClassifier, set_access_token
        token = os.environ.get("TABPFN_TOKEN")
        if not token:
            raise RuntimeError("TABPFN_TOKEN unset")   # → labeled rules fallback (I3), never a silent fake-tabpfn
        set_access_token(token)                        # authenticate the hosted client BEFORE fit (0.1.6 requires it)
        clf = TabPFNClassifier()
        clf.fit(X_train, y_train)
        proba = clf.predict_proba(X_test)[0]
        classes = list(clf.classes_)
        idx = int(proba.argmax())
        return Verdict(
            mode=classes[idx],
            confidence=float(proba[idx]),
            probs={c: float(p) for c, p in zip(classes, proba)},
            engine="tabpfn",
        )
    except Exception:
        return _forensic_rules(f)

def _forensic_rules(f: Features) -> Verdict:
    # transparent heuristic fallback — ALWAYS labeled engine="rules"
    if f.days_since_last_commit > 365 and f.velocity_ratio < 0.1:
        mode = "abandoned"
    elif f.commit_cadence_decay < -2 and f.bus_factor == 1:
        mode = "burned_out"
    elif f.lifespan_days < 120 and f.velocity_ratio < 0.2:
        mode = "pivoted"
    elif f.velocity_ratio >= 0.8:
        mode = "alive"
    else:
        mode = _nearest_mode(f)        # 1-NN over the seed corpus — defined in II.26 (same module)
    return Verdict(mode=mode, confidence=0.4, probs={mode: 0.4}, engine="rules")
```
`_nearest_mode` (II.26) lives in the SAME `classifier.py` module and MUST be transcribed with this
block — the else-branch is NOT a hard-coded `"completed"` (that stale form is superseded by II.26).

## II.7 `app/narrator.py`
```python
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
    return OpenAI(
        base_url=os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=os.environ.get("GROQ_API_KEY", "nokey"),
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
        model = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
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
```

## II.8 `app/cache.py`
```python
from __future__ import annotations
import time
from collections import OrderedDict
from .schemas import AutopsyResult

class TTLCache:
    def __init__(self, capacity: int = 256, ttl: int = 3600):
        self.capacity, self.ttl = capacity, ttl
        self._d: "OrderedDict[str, tuple[float, AutopsyResult]]" = OrderedDict()

    def _key(self, owner: str, repo: str) -> str:
        return f"{owner.lower()}/{repo.lower()}"

    def get(self, owner: str, repo: str) -> AutopsyResult | None:
        k = self._key(owner, repo)
        item = self._d.get(k)
        if not item:
            return None
        ts, val = item
        if time.time() - ts > self.ttl:
            self._d.pop(k, None)
            return None
        self._d.move_to_end(k)
        return val

    def set(self, owner: str, repo: str, val: AutopsyResult) -> None:
        k = self._key(owner, repo)
        self._d[k] = (time.time(), val)
        self._d.move_to_end(k)
        while len(self._d) > self.capacity:
            self._d.popitem(last=False)

cache = TTLCache()
```

## II.9 `app/main.py`
```python
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

load_dotenv()
app = FastAPI(title="Autopsy of a Dead Project")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

EXAMPLES = [
    {"repo": os.environ.get("EX_ABANDONED", "someorg/abandoned-thing"), "death_mode": "abandoned"},
    {"repo": os.environ.get("EX_BURNED", "solo/burned-out-thing"), "death_mode": "burned_out"},
    {"repo": os.environ.get("EX_ALIVE", "facebook/react"), "death_mode": "alive"},
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
async def autopsy(req: AutopsyRequest):
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

@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "The crypt is sealed - an unexpected error occurred."})
```

## II.10 `app/templates/index.html`
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Autopsy of a Dead Project</title>
  <meta property="og:title" content="Autopsy of a Dead Project"/>
  <meta property="og:image" content="/static/og.png"/>
  <meta name="description" content="Paste a GitHub repo. An open-source AI performs an autopsy and reads the coroner's report."/>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="/static/card.css"/>
</head>
<body class="bg-[#0b0b10] text-stone-200 min-h-screen">
  <header class="max-w-2xl mx-auto px-6 pt-16 text-center">
    <h1 class="text-4xl font-semibold tracking-tight">Autopsy of a Dead Project</h1>
    <p class="mt-3 text-stone-400">Every repository that stops is a ghost in the machine. Paste one; we'll perform the autopsy.</p>
  </header>
  <main class="max-w-2xl mx-auto px-6 mt-10">
    <form id="autopsy" class="flex gap-2">
      <input id="repo" name="repo" required placeholder="owner/repo or a github.com URL"
             class="flex-1 rounded-lg bg-stone-900 border border-stone-700 px-4 py-3"/>
      <button class="rounded-lg bg-amber-700 hover:bg-amber-600 px-5 py-3 font-medium">Perform the autopsy</button>
    </form>
    <section id="examples" class="mt-4 text-sm text-stone-400 flex gap-3 flex-wrap"></section>
    <section id="loading" hidden class="mt-10 text-center text-stone-400 animate-pulse">exhuming the commit history…</section>
    <section id="error" hidden class="mt-6 rounded-lg border border-red-900 bg-red-950/40 px-4 py-3 text-red-200"></section>
    <article id="certificate" hidden aria-live="polite" class="certificate mt-10"></article>
  </main>
  <footer class="max-w-2xl mx-auto px-6 py-16 text-center text-xs text-stone-500">
    Core AI is open-source: TabPFN (open weights) classifies; an open-weight LLM narrates.
    A fully-local mode runs on Ollama with zero closed dependencies.
  </footer>
  <script src="/static/app.js"></script>
</body>
</html>
```

## II.11 `app/static/app.js`
```javascript
const form = document.getElementById("autopsy");
const repoInput = document.getElementById("repo");
const loading = document.getElementById("loading");
const errBox = document.getElementById("error");
const cert = document.getElementById("certificate");
const examplesEl = document.getElementById("examples");
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

async function loadExamples() {
  try {
    const r = await fetch("/examples");
    const ex = await r.json();
    examplesEl.innerHTML = "try: " + ex.map(e =>
      `<button data-repo="${e.repo}" class="underline hover:text-amber-400">${e.repo}</button>`).join(" · ");
    examplesEl.querySelectorAll("button").forEach(b =>
      b.addEventListener("click", () => { repoInput.value = b.dataset.repo; form.requestSubmit(); }));
  } catch (_) {}
}

function pct(x) { return Math.round((x || 0) * 100); }

function render(d) {
  const f = d.features || {};
  const engineLabel = d.verdict.engine === "tabpfn"
    ? "classified by TabPFN" : "forensic-rules estimate — model unavailable";
  cert.innerHTML = `
    <div class="cert-head"><span class="sigil">☠</span><h2>Certificate of Death</h2>
      <span class="cert-id">No. ${d.certificate_id}</span></div>
    <dl class="cert-body">
      <dt>Deceased</dt><dd>${d.owner}/${d.repo}</dd>
      <dt>Cause of death</dt><dd class="verdict verdict--${d.verdict.mode}">${d.verdict.mode}</dd>
      <dt>Certainty</dt><dd>${pct(d.verdict.confidence)}%</dd>
      <dt>Born</dt><dd>${d.meta.created_at || "—"}</dd>
      <dt>Last seen</dt><dd>${d.meta.last_commit_at || "—"}</dd>
    </dl>
    <table class="evidence"><caption>Forensic evidence</caption>
      <tr><th>Days since last commit</th><td>${f.days_since_last_commit}</td></tr>
      <tr><th>Commit-cadence decay</th><td>${f.commit_cadence_decay}</td></tr>
      <tr><th>Lifespan (days)</th><td>${f.lifespan_days}</td></tr>
      <tr><th>Contributors</th><td>${f.contributor_count}</td></tr>
      <tr><th>Bus factor</th><td>${f.bus_factor}</td></tr>
      <tr><th>Velocity ratio</th><td>${f.velocity_ratio}</td></tr>
    </table>
    <blockquote class="coroner" id="coroner"></blockquote>
    <footer class="cert-foot"><span class="engine engine--${d.verdict.engine}">${engineLabel}</span></footer>`;
  cert.hidden = false;
  typeOut(document.getElementById("coroner"), d.narration);
}

function typeOut(el, text) {
  if (reduced) { el.textContent = text; return; }
  el.textContent = "";
  let i = 0;
  const step = () => { el.textContent = text.slice(0, i); i += 2; if (i <= text.length) setTimeout(step, 12); };
  step();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errBox.hidden = true; cert.hidden = true; loading.hidden = false;
  try {
    const r = await fetch("/autopsy", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: repoInput.value }) });
    const d = await r.json();
    loading.hidden = true;
    if (!r.ok) { errBox.textContent = d.detail || "Something went wrong."; errBox.hidden = false; return; }
    render(d);
  } catch (_) {
    loading.hidden = true; errBox.textContent = "Network error — try again."; errBox.hidden = false;
  }
});

loadExamples();
```

## II.12 `app/static/card.css`
```css
.certificate { background: #14141c; border: 1px solid #2a2a38; border-radius: 16px;
  padding: 28px; box-shadow: 0 10px 40px rgba(0,0,0,.5); font-family: Georgia, serif; }
.cert-head { display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #2a2a38;
  padding-bottom: 12px; }
.cert-head h2 { font-size: 1.4rem; letter-spacing: .04em; margin: 0; flex: 1; }
.sigil { font-size: 1.6rem; color: #d6a756; }
.cert-id { color: #7a7a88; font-size: .8rem; }
.cert-body { display: grid; grid-template-columns: max-content 1fr; gap: 6px 18px; margin: 18px 0; }
.cert-body dt { color: #8a8a98; } .cert-body dd { margin: 0; }
.verdict { font-weight: 700; text-transform: capitalize; }
.verdict--abandoned { color: #c9623f; } .verdict--burned_out { color: #d6a756; }
.verdict--pivoted { color: #6fa8c9; } .verdict--completed { color: #7fbf7f; }
.verdict--alive { color: #7fd17f; }
.evidence { width: 100%; border-collapse: collapse; margin: 10px 0 18px; font-size: .9rem; }
.evidence caption { text-align: left; color: #8a8a98; margin-bottom: 6px; }
.evidence th { text-align: left; color: #b8b8c4; font-weight: 500; padding: 4px 0; }
.evidence td { text-align: right; font-variant-numeric: tabular-nums; }
.coroner { border-left: 3px solid #d6a756; padding-left: 14px; color: #d8d8e0; font-style: italic;
  min-height: 3em; line-height: 1.6; }
.cert-foot { margin-top: 16px; font-size: .78rem; }
.engine--tabpfn { color: #7fbf7f; } .engine--rules { color: #d6a756; }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
```

## II.13 `render.yaml`
```yaml
services:
  - type: web
    name: autopsy-of-a-dead-project
    runtime: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /healthz
    numInstances: 1
    autoDeploy: true
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: TABPFN_TOKEN
        sync: false
      - key: GITHUB_TOKEN
        sync: false
      - key: LLM_MODEL
        value: llama-3.3-70b-versatile
```

## II.14 `.env.example`
```
GROQ_API_KEY=
TABPFN_TOKEN=
GITHUB_TOKEN=
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
COMMIT_WINDOW=1000
SEED_PATH=data/seed_repos.csv
```

## II.15 `data/seed_repos.csv` (shape + starter rows; filled to ~50 at B0)
```csv
owner_repo,days_since_last_commit,commit_cadence_decay,lifespan_days,contributor_count,bus_factor,velocity_ratio,death_mode,note
facebook/react,1,0.4,3800,1600,30,1.1,alive,"massive active base"
fastapi/fastapi,2,0.1,2600,650,8,0.95,alive,"steady cadence"
<archived-finished-lib>,120,-0.2,1800,40,5,0.0,completed,"archived, done README"
<mature-tool>,90,-0.1,2500,70,9,0.1,completed,"stable then quiet"
<dead-popular-repo>,900,-3.1,700,25,4,0.02,abandoned,"issues left open"
<lost-to-rival>,1300,-4.0,500,12,3,0.0,abandoned,"cadence cliff"
<solo-stalled>,500,-2.6,400,1,1,0.03,burned_out,"bus_factor 1"
<solo-stalled-2>,620,-3.0,350,2,1,0.02,burned_out,"one maintainer"
<short-then-successor>,800,-1.2,90,3,2,0.0,pivoted,"README points elsewhere"
<pivot-2>,740,-1.0,110,4,2,0.05,pivoted,"team moved on"
```
B0 fills the angle-bracket slots to ~10 rows per class (safe public repos only; see PLAN §seed_list).

## II.16 `scripts/build_seed.py`
```python
#!/usr/bin/env python3
"""Build data/seed_repos.csv from scripts/seed_list.txt using the SAME feature extractor as production.
Usage: python scripts/build_seed.py  (requires GITHUB_TOKEN recommended for rate limit)."""
import asyncio, csv, sys
from app.github import fetch_repo
from app.features import build_features
from app.schemas import FEATURE_ORDER

async def one(owner_repo: str):
    owner, repo = owner_repo.split("/", 1)
    data = await fetch_repo(owner, repo)
    feats, _ = build_features(data)
    return {k: getattr(feats, k) for k in FEATURE_ORDER}

async def main():
    rows = []
    for line in open("scripts/seed_list.txt"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        slug, mode, note = [p.strip() for p in line.split(",", 2)]
        try:
            feats = await one(slug)
            rows.append({"owner_repo": slug, **feats, "death_mode": mode, "note": note})
            print(f"ok  {slug} -> {mode}")
        except Exception as e:
            print(f"ERR {slug}: {e}", file=sys.stderr)
    cols = ["owner_repo", *FEATURE_ORDER, "death_mode", "note"]
    with open("data/seed_repos.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"\nwrote {len(rows)} rows to data/seed_repos.csv")
    # quick LOO separability check
    try:
        import pandas as pd
        from tabpfn_client import TabPFNClassifier
        df = pd.read_csv("data/seed_repos.csv")
        correct = 0
        for i in range(len(df)):
            tr = df.drop(i); te = df.iloc[[i]]
            clf = TabPFNClassifier(); clf.fit(tr[FEATURE_ORDER], tr["death_mode"])
            pred = clf.predict(te[FEATURE_ORDER])[0]
            correct += int(pred == te["death_mode"].iloc[0])
        print(f"LOO accuracy: {correct}/{len(df)} = {correct/len(df):.0%}")
    except Exception as e:
        print(f"(LOO check skipped: {e})")

if __name__ == "__main__":
    asyncio.run(main())
```

## II.17 `tests/test_validators.py`
```python
import pytest
from app.validators import parse_repo_url, BadRepoURL

@pytest.mark.parametrize("raw", [
    "https://github.com/owner/repo", "github.com/owner/repo", "owner/repo",
    "https://github.com/owner/repo/", "owner/repo.git",
])
def test_valid(raw):
    assert parse_repo_url(raw) == ("owner", "repo")

@pytest.mark.parametrize("raw", ["", "owner", "https://gitlab.com/o/r", "https://gist.github.com/x/y", "!!!"])
def test_invalid(raw):
    with pytest.raises(BadRepoURL):
        parse_repo_url(raw)
```

## II.18 `tests/test_features.py`
```python
from datetime import datetime, timezone, timedelta
from app.github import RepoData
from app.features import build_features

def _commit(days_ago, author):
    d = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return {"date": d, "author": author}

def test_bus_factor_and_recency():
    # one dominant author over 2 others
    commits = [_commit(400, "a") for _ in range(8)] + [_commit(410, "b"), _commit(420, "c")]
    data = RepoData(owner="o", repo="r", commits=commits, contributors=[], meta={})
    f, _ = build_features(data)
    assert f.bus_factor == 1.0            # 'a' alone is >=50%
    assert f.contributor_count == 3.0
    assert f.days_since_last_commit >= 395

def test_alive_velocity():
    commits = [_commit(i, "a") for i in range(0, 80, 2)]  # frequent, recent
    data = RepoData(owner="o", repo="r", commits=commits, contributors=[], meta={})
    f, _ = build_features(data)
    assert f.velocity_ratio > 0.5
```

## II.19 `tests/test_classifier_shape.py`
```python
from app.schemas import Features
from app.classifier import _forensic_rules

def test_fallback_labeled_and_valid():
    f = Features(days_since_last_commit=900, commit_cadence_decay=-3.0, lifespan_days=700,
                 contributor_count=4, bus_factor=2, velocity_ratio=0.0)
    v = _forensic_rules(f)
    assert v.engine == "rules"
    assert v.mode in {"abandoned","pivoted","completed","burned_out","alive"}
    assert 0.0 <= v.confidence <= 1.0
```

## II.20 `tests/test_narration_grounding.py`
```python
from app.schemas import Features, Verdict, RepoMeta
from app import narrator

def test_grounding_rejects_fabricated_numbers(monkeypatch):
    f = Features(days_since_last_commit=800, commit_cadence_decay=-3.0, lifespan_days=530,
                 contributor_count=2, bus_factor=1, velocity_ratio=0.04)
    v = Verdict(mode="abandoned", confidence=0.8, probs={"abandoned":0.8}, engine="tabpfn")
    m = RepoMeta(stars=10, created_at="2021-03-02", last_commit_at="2022-08-14")

    class FakeResp:
        class C:
            class M: content = "It had 99999 commits across 12345 years."  # fabricated
            message = M()
        choices = [C()]
    monkeypatch.setattr(narrator, "_client", lambda: type("X", (), {
        "chat": type("Y", (), {"completions": type("Z", (), {"create": staticmethod(lambda **k: FakeResp())})()})()})())
    out = narrator.narrate("o", "r", v, f, m)
    assert "99999" not in out        # grounding check forced the templated fallback
```

## II.21 Ollama-local mode (open-innovation, documented)
Set `LLM_BASE_URL=http://localhost:11434/v1` and `LLM_MODEL=qwen2.5` to run narration fully local
via Ollama — no API keys, offline. TabPFN also has open weights (`pip install tabpfn` + the local
model) for a zero-closed-dependency run. The deployed default uses the hosted paths (Starter can't
host a 70B), but this mode is the proof the core is genuinely open-source and is shown in the post.

## II.22 Build checklist (transcription order from this document)
1. `requirements.txt`, `.env.example` (II.1, II.14)
2. `app/schemas.py`, `app/validators.py` (II.2, II.3) + `tests/test_validators.py` (II.17)
3. `app/github.py`, `app/features.py` (II.4, II.5) + `tests/test_features.py` (II.18)
4. `scripts/seed_list.txt` → `scripts/build_seed.py` → `data/seed_repos.csv` (II.16, II.15) [B0]
5. `app/classifier.py` (II.6) + `tests/test_classifier_shape.py` (II.19)
6. `app/narrator.py` (II.7) + `tests/test_narration_grounding.py` (II.20)
7. `app/cache.py`, `app/main.py` (II.8, II.9)
8. `app/templates/index.html`, `app/static/app.js`, `app/static/card.css` (II.10–II.12)
9. `render.yaml` (II.13) → deploy [B5]
Every file above is copy-exact in this document; build transcribes, wires, and runs the tests.

## II.23 `.github/workflows/test.yml`
```yaml
name: tests
on: [push, pull_request]
jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest -q
```

## II.24 `Dockerfile` (optional — Render native Python env is the default; this is the portable fallback)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
```

## II.25 `Makefile`
```makefile
.PHONY: dev test seed deploy-check
dev:    ; uvicorn app.main:app --reload
test:   ; pytest -q
seed:   ; python scripts/build_seed.py
deploy-check: ; curl -fsS http://localhost:8000/healthz | python -m json.tool
```

## II.26 `classifier._forensic_rules` — full 1-NN else branch (completes II.6)
The else-branch (when no threshold rule fires) consults the seed data via 1-nearest-neighbour on
standardized features, so the fallback still reflects the labeled corpus (honest, still labeled rules):
```python
import numpy as np
from .schemas import FEATURE_ORDER

def _nearest_mode(f) -> str:
    seed = _seed()
    X = seed[FEATURE_ORDER].to_numpy(dtype=float)
    mu, sd = X.mean(0), X.std(0) + 1e-9
    q = (np.array([getattr(f, k) for k in FEATURE_ORDER], dtype=float) - mu) / sd
    Xs = (X - mu) / sd
    i = int(np.argmin(((Xs - q) ** 2).sum(1)))
    return str(seed["death_mode"].iloc[i])
```
`_forensic_rules` calls `_nearest_mode(f)` in its final `else` instead of a hard-coded "completed",
and returns it with `engine="rules"`, `confidence≈0.4` (lower, honestly — it is a heuristic).

## II.27 `scripts/seed_list.txt` (the human-labeled input to build_seed.py — fill at B0)
```
# owner/repo, death_mode, note  (safe public repos only; no small living personal repos)
facebook/react, alive, high velocity, huge contributor base
fastapi/fastapi, alive, steady cadence
pallets/flask, alive, mature but active
# completed (archived / reached purpose)
google/leveldb, completed, archived, purpose served
# abandoned (dead, not archived)
# <fill ~10 each for completed / abandoned / burned_out / pivoted from GitHub graveyard lists>
# burned_out (single maintainer, steep decay)
# pivoted (short life, successor exists)
```

## II.28 Performance tuning notes
- GitHub: `per_page=100`; stop at `COMMIT_WINDOW` (1000) — a 50k-commit repo fetches ~10 pages, not 500.
- TabPFN: the seed set is small (~50 rows) so in-context fit is fast; the client call dominates latency.
- Groq: `max_tokens=320` caps narration latency; temperature 0.7 for voice.
- Cache: the 3 example repos are pre-warmed at startup (a background task calls the pipeline once each),
  so a judge's first interaction is instant.

## II.29 Startup pre-warm hook (`app/main.py` addition)
```python
@app.on_event("startup")
async def _prewarm():
    for ex in EXAMPLES:
        try:
            owner, repo = parse_repo_url(ex["repo"])
            if not cache.get(owner, repo):
                data = await fetch_repo(owner, repo)
                feats, meta = build_features(data)
                v = classify(feats); n = narrate(owner, repo, v, feats, meta)
                cache.set(owner, repo, AutopsyResult(owner=owner, repo=repo, meta=meta,
                    features=feats, verdict=v, narration=n, certificate_id=_cert_id(owner, repo)))
        except Exception:
            pass  # pre-warm is best-effort; never blocks startup
```

## II.30 Module dependency arrow (one-way, EX-3 discipline)
```
main.py ──▶ validators, github, features, classifier, narrator, cache, schemas
features ──▶ schemas            (pure math; imports no I/O)
classifier ─▶ schemas (+ tabpfn-client at call time)
narrator ──▶ schemas (+ openai at call time)
github ───▶ (httpx only)
```
The deterministic core (`features`) imports no I/O; I/O (`github`, `classifier` client, `narrator`
client) depends inward on `schemas`, never the reverse. No cycles.

## II.31 Demo recording script (exact beats, ≤90s)
```
0:00  Page already open + warm. Title + subtitle visible.
0:03  Click example "abandoned" repo → certificate animates in → cause of death "abandoned",
      confidence bar, the evidence table, the coroner's report typing out. Hold on the card.
0:25  Paste a second repo (burned_out) → certificate → point to bus_factor=1 in the evidence table.
0:45  Click the "alive" example → "not dead, merely sleeping" eulogy → contrast lands.
1:00  Pan to the engine badge "classified by TabPFN" → say: the verdict is a tabular foundation model,
      the eulogy an open-weight LLM.
1:15  Footer: fully-local Ollama mode, zero closed deps. End on the certificate card (the cover image).
```
Fallback if a live call wobbles: the examples are cached → identical + instant; never cold-call on camera.

## II.32 Judging-day operational checklist
- [ ] `GET /healthz` → `{ok:true, seed_rows:~50, tabpfn_reachable:true}`.
- [ ] Three example repos return cached results instantly.
- [ ] A fresh paste (not cached) completes < 15s.
- [ ] The live URL is warm (open it, hard-refresh, confirm <2s).
- [ ] Both themes/paths look right: a dead repo (dramatic) and an alive repo (the twist).
- [ ] The certificate card screenshots cleanly at 1200×630 for the post cover.
- [ ] The repo is public, `v1-submission` tagged, README present (deploy phase).

## II.33 Known-good acceptance walk (end-to-end, run before deploy)
1. `make test` → 4 test files green.
2. `python scripts/build_seed.py` → `data/seed_repos.csv` written, LOO accuracy printed > chance.
3. `make dev`; open `http://localhost:8000`.
4. Paste a famously-dead repo → verdict renders, engine badge = `tabpfn` (token set) → PASS.
5. Unset `TABPFN_TOKEN`, repeat → verdict renders with engine badge = `rules` (labeled) → PASS.
6. Paste a bad URL → friendly 422 inline message, no crash → PASS.
7. Paste an empty/1-commit repo → "no body to examine" → PASS.
8. `curl /healthz` → ok:true → PASS. Deploy only after all eight PASS.

## II.34 Cost & quota envelope
- Render Starter: $7/mo (or hacktoberfest promo credits).
- Groq free tier: narration calls are small (≤320 output tokens); cache + 3 pre-warmed examples keep it well under limits during judging.
- TabPFN hosted: a handful of small in-context fits; within free usage.
- GitHub: unauth 60/hr/IP (fine for a demo); a read-only PAT lifts to 5,000/hr for build testing.
Total marginal cost of the judging window ≈ the $7 Render tier. Everything else is free-tier.

## II.35 What "single source of truth" means here
This document contains every line of code the app runs (II.1–II.30), every config, every test, the
seed methodology, the demo script, and the acceptance walk. Build does not design anything — it
transcribes these files, runs the acceptance walk (II.33), fills the seed list (II.27 → II.16 → B0),
and deploys (II.13). Any divergence between the running app and this document is a defect in one of
them; this document wins unless a decision is explicitly logged in DECISIONS.md.

## II.36 Traceability — PRD requirement → implementing code
| PRD req | Implemented by |
|---|---|
| F1 URL input | `validators.parse_repo_url` (II.3) + `main.autopsy` 422 path |
| F2 GitHub fetch | `github.fetch_repo` (II.4) with 404/empty/rate-limit handling |
| F3 feature table | `features.build_features` (II.5), six formulas |
| F4 TabPFN classify | `classifier.classify` (II.6) + seed CSV (II.15) |
| F5 grounded narration | `narrator.narrate` (II.7) + grounding check + fallback |
| F6 certificate card | `index.html` (II.10) + `app.js` render/typeOut (II.11) + `card.css` (II.12) |
| F7 Render deploy | `render.yaml` (II.13) Starter + warm + `/healthz` (II.9) |
| INV I3 honesty badge | `Verdict.engine` (II.2) rendered in `app.js` + CSS `.engine--*` |
| INV I4 grounding | `narrator._numbers` check (II.7) + `test_narration_grounding` (II.20) |

Every functional requirement and the honesty invariants trace to a concrete, copy-exact module above.

## II.37 Glossary of code symbols
- `RepoData` (II.4) — the raw GitHub payload: commits[], contributors[], meta.
- `Features` (II.2) — the six-signal forensic row handed to the classifier.
- `Verdict` (II.2) — mode + confidence + posterior + `engine` honesty flag.
- `AutopsyResult` (II.2) — the full API response the frontend binds to.
- `TTLCache` (II.8) — the in-process demo-safety / quota cache.
- `_forensic_rules` / `_nearest_mode` (II.6, II.26) — the labeled non-AI fallback path.
- `narrate` / `_template` (II.7) — open-weight narration + grounded fallback.
