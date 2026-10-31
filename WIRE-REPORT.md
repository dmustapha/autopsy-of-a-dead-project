# Wire Report

**Status:** WIRED-WITH-DEGRADATION
**Date:** 2026-10-30
**Project:** dev-ghost — "Autopsy of a Dead Project"
**Pipeline position:** After debug (confidence 92), before verify_milestone
**Run profile:** SPRINT · **Mode:** fresh (conductor-dispatched) · **Depth:** FULL, re-pointed per ADAPTATION-PLAYBOOK §wire

> **One-line verdict:** GitHub is proven LIVE end-to-end; TabPFN and Gemma are honestly marked **DEPLOY-GATED deep integrations** (auth/contract proven, live happy-paths owned by deploy — DEV-002/DEV-004). **No integration is reported WIRED over its labeled fallback.**

## Project Topology

| Component | Type | Entry Point |
|-----------|------|-------------|
| web | backend (FastAPI) | app/main.py (`/autopsy`, `/healthz`, rate limiter) |
| github-client | service | app/github.py (`fetch_repo`, `follow_redirects=True`) |
| classifier | service | app/classifier.py (`classify` — TabPFN + labeled rules fallback) |
| narrator | service | app/narrator.py (`narrate` — Gemma via Ollama + grounded template fallback) |
| features | service | app/features.py (`build_features` — 6-feature extractor) |
| card-ui | frontend | app/templates/index.html + app/static/{app.js,card.css} |

6 components, 6 connections. No "Integration Map" heading in ARCHITECTURE.md → discovery-mode topology.

## Connection Graph

| From | To | Type | Credential | Status |
|------|----|------|-----------|--------|
| github-client | GitHub REST API | api-call | GITHUB_TOKEN (optional) | **PASS** |
| classifier | TabPFN (Prior Labs hosted) | api-call | TABPFN_TOKEN | **PARTIAL** (auth ✓ / inference 503) |
| narrator | Gemma via Ollama | api-call | LLM_API_KEY (keyless) | **PARTIAL** (contract ✓ / no local daemon) |
| web | github-client | sdk | — | PASS |
| web | classifier | sdk | — | PASS |
| web | narrator | sdk | — | PASS |

## Credential Audit

| Env Var | Required By | Status | Source |
|---------|------------|--------|--------|
| TABPFN_TOKEN | classifier → TabPFN | **RESOLVED + AUTHENTICATES** (len 53, prefix `tabpfn_…`) | .env (staged) — `set_access_token` SUCCESS in 1545ms |
| LLM_API_KEY | narrator → Ollama | RESOLVED (`ollama` — keyless placeholder, **non-decorative**; Gemma needs no key) | .env |
| LLM_BASE_URL / LLM_MODEL | narrator → Ollama | RESOLVED (`http://localhost:11434/v1`, `gemma2:2b`) | .env |
| GITHUB_TOKEN | github-client → GitHub | ABSENT (optional — ran on 60/hr unauth limit; lifts to 5000/hr if added) | n/a |

