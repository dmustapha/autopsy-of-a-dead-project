# WINNER-BRIEF — DEV Hacktoberfest Wk4 "Ghost in the Machine"

**Recommended winner (pending CP2 — Dami's pick):** **Autopsy of a Dead Project**
**Profile:** SPRINT · 1-day-equivalent build · the dev.to post is the deliverable (writing judged heaviest).

## Thesis
WINNING ARGUMENT: In a field crowded with ghost-story generators and haunted terminals, "Autopsy of a Dead Project" wins because it is the ONE concept where the open-source AI is genuinely load-bearing (not decoration), it unlocks three prize tracks at once, and it writes up into a gripping, first-person developer build-story — the single heaviest-judged axis.

- **Open-weight core is load-bearing (substitution test PASSES):** remove the tabular model and the app degrades to a git-stats page. Two distinct AI roles: **TabPFN** (Prior Labs open tabular foundation model) *classifies* a repo's death-mode from a feature table; a **Groq-hosted open-weight model** (Llama/Qwen) *narrates* the coroner's report / eulogy.
- **Tri-track grand-slam:** Overall ($250) + Best Use of Render ($200) + Best Use of TabPFN ($200). TabPFN is the beating heart, not a bolt-on — so the sponsor category is earned, not gamed.
- **Theme fit, question-shifted off the herd:** "Ghost in the Machine" read literally — the ghosts of dead code. Spooky AND functional AND (optionally) memorial (eulogy ending). Avoids collision with the ghost-story cluster and competitor PhantomTerminal.
- **Narratability:** feature-engineering → classification → AI narration → shareable artifact is a clean four-beat story arc; the "death certificate" card is a natural post hero image.

## What the user does (the one loop)
1. Paste a PUBLIC GitHub repo URL.
2. App fetches git/commit history → builds a feature TABLE (commit-cadence decay slope, days-since-last-commit, contributor count / bus-factor, PR merge rate — Issues/PR half-life is a bonus signal, not a gate).
3. **TabPFN** classifies death-mode (abandoned / pivoted / completed / burned-out) with calibrated confidence.
4. **Groq open-weight model** narrates a spooky coroner's report / eulogy that types out.
5. Output: a shareable "death certificate" card (cover-image + demo-video material).

## Scored pool (round_0, 4 independent scorers — criteria-weighted, Writing×0.40)
| Idea | Weighted | Tracks | Note |
|------|:--:|------|------|
| **#1 Autopsy of a Dead Project** | **8.61** | Overall+Render+TabPFN | Unanimous #1, divergence 0.80; substitution test passes |
| #2 Ofrenda / Voicekeeper | 7.35 | Overall+Render | High divergence 2.40 (dead-demo risk: local-Ollama>512MB) |
| #3 The Necromancer | 7.18 | Overall+Render | Live-sandbox runner risk |
| #4 Haunted Dependency | 6.83 | Overall+Render+TabPFN | Weaker sibling of #1 (deps vs repo) |

Killed: F Haunted Repo (herd collision, un-fixable); H2 Autopsy+Resurrect (two-product scope).

## Independent cross-model review (Sonnet, LAW#9) — verdict AGREE
- **Load-bearing CONTINGENT on a seed dataset:** TabPFN is a few-shot in-context learner — it needs labeled (X_train, y_train) rows at inference. **Lock before coding:** ship a hardcoded **~50-repo labeled seed dataset** (known dead repos hand-tagged by death-mode). This is the linchpin that makes TabPFN honestly causal; ~2h of curation, and it becomes a describable post artifact ("we hand-labeled 60 dead repos").
- **Scope cuts to protect the 1-day timeline:** (1) drop Issues/PR-half-life API (paginated, slow) — core features are commit-history + contributor + recency; (2) drop server-side card rendering — style a DOM card + screenshot it; (3) drop multi-repo comparison — one URL → one certificate is a complete loop.
- Writes up better than the memorial alternative (two distinct AI roles = stronger technical story + cleaner track targeting).

## Open-weight model + framework
- **Classification:** TabPFN via hosted `tabpfn-client` (API key) — sidesteps the local-weights browser license-accept (awkward headless).
- **Narration:** Groq free API serving an open-weight Llama/Qwen (OpenAI-compatible, ~85ms TTFB, no card).
- **Open-innovation narrative for the post:** mention Ollama + Gemma/Qwen fully-local/offline mode.

## Partner categories targeted
Render (committed — durable Starter $7 tier, kept warm through Nov-2 judging; dl-1) + TabPFN (load-bearing core).

## Standalone ruling
Standalone-fresh (CP1) — brand-new in-window, no pre-existing code.

## Handoff to forge
Scope ONE page, one paste-field, live on Render Starter. Build order: seed dataset → feature extractor → TabPFN classify → Groq narrate → certificate card → Render deploy. Post hook/title candidate: *"I performed an autopsy on my dead side-projects. An open-weight AI told me how they died."*

## Risk Register
- R1 — TabPFN not load-bearing without labeled rows → ship a hardcoded ~50-repo labeled seed dataset (lock before coding). [HIGH / mitigated]
- R2 — Render free tier spins down → dead demo in Nov-2 judging week → deploy durable Starter $7/mo, kept warm. [HIGH / mitigated]
- R3 — GitHub Issues/PR API pagination burns build time → cut from core feature table, commit-history+recency+contributors only. [MED / mitigated via scope cut]
- R4 — Server-side card rendering (puppeteer on Starter) adds deploy complexity → render DOM card + screenshot instead. [MED / mitigated via scope cut]
- R5 — Death-mode labels not cleanly derivable from git features → validate feature→label separability on the seed set before wiring the UI. [MED / open until build]
- R6 — Groq free-tier rate limits during the demo → cache the narration per repo; pre-warm the demo repos. [LOW / mitigated]
- R7 — tabpfn-client API key / license friction headless → use hosted client with key in env, avoid local-weights browser license-accept. [MED / mitigated]
- R8 — Theme reads as a spooky skin not genuine interpretation → lean the coroner/eulogy narrative into "Ghost in the Machine = ghosts of dead code"; verify against the live challenge page on build day (DS-1). [MED / open until build-day page read]
- R9 — Writing quality (heaviest axis) under-invested because build ran long → timebox the app, reserve a hard block for the docs-writer-grade post. [HIGH / process guardrail]
- R10 — Large repos make git history fetch slow → cap history window (e.g. last N commits) + add a loading state. [LOW / mitigated]
