# Verify Report — MILESTONE mode

**Decision:** ✅ **PROCEED**
**Date:** 2026-10-30
**Project:** dev-ghost — "Autopsy of a Dead Project"
**Pipeline position:** After wire (WIRED-WITH-DEGRADATION), before design
**Run profile:** SPRINT · **Mode:** fresh (conductor-dispatched) · **Depth:** FULL, re-pointed per ADAPTATION-PLAYBOOK §verify_milestone (607 lines / sha8 c44c0945)

> **One-line verdict:** The dual open-weight core (TabPFN + Gemma) is **PRESENT-AND-WIRED**; both run on **labeled, honest fallbacks** locally (not a HOLD); 0/5 VF failures; 0% PRD feature-delta; DEV-002/DEV-004 correctly **deploy-owned**, not milestone blockers.

---

## 1. VF Recompute Sampling (HOLD at 2+ failures)

| VF | Source | Claim | Expected | Actual | Result |
|----|--------|-------|----------|--------|:------:|
| VF-1 | build/debug | seed CSV 48 rows, 5 balanced modes | `48 {abandoned:10,alive:10,burned_out:9,completed:9,pivoted:10}` | identical | **PASS** |
| VF-2 | build/debug | offline suites green | ≥14 passed | **24 passed** (debug added 10 hardening tests) | **PASS** |
| VF-3 | build | rules fallback ALWAYS labels `engine=rules` | `rules` | `rules` | **PASS** |
| VF-W2 | wire | `TABPFN_TOKEN` authenticates live (inference 503) | `AUTH_OK` | `AUTH_OK` | **PASS** |
| VF-W3 | wire/debug | grounding rejects fabricated `99999`, accepts true numbers | `True False` | `True False` | **PASS** |

**5 sampled / 5 PASS / 0 FAIL** — far under the 2+ HOLD threshold. VF-W1 (GitHub live fetch) was intentionally **not re-counted** to avoid consuming the 60/hr unauth limit (a 403 there is NOT a failure, per dispatch; wire already proved it LIVE on 4 real repos). The two preferred no-network-sensitive VFs (VF-W2 auth-cache, VF-W3 pure function) both pass.

---

## 2. PRD Feature-Delta (HOLD at >30% MISSING/PARTIAL)

| Surface | Status | Evidence |
|---------|:------:|----------|
| `features.py` — 6-feature extractor | **PRESENT** | `build_features()` emits all 6: days_since_last_commit, commit_cadence_decay (slope), lifespan_days, contributor_count, bus_factor, velocity_ratio |
| `classifier.py` — dual-engine | **PRESENT** | `classify()` fits `TabPFNClassifier` (auth before fit) → `engine="tabpfn"`; `_forensic_rules` → `_nearest_mode` (1-NN, never hard-coded) → `engine="rules"` |
| `narrator.py` — grounded | **PRESENT** | Gemma via Ollama OpenAI-compat client (gemma2:2b); 2-attempt retry w/ grounding re-prompt; `_grounded`/`_metric_values`/`_numbers` binding gate; labeled `_template` fallback |
| `/autopsy` | **PRESENT** | `@app.post` w/ rate_limit + `AutopsyResult` model |
| `/healthz` | **PRESENT** | `@app.get` (token-presence proxy per invariant, test-asserted) |
| seed CSV (48 / 5 modes) | **PRESENT** | VF-1 |
| certificate card | **PRESENT** | `index.html #certificate` + `app.js` renders "Certificate of Death", verdict/confidence/evidence table, honest engine badge |

**0% MISSING/PARTIAL.** No boilerplate; every surface has real substance. No drift from `ARCHITECTURE.md`.

---

## 3. Architecture CORE Check — PRESENT-AND-WIRED

The dual open-weight core is the whole thesis. Both components are **imported, called with real data, and wired into the core UX** — neither is a stub.