**Secret posture:** `.env` is gitignored/**untracked**. The `env-proof/secret` gate ran a REAL secret sweep over `git ls-files` → **CLEAN** (all tracked `TABPFN_TOKEN`/`GROQ_API_KEY`/`GITHUB_TOKEN` hits are empty doc placeholders, not real-shaped values; no tracked binaries). No mock-mode flags found.

## Integration Test Results

| Connection | Test Type | Result | Time | Notes |
|-----------|-----------|:------:|-----:|-------|
| github-client → GitHub REST API | real endpoint (live) | **PASS** | 12365ms | 4 real repos fetched; org-moved `reactjs/redux` 301-followed to redux's canonical data (61440★); `rate_limited(403)` hit organically; `not_found/empty/301-follow` re-proven through real `fetch_repo` via MockTransport |
| classifier → TabPFN (Prior Labs) | real endpoint (live) | **PARTIAL** | 1545ms | `set_access_token` SUCCESS (token valid, auth up); real `classify()` → inference **503** → labeled `engine="rules"` fallback (no silent fake) |
| narrator → Gemma via Ollama | contract + fallback | **PARTIAL** | 1269ms | No daemon on :11434 → labeled template fallback ("Generated without the language model."); grounding guard proven load-bearing |

### GitHub — proven LIVE end-to-end (the only integration fully closable now)
- **`bower/bower`** ✓ (archived/abandoned exemplar, 14896★, created 2012-09-07, 1000 commits / 100 contributors)
- **`sindresorhus/caprine`** ✓ (7407★, created 2015-09-16)
- **`fastapi/fastapi`** ✓ (alive exemplar, 104261★, created 2018-12-08)
- **`reactjs/redux`** ✓ **ORG-MOVED** — 301-redirects to `reduxjs/redux`; the canonical redux payload (61440★, created 2015-05-29) came through, **proving `follow_redirects=True` chased the 301**. Without the flag, httpx returns the bare 301 and the parse breaks.
- **Error kinds:** `rate_limited` (403) proven **live/organic** on the 5th call; `not_found` (404), `empty` (409), and `301-follow` re-proven deterministically through the *real* `fetch_repo` code via `httpx.MockTransport` (the live 404 path was blocked by the exhausted unauth rate limit). Evidence: `evidence/wire/github-integration.json`.

## Deep-Integration Proof (6-criteria, re-aimed at TabPFN + Gemma per §wire)

The generic 6 criteria are re-pointed to this non-chain project's honesty surface. **CRIT catchers (crit-1…6 / BT-5 — the decorative/fake detectors): CLEAN** — `wire_deep_integration_gap` emits ZERO CRIT findings; no criterion is falsely marked proven.

| Criterion | TabPFN | Gemma |
|---|---|---|
| 1 Load-bearing | DEPLOY-GATED — verdict comes from TabPFN posterior when live; labeled `rules` fallback is an honesty feature | DEPLOY-GATED — eulogy comes from Gemma weights when live; labeled template is an honesty feature |
| 2 Sole-provider | DEPLOY-GATED — live, `engine="tabpfn"` is sole verdict source | DEPLOY-GATED — live, Gemma is sole eulogy source |
| 5 Fail-closed | **PROVEN NOW** — 503 logged + fell to labeled rules; never silent fake | **PROVEN NOW** — no daemon → labeled template; `_grounded` rejects fabricated `99999`/`530-maintainers` |
| 4 Live-tested | DEPLOY-GATED (DEV-002: auth up, inference 503) | DEPLOY-GATED (DEV-004: no local daemon) |
| 3 Multi-party / 6 Non-custodial / BT-5 browser | N/A (no chain / signers / custody) · browser proof deploy-owned | N/A · browser proof deploy-owned |

Evidence: `evidence/wire/model-integrations.json`, `evidence/wire/tabpfn-inference-503.log`.

## Blockers

| # | Blocker | Type | Connection | Recovery Hint |
|---|---------|------|-----------|---------------|
| 1 | **DEV-002** — TabPFN auth PROVEN but Prior Labs **inference** endpoint 503; app runs on labeled rules fallback; `engine="tabpfn"` + real LOO not yet proven | connection-failed (deploy-gated) | classifier → TabPFN | **DEPLOY-OWNED:** re-attempt fit/predict on Oracle. If recovered → capture live `engine="tabpfn"` card + measure real LOO (closes DEV-002). If still 503 → surface to Dami as a prize-level call; never silently ship on fallback. |
| 2 | **DEV-004** — no local Ollama daemon; real Gemma eulogy cannot be produced locally; narrate() uses labeled template | connection-failed (deploy-gated) | narrator → Gemma | **DEPLOY-OWNED:** install Ollama on Oracle, pull `gemma2:2b`, point `LLM_BASE_URL` at `http://localhost:11434/v1`, verify a real grounded (non-templated) eulogy renders (closes DEV-004). |

## Honest-Gaps (§14)

1. **TabPFN inference still 503 (DEV-002).** Build-day degradation persists. What CHANGED since build: the **auth** service is now UP and the staged token authenticates (`set_access_token` SUCCESS) — so the *only* remaining deploy-time variable is inference-service availability, not credentials or code. The real leave-one-out separability number and a live `engine="tabpfn"` card are **deploy/livetest-owned**. If Prior Labs is still 503 at deploy, that is a surfaced, prize-level decision for Dami — not a silent fallback ship.
2. **Gemma not exercised locally (DEV-004).** No Ollama daemon exists on this machine (by design — deploy co-locates it on Oracle). The contract is documented and the fallback + grounding guard are proven; a genuine Gemma eulogy is deploy/livetest-owned.
3. **GitHub live 404 path proven via real code + MockTransport, not a live 404 call.** The unauthenticated 60/hr limit was exhausted by the 4 full live fetches (each paginates ~1000 commits), so the live 404 would itself return 403. The 403/rate-limit path was instead proven **live/organically**, and 404/empty/301 were re-proven through the real `fetch_repo` with controlled responses. Adding `GITHUB_TOKEN` (5000/hr) removes this constraint at deploy.
4. **SPRINT shallow-policy OVERRIDE — surfaced loudly, not buried.** `di_shallow_gap` flags TabPFN + Gemma as "not proven DEEP under SPRINT = blocking." That generic rule assumes a non-DEEP integration is a *decorative fake on a live judged surface*. Here there is no live surface yet — it is created at **DEPLOY**, the phase that explicitly OWNS closing DEV-002/DEV-004 ("UNTESTED-by-design", BUILD-VERIFIED.md). Per the ratified Dami ruling 2026-10-30 (ADAPTATION-PLAYBOOK §wire) + debug's deploy-ownership handoff, the disposition is **WIRED-WITH-DEGRADATION with the obligation carried as deploy-owned blockers**, not wire-BLOCKED. The CRIT "fake-detector" catchers are clean; nothing decorative was passed.

## Summary

- Components discovered: **6**
- Connections mapped: **6** (3 external integrations)
- Credentials audited: **4** (3 resolved / 1 optional-absent; TABPFN_TOKEN authenticates)
- Integration tests: **1 PASS / 2 PARTIAL / 0 FAIL** (both PARTIALs are deploy-gated-by-design, not failures)
- Deep-integration CRIT catchers: **CLEAN** (0 decorative/fake)
- env-proof/secret gate: **CLEAN**
- Mock warnings: **0**
- Verdict: **WIRED-WITH-DEGRADATION** — never WIRED-on-fallback.
