# PLAN — Autopsy of a Dead Project (phased, 1-day SPRINT)

**PRE-BUILD (do before Day 1):** obtain + verify `TABPFN_TOKEN` (tabpfn-client registration may need an email-confirm loop — a blocked B2 mid-day is avoidable) and `GROQ_API_KEY`; confirm the Render account + Starter credits. See .input-manifest.json.

Each phase ≤ a half-day chunk; ordered so the linchpin (seed dataset) and the load-bearing core (TabPFN) are proven before UI polish.

## Build phases
- **B0 · Seed dataset (LINCHPIN, first).** Curate `data/seed_repos.csv`: ~50 known repos (abandoned/pivoted/completed/burned-out/alive), each with the F3 feature row + label. Source from GitHub graveyard lists, famous archived repos, and a few alive controls. Validate feature→label separability before wiring anything. *Exit: CSV loads, classes are balanced-ish, a quick TabPFN sanity-fit separates them; capture 5–10 surprising labeling observations to `data/NOTES.md` (raw material for the post's best paragraphs — protects the heaviest axis).* **Tactic:** seed 15–20 obvious cases (very-active + explicitly-archived) to prove separability FIRST, then pad to 50.
- **B1 · Feature extractor.** `github.py` + `features.py`: given owner/repo, fetch commits+contributors, build the feature row. Handle 404 / empty / archived / huge repos (cap commit window). *Exit: any public repo → a numeric feature row; unit tests pass.*
- **B2 · TabPFN classifier.** `classifier.py`: load seed CSV as in-context train, classify the target, return (death_mode, confidence, probs). Transparent forensic-rules fallback if client unreachable. *Exit: 3 known repos classify sensibly; confidence returned.*
- **B3 · Groq narration.** `narrator.py`: verdict+features → a grounded coroner's report/eulogy (cites the real features, no invented numbers). *Exit: narration reads well, grounded, 120–200 words.*
- **B4 · Web UI (one page).** `index.html` + `main.py` routes: paste field, loading state, death-certificate card, typing animation, OG/cover image. *Exit: full loop works locally end-to-end.*
- **B5 · Deploy (Render, durable warm).** `render.yaml` Starter + min-instances=1 + `/healthz` + external warm-ping. Env: `GROQ_API_KEY`, `TABPFN_TOKEN`, optional `GITHUB_TOKEN`. *Exit: public URL responds <2s; full loop works live; spot-check RAM on Starter (512MB ceiling — pandas+numpy+tabpfn-client import footprint) before demo recording.*
- **B6 · Demo-prep handoff.** Pre-warm 3 demo repos (one per death-mode); capture screenshots for the post. *Exit: artifacts ready for design/demo/package phases.*

## Downstream (owned by later phases — do not build here)
- Design pass / screenshots carry the post → design + deploy.
- Demo GIF/video → demo.
- The dev.to POST (the deliverable) → package (docs-writer-grade).

## Skill-Ownership Map (routing pass SO-2)
Load-bearing judged-surface deliverables, each tagged with its registry owner in `owner: X @ phase`:
- **PRD / ARCHITECTURE / PLAN / DECISIONS / SECURITY / LIMITATIONS / SUBMISSION_STATUS** → owner: hackathon-forge @ forge
- **Application code + seed dataset + tests** → owner: implementation (build) @ build
- **claims.json + evidence/** → owner: build @ build (verify populates, deploy renders)
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
# write app/github.py, app/features.py, app/schemas.py (ARCHITECTURE II.2,II.4,II.5)  [needed by build_seed]
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
