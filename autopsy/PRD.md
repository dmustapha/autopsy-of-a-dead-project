# PRD — Autopsy of a Dead Project

**Hackathon:** DEV Hacktoberfest Open-Source AI Challenge — Week 4: "Ghost in the Machine"
**Track:** Overall ($250) + Best Use of Render ($200) + Best Use of TabPFN ($200) — tri-track grand slam
**Deadline:** 2026-10-31 11:59 PM PDT (internal cutoff: published 18:00 WAT Oct 31)
**Profile:** SPRINT · 1-day-equivalent build · scope_mode: `standard`
**Source:** warroom (unanimous #1, weighted 8.61)

---

## Section 1: Project Overview

**One-liner:** Paste a public GitHub repo URL and an open-weight AI performs an autopsy — it reads the repo's git history, classifies *how the project died*, and narrates a spooky coroner's report, ending in a shareable death certificate.

**Problem statement (the shocking number):** Over 90% of open-source side projects are abandoned — and GitHub is a graveyard of them. But no tool tells you *how* a project died, only *that* it went quiet. The cause-of-death is written in the commit history; nobody reads the autopsy.

**Solution summary:** `Autopsy` is a one-page web app. You paste a public GitHub repo URL. The app fetches the repo's commit history and metadata via the GitHub REST API and engineers a small feature table (commit-cadence decay, days-since-last-commit, contributor count / bus-factor, lifespan, star/issue ratios). **TabPFN**, Prior Labs' open tabular foundation model, classifies the repo's death-mode — `abandoned`, `pivoted`, `completed`, or `burned-out` — with a confidence distribution, trained in-context on a hand-labeled seed dataset of ~50 real dead repos. A **Groq-hosted open-weight model** (Llama/Qwen-class) then narrates a coroner's report / eulogy in a spooky-but-forensic voice, which types out character by character. The output is a styled "death certificate" card — the post's hero image and the demo's climax.

**Why this wins (mapped to judging criteria):**
- **Writing quality (~40%, heaviest):** feature-engineering → classification → AI narration → shareable artifact is a clean four-beat arc. First-person build-story with a measured table and a death-certificate hero image — exactly the winning-post anatomy (munim study: 86% of winners are longer, 80% have a cover image, 29% have a table).
- **Theme relevance (~20%):** "Ghost in the Machine" read literally — the ghosts of dead *code*. A coroner's séance over a commit DAG. Spooky AND functional AND memorial (the eulogy ending). Question-shifted off the ghost-story-generator / haunted-terminal herd.
- **Creativity (~18%):** nobody else in the field is doing tabular prediction over git history. Blue-ocean angle.
- **Technical execution (~15%):** a live deployed app on Render beats a local screenshot; the full loop works end-to-end.
- **Partner tech (~7%):** TabPFN is load-bearing (the verdict IS its output — substitution test passes); Render hosts the live demo durably.

**Thesis framing (§1 = Thesis field 1, WINNING ARGUMENT):** The one concept where the open-source AI is genuinely load-bearing (not decoration), unlocks three prize tracks at once, and writes up into a gripping first-person developer build-story — the single heaviest-judged axis. *Drift tripwire check:* the headline is the forensic autopsy, NOT a ghost-story generator, NOT a haunted terminal, NOT a git-stats page.

---

## Section 2: System Architecture Overview

```
                    ┌──────────────────────────────────────────────────┐
                    │               Render Starter ($7/mo)              │
                    │              single FastAPI web service           │
   browser          │                                                  │
  ┌────────┐ paste  │  ┌──────────┐   ┌─────────────┐   ┌────────────┐ │
  │ one-   │ URL    │  │  routes  │──▶│   features   │──▶│  classify  │ │ ──▶ tabpfn-client
  │ page   │───────▶│  │ (FastAPI)│   │  (git→table) │   │  (TabPFN)  │ │ ◀── proba
  │ paste  │        │  └────┬─────┘   └──────┬───────┘   └─────┬──────┘ │
  │ field  │◀───────│       │                │                 │        │
  └────────┘ HTML/  │       │                ▼                 ▼        │
   death     stream │       │          GitHub REST API   ┌───────────┐  │
   certificate      │       └─────────────────────────▶ │  narrate  │  │ ──▶ Groq API
                    │                                    │  (Groq)   │  │ ◀── tokens
                    │                                    └───────────┘  │
                    │   seed_dataset.csv (committed ~50-repo artifact)  │
                    └──────────────────────────────────────────────────┘
```

**Component table:**

| Name | Type | Purpose | Key Dependencies |
|------|------|---------|------------------|
| `app` (routes) | FastAPI web service | Serve the one page, accept the pasted URL, orchestrate the loop, stream the result | fastapi, jinja2, uvicorn |
| `github` | module | Fetch commits + repo meta + contributors for a public repo (no clone) | requests, GitHub REST API |
| `features` | module | Engineer the feature table from raw git history | python (pure), pandas-free (stdlib + numpy) |
| `classify` | module | TabPFN in-context classification over the seed dataset | tabpfn-client, seed_dataset.csv |
| `narrate` | module | Groq open-weight model narration (streamed) | groq SDK |
| `seed_dataset.csv` | build artifact | ~50 hand-labeled dead repos (features + death-mode label) | committed to repo |
| `certificate` | template | Styled death-certificate DOM card | jinja2 + CSS |

**Data flow:** URL → `github.fetch()` → raw commit/meta/contributor JSON → `features.build()` → one feature row → `classify.predict()` (fits TabPFN on seed_dataset.csv, predicts the pasted repo's row) → `{death_mode, proba[]}` → `narrate.stream()` (feeds verdict + features to Groq) → streamed coroner's report → `certificate` card rendered with verdict + confidence bars + narration.

**State management:** Stateless. The only persistent artifact is `seed_dataset.csv`, committed to the repo (not runtime-written). Per-repo results are cached in an in-process LRU for the pre-warmed demo repos; cache loss on restart costs one recompute, never data.

---

## Section 3: User Flows

**Flow 1 — Cold judge, pre-seeded first visit (the Judge Experience):**
1. Judge opens the live Render URL.
2. Landing shows: a one-line legibility statement ("Paste a dead GitHub repo. An open-weight AI tells you how it died."), a paste field, and — immediately visible — a completed death-certificate for a pre-seeded famous dead repo (no empty state).
3. Judge understands what it does in <10s, sees the core value (a real verdict) in <30s, and can try it in <60s by pasting any URL.

**Flow 2 — Happy path (paste → autopsy):**
1. User pastes `https://github.com/owner/repo`.
2. App validates + parses owner/repo. Loading state: "Exhuming commit history…".
3. `github.fetch` pulls commits (capped at last N=300), repo meta, contributors.
4. `features.build` computes the feature row. Loading state: "Reading the cause of death…".
5. `classify.predict` returns death-mode + confidence distribution. Confidence bars render.
6. `narrate.stream` types out the coroner's report character-by-character.
7. Death-certificate card assembles: verdict, confidence bars, narration, repo name, "time of death" (last commit date), lifespan.

**Flow 3 — Error / edge cases:**
- Invalid URL (not a github.com repo) → inline message "That's not a GitHub repo URL — paste a public repo."
- Repo not found / private (404) → "This grave is empty or sealed (repo not found or private)."
- Repo is alive (pushed within 30 days) → verdict may be `completed` or a playful "This one's still breathing" note; still runs the full loop honestly.
- GitHub rate limit (403/429) → "The crypt is busy (GitHub rate limit) — try again in a minute." (Mitigated by optional GITHUB_TOKEN raising to 5000/hr.)
- Groq rate limit → fall back to the cached narration for demo repos; for a cold repo, show the verdict + a terse templated epitaph and a "narration unavailable" honest note (never fabricate).

---

## Section 4: Technical Specifications

**4.1 `github` module**
- Purpose: fetch a public repo's commit history, metadata, and contributor list without cloning.
- Interface: `fetch(owner: str, repo: str) -> RepoData` where `RepoData = {commits: list[dict], meta: dict, contributors: list[dict]}`.
- Consumes: GitHub REST API. `GET /repos/{o}/{r}/commits` (per_page=100, Link-header pagination, cap at 300 commits), `GET /repos/{o}/{r}`, `GET /repos/{o}/{r}/contributors`.
- Auth: optional `GITHUB_TOKEN` as `Authorization: Bearer <token>` (60/hr → 5000/hr). Works unauthenticated for the demo.
- Headers: `Accept: application/vnd.github+json`, `X-GitHub-Api-Version: 2026-03-10`.
- Performance: cap history at last 300 commits to bound latency on large repos.

**4.2 `features` module**
- Purpose: engineer a single feature row from raw git history.
- Interface: `build(repo_data: RepoData) -> dict[str, float]`.
- Feature columns (the measured table): `days_since_last_commit`, `lifespan_days`, `total_commits`, `commit_cadence_decay` (ratio of commit rate in the last third of the lifespan vs the first third), `contributor_count`, `bus_factor` (top-1 contributor's share of commits), `stars`, `open_issues`, `archived` (0/1), `commits_per_week_peak`.
- Dependencies: numpy for the decay slope; otherwise stdlib.

**4.3 `classify` module (TabPFN — load-bearing core)**
- Purpose: classify the pasted repo's death-mode by in-context learning over the seed dataset.
- Interface: `predict(feature_row: dict) -> {death_mode: str, proba: dict[str,float], classes: list[str]}`.
- Mechanism: on startup, load `seed_dataset.csv` → `(X_train, y_train)`. Per request: `TabPFNClassifier().fit(X_train, y_train).predict_proba(X_test_single_row)`. Classes: `abandoned | pivoted | completed | burned-out`.
- Auth: `set_access_token(TABPFN_TOKEN)` at startup (headless, no browser).
- **Honesty invariant:** TabPFN is the SOLE provider of the verdict. No rules engine substitutes for it. If tabpfn-client is unreachable, the app shows a BLOCKED state ("the coroner is unavailable"), never a fabricated verdict.
- Note: `predict_proba` is NOT documented as calibrated by default — the post describes it as a "confidence distribution," not "calibrated probability," unless `eval_metric` calibration is wired and verified at build.

**4.4 `narrate` module (Groq — open-weight narration)**
- Purpose: narrate a spooky-but-forensic coroner's report from the verdict + features.
- Interface: `stream(verdict: str, proba: dict, features: dict, repo_name: str) -> Iterator[str]`.
- Mechanism: `Groq(api_key=GROQ_API_KEY).chat.completions.create(model=<free-tier open-weight id>, messages=[system, user], stream=True)`; yield `chunk.choices[0].delta.content` (guard `None`).
- Model: `openai/gpt-oss-20b` (free-tier-safe open-weight). Fallback: `qwen/qwen3.8-27b`. **NOT** `llama-3.3-70b-versatile` (decommissioned on free tier 2026-08-16).
- Caching: narration cached per repo (LRU) to survive Groq rate limits during the demo.

**4.5 `certificate` template**
- Purpose: render the styled death-certificate DOM card.
- Content: repo name, death-mode verdict (large), confidence bars (one per class), "time of death" (last commit date), lifespan, the typed narration, a subtle tombstone/parchment aesthetic.
- Rendered server-side as HTML (Jinja2) + CSS; screenshotted for the post hero image (no server-side puppeteer — scope cut R4).

---

## Section 5: API Contracts

**5.1 GitHub REST API**
- `GET https://api.github.com/repos/{owner}/{repo}/commits?per_page=100` → `[{sha, commit:{author:{date}}, ...}]`. Paginate via `Link` header (`r.links.next.url`). Cap at 300.
- `GET https://api.github.com/repos/{owner}/{repo}` → `{pushed_at, created_at, stargazers_count, open_issues_count, archived, ...}`.
- `GET https://api.github.com/repos/{owner}/{repo}/contributors?per_page=100` → `[{login, contributions}]` (sorted desc).
- Auth: `Authorization: Bearer {GITHUB_TOKEN}` (optional). Rate limit: 60/hr unauth, 5000/hr auth.
- Errors: 404 (not found/private), 403/429 (rate limit), 451 (DMCA takedown — treat as "grave sealed").

**5.2 TabPFN (tabpfn-client hosted)**
- Python client, not raw HTTP. `set_access_token(TABPFN_TOKEN)`; `TabPFNClassifier().fit(X, y).predict_proba(X_test)`.
- Auth: `TABPFN_TOKEN` env (from platform.priorlabs.ai/account/api-keys).
- Limits: hosted TabPFN-3.5 handles far more than the seed set needs (1M rows / 2k features / 160 classes); our ~50 rows × ~10 features × 4 classes is trivially within bounds.
- Errors: auth failure → BLOCKED state; rate/timeout → retry once then BLOCKED (never fabricate).

**5.3 Groq API**
- OpenAI-compatible via `groq` SDK. `client.chat.completions.create(model, messages, stream=True)`.
- Auth: `GROQ_API_KEY` env (console.groq.com, no card).
- Model IDs (free-tier-safe, verified 2026-10-29): `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`. ~1000 req/day free.
- Errors: 429 rate limit → cached narration (demo) or honest "narration unavailable" note (cold repo).

---

## Section 6: Demo Script

Target: ~90s recorded demo (conductor videoLengthRequirement=90), embedded as a GIF/video in the post (42% winner separator).

| # | On screen | Voiceover (first-person, active, no em-dash) | Duration |
|---|-----------|-----------------------------------------------|----------|
| 1 | Landing page, pre-seeded certificate visible | "Every dev has a graveyard of dead side projects. I built a tool that performs an autopsy on them." | 12s |
| 2 | Paste a famous dead repo URL, click Autopsy | "I paste a public GitHub repo. No login, no setup." | 8s |
| 3 | Loading states: "Exhuming commit history…" → "Reading the cause of death…" | "It pulls the git history and builds a feature table from how the project actually behaved." | 15s |
| 4 | Confidence bars render, verdict shows "ABANDONED 71%" | "TabPFN, an open tabular foundation model, classifies the death mode in one forward pass. This verdict is the model's output, not a rule I wrote." | 18s |
| 5 | Coroner's report types out | "Then an open-weight model on Groq narrates the coroner's report. The ghost in this machine is the ghost of dead code." | 20s |
| 6 | Full death-certificate card | "One URL, one certificate. Live on Render. Here's how I built it." (cut to post) | 17s |

**Voice & copy compliance:** no em-dashes in voiceover; active voice; no buzzwords; technical-but-direct. YouTube title ≤100 chars, first-person + number: *"I performed an autopsy on 50 dead GitHub repos. An open-weight AI told me how they died."*

---

## Section 7: Risk Register

| # | Risk | Severity | Likelihood | Impact | Mitigation | Decision Tree |
|---|------|:--:|:--:|------|-----------|:--:|
| R1 | TabPFN not load-bearing without labeled rows | HIGH | — | Verdict becomes a bolt-on; TabPFN track lost | Ship hardcoded ~50-repo labeled seed dataset (lock FIRST, Phase 1 build task) | DT-1 |
| R2 | Render free tier spins down → dead judging demo | HIGH | MED | Judge sees a 30-60s hang → scored dead | Durable Starter $7/mo, kept warm via 10-min /healthz heartbeat | DT-2 |
| R3 | GitHub Issues/PR pagination burns build time | MED | — | Scope overrun | CUT from core features; commit-history + recency + contributors only | DT-3 |
| R4 | Server-side card rendering adds deploy complexity | MED | — | Puppeteer on 512MB Starter is fragile | Render DOM card + screenshot manually; no server-side render | — |
| R5 | Death-mode labels not cleanly separable from git features | MED | MED | TabPFN accuracy poor, verdicts look random | Validate feature→label separability on seed set BEFORE wiring UI (hold-out check) | DT-4 |
| R6 | Groq free-tier rate limit during demo | LOW | MED | Narration fails live | Cache narration per repo; pre-warm demo repos; honest fallback note | DT-5 |
| R7 | tabpfn-client key / license friction headless | MED | LOW | Classify dead on Render | Hosted client + TABPFN_TOKEN env (verified headless path, no browser) | DT-6 |
| R8 | Theme reads as a spooky skin, not genuine interpretation | MED | MED | Theme score (~20%) suffers | Lean coroner/eulogy narrative into "ghosts of dead code"; read LIVE challenge page build day (DS-1) | DT-7 |
| R9 | Writing (heaviest axis) under-invested because build ran long | HIGH | MED | Lose the Overall track | Timebox the app; reserve a hard block for the docs-writer-grade post | DT-8 |
| R10 | Large repos make git fetch slow | LOW | MED | Latency / timeout | Cap history at last 300 commits + loading state | DT-9 |
| R11 | TabPFN proba presented as "calibrated" when it is not by default | MED | LOW | Overclaim a judge can check → credibility hit | Describe as "confidence distribution"; only claim calibration if eval_metric wired + verified | DT-4 |

11 risks across Technical (R1,R5,R7,R10,R11), Infra/Demo (R2,R4,R6), Scope (R3), Theme/Judging (R8), Time (R9).

---

## Section 7.4b → see USER-ONBOARDING.md
## Section 7.4c → see ROUTE-ARCHITECTURE.md

## Section 7.5: Judge Experience

- **First-visit state:** the live URL opens with a pre-computed death-certificate for a famous dead repo already on screen (seeded) — no empty state, no login wall. Paste field above it.
- **Seed script requirements:** `scripts/seed_demo.py` pre-warms the LRU cache for 3 demo repos (one per interesting death-mode) by running the full loop at startup, so the first judge click is instant and the landing shows a real certificate.
- **10-second test:** hero line "Paste a dead GitHub repo. An open-weight AI tells you how it died." + a visible certificate.
- **30-second test:** the confidence bars + verdict of the seeded certificate communicate the core value.
- **60-second test:** the paste field + "Autopsy" button is the single hero CTA; pasting any URL runs the loop.
- **Demo-Insurance Invariant Check:** the seeded certificates are REAL outputs (the full loop genuinely run in advance on real repos), not fabricated state — Thesis invariant 5 holds. The honest fallback (Groq down → "narration unavailable" note) never fabricates a verdict.
- **Keys-off-host:** non-custody. No keys/funds on host. Cold judge completes the hero path with zero local setup.

## Section 7.6: Judge Proof Artifacts

- **Proof section:** a `## How I Built It` + `## Open Innovation` section in the dev.to post naming the exact open-weight model, the TabPFN classifier, and the seed-dataset artifact. A repo `README` "Proof" block listing the live Render URL + the committed `seed_dataset.csv`.
- **Required artifacts:** live Render URL; the ~50-row labeled `seed_dataset.csv` (the describable post artifact "I hand-labeled 50 dead repos"); a hold-out accuracy number from the separability check (R5); screenshots of 3 death-certificates.
- **Proof generation:** build runs `scripts/eval_seed.py` to produce the hold-out accuracy figure; the demo phase captures the certificate screenshots.

---

## Section 8: Day-by-Day Build Plan

SPRINT 1-day-equivalent. Deadline Oct 31 18:00 WAT. ~2 effective build days remain (Oct 30–31). `scope_mode: standard` (fewer REAL features, full doc depth).

| Block | Objective | Deliverable |
|-------|-----------|-------------|
| Day 1 AM | DS-1 live-page read; seed dataset (~50 repos hand-labeled); feature extractor; separability check | `seed_dataset.csv`, `features.py`, hold-out accuracy |
| Day 1 PM | TabPFN classify + Groq narrate wired; FastAPI one-page loop end-to-end locally | working localhost loop |
| Day 2 AM | Certificate card styling; seed/demo cache; error states; deploy to Render Starter (kept warm) | live Render URL |
| Day 2 PM | **Hard-reserved writing block** — the dev.to post (cover image, ~2k words, table, demo GIF, first-person title); submit | published post |

Buffer: the writing block is protected (R9) — if the app runs long, cut polish, never the post.

## Section 9: Dependencies & Prerequisites

- **Accounts/keys:** GROQ_API_KEY (console.groq.com, no card), TABPFN_TOKEN (platform.priorlabs.ai), Render account (durable Starter $7/mo), optional GITHUB_TOKEN. See `.input-manifest.json`.
- **Dev tools:** Python 3.10+, pip. Packages: fastapi, uvicorn, jinja2, requests, numpy, tabpfn-client, groq.
- **Manual setup:** read the LIVE Wk4 challenge page on build day (DS-1); hand-label ~50 dead repos for the seed dataset; accept Render spend.

## Section 10: Concerns Compliance

| Concern | How the PRD addresses it |
|---------|--------------------------|
| [C] Demo end-to-end | Flow 2 + Section 7.5 seed script; the full loop is the hero path, pre-warmed |
| [C] Render durability | R2 + durability-tier.json: Starter $7/mo, kept warm, stateless |
| [C] TabPFN load-bearing | Section 4.3 honesty invariant: sole provider, no rules fallback; R1 seed dataset locked first |
| [I] Writing time | Section 8 hard-reserved writing block; R9 |
| [I] Theme fidelity | R8; coroner/ghosts-of-dead-code framing; DS-1 live-page read |
| [A] Card polish | Section 4.5; advisory, after the loop + post |

All [C] concerns addressed. PRD complete.