| Component | Status | Local state (HONEST, not a HOLD) |
|-----------|:------:|----------------------------------|
| **TabPFN** (Prior Labs tabular FM) | PRESENT-AND-WIRED | Inference 503 → falls to labeled `engine="rules"`; `set_access_token` proven live |
| **Gemma** (gemma2:2b via Ollama) | PRESENT-AND-WIRED | No local daemon → falls to labeled `"(Generated without the language model.)"`; grounding guard load-bearing |

Per wire's handoff and BUILD-VERIFIED (DEV-002/DEV-004 UNTESTED-by-design), **fallback-active locally is HONEST, not a HOLD** — the engine labels itself (`engine="rules"` / templated eulogy). Absent/stub would be a HOLD; neither is. The deploy-gated 503/no-daemon is **NOT** held against this milestone.

---

## 4. Demo-Path Check — now-runs vs deploy-needs

**Runs NOW (local, green):**
GitHub fetch (301-follow + all error kinds) → 6-feature extraction → rules verdict (labeled `engine=rules`) → templated grounded eulogy → certificate card with honest badge → `/healthz` 200 → full error matrix (bad input 422 / 404 friendly 422 / no uncaught 500).

**Needs DEPLOY:**
- Real `engine="tabpfn"` card + measured leave-one-out separability number — **DEV-002** (Prior Labs inference recovery).
- Real non-templated Gemma eulogy via co-located Ollama on the Oracle box — **DEV-004**.

Demo path is **green for everything except the two model happy-paths**, which are architecturally owned by deploy.

---

## 5. Kill-Zone Early Warnings

**KZ-4 (sponsor-call) — RE-AIMED onto TabPFN + Gemma as the "sponsors":**
⚠️ **EARLY WARNING.** Both partner models are currently on labeled fallbacks locally. This is honest and correct at this milestone, BUT: **the two $200 categories are won only if the models genuinely do the work live.** A deploy that fails to flip TabPFN to `engine="tabpfn"` and produce a real Gemma eulogy is **the category-losing event** — downstream HOLD logic (livetest F3 ABCD, verify_preflight KZ-4) must treat a deploy-time fallback as the loss condition it is. If TabPFN is still 503 at deploy, that is a prize-level call to surface to Dami, never a silent fallback ship.

**KZ-3 (contract-chain):** SKIPPED — no contracts exist in this project.

---

## 6. Deploy-Owned Blockers (recorded, NOT milestone HOLDs)

| ID | Owner | Detail | Milestone treatment |
|----|:-----:|--------|---------------------|
| DEV-002 | deploy | TabPFN inference 503; **auth PROVEN** (`set_access_token` SUCCESS). Re-attempt on Oracle; if still 503 → surface to Dami. | Correctly owned by deploy — PROCEED records it, does not HOLD |
| DEV-004 | deploy | Gemma no local daemon (expected). Install Ollama + `ollama pull gemma2:2b` on Oracle; verify real grounded eulogy. | Correctly owned by deploy — PROCEED records it, does not HOLD |

---

## 7. Honest Gaps

1. Real TabPFN LOO number + live `engine="tabpfn"` card UNMEASURED until deploy (DEV-002). Current honest proxy: 1-NN LOO = **31% (chance 20%)**.
2. Real Gemma eulogy register/latency UNVERIFIED until deploy (DEV-004).
3. `claims.json` rows `certificate-screenshots` (design-owned) + `live-deploy-warm` (deploy-owned) are `pending` — downstream, not milestone-blocking. The other 8 claim rows are `verified`.
4. VF-W1 GitHub live fetch not re-counted to preserve the unauth rate limit; proven LIVE by wire.

---

## Summary

- VF sampled / passed: **5 / 5** (0 failures; HOLD at 2+)
- PRD feature-delta MISSING/PARTIAL: **0%** (HOLD at >30%)
- Architecture core: **PRESENT-AND-WIRED** (TabPFN + Gemma; honest fallbacks)
- Demo path: **green** except the two deploy-gated model happy-paths
- KZ-4: **early-warning raised** (models on fallbacks; deploy is where the categories are won/lost)
- DEV-002 / DEV-004: **recorded deploy-owned**, not milestone HOLDs
- **DECISION: PROCEED → design**
