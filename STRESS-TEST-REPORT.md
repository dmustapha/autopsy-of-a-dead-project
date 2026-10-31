# STRESS-TEST-REPORT — Autopsy of a Dead Project

## Summary
**Confidence: 95/100 — Battle-tested.** 50/50 tests green (47 baseline + 3 new falsification).
1 P0 bug found and fixed. The core forensic loop's honesty (engine labeling + number grounding)
is PROVEN load-bearing by no-op ablation, not asserted.

## Coverage Declaration
- **P0 (`/autopsy`): exhaustive** — 8 edge classes + concurrency, all pass with themed friendly
  errors and NO uncaught 500 (after the fix below).
- **P1: sampled** — GitHub 404 / rate-limit / network-failure paths, `/examples`, `/healthz`, cache.
- **P2: smoke** — static card + logo serving; both card states render (design qa).

## Phase Results
- **Phase 4 — Backend API (P0):** the `/autopsy` judge-paste battery. All inputs return the correct
  themed 4xx; one input (`../../etc/passwd`) previously returned a **500** — now a friendly 422.
  Giant repo (`torvalds/linux`) → 200. 5× concurrent → all 200, no race.
- **Phase 8.5 — Self-falsification + ablation (the thesis guard):**
  - `test_claim_engine_badge_is_honest_on_fallback` — a rules fallback must stamp `engine=rules*`, never `tabpfn`.
  - `test_claim_grounding_rejects_fabricated_number` — a eulogy citing `99999` (not in evidence) is rejected.
  - **Ablation:** no-op `_grounded` → the fabrication test goes RED; no-op the engine-label → the honesty
    test goes RED. Both reverted (`git checkout`); suite GREEN after. Evidence:
    `tests/ablation/grounding_noop.log`, `tests/ablation/classifier_label_noop.log`.
- **Phases 2/2.5/3/5/5.5:** folded/skipped with recorded reasons (single synchronous endpoint, no
  contracts, no agent loop; visual covered by design qa).

## Fixes Applied
| ID | File | Fix | Verified |
|---|---|---|---|
| ST-P0-SEC-01 | `app/validators.py` | `_SLUG` allowed `.`, so `..`/dot-only owner-repo (e.g. `../../etc/passwd`) passed validation and hit an uncaught 500 on the GitHub fetch. Added `_HAS_ALNUM` + dot-only reject → friendly 422. | ✅ live (422) + unit |

## Unresolved Issues
None.

## Honest Gaps
- **Gemma live-narration consistency** is OUT_OF_SLICE here — it's a deploy/livetest item (DEV-004);
  stress exercises the labeled-fallback path (correct behavior), not live-Gemma determinism.
- **Load/soak testing** not run (not a prize axis for a dev.to post; the 5× concurrency smoke passed).
