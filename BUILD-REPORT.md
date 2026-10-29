# Build Report — Autopsy of a Dead Project
Generated: 2026-10-29
Builder: hackathon-build skill (conductor-dispatched, fresh)

## Summary
| Phase | Steps | Status | Notes |
|-------|-------|--------|-------|
| B0 Seed dataset (linchpin) | 0.1–0.4 | PASS-WITH-BLOCKER | 48-row CSV, all 5 classes, balance 10/10/10/9/9. TabPFN LOO UNMEASURABLE (Prior Labs 503 outage); 1-NN proxy LOO = 31%. Documented rules-primary fallback (ADR-007). |
| B1 Feature extractor | 1.1–1.3 | PASS | github.py redirect fix + validators/features tests green. |
| B2 TabPFN classifier | 2.1–2.2 | PASS-WITH-BLOCKER | classifier.py + 1-NN fallback written; shape test green. TabPFN happy path UNTESTED (service 503); rules path proven. |
| B3 Gemma narration | 3.1–3.2 | PASS-WITH-BLOCKER | narrator.py wired to Ollama/Gemma (FINAL STACK) + grounding test green. Gemma-via-Ollama deferred to deploy (no local Ollama); proven end-to-end via templated fallback. |
| B4 Web UI + local loop | 4.1–4.3 | PASS | Full local e2e loop: real repo → classify → grounded eulogy → rendered card. Rate limiter wired. |
| B5 Deploy artifacts (Oracle) | 5.1 | ARTIFACTS-ONLY | systemd units, nginx conf, requirements, runbook committed. NO remote provisioning (conductor's deploy phase). |
| B6 Evidence + claims | 6.1–6.2 | PASS | claims.json + NOTES.md (6 blocks). Screenshots deferred to design phase. |

## Deviations from Architecture

Each deviation is a DEV-NNN record. Debug phase 2 and wire phase 1 grep for `DEV-` entries.

| ID | Component | ARCHITECTURE Said | ACTUAL | Reason | Class | Downstream Impact |
|----|-----------|-------------------|--------|--------|-------|-------------------|
| DEV-001 | app/github.py (II.4) | `httpx.AsyncClient(...)` without follow_redirects; `raise_for_status()` on the meta GET | Added `follow_redirects=True` to the client | 6 of 50 seed repos (incl. `facebook/react`, `zeit/next.js`, `twitter/bootstrap`) return GitHub `301 Moved Permanently` to their renamed canonical path; `raise_for_status()` was rejecting them and dropping the rows | DEGRADED→fixed (COSMETIC net: behavior now correct) | Positive: seed set recovered from 42→48 rows, all 5 classes balanced. No shape change. |
| DEV-002 | app/classifier.py (II.6) TabPFN happy path | `classify()` fits TabPFN and returns `engine="tabpfn"` on the happy path | TabPFN hosted endpoint returns HTTP 503 "Service is disabled" on every `fit`; `classify()` falls through its `except` to the labeled `engine="rules"` 1-NN+threshold path | Prior Labs server-side outage (token authenticated OK via `set_access_token`; not a credential/code fault). INVARIANTS ESCALATE + V.B0 fallback invoked (ADR-007) | **UNTESTED** | The `engine="tabpfn"` path and the real TabPFN LOO separability number were never exercised this build. Re-verify at deploy/livetest when the service returns. The `engine="rules"` path is fully proven and surfaced honestly on the card. |
| DEV-003 | app/narrator.py (II.7) `_client()` | base_url defaults to Groq, `api_key=GROQ_API_KEY` | base_url defaults to Ollama (`http://localhost:11434/v1`), `api_key` reads `LLM_API_KEY` first; `LLM_MODEL` defaults to `gemma2:2b` | FINAL STACK / ADR-005b + ARCH PART III.1 ("II.7 client block updated"): narration = Gemma via Ollama, keyless. Raw II.7 Groq defaults are superseded | DEGRADED (env-driven; correct per PART III) | Narration target is Gemma/Ollama. No local Ollama on this build machine → see DEV-004. |
| DEV-004 | Narration live path (Gemma/Ollama) | Gemma via Ollama narrates every eulogy | No Ollama daemon on the build host; the narrator's `try` raises on connect and returns the labeled templated eulogy (`_template`) | Ollama is co-located on the Oracle deploy VM, not the local build machine (per dispatch instruction: wire to Ollama, verify loop via fallback, defer Gemma verification to deploy) | **UNTESTED** | Gemma-via-Ollama narration must be verified at the Oracle deploy phase where Ollama runs. The grounding+fallback machinery IS proven (grounding test green; templated fallback renders end-to-end). |

## Failed Attempts & Resolutions
| Step | Error | Attempts | Resolution |
|------|-------|----------|------------|
| B0 LOO | TabPFN `fit` → HTTP 503 "Service is disabled" | 3 retries + direct endpoint probe + separate auth probe | Confirmed server-side outage (auth OK, service down). Recorded honestly; invoked rules-primary fallback (ADR-007). Not retried further — third-party outage, not fixable in build. |
| B0 seed build | 8 repos dropped (6× 301 redirect, 2× 404) on first run | 1 | Fixed the 6 redirects via DEV-001; the 2 genuine 404s (`facebookarchive/fixit`, `substack/node-mkdirp`) stay dropped per V.B0 decision tree ("one bad seed never blocks B0"). |

## Verification Results
| Phase | Command | Expected | Actual | Pass? |
|-------|---------|----------|--------|-------|
| TabPFN token | `set_access_token(TABPFN_TOKEN)` | token accepted | AUTH OK (user endpoint reachable, token valid, len 53) | YES |
| TabPFN service | `TabPFNClassifier().fit(X,y)` | 200 + proba | HTTP 503 "Service is disabled" ×3 | NO (outage) |
| B0 | `python scripts/build_seed.py` | CSV, 5 classes, LOO≥60% | CSV 48 rows, 5 classes 10/10/10/9/9; LOO unmeasurable (503); 1-NN proxy 31% | PARTIAL (see ADR-007) |

## Known Risks (for debug)
- **TabPFN happy path unproven (DEV-002):** the entire `engine="tabpfn"` branch and the real separability number depend on the Prior Labs service recovering. Debug/livetest must re-run V.B2 when it is back.
- **Gemma-via-Ollama unproven locally (DEV-004):** narration quality/register on real Gemma output is unverified until the Oracle deploy phase. The templated fallback is what renders locally.
- **abandoned↔completed separability:** the hardest pair (9 proxy confusions); the discriminating `is_archived` boolean is deliberately absent from the feature row (documented limitation). TabPFN may separate it better than 1-NN, but that is unverified (outage).
- **GitHub unauthenticated rate limit (60/hr):** build used Dami's `gh` CLI token (5000/hr) for the 50-repo fetch; production relies on an optional `GITHUB_TOKEN`. Without one, heavy judging traffic could rate-limit (friendly 422 handled).

## Contract Addresses
| Contract | Network | Address | Tx Hash |
|----------|---------|---------|---------|
| (none — no smart contracts in this project) | — | — | — |

## Environment Variables Added
| Key | Source Step | Value/Description |
|-----|-----------|-------------------|
| EX_ABANDONED / EX_BURNED / EX_ALIVE | B6 | Safe real example repos for the prewarm/example buttons (set at B6) |
