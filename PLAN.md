# PLAN — Autopsy of a Dead Project (phased, 1-day SPRINT)

**PRE-BUILD (do before Day 1):** obtain + verify `TABPFN_TOKEN` (tabpfn-client registration may need an email-confirm loop — a blocked B2 mid-day is avoidable) and `GROQ_API_KEY`; confirm the Render account + Starter credits. See .input-manifest.json.

Each phase ≤ a half-day chunk; ordered so the linchpin (seed dataset) and the load-bearing core (TabPFN) are proven before UI polish.

## Build phases
- **B0 · Seed dataset (LINCHPIN, first).** Curate `data/seed_repos.csv`: ~50 known repos (abandoned/pivoted/completed/burned-out/alive), each with the F3 feature row + label. Source from GitHub graveyard lists, famous archived repos, and a few alive controls. Validate feature→label separability before wiring anything. *Exit: CSV loads, classes are balanced-ish, a quick TabPFN sanity-fit separates them; capture 5–10 surprising labeling observations to `data/NOTES.md` (raw material for the post's best paragraphs — protects the heaviest axis).* **Tactic:** seed 15–20 obvious cases (very-active + explicitly-archived) to prove separability FIRST, then pad to 50.
- **B1 · Feature extractor.** `github.py` + `features.py`: given owner/repo, fetch commits+contributors, build the feature row. Handle 404 / empty / archived / huge repos (cap commit window). *Exit: any public repo → a numeric feature row; unit tests pass.*
- **B2 · TabPFN classifier.** `classifier.py`: load seed CSV as in-context train, classify the target, return (death_mode, confidence, probs). Transparent forensic-rules fallback if client unreachable. *Exit: 3 known repos classify sensibly; confidence returned.*
- **B3 · Groq narration.** `narrator.py`: verdict+features → a grounded coroner's report/eulogy (cites the real features, no invented numbers). *Exit: narration reads well, grounded, 120–200 words.*
- **B4 · Web UI (one page).** `index.html` + `main.py` routes: paste field, loading state, death-certificate card, typing animation, OG/cover image. *Exit: full loop works locally end-to-end.*
- **B5 · Deploy (Oracle Always-Free VM; ADR-005b).** Provision via `oci`/SSH; install Ollama + `ollama pull gemma2:2b`; uvicorn+nginx+systemd per ARCHITECTURE PART III runbook; open 80/443 in BOTH the OCI security list AND the instance firewall. NO render.yaml. Env: `GROQ_API_KEY`, `TABPFN_TOKEN`, optional `GITHUB_TOKEN`. *Exit: public URL responds <2s; full loop works live; spot-check RAM on Starter (512MB ceiling — pandas+numpy+tabpfn-client import footprint) before demo recording.*
- **B6 · Demo-prep handoff.** Pre-warm 3 demo repos (one per death-mode); capture screenshots for the post. *Exit: artifacts ready for design/demo/package phases.*

## Downstream (owned by later phases — do not build here)
- Design pass / screenshots carry the post → design + deploy.
- Demo GIF/video → demo.
- The dev.to POST (the deliverable) → package (docs-writer-grade).

## Skill-Ownership Map (routing pass SO-2)
Load-bearing judged-surface deliverables, each tagged with its registry owner in `owner: X @ phase`:
- **PRD / ARCHITECTURE / PLAN / DECISIONS / SECURITY / LIMITATIONS / SUBMISSION_STATUS** → owner: hackathon-forge @ forge
- **Application code + seed dataset + tests** → owner: implementation (build) @ build
- **claims.json + evidence/** → owner: build @ build (build scaffolds the ledger; verify fills rows; rendered downstream)
- **UI visual direction** → owner: design @ design
- **UI visual polish / revamp** → owner: ui-revamp @ design_forge
- **DESIGN_SYSTEM.md / brand.json / logo/OG set** → owner: design-forge @ design_forge
- **README** → owner: deploy-to-github @ deploy
- **Screenshots** → owner: deploy-to-github @ deploy
- **Live Render deployment** → owner: deploy-to-github @ deploy
- **Demo video/GIF** → owner: hackathon-demo @ demo
- **The dev.to blog post (THE entry) + submission bundle** → owner: hackathon-package @ package

## Risk→mitigation (from WINNER-BRIEF Risk Register)
R1 seed-dataset is the linchpin → B0 first. R2 Render durable warm → B5 min-instances=1. R3 Issues API cut → features from commits only. R5 label separability → validated at B0 exit. R6 Groq limits → cache + pre-warm. R8 theme reads as skin → read live challenge page on build day (DS-1), lean the coroner/eulogy narrative. R9 writing starved → timebox B0–B6, reserve a hard block for the post.

---

## Per-phase task checklists + acceptance tests

### B0 · Seed dataset (LINCHPIN)
- [ ] Draft the labeling rubric (PRD §16) and the 5-mode definitions.
- [ ] Collect 15–20 "obvious" repos first (very-active + explicitly-archived) to prove separability.
- [ ] Write a one-off `scripts/build_seed.py` that runs the real feature extractor over each seed repo → fills `seed_repos.csv` (features computed the SAME way as production, not by hand).
- [ ] Pad to ~50 rows, ~10 per class (±3).
- [ ] Validate: leave-one-out TabPFN fit; if classes bleed, refine features/labels.
- [ ] Capture 5–10 surprising observations → `data/NOTES.md`.
- **Acceptance:** CSV loads; 5 classes present; LOO accuracy visibly better than chance; NOTES.md has ≥5 entries.

### B1 · Feature extractor
- [ ] `github.py`: async fetch commits (windowed) + contributors + meta; 404/403/empty/archived handled.
- [ ] `features.py`: the six features per §5 formulas; context columns carried.
- [ ] Unit tests on a synthetic commit series (known decay slope, known bus factor).
- **Acceptance:** `test_features.py` green; a real repo → a full feature row in <4s.

### B2 · TabPFN classifier
- [ ] `classifier.py`: seed CSV as in-context train; `classify()` returns mode+confidence+probs+engine.
- [ ] `_forensic_rules` fallback (full threshold table, §16 ARCH) labeled `engine="rules"`.
- [ ] Startup self-check: log seed-row count + one probe classification.
- **Acceptance:** 3 known repos classify sensibly; fallback path labeled; `test_classifier_shape.py` green.

### B3 · Groq narration
- [ ] `narrator.py`: grounded system prompt; evidence block; one retry on a grounding-check failure.
- [ ] Register swap via `LLM_BASE_URL`/`LLM_MODEL` (Ollama-local ready).
- **Acceptance:** 120–200 words, no number absent from evidence; `test_narration_grounding.py` green.

### B4 · Web UI (one page)
- [ ] `index.html` + routes; paste field; loading state; certificate card; typing JS; `prefers-reduced-motion`.
- [ ] `/examples` (3 pre-warmed repos); engine badge; share button; OG image.
- **Acceptance:** full loop local end-to-end; card screenshot-clean at 1200×630; a11y checks (§18 PRD) pass.

### B5 · Deploy (Render, durable warm)
- [ ] `render.yaml` (Starter, numInstances=1, healthCheckPath); `requirements.txt` pinned.
- [ ] Env vars set; `/healthz` green incl `tabpfn_reachable`; RAM spot-check <512MB.
- [ ] External warm-ping cron on `/healthz`.
- **Acceptance:** public URL <2s warm; full loop live; healthz green.

### B6 · Demo-prep handoff
- [ ] Pre-warm 3 demo repos (abandoned / burned_out / alive); screenshot each certificate → `evidence/`.
- [ ] Emit `claims.json` rows (TabPFN-classifies, live-on-Render, open-weight-narration).
- **Acceptance:** 3 screenshots on disk; claims.json valid; handoff note to design/demo/package.

---

## Day-of timeline (1-day-equivalent, timeboxed to protect the post)
| Block | Phase | Hard stop |
|---|---|---|
| 0:00–0:20 | PRE-BUILD: tokens (TABPFN, GROQ), Render acct, **read the LIVE challenge page (DS-1)** | 0:20 |
| 0:20–2:30 | B0 seed dataset + NOTES.md | 2:30 |
| 2:30–3:30 | B1 feature extractor | 3:30 |
| 3:30–4:30 | B2 classifier (+fallback) | 4:30 |
| 4:30–5:15 | B3 narration | 5:15 |
| 5:15–7:00 | B4 UI | 7:00 |
| 7:00–8:00 | B5 deploy + warm | 8:00 |
| 8:00–8:30 | B6 demo-prep + screenshots | 8:30 |
| **8:30–END** | **THE POST (heaviest axis) — docs-writer-grade, reserved block** | publish ≤ Oct 31 18:00 WAT |

If any block overruns, cut app polish — never the post block.

---

## Demo runbook (for demo-rehearsal / demo phases)
1. Confirm `/healthz` green (tabpfn_reachable:true) and the 3 examples are warm/cached.
2. Record the loop: paste a famously-dead repo → autopsy → certificate types out → screenshot.
3. Show two more modes (an alive repo, a burned_out repo) for contrast.
4. Keep it <90s; the certificate card is the money shot (post hero image).
5. Fallback if a live call wobbles: use a cached example (identical, instant) — never a cold call on camera.

---

## Post-writing sub-plan (package phase — the deliverable)
- Pull the real numbers from B6 (engine mix, death-mode distribution, median latency) into a results table.
- Lead with the first-person hook; weave in the `data/NOTES.md` observations (what surprised me labeling 50 dead repos).
- Embed the demo GIF/video high; cover image = the death-certificate card.
- Explain the open-source-AI core honestly (TabPFN classify + open-weight narrate + Ollama-local).
- Tags `devchallenge` + `hf26challenge`; live link + repo link; ≥1 table; first-person number-in-title.

---

## Test matrix (what must be green before deploy)
| Test | Phase | Blocks |
|---|---|---|
| `test_validators.py` | B1 | deploy |
| `test_features.py` | B1 | deploy |
| `test_classifier_shape.py` | B2 | deploy |
| `test_narration_grounding.py` | B3 | deploy |
| manual: 3 death-modes classify sensibly | B2 | demo |
| manual: a11y (keyboard, reduced-motion, contrast) | B4 | deploy |
| manual: RAM <512MB on Starter | B5 | demo |

---

## Rollback / recovery
Render keeps prior deploys → one-click rollback to the last green build. If TabPFN or Groq is down
during judging, the labeled fallbacks keep the app honest and functional; cached examples always work.

---

## PRE-BUILD checklist (detailed — do before Day 1 clock starts)
- [ ] **TABPFN_TOKEN** — register at priorlabs.ai / the tabpfn-client flow; complete any email-confirm loop; `python -c "from tabpfn_client import TabPFNClassifier"` + a one-row probe succeeds. (A blocked B2 mid-day is the avoidable risk the Sonnet review flagged.)
- [ ] **GROQ_API_KEY** — console.groq.com free key; curl the chat endpoint once to confirm the model id resolves.
- [ ] **Render account** — confirm login; check hacktoberfest.com/my/promos for Render credits to cover Starter; note the deploy-from-GitHub flow.
- [ ] **GITHUB_TOKEN (optional)** — a read-only PAT to lift the 60/hr unauth limit during build testing.
- [ ] **Read the LIVE Wk4 challenge page (DS-1)** — confirm exact theme prompt + required tags (`devchallenge`+`hf26challenge`) + any rule nuance before locking framing.

## Repo / git strategy
- One public GitHub repo, created fresh in-window (originality rule: no pre-existing code).
- Trunk-based: commit per phase (`B0 seed`, `B1 features`, …) so progress is legible in the post.
- `.gitignore`: `.venv`, `.env`, `__pycache__`, `*.pyc`. `.env.example` committed (no secrets).
- Tag `v1-submission` at the state the post links to.

## Environment setup (`.env.example`)
```
GROQ_API_KEY=
TABPFN_TOKEN=
GITHUB_TOKEN=          # optional
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
COMMIT_WINDOW=1000
CACHE_TTL=3600
```

## CI (lightweight — GitHub Actions)
A single workflow `.github/workflows/test.yml`: on push, set up Python 3.11, `pip install -r
requirements.txt`, run `pytest`. Keeps the four unit tests green and is a credibility signal in the
repo the post links. No deploy-from-CI (Render auto-deploys from the connected repo).

## `scripts/build_seed.py` spec (how the seed CSV is actually produced)
- Input: a hand-maintained `scripts/seed_list.txt` of `owner/repo, death_mode, note` (the human labels).
- For each row: call the SAME `github.fetch_repo` + `features.build_features` used in production, so
  seed features are computed identically to inference-time features (no drift).
- Output: `data/seed_repos.csv` with the six features + `death_mode` + `note`.
- Also emits a quick LOO (leave-one-out) TabPFN accuracy to the console — the B0 separability gate.
- Rerunnable; idempotent; the human only edits `seed_list.txt`.

## `claims.json` schema (machine claims ledger — build emits, verify fills, deploy renders)
```json
{ "claims": [
  {"id":"tabpfn-classifies","text":"TabPFN produces the death-mode verdict","evidence":"evidence/abandoned.png","status":"pending"},
  {"id":"live-on-render","text":"App is live on a durable Render URL","evidence":"<url>","status":"pending"},
  {"id":"open-weight-narration","text":"Narration uses an open-weight model via Groq","evidence":"app/narrator.py","status":"pending"},
  {"id":"open-source-core","text":"No closed model in the core path","evidence":"requirements.txt","status":"pending"}
]}
```

## Per-phase contingencies
- **B0 can't separate classes** → add 2–3 more discriminating seed rows per bleeding pair; if still bleeding, drop the weakest feature and re-LOO. Timebox: if not separable by 2:30, ship with the forensic-rules engine as primary and frame TabPFN as the "assist" (degrades the TabPFN-track story but keeps the app honest).
- **TabPFN client flaky at B2** → the labeled fallback keeps the loop working; retry client on a backoff; the engine badge tells the truth.
- **Groq quota/latency at B3** → cache aggressively; pre-warm examples; templated eulogy as last resort.
- **UI eats time at B4** → ship the card unstyled-but-correct first; polish only if the post block isn't threatened.
- **Render RAM >512MB at B5** → lazy-import pandas/tabpfn inside the handler; if still tight, bump to the next Render tier (credits permitting) rather than lose the live demo.
- **Day running long** → the day-of timeline's hard stops cut app polish, never the post block.

## Publication checklist (package phase, dev.to)
- [ ] Draft in the DEV editor; front-matter tags include BOTH `devchallenge` and `hf26challenge`.
- [ ] Cover image = the death-certificate card (1200×630).
- [ ] Embedded demo GIF/video near the top.
- [ ] ≥1 table (the evidence table and/or the results table).
- [ ] First-person, number-in-title.
- [ ] Live Render link + public repo link both present and working.
- [ ] Open-source-AI explanation + open-innovation (Ollama-local) paragraph.
- [ ] Publish via Dami's dev.to session (claude-in-chrome) — SURFACE when the draft is ready.
- [ ] Published by Oct 31, 18:00 WAT (internal cutoff).

## Phase dependency graph
```
PRE-BUILD ─▶ B0 ─▶ B1 ─▶ B2 ─▶ B3 ─▶ B4 ─▶ B5 ─▶ B6 ─▶ (design/demo) ─▶ PACKAGE (the post)
                 └────────── seed feeds B2 ──────────┘
```
Everything after B0 depends on the seed existing; B2 and B3 can be smoke-tested with a single repo
before B4 wires the UI. The post (package) depends on B6 artifacts (screenshots, NOTES.md, claims.json).

---

## Quality bar per phase (what "good" looks like, beyond "done")
- **B0:** not just a CSV — a *defensible* one. Each label traceable to the rubric; LOO visibly > chance; NOTES.md reads like field notes a human would find interesting (the post's soul).
- **B1:** features are *correct*, not just present — the synthetic-series test pins the decay-slope and bus-factor math so a wrong formula can't pass silently.
- **B2:** the verdict is *calibrated* — confidence means something; a clearly-alive repo scores `alive` with high confidence, a clearly-dead one `abandoned`. The engine badge never lies.
- **B3:** narration is *grounded and moving* — it cites the real numbers AND reads like a eulogy worth sharing, not a stats dump. Reverent voice, not mocking.
- **B4:** the card is *screenshot-worthy* — it is the cover image; it must look like something a judge wants to share. Loading state is tasteful, not a spinner.
- **B5:** *warm and honest* — `/healthz` shows `tabpfn_reachable:true`; a judge landing cold still gets <2s.
- **B6:** evidence is *real* — screenshots are of actual live runs, claims.json rows point to those artifacts, not aspirations.

## Demo-rehearsal footgun list (pre-recording)
- A cold Render instance on camera → pre-warm + warm-ping; open the tab 1 min before recording.
- A live API wobble mid-take → use a cached example (identical, instant); never cold-call on camera.
- A repo whose verdict embarrasses a living maintainer → only demo archived/giant-active repos.
- The typing animation running too long for a 90s clip → keep narration ≤180 words; speed the typewriter.
- Reduced-motion users / a judge with motion sensitivity → the clip shows the instant-text fallback too.
- Forgetting the engine badge in frame → it's the proof TabPFN served; keep it visible in the screenshot.

## Handoff artifact manifest (what each phase leaves for the next)
| Phase | Leaves on disk | Consumed by |
|---|---|---|
| B0 | `data/seed_repos.csv`, `data/NOTES.md` | B2 (train), package (post material) |
| B1 | `app/github.py`, `app/features.py`, tests | B2 |
| B2 | `app/classifier.py`, tests | B3, B4 |
| B3 | `app/narrator.py`, tests | B4 |
| B4 | `app/main.py`, `templates/`, `static/` | B5, demo |
| B5 | `render.yaml`, live URL, `/healthz` | livetest, demo, deploy |
| B6 | `evidence/*.png`, `claims.json` | design, demo, package |

## How the post gets its best material from the build (observation capture)
The heaviest-judged axis is writing, and the best writing comes from real moments, not abstractions.
Deliberate capture points: (1) B0 — the surprising repos while labeling ("this one I was sure died
but it's alive"); (2) B2 — any repo the model classified against your intuition (correctly or not);
(3) B5 — the Render durable-tier lesson in practice; (4) B6 — the graveyard census numbers. Each is
a paragraph the package phase can't invent — so they're captured to `data/NOTES.md` as they happen.

## Effort estimate + critical path
Critical path is B0 → B2 (seed quality gates classifier quality). B0 is the longest single block
(~2h) and the highest-variance; everything downstream is mechanical once the seed separates. UI
(B4) is the second-largest but lowest-risk. The post block is reserved and protected regardless of
app overrun — if the day compresses, the app ships lean and the post ships full.

---

## Testing strategy in depth
- **`test_validators.py`** — asserts: full URL, `github.com/owner/repo`, bare `owner/repo`, trailing slash, `.git` suffix all parse to the same `(owner, repo)`; a gist URL, a non-GitHub host, and gibberish each raise the 422 path (no uncaught exception).
- **`test_features.py`** — builds a synthetic commit series with a KNOWN decay slope and a KNOWN two-author split; asserts `commit_cadence_decay`, `bus_factor`, and `velocity_ratio` match hand-computed values within tolerance. This is the test that stops a silently-wrong formula from shipping.
- **`test_classifier_shape.py`** — asserts `classify()` returns a mode in the allowed set, a confidence in [0,1], a posterior summing to ~1, and `engine` set; and that the forced-fallback path returns `engine="rules"`.
- **`test_narration_grounding.py`** — mocks Groq to return a narration with a fabricated number; asserts the grounding check catches it and triggers the retry/fallback.
- **Not unit-tested (by choice):** the live GitHub/TabPFN/Groq calls (covered by the manual 3-repo smoke + livetest phase); the typing animation (manual a11y check). Documented so the coverage gap is intentional, not an oversight.

## Build-time security/privacy checklist (cross-ref SECURITY.md)
- [ ] No secret in any committed file; `.env` git-ignored; `.env.example` has empty values.
- [ ] `validators.parse_repo_url` allow-lists github.com only; no arbitrary-URL fetch reaches `httpx`.
- [ ] Narration prompt receives ONLY the numeric evidence block, never raw repo text (anti-injection).
- [ ] Request log carries no secrets, no PII, no raw repo content.
- [ ] Per-IP soft rate limit on `/autopsy` to bound quota abuse.

## Definition of done (forge → build gate)
This plan is "done enough to build" when: the stack is locked (it is), every phase has an acceptance
test (it does), the seed-dataset methodology is specified (it is), the required credentials are
enumerated with acquisition steps (they are), and the post-protection timeline is explicit (it is).
Build may start at B0 with zero unspecified decisions — which is the real floor this document had to clear.

---

## Starter `scripts/seed_list.txt` (initial labeled candidates for B0)
A concrete starting point (expand to ~50, ~10/class; verify each is safe to feature publicly):
```
# owner/repo, death_mode, note
# --- alive (controls) ---
facebook/react, alive, high velocity, huge contributor base
fastapi/fastapi, alive, steady cadence, healthy bus factor
# --- completed ---
<archived-but-finished-lib>, completed, archived with a clear "done" README
<mature-stable-tool>, completed, long lifespan then deliberate quiet, releases tagged
# --- abandoned ---
<once-popular-dead-repo>, abandoned, no commits in 2+ years, issues left open
<framework-that-lost-to-a-rival>, abandoned, cadence fell off a cliff, not archived
# --- burned_out ---
<solo-maintainer-stalled>, burned_out, bus_factor=1, steep decay to zero
# --- pivoted ---
<short-lived-then-successor>, pivoted, <4 months active, README points to a successor repo
```
Rule: never seed a small living personal repo whose "abandoned" label could embarrass its author;
prefer famous archived/giant-active repos. Fill the angle-bracket slots at B0 from GitHub graveyard
lists; record the human reason in the `note` column (it feeds `data/NOTES.md` and the post).

## Source-of-truth pointers
- Product intent → PRD.md · System design → ARCHITECTURE.md · Build order → this file.
- Decisions log → DECISIONS.md · Honest gaps → LIMITATIONS.md · Threat model → SECURITY.md.
- Submission requirements → SUBMISSION_STATUS.md · Required inputs → .input-manifest.json.
- Winner rationale → warroom/WINNER-BRIEF.md + FINAL-VERDICT-V1.md.

## Versioning intent
`v1-submission` = the state the dev.to post links to (tagged at B6/deploy). Post-submission tweaks
(if any) go on a branch so the submitted commit stays pinned and reproducible for judges.

---

# PART II — DETAILED PHASED EXECUTION (exact commands · expected output · decision trees · commit messages)

All commands run from the repo root in the venv. ARCHITECTURE.md (Part II) is the copy-exact source
for every file; this section is the ORDER + the gates + the branch logic at each risk point.

## PRE-BUILD (before the clock)
**Commands**
```
mkdir -p dev-ghost-autopsy && cd dev-ghost-autopsy
git init && python -m venv .venv && source .venv/bin/activate
printf "GROQ_API_KEY=\nTABPFN_TOKEN=\nGITHUB_TOKEN=\n" > .env   # fill real values
# verify tokens BEFORE building:
python -c "import os;assert os.environ.get('GROQ_API_KEY'),'GROQ missing'"
python - <<'PY'
from openai import OpenAI; import os
c=OpenAI(base_url="https://api.groq.com/openai/v1",api_key=os.environ["GROQ_API_KEY"])
print(c.chat.completions.create(model="llama-3.3-70b-versatile",
  messages=[{"role":"user","content":"say ok"}],max_tokens=5).choices[0].message.content)
PY
python -c "from tabpfn_client import TabPFNClassifier; print('tabpfn import ok')"
```
**Expected output:** `ok` from Groq; `tabpfn import ok`. Read the LIVE challenge page; confirm tags `devchallenge`+`hf26challenge`.
**Decision tree:** Groq call fails → fix key / model id before B3. · tabpfn import/auth fails → resolve token (email-confirm loop) NOW, not at B2. · live page reveals a rule nuance → note it in SUBMISSION_STATUS before locking framing.
**Commit:** `chore: scaffold repo, venv, env; verify groq+tabpfn tokens`

## B0 — Seed dataset (LINCHPIN)
**Commands**
```
mkdir -p app data scripts tests
# write scripts/seed_list.txt (ARCHITECTURE II.27) with 15-20 obvious cases first
# write app/github.py, app/features.py, app/schemas.py (ARCHITECTURE II.2,II.4,II.5)
#   OWNERSHIP: these three files are FIRST-WRITTEN here at B0 (build_seed.py needs them to compute seed
#   features with the SAME extractor as production — no train/serve skew). B1 does NOT re-write them; B1
#   finalizes their edge-handling (404/empty/archived/huge) and adds the unit tests. First-write = B0.
# write scripts/build_seed.py (ARCHITECTURE II.16)
export GITHUB_TOKEN=...   # recommended for rate limit
python scripts/build_seed.py
```
**Expected output:** `ok <repo> -> <mode>` per row; `wrote N rows to data/seed_repos.csv`; `LOO accuracy: X/N = P%`.
**Decision tree:**
- LOO accuracy ≳ 60% and all 5 classes present → PASS; capture 5–10 observations to `data/NOTES.md`; pad to ~50.
- Classes bleed (e.g. abandoned↔burned_out) → add 2–3 sharper exemplars to the bleeding pair; re-run. Do NOT relabel arbitrarily.
- A repo errors (404/empty) → drop it from seed_list; never block the build on one bad row.
- Not separable by the B0 timebox (2:30) → ship with forensic-rules as primary, frame TabPFN as "assist" in the post (degrades the TabPFN-track story but keeps the app honest). Log the decision in DECISIONS.md.
**Commit:** `feat(seed): hand-labeled ~50-repo seed dataset + build_seed.py; LOO validated`

## B1 — Feature extractor
**Commands**
```
# app/github.py + app/features.py already drafted in B0; finalize edge handling
# write tests/test_features.py, tests/test_validators.py + app/validators.py (ARCHITECTURE II.3,II.17,II.18)
pytest -q tests/test_features.py tests/test_validators.py
```
**Expected output:** `4 passed` (or the count of parametrized cases) — green.
**Decision tree:** a feature test fails → the formula is wrong (not the test); fix `features.py` against the hand-computed expected value. · a real repo fetch is slow → confirm COMMIT_WINDOW cap is applied.
**Commit:** `feat(features): six git-forensic features + url validation; tests green`

## B2 — TabPFN classifier
**Commands**
```
# write app/classifier.py (ARCHITECTURE II.6 + II.26 nearest-mode) ; tests/test_classifier_shape.py (II.19)
pytest -q tests/test_classifier_shape.py
python - <<'PY'
import asyncio
from app.github import fetch_repo; from app.features import build_features; from app.classifier import classify
async def go(slug):
    o,r=slug.split("/"); d=await fetch_repo(o,r); f,_=build_features(d); v=classify(f)
    print(slug, v.mode, round(v.confidence,2), v.engine)
asyncio.run(go("<a-known-dead-repo>")); asyncio.run(go("facebook/react"))
PY
```
**Expected output:** dead repo → a death-mode with `engine=tabpfn`; react → `alive`. Fallback test green.
**Decision tree:** classify raises (client/token) → the `except` path returns `engine=rules`; confirm the badge logic. · a clearly-dead repo classifies `alive` → seed signal is off; revisit B0 features/labels. · confidence absurdly low across the board → seed too small/noisy; add exemplars.
**Commit:** `feat(classify): TabPFN in-context death-mode classifier + labeled rules fallback`

## B3 — Groq narration
**Commands**
```
# write app/narrator.py (ARCHITECTURE II.7) ; tests/test_narration_grounding.py (II.20)
pytest -q tests/test_narration_grounding.py
python - <<'PY'
from app.schemas import Features,Verdict,RepoMeta; from app.narrator import narrate
f=Features(days_since_last_commit=806,commit_cadence_decay=-3.4,lifespan_days=530,contributor_count=2,bus_factor=1,velocity_ratio=0.04)
v=Verdict(mode="abandoned",confidence=0.81,probs={"abandoned":0.81},engine="tabpfn")
print(narrate("someuser","deadrepo",v,f,RepoMeta(created_at="2021-03-02",last_commit_at="2022-08-14")))
PY
```
**Expected output:** a 120–200 word grounded eulogy in the coroner register; grounding test green.
**Decision tree:** narration cites a fabricated number → grounding check should catch it; if it slips, tighten `_numbers` regex. · tone too flippant → strengthen the SYSTEM reverence clause. · output too long → lower `max_tokens`.
**Commit:** `feat(narrate): grounded open-weight coroner's report + templated fallback`

## B4 — Web UI (one page)
**Commands**
```
# write app/cache.py, app/main.py (ARCHITECTURE II.8,II.9 + II.29 prewarm)
# write app/templates/index.html, app/static/app.js, app/static/card.css (II.10,II.11,II.12)
# add a placeholder app/static/og.png (replaced by the real card screenshot at B6/design)
uvicorn app.main:app --reload
# in another shell:
curl -s localhost:8000/healthz
curl -s -X POST localhost:8000/autopsy -H 'content-type: application/json' -d '{"repo_url":"facebook/react"}' | python -m json.tool
```
**Expected output:** `/healthz` → `{ok:true,...}`; `/autopsy` → a full `AutopsyResult` JSON; the page renders the certificate card and types the eulogy in a browser.
**Decision tree:** card overflows / unreadable → fix `card.css` before screenshotting (it is the cover image). · typewriter janky → ensure reduced-motion branch + the 12ms step. · static not served → confirm the `StaticFiles` mount path.
**Commit:** `feat(ui): one-page autopsy UI, certificate card, typing eulogy, examples`

## B5 — Deploy (Render, durable warm)
**Commands**
```
# write requirements.txt, render.yaml, .github/workflows/test.yml (ARCHITECTURE II.1,II.13,II.23)
git add -A && git commit -m "chore: deploy config (render.yaml, requirements, CI)"
git branch -M main && git remote add origin <github-url> && git push -u origin main
# Render dashboard: New Web Service → connect repo (reads render.yaml) → set env GROQ_API_KEY, TABPFN_TOKEN, GITHUB_TOKEN → deploy
# after deploy:
curl -s https://<app>.onrender.com/healthz
```
**Expected output:** Render build succeeds; `/healthz` → `{ok:true, tabpfn_reachable:true}`; the page loads warm.
**Decision tree:** build fails on a dep → pin/adjust `requirements.txt`. · RAM >512MB (instance restarts) → lazy-import pandas/tabpfn inside the handler; if still tight, bump tier (credits). · cold/slow first load → confirm `plan:starter` + `numInstances:1`; add the external warm-ping cron on `/healthz`. · `tabpfn_reachable:false` → the token env var isn't set on Render.
**Commit:** `feat(deploy): live on Render Starter (warm) + health check`

## B6 — Demo-prep handoff
**Commands**
```
# choose the 3 example repos (one each abandoned/burned_out/alive) from the seed set; set EX_* env on Render
mkdir -p evidence
# capture a screenshot of each certificate at 1200x630 (browser or playwright) -> evidence/{abandoned,burned_out,alive}.png
# write claims.json (PLAN claims schema) with evidence pointers; set rows to verified where screenshots exist
```
**Expected output:** 3 screenshots in `evidence/`; `claims.json` valid with real evidence pointers; `data/NOTES.md` has ≥5 observations.
**Decision tree:** a chosen example embarrasses a living maintainer → swap for an archived/giant repo. · a screenshot is cluttered → adjust card CSS, re-shoot (it's the cover image).
**Commit:** `chore(demo): pre-warmed examples, evidence screenshots, claims.json`

## GATE — acceptance walk before publish (ARCHITECTURE II.33 / PRD §74)
Run all 12 manual QA steps + the 4 unit tests + `/healthz`. All green → the app is DONE; hand off to
design (screenshots), demo (video), package (the post). Any red → fix before the post block.

---

# PART III — SUPPORTING EXECUTION DETAIL

## Commit-message convention
`<type>(<scope>): <summary>` — types: feat / fix / chore / docs / test. One commit per phase (B0–B6)
so the git history reads as the build-story (useful material for the post). Tag `v1-submission` at
the commit the dev.to post links to.

## Branch strategy
Trunk-based on `main`. If a post-submission tweak is needed, branch `post-submit/<x>` so the
submitted commit stays pinned. No long-lived branches during the 1-day build.

## CI gate
`.github/workflows/test.yml` runs `pytest` on every push. A red CI is a build-stop: fix before
continuing. CI green is also a credibility signal in the repo the post links.

## Environment matrix
| Env | GROQ_API_KEY | TABPFN_TOKEN | GITHUB_TOKEN | LLM_BASE_URL |
|---|---|---|---|---|
| local dev | real | real | optional | Groq (or Ollama for local mode) |
| CI | not needed (tests mock/network-free) | not needed | not needed | — |
| Render prod | set (dashboard) | set | optional | Groq |
| Ollama-local demo | — | optional (local weights) | optional | http://localhost:11434/v1 |

## Rollback / recovery
Render keeps prior deploys → one-click rollback to the last green build. If TabPFN/Groq are down
during judging, the labeled fallbacks keep the app honest; cached examples always work. A non-200 on
`/healthz` (seen via the warm-ping) is the redeploy/rollback trigger.

## Time contingency ladder (if the day compresses)
1. Cut app visual polish (keep the card correct but less styled).
2. Cut the 3rd example (ship 2).
3. Cut the forensic-rules 1-NN else branch (keep the threshold rules).
NEVER cut: the seed dataset (B0), the TabPFN happy path (B2), the live deploy (B5), or the post block.

## Definition of done (build → design/demo/package handoff)
All of: 4 unit tests green in CI; the 12-step manual QA passes; live Render URL warm with
`engine=tabpfn` on the happy path; 3 examples pre-warmed + screenshotted; `claims.json` + `data/NOTES.md`
present. This is the single gate; package does not start the post until it is met.

---

# PART IV — FILE-BY-FILE TRANSCRIPTION SEQUENCE (the exact order a build agent writes files)

ARCHITECTURE.md PART II is the copy-exact source for every file. This section is the ORDER those
files are transcribed in, WHY that order (dependency direction), the EXACT command that proves each
file lands correctly, and the EXPECTED OUTPUT transcript at each checkpoint. A build agent transcribes
top-to-bottom; nothing below depends on anything written after it. The module import direction is
one-way (`main → {validators, github, features, classifier, narrator, cache, schemas}`), so files are
written inner-first and the entrypoint (`main.py`) last — a file never imports something not yet on disk.

## IV.0 — Transcription order (dependency-sorted)
```
1.  requirements.txt            (ARCH II.1)   — pin deps first; pip install can run while you write code
2.  app/__init__.py             (empty)       — makes `app` a package
3.  app/schemas.py              (ARCH II.2)   — pure types, zero imports from siblings
4.  app/validators.py           (ARCH II.3)   — pure, imports only stdlib
5.  app/github.py               (ARCH II.4)   — imports httpx + schemas (RepoMeta)
6.  app/features.py             (ARCH II.5)   — imports schemas (Features); pure math over github output
7.  app/classifier.py           (ARCH II.6 + II.26) — imports pandas/numpy/tabpfn-client + schemas
8.  app/narrator.py             (ARCH II.7)   — imports openai + schemas
9.  app/cache.py                (ARCH II.8)   — stdlib LRU wrapper
10. app/main.py                 (ARCH II.9 + II.29) — imports ALL siblings; the only FastAPI file
11. app/templates/index.html    (ARCH II.10)
12. app/static/app.js           (ARCH II.11)
13. app/static/card.css         (ARCH II.12)
14. render.yaml                 (ARCH II.13)
15. .env.example                (ARCH II.14)
16. data/seed_repos.csv header  (ARCH II.15)  — header + starter rows; filled to ~50 at B0
17. scripts/seed_list.txt       (ARCH II.27)  — the human labels
18. scripts/build_seed.py       (ARCH II.16)  — produces the CSV from the list
19. tests/test_validators.py    (ARCH II.17)
20. tests/test_features.py      (ARCH II.18)
21. tests/test_classifier_shape.py (ARCH II.19)
22. tests/test_narration_grounding.py (ARCH II.20)
23. .github/workflows/test.yml  (ARCH II.23)
24. Makefile                    (ARCH II.25)   — optional, convenience targets
```
This order is also the B0→B5 phase order compressed: files 1–6 + 16–18 are B0/B1, 7 is B2, 8 is B3,
9–13 are B4, 14–15 + 23 are B5. Writing in this order means `python -c "import app.main"` succeeds the
first time after file 10 (no forward reference ever dangles).

## IV.1 — Per-file landing check (write → prove, one file at a time)
After transcribing each Python module, run the single import/compile check below BEFORE moving on. A
file that imports clean is the cheapest possible proof the transcription had no syntax/paste error.
This is the "write then read the diff" discipline applied per file.

| # | File | Landing check (run from repo root, venv active) | Expected |
|---|---|---|---|
| 3 | `app/schemas.py` | `python -c "from app.schemas import AutopsyResult, FEATURE_ORDER; print(len(FEATURE_ORDER))"` | `6` |
| 4 | `app/validators.py` | `python -c "from app.validators import parse_repo_url; print(parse_repo_url('https://github.com/facebook/react'))"` | `('facebook', 'react')` |
| 5 | `app/github.py` | `python -c "import app.github; print(app.github.COMMIT_WINDOW)"` | `1000` (or the COMMIT_WINDOW env) |
| 6 | `app/features.py` | `python -c "from app.features import build_features; print('ok')"` | `ok` |
| 7 | `app/classifier.py` | `python -c "from app.classifier import classify, _forensic_rules; print('ok')"` | `ok` |
| 8 | `app/narrator.py` | `python -c "from app.narrator import narrate; print('ok')"` | `ok` |
| 9 | `app/cache.py` | `python -c "from app.cache import cache_get, cache_set; print('ok')"` | `ok` |
| 10 | `app/main.py` | `python -c "from app.main import app; print([r.path for r in app.routes])"` | includes `/`, `/autopsy`, `/healthz` |

**Decision tree at any landing check:**
- `ModuleNotFoundError: app` → you ran from the wrong directory, or `app/__init__.py` is missing. `cd` to repo root; create the empty `__init__.py`.
- `ImportError: cannot import name X` → the transcription dropped a symbol; diff the file against ARCH II.N and re-paste the missing definition. Do NOT invent the symbol.
- `SyntaxError` → a paste truncation (common on long triple-quoted blocks like the narrator prompt); re-copy the whole code block from ARCH, not a patch.
- A third-party `ModuleNotFoundError` (e.g. `httpx`, `tabpfn_client`) → `pip install -r requirements.txt` did not finish or the venv isn't active. `source .venv/bin/activate && pip install -r requirements.txt`.

## IV.2 — The import smoke (after file 10)
```
python -c "from app.main import app; print('routes:', sorted(r.path for r in app.routes))"
```
**Expected:** `routes: ['/', '/autopsy', '/examples', '/healthz', '/static']` (exact set may vary by
StaticFiles mount; `/`, `/autopsy`, `/healthz` MUST be present).
**If this fails,** the failure is in one of files 3–10 — bisect by importing each sibling alone
(`python -c "import app.classifier"`) to find the one that throws. The first sibling that throws is the
bug; fix it against its ARCH II.N block before re-running the smoke.

---

# PART V — PER-PHASE VERIFICATION PROTOCOL (what "proven" means, with transcripts)

Each phase below restates its exit gate as a RUNNABLE check with the EXACT expected console output, then
a decision tree for every way the check can fail. "Proven" = the transcript matches; a phase is never
marked done on a self-report. This is the build agent's acceptance protocol — it maps 1:1 to the B0–B6
acceptance tests above but adds the exact evidence each produces.

## V.B0 — Seed dataset separability (the single most important gate)
**Run:**
```
python scripts/build_seed.py 2>&1 | tee data/build_seed.log
```
**Expected transcript (shape):**
```
ok facebook/react -> alive
ok fastapi/fastapi -> alive
...
ok <owner>/<repo> -> pivoted
wrote 50 rows to data/seed_repos.csv
class balance: alive=10 completed=10 abandoned=10 burned_out=10 pivoted=10
LOO accuracy: 38/50 = 76%
confusion (worst pair): abandoned<->burned_out 4 swaps
```
**PASS criteria (all):** CSV written; all 5 classes present; LOO accuracy ≥ 60% (chance = 20%); no
single class fully absorbed by another.
**Decision tree:**
- LOO 60–75% with one bleeding pair → acceptable; note the pair in `data/NOTES.md`; the narration never
  claims more certainty than the confidence reflects. Proceed.
- LOO < 60% → the seed is noisy. Add 2–3 UNAMBIGUOUS exemplars to the bleeding pair (an obviously-archived
  repo for `completed`, an obviously-dead-2yr repo for `abandoned`). Re-run. Do NOT relabel existing rows
  to chase accuracy (that's overfitting the LOO, not improving separability).
- A single class has 0 correct LOO predictions → that class's definition overlaps a neighbor. Re-read PRD
  §16 rubric; the most common culprit is `pivoted` vs `abandoned` (a pivot has a successor pointer; an
  abandonment does not). Sharpen the 2–3 clearest `pivoted` seeds.
- `build_seed.py` errors on a row (404/empty) → drop that row from `seed_list.txt`; one bad seed never
  blocks B0. Log the drop in `data/NOTES.md`.
- Not separable by the 2:30 hard stop → execute the documented fallback: ship `engine="rules"` as primary,
  record the decision in DECISIONS.md, reframe TabPFN as the "assist" in the post. The app stays honest.
**Evidence left on disk:** `data/seed_repos.csv`, `data/build_seed.log`, `data/NOTES.md` (≥5 entries).

## V.B1 — Feature correctness (synthetic-series pin)
**Run:**
```
pytest -q tests/test_features.py tests/test_validators.py
```
**Expected:** `....  [100%]  <N> passed in <t>s` (N = count of parametrized cases, ≥ 8).
**What this proves:** `test_features.py` builds a commit series with a KNOWN decay slope and a KNOWN
two-author split, then asserts `commit_cadence_decay`, `bus_factor`, and `velocity_ratio` equal the
hand-computed values within tolerance. A wrong formula CANNOT pass — this is the gate that stops a
silently-miscomputed feature from poisoning every downstream verdict.
**Decision tree:**
- A feature assertion fails → the FORMULA is wrong, not the test. Open ARCH II.5, recompute the expected
  value by hand against the synthetic series, fix `features.py`. Never loosen the tolerance to pass.
- `test_validators.py` fails on a URL form → `parse_repo_url` dropped a case (trailing slash, `.git`
  suffix, bare `owner/repo`). Fix against ARCH II.3; all forms MUST normalize to the same `(owner, repo)`.
- A real-repo fetch in manual testing is slow (>4s) → confirm `COMMIT_WINDOW` cap is applied in
  `github.py` (a repo with 50k commits must not paginate all of them).
**Evidence:** green pytest transcript; a manual `build_features` on one real repo returning a full row.

## V.B2 — Classifier load-bearing + honest fallback
**Run:**
```
pytest -q tests/test_classifier_shape.py
python - <<'PY'
import asyncio
from app.github import fetch_repo
from app.features import build_features
from app.classifier import classify
async def go(slug):
    o, r = slug.split("/"); d = await fetch_repo(o, r); f, _ = build_features(d); v = classify(f)
    print(f"{slug:28} {v.mode:14} conf={v.confidence:.2f} engine={v.engine}")
asyncio.run(go("facebook/react"))
asyncio.run(go("<a-known-dead-repo>"))
PY
```
**Expected transcript:**
```
. [100%]  <N> passed
facebook/react               alive          conf=0.8x engine=tabpfn
<owner>/<dead-repo>          abandoned      conf=0.7x engine=tabpfn
```
**PASS criteria:** shape test green; a clearly-alive repo → `alive` with `engine=tabpfn`; a clearly-dead
repo → a death-mode with `engine=tabpfn`; the forced-fallback test returns `engine="rules"`.
**Decision tree:**
- `classify()` raises on the TabPFN client (token/network) → the `except` branch MUST return a verdict
  with `engine="rules"` (ARCH II.26). Confirm the badge logic surfaces `rules`. A raise reaching the user
  is an I6 violation — fix the try/except, do not swallow silently.
- A clearly-dead repo classifies `alive` → the SEED signal is off, not the classifier. Return to B0: the
  dead-class exemplars don't separate. This is why B0 gates B2 on the critical path.
- Confidence is ~0.2 (uniform) across every input → the seed is too small or too noisy for in-context
  learning. Add exemplars; re-run build_seed; re-test.
- The fallback test does NOT set `engine="rules"` → the fallback is mislabeled; a judge would see a
  heuristic verdict presented as the model (I3 violation). Fix `_forensic_rules` to set the flag.
**Evidence:** green shape test; the 2-repo transcript showing `engine=tabpfn` on the happy path.

## V.B3 — Narration grounded (no hallucinated facts)
**Run:**
```
pytest -q tests/test_narration_grounding.py
python - <<'PY'
from app.schemas import Features, Verdict, RepoMeta
from app.narrator import narrate
f = Features(days_since_last_commit=806, commit_cadence_decay=-3.4, lifespan_days=530,
             contributor_count=2, bus_factor=1, velocity_ratio=0.04)
v = Verdict(mode="abandoned", confidence=0.81, probs={"abandoned": 0.81}, engine="tabpfn")
print(narrate("someuser", "deadrepo", v, f, RepoMeta(created_at="2021-03-02", last_commit_at="2022-08-14")))
PY
```
**Expected:** grounding test green; a 120–200-word eulogy in the coroner register that cites ONLY numbers
present in the evidence block (806 days, 2 contributors, bus factor 1) and invents none.
**Decision tree:**
- The grounding test (which mocks Groq to return a FABRICATED number) does NOT catch it → the `_numbers`
  extraction/compare in `narrator.py` is too loose. Tighten the regex so any numeric token in the output
  absent from the evidence block triggers the retry/fallback. This test existing-and-passing is I4.
- The eulogy reads flippant / mocking → strengthen the SYSTEM reverence clause (ARCH II.7). The register is
  a coroner/eulogy, never a roast; a mocking tone fails the theme-interpretation bar (PRD §36).
- Output > 200 words → lower `max_tokens`; the typing animation on a long eulogy overruns the 90s demo.
- Groq returns an auth/model error in manual testing → the PRE-BUILD Groq probe should have caught this;
  re-verify `LLM_MODEL` resolves (model ids rotate on Groq).
**Evidence:** green grounding test; a sample grounded eulogy pasted into `data/NOTES.md`.

## V.B4 — Full loop end-to-end (local)
**Run (two shells):**
```
# shell 1
uvicorn app.main:app --reload
# shell 2
curl -s localhost:8000/healthz | python -m json.tool
curl -s -X POST localhost:8000/autopsy -H 'content-type: application/json' \
  -d '{"repo_url":"facebook/react"}' | python -m json.tool
```
**Expected `/healthz`:** `{"ok": true, "tabpfn_reachable": true, ...}`.
**Expected `/autopsy`:** a full `AutopsyResult` JSON (PRD §23) with `owner`, `repo`, `meta`, `features`,
`verdict` (mode/confidence/probs/engine), `narration`, `certificate_id`. In a browser, the page renders
the certificate card and types the eulogy.
**Decision tree:**
- `/autopsy` returns 500 → an uncaught path (I6 violation). Check the server log; the most likely culprit
  is a GitHub edge (empty/archived repo) not mapped in the error matrix (ARCH §11). Add the branch.
- Card overflows / text unreadable → fix `card.css` BEFORE screenshotting. The card is the cover image; an
  ugly card loses the heaviest-judged axis's hero asset.
- Typewriter janky or ignores reduced-motion → confirm the `prefers-reduced-motion` branch renders the
  eulogy instantly (ARCH II.11); the 12ms step is the animated path only.
- Static assets 404 → confirm the `StaticFiles` mount path in `main.py` matches the `/static/...` hrefs.
**Evidence:** the two curl transcripts; a local screenshot of the rendered card.

## V.B5 — Live, warm, honest (Render)
**Run (after Render deploy):**
```
curl -s -w '\n[%{http_code}] %{time_total}s\n' https://<app>.onrender.com/healthz
curl -s -X POST https://<app>.onrender.com/autopsy -H 'content-type: application/json' \
  -d '{"repo_url":"facebook/react"}' -w '\n[%{http_code}] %{time_total}s\n' | tail -3
```
**Expected:** `/healthz` → `{"ok": true, "tabpfn_reachable": true}` with `[200]` and `time_total` < 2s on
a warm instance; `/autopsy` → `[200]` with a full result, first warm call typically 2–6s (TabPFN + Groq
round-trips).
**PASS criteria (I5):** plan is Starter, `numInstances=1`, `/healthz` 200 warm < 2s, `tabpfn_reachable:true`.
**Decision tree:**
- Render build fails on a dependency → pin/adjust `requirements.txt` (a wheel may be unavailable for the
  pinned version on Render's Python). Bump the patch, re-deploy.
- Instance restarts / OOM (RAM > 512MB) → lazy-import pandas/tabpfn-client INSIDE the handler, not at
  module top (ARCH II.28). Spot-check with Render's metrics tab. If still tight after lazy-import, bump to
  the next tier (credits permitting) rather than lose the live demo — losing live-on-Render loses a track.
- Cold / slow first load → confirm `plan: starter` + `numInstances: 1` in `render.yaml` (free tier spins
  to zero; that's the dl-1 vector). Add the external warm-ping cron on `/healthz` (ARCH II.25).
- `tabpfn_reachable: false` on live but true local → the `TABPFN_TOKEN` env var isn't set in the Render
  dashboard. Set it; redeploy.
**Evidence:** the two live curl transcripts with http_code + time_total; a Render metrics screenshot
showing RAM < 512MB.

## V.B6 — Evidence is real
**Run:** capture a certificate screenshot for each of 3 example repos (one each
abandoned / burned_out / alive) at 1200×630, write `claims.json` with evidence pointers.
**Expected:** 3 PNGs in `evidence/`; `claims.json` validates; every row's `evidence` points to a file that
exists or a live URL that 200s; `data/NOTES.md` ≥ 5 observations.
**Decision tree:**
- A chosen example embarrasses a living maintainer → swap for an archived/giant repo (PRD §30). Never ship
  a verdict that could harm a real person's small project.
- A screenshot is cluttered → adjust card CSS, re-shoot. It is the cover image.
- A `claims.json` row has no real evidence yet → leave it `pending`; verify/deploy fill it. Never mark a
  claim `verified` without a real artifact (the fixture-shortcircuit trap — a claim proven by an
  aspiration is not proven).
**Evidence:** `evidence/{abandoned,burned_out,alive}.png`; a valid `claims.json`.

## V.GATE — the single build→handoff gate (run before any post work)
```
pytest -q                                   # all 4 suites green
curl -s https://<app>.onrender.com/healthz  # {ok:true, tabpfn_reachable:true}
ls evidence/*.png | wc -l                   # 3
python -c "import json; d=json.load(open('claims.json')); print(len(d['claims']),'claims')"
grep -c '^## ' data/NOTES.md                # ≥5 observation BLOCKS (each a `## ` heading — not raw lines)
```
All green → the app is DONE; hand off to design (screenshots) → demo (video) → package (the post). Any red
→ fix before the post block opens. This is the one gate; package does not start the write-up until it passes.

---

# PART VI — DEPLOY & POST EXECUTION WALKTHROUGHS (step-by-step, with the branch logic)

## VI.1 — Render deploy, click-by-click
1. `git push -u origin main` (the repo must be public — originality + the post links it).
2. Render dashboard → **New → Web Service** → connect the GitHub repo. Render reads `render.yaml`.
3. Confirm the blueprint: **Environment** Python, **Plan** Starter ($7), **Instances** 1,
   **Health Check Path** `/healthz`, **Start Command** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. **Environment** tab → add `GROQ_API_KEY`, `TABPFN_TOKEN` (required), `GITHUB_TOKEN` (optional). These are
   NEVER in the repo (I10) — only here.
5. **Create Web Service** → watch the build log. First build installs the pinned deps (~2–3 min).
6. When live, run the V.B5 checks. If `tabpfn_reachable:false`, the token env is missing (step 4).
7. Add the external warm-ping (a free cron-ping service or a GitHub Action on a schedule hitting
   `/healthz` every 10 min) — belt-and-braces against spin-down even though Starter is always-on (I5).
8. **Branch logic:** build fail → read the log, 90% of the time it's a dep wheel; fix `requirements.txt`.
   OOM → lazy-import (ARCH II.28). Slow cold → verify plan/instances; free tier is the failure mode.

## VI.2 — The dev.to post (the deliverable — package phase owns this, plan is here for traceability)
The post is NOT built in this forge/build pipeline; `hackathon-package` owns it (Skill-Ownership Map).
This sub-plan exists so the build captures the RAW MATERIAL the post needs, as it happens:
1. **Hook (first-person, number-in-title):** candidate title *"I performed an autopsy on my dead
   side-projects. An open-weight AI told me how they died."* Lead with the moment, not the architecture.
2. **The idea & theme (~200w):** "Ghost in the Machine = the ghosts of dead code." Interpretation, not skin.
3. **How it works (~350w + the evidence table):** feature table → TabPFN classify → open-weight narrate.
   Pull the real numbers from B6 (engine mix, death-mode distribution, median latency).
4. **The seed dataset (~300w — the human story):** the `data/NOTES.md` observations. "This one I was sure
   died — it's alive." This section is the soul; it cannot be invented at write-time, only harvested.
5. **Open-source-AI explanation + open-innovation:** TabPFN (open weights) + Groq open-weight + the
   Ollama-local/offline paragraph (II.21). Be honest about what's load-bearing.
6. **Results table + live link + repo link.** Tags: BOTH `devchallenge` and `hf26challenge`.
7. **Cover image** = the death-certificate card (1200×630). **Embed** the demo GIF high.
8. **Publish** via Dami's dev.to session (claude-in-chrome) — SURFACE to Dami when the draft is ready;
   do NOT auto-publish. Internal cutoff: Oct 31, 18:00 WAT.

## VI.3 — Why this plan can't be blocked mid-build (pre-cleared decisions)
Build may start at B0 with ZERO unspecified decisions because every risk point above has a pre-written
branch: the stack is locked, every file has a copy-exact source (ARCH II), every phase has a runnable
exit transcript, the seed methodology is specified (build_seed.py), the credentials are enumerated with
acquisition steps (.input-manifest.json), the fallback for an un-separable seed is written (rules-primary),
and the post-protection timeline is explicit. The only valid mid-build stop is an external outage (TabPFN
or Groq down) — and even that has a path (labeled fallback + cached examples). That is the real floor this
document had to clear: a developer with zero context builds and ships from these three documents alone.

---

# PART VII — WORKED END-TO-END TRACE (one repo through every stage, with real intermediate values)

This is a single concrete walk of the one loop, so the build agent knows EXACTLY what each stage should
produce for a known input and can spot a wrong intermediate value immediately. Values are illustrative of
a classic abandoned single-maintainer repo (the numbers are the kind B1 should produce; the build proves
them against the live fetch). Trace a real dead repo on build day and paste the actual numbers into
`data/NOTES.md`.

## VII.1 — Input
```
paste: https://github.com/someuser/deadtool        (a once-popular tool, no commits in ~2.2 years)
```

## VII.2 — Stage 1: validate (`validators.parse_repo_url`)
```
parse_repo_url("https://github.com/someuser/deadtool")  ->  ("someuser", "deadtool")
```
All of these must normalize to the SAME tuple (the `test_validators.py` parametrization):
`https://github.com/someuser/deadtool`, `github.com/someuser/deadtool`, `someuser/deadtool`,
`someuser/deadtool/`, `someuser/deadtool.git`. A gist URL, a non-github host, and `""` each raise
`BadRepoURL` → the route returns 422 with a friendly message (PRD §31), never a 500.

## VII.3 — Stage 2: fetch (`github.fetch_repo`)
Two API calls (repo meta + windowed commits + contributors). Illustrative shape:
```
meta:        stars=4200, primary_language="Go", created_at="2019-05-02",
             last_commit_at="2022-08-14", is_archived=false
commits:     641 commits over the lifespan (under the 1000 window — no cap hit)
contributors: {alice: 590, bob: 38, others: 13}  (distinct authors = 7)
```
Edge branches this stage must handle: 404 → `RepoError("not_found")`; 0–1 commits →
`RepoError("empty")` → `insufficient_history` verdict (skip classify); 403 w/ rate headers →
`RepoError("rate_limited")` → the "come back in N min" state (PRD §31 / Flow H).

## VII.4 — Stage 3: features (`features.build_features`) — the forensic evidence
Computed from the fetch above, using the ARCH §5 formulas. Expected row (the kind B1 produces):
```
days_since_last_commit = (now - 2022-08-14).days          ≈ 806
commit_cadence_decay   = OLS slope of monthly commit count ≈ -3.4   (commits/month per month, steep down)
lifespan_days          = (2022-08-14 - 2019-05-02).days    ≈ 1200
contributor_count      = 7
bus_factor             = 1        (alice alone is ≥50% of commits: 590/641 = 92%)
velocity_ratio         = commits_last_90d / expected       ≈ 0.00  (zero recent commits → fading→dead)
```
These six are the ONLY columns TabPFN sees. The context columns (stars, language, is_archived,
created_at, last_commit_at, total_commits) ride along for the narration, NOT the classification.
**Spot-check the math:** `bus_factor=1` because one author crosses the 50% cumulative share;
`velocity_ratio≈0` because `commits_last_90d=0`. If B1 produces `bus_factor=7` or `velocity_ratio=1.0`
for this input, the formula is transcribed wrong — fix against ARCH II.5 before proceeding.

## VII.5 — Stage 4: classify (`classifier.classify`) — TabPFN, load-bearing
```
X_train, y_train = seed_repos.csv[6 features], seed_repos.csv["death_mode"]   # ~50 labeled rows
X_test           = [[806, -3.4, 1200, 7, 1, 0.00]]
clf = TabPFNClassifier(); clf.fit(X_train, y_train); proba = clf.predict_proba(X_test)[0]
->  Verdict(mode="abandoned", confidence=0.81,
            probs={"abandoned":0.81,"burned_out":0.12,"completed":0.04,"pivoted":0.02,"alive":0.01},
            engine="tabpfn")
```
The verdict is `predict_proba`'s argmax — this is the substitution-test core (remove TabPFN and only
`_forensic_rules` remains, explicitly NOT AI). If the TabPFN client is unreachable, the SAME input goes
to `_forensic_rules` (ARCH II.26): `days_since_last_commit=806>365 and velocity_ratio=0<0.1 → abandoned`,
returned as `engine="rules"` with the badge telling the truth.

## VII.6 — Stage 5: narrate (`narrator.narrate`) — open-weight, grounded
The narrator receives ONLY the evidence block (the six features + verdict + the two dates), never raw
repo text (I4 anti-injection). It returns a 120–200-word coroner's report that cites ONLY those numbers:
```
EVIDENCE BLOCK (what the model sees):
  verdict: abandoned (confidence 0.81, via TabPFN)
  last commit: 2022-08-14 (806 days ago)   lifespan: ~3.3 years
  contributors: 7   bus factor: 1   recent velocity: ~0
NARRATION (grounded; every number above may appear, none else may):
  "Time of death: roughly 806 days ago. deadtool lived three and a half years... carried, in the end,
   by a single pair of hands — a bus factor of one. The commit cadence had been falling for months
   before the silence... "
```
**The grounding check** scans the output for any numeric/date token NOT in the evidence block; a
fabricated "12 contributors" or a wrong date triggers one retry, then the labeled templated eulogy.
`test_narration_grounding.py` proves this by mocking a fabricated number and asserting it's caught.

## VII.7 — Stage 6: render (certificate card + typing eulogy)
```
AutopsyResult {
  owner:"someuser", repo:"deadtool",
  meta:{stars:4200, primary_language:"Go", is_archived:false, ...},
  features:{...the six...},
  verdict:{mode:"abandoned", confidence:0.81, engine:"tabpfn", probs:{...}},
  narration:"Time of death: roughly 806 days ago...",
  certificate_id:"<slug-hash>"
}
```
The page renders the death-certificate card (ARCH §23 card markup — PART I; distinct from II.23 which is
the CI workflow), shows the **engine badge**
(`TabPFN` — the proof the model served, I3), and types the eulogy (reduced-motion → instant). This card
at 1200×630 is the post's cover image. The whole loop warm on Render is ~2–6s (TabPFN + Groq round-trips).

## VII.8 — What a WRONG trace looks like (so the build agent catches it)
- `parse_repo_url` returns `("someuser", "deadtool.git")` → the `.git` strip is missing (ARCH II.3 bug).
- `bus_factor` > 1 for a 92%-single-author repo → the cumulative-share loop is wrong (ARCH II.5 bug).
- Verdict `engine="tabpfn"` but TabPFN was never called (client swallowed) → an I2 violation; the verdict
  is a rule dressed as the model. The engine flag MUST reflect the real path.
- Narration contains "150 stars" when the evidence says 4200 → grounding check failed to fire (I4 bug).
Each of these is caught by a specific unit test or the per-file landing check — none can ship silently.

---

# PART VIII — ENVIRONMENT, TROUBLESHOOTING & CI RUNBOOK

## VIII.1 — Local dev bring-up (from a clean clone)
```
git clone <repo-url> && cd <repo>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill GROQ_API_KEY, TABPFN_TOKEN (GITHUB_TOKEN optional)
python scripts/build_seed.py    # produces data/seed_repos.csv (B0) — run once
uvicorn app.main:app --reload   # http://localhost:8000
```
**Expected:** uvicorn logs `Application startup complete`; the startup hook logs the seed row count and
one probe classification (ARCH II.29 / §18 observability). If startup logs `seed rows: 0`, the CSV wasn't
built — run `build_seed.py`.

## VIII.2 — Troubleshooting matrix (symptom → cause → fix)
| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: app` | wrong cwd / missing `app/__init__.py` | `cd` to repo root; `touch app/__init__.py` |
| `ModuleNotFoundError: tabpfn_client` | deps not installed / venv inactive | `source .venv/bin/activate && pip install -r requirements.txt` |
| startup `seed rows: 0` | `data/seed_repos.csv` not built | `python scripts/build_seed.py` |
| `/healthz` `tabpfn_reachable:false` | `TABPFN_TOKEN` unset / expired | set it in `.env` (local) or Render dashboard; re-probe |
| `/autopsy` 422 on a real repo | URL form not handled | check `parse_repo_url` against ARCH II.3; add the case |
| `/autopsy` 500 | uncaught GitHub edge (empty/archived) | map it in the error matrix (ARCH §11); never 500 (I6) |
| verdict always `engine=rules` | TabPFN client raising every call | token/network; read the `reason` string the fallback logged |
| narration cites a wrong number | grounding regex too loose | tighten `_numbers` in `narrator.py`; re-run grounding test |
| Render build fails on a wheel | pinned version has no Render wheel | bump the patch in `requirements.txt`; re-deploy |
| Render instance OOM-restarts | pandas/tabpfn imported at module top | lazy-import inside the handler (ARCH II.28) |
| Render cold/slow first hit | free tier / wrong plan | `render.yaml` must be `plan: starter`, `numInstances: 1`; add warm-ping |
| Groq `model_not_found` | model id rotated | update `LLM_MODEL`; re-probe the Groq chat endpoint |

## VIII.3 — CI (`.github/workflows/test.yml`, ARCH II.23)
On every push: set up Python 3.11 → `pip install -r requirements.txt` → `pytest`. The four unit tests are
network-free (mocks/synthetic series), so CI needs NO secrets. A red CI is a build-stop. CI green is also
a credibility signal in the public repo the post links. No deploy-from-CI — Render auto-deploys from the
connected repo on push to `main`.

## VIII.4 — The credentials gate (do this before the clock, per .input-manifest.json)
| Input | Tier | Verify command | Blocks |
|---|---|---|---|
| `GROQ_API_KEY` | required | Groq chat probe (PRE-BUILD) returns `ok` | B3, B5 |
| `TABPFN_TOKEN` | required | `from tabpfn_client import TabPFNClassifier` + one-row probe | B2, B5 |
| `RENDER_ACCOUNT` | required | login confirmed; Starter credits checked (hacktoberfest promos) | B5 |
| `GITHUB_TOKEN` | optional | a single authed `GET /rate_limit` shows the lifted limit | nothing (unauth works) |
| `DEVTO_LOGIN` | deferred | Dami's dev.to session via claude-in-chrome (package phase) | post publish only |
A required input unresolved by the clock-start is the ONE pre-build stop — resolve it (the tabpfn-client
email-confirm loop is the classic time-sink the Sonnet review flagged) before B0, not mid-B2.

## VIII.5 — Final pre-submission checklist (maps to SUBMISSION_STATUS.md)
- [ ] Live Render URL warm, `/healthz` 200 < 2s, `tabpfn_reachable:true`.
- [ ] Public repo pushed; `v1-submission` tag at the commit the post links.
- [ ] 4 unit tests green in CI (the badge is visible on the repo).
- [ ] 3 example certificates screenshotted in `evidence/`; `claims.json` rows point to real artifacts.
- [ ] `data/NOTES.md` ≥ 5 observations harvested during build (post raw material).
- [ ] The post: first-person number-in-title, ≥1 table, demo GIF embedded high, cover = the card,
      BOTH tags `devchallenge` + `hf26challenge`, live + repo links working.
- [ ] Open-source-AI explanation honest (TabPFN load-bearing + open-weight narration + Ollama-local note).
- [ ] Published by Oct 31, 18:00 WAT (internal cutoff) via Dami's dev.to session — SURFACE before publish.

## VIII.6 — Commit & tag ledger (the git history IS the build-story the post reuses)
One commit per phase, so `git log --oneline` reads as a narrative a judge (and the post) can follow.
```
chore: scaffold repo, venv, env; verify groq+tabpfn tokens       # PRE-BUILD
feat(seed): hand-labeled ~50-repo seed dataset + build_seed.py; LOO validated   # B0
feat(features): six git-forensic features + url validation; tests green          # B1
feat(classify): TabPFN in-context death-mode classifier + labeled rules fallback # B2
feat(narrate): grounded open-weight coroner's report + templated fallback        # B3
feat(ui): one-page autopsy UI, certificate card, typing eulogy, examples         # B4
chore: deploy config (render.yaml, requirements, CI)                             # B5 (pre-deploy)
feat(deploy): live on Render Starter (warm) + health check                       # B5
chore(demo): pre-warmed examples, evidence screenshots, claims.json              # B6
```
Then `git tag v1-submission` at the commit the dev.to post links. Any post-submission tweak goes on a
`post-submit/<x>` branch so the submitted commit stays pinned and reproducible for judges (I9 originality).

## VIII.7 — Observation-capture discipline (protecting the heaviest axis, I8)
The post's best paragraphs come from real build moments, not retrofitted abstraction. `data/NOTES.md`
grows DURING the build at four deliberate capture points — never reconstructed after:
1. **B0 (labeling):** the surprising repos — "I was sure this one was dead; it's quietly alive." The
   human reasoning behind each ambiguous label (abandoned vs burned_out vs pivoted) is the seed story.
2. **B2 (classifying):** any repo TabPFN classified against your intuition — correctly (the model saw
   something you didn't) or wrongly (what the seed was missing). Both are honest, interesting paragraphs.
3. **B5 (deploying):** the Render durable-tier lesson in practice — why free-tier spin-down would have
   killed the demo in the judging window, and what warm actually cost.
4. **B6 (census):** the graveyard numbers — death-mode distribution across the examples, engine mix,
   median latency. These feed the post's results table (PRD §37).
Each is captured as it happens because the package phase cannot invent them later — this is why the
build, not just the write-up, owns the raw material.

## VIII.8 — Decision provenance (where every locked choice came from — cross-ref DECISIONS.md)
So the build never re-litigates a settled call mid-phase:
- **TabPFN via hosted `tabpfn-client` (not local weights)** → avoids the headless browser license-accept;
  warroom + Sonnet review. Keeps B2 unblocked.
- **Groq-served open-weight narration (not a closed model)** → the challenge premise requires open AI;
  Groq gives ~85ms TTFB, no GPU. Swappable to Ollama-local via `LLM_BASE_URL` (I1, I11).
- **~50-repo hand-labeled seed, built by the real extractor** → TabPFN is few-shot in-context; without
  labeled rows it is not load-bearing (Sonnet review linchpin). `build_seed.py` computes seed features the
  SAME way as inference so there's no train/serve skew.
- **Issues/PR signals cut; server-side card render cut; multi-repo compare cut** → 1-day scope protection
  (Sonnet review scope cuts). Each cut is in LIMITATIONS.md as a conscious choice, not an omission.
- **Render Starter $7, numInstances=1, warm-pinged** → the dl-1 free-tier spin-down vector would hand a
  judge a dead link in the Nov-2 window; durability-tier.json records the conscious TIER-CHOICE (I5).
- **Standalone-fresh, in-window repo** → originality rule (CP1); no pre-existing code reused (I9).
These are RULED — a build phase that wants to reopen one STOPS and surfaces to Dami, it does not decide.

---

# PART IX — PHASED TASK STRUCTURE (canonical Phase N / Task N.X index)
The B0–B6 phases above, indexed in the canonical phased form. Each Task N.X maps to the detailed
commands/decision-trees in PART II.

## Phase 0 — Seed dataset (linchpin)
- Task 0.1 — Draft `scripts/seed_list.txt` (15–20 obvious cases first; rubric per PRD §48).
- Task 0.2 — Write `app/github.py`, `app/features.py`, `app/schemas.py` (ARCHITECTURE II.2/II.4/II.5).
- Task 0.3 — Write + run `scripts/build_seed.py` → `data/seed_repos.csv`; validate LOO separability.
- Task 0.4 — Capture 5–10 observations to `data/NOTES.md`; pad seed to ~50 (~10/class).

## Phase 1 — Feature extractor
- Task 1.1 — Finalize edge handling in `github.py`/`features.py` (404/empty/archived/window cap).
- Task 1.2 — Write `app/validators.py` + `tests/test_validators.py` + `tests/test_features.py`.
- Task 1.3 — `pytest` these green.

## Phase 2 — TabPFN classifier
- Task 2.1 — Write `app/classifier.py` (II.6 with `set_access_token`) + the 1-NN fallback (II.26).
- Task 2.2 — `tests/test_classifier_shape.py` green; smoke-classify 3 known repos.

## Phase 3 — Groq narration
- Task 3.1 — Write `app/narrator.py` (grounded prompt + grounding check + templated fallback).
- Task 3.2 — `tests/test_narration_grounding.py` green; eyeball the register per death-mode.

## Phase 4 — Web UI
- Task 4.1 — Write `app/cache.py`, `app/main.py` (+ startup prewarm II.29).
- Task 4.2 — Write `templates/index.html`, `static/app.js`, `static/card.css`.
- Task 4.3 — Local end-to-end loop + a11y checks; card screenshot-clean at 1200×630.

## Phase 5 — Deploy (Render, durable warm)
- Task 5.1 — Write `requirements.txt`, `render.yaml`, CI workflow; push to GitHub.
- Task 5.2 — Render web service from `render.yaml`; set env; confirm `/healthz` + warm <2s; RAM spot-check.

## Phase 6 — Demo-prep handoff
- Task 6.1 — Choose + set the 3 example repos; capture `evidence/*.png` screenshots.
- Task 6.2 — Write `claims.json` with evidence pointers; confirm `data/NOTES.md`; hand off to design/demo/package.
