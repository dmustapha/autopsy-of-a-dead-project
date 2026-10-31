# STRESS-TEST-PLAN — Autopsy of a Dead Project

Re-pointed per ADAPTATION-PLAYBOOK §stress_test: contract-stress + AI-agent batteries N/A (no
contracts, no agent loop); that budget re-aimed at the `/autopsy` judge-paste surface + the
self-falsification/ablation honesty battery (the essay's credibility).

## Coverage Tiers
| Tier | Features | Rule | Achieved |
|---|---|---|---|
| **P0 — exhaustive** | `/autopsy` endpoint (the judge-paste surface) | every edge class | 8 edge classes × 1 endpoint, all exercised |
| **P1 — sampled** | `/examples`, `/healthz`, caching, GitHub error kinds | ≥3 riskiest classes | covered (404/ratelimit/network-fail) |
| **P2 — smoke** | static page render, logo serving | happy path | card renders both states (design qa) |

## Test Matrix — `/autopsy` (P0, exhaustive)
| Class | Input | Expected |
|---|---|---|
| empty | `repo_url=""` | 422 min-length |
| malformed | `not-a-repo` | 422 "doesn't look like a GitHub grave" |
| nonexistent | `ghost/does-not-exist-…` | 422 "Couldn't exhume this grave" |
| **path traversal** | `../../etc/passwd` | 422 (was 500 — FIXED ST-P0-SEC-01) |
| oversized | 5000-char slug | 422 max-length |
| missing field | `{}` | 422 field required |
| XSS | `<script>…` | 422 invalid owner/repo |
| giant repo | `torvalds/linux` | 200 (handles large) |
| concurrency | 5× simultaneous | all 200, no race |

## Honesty battery (Phase 8.5 — full depth)
- **Self-falsification** (feed a lie → assert red): engine badge honest on fallback; grounding rejects a fabricated 99999.
- **No-op ablation** (prove load-bearing): no-op `_grounded` → fabrication test goes red; no-op engine-label → honesty test goes red. Both reverted; suite green after.

## Skipped (declared)
- Phase 2.5 end-to-end async: SKIPPED — autopsy is a single synchronous ~10s request, no job/stream/queue.
- Phase 5 contract: SKIPPED — no smart contracts.
- Phase 5.5 AI-agent: SKIPPED — no agent loop (single classify + single narration call, no tool-calling).
- Frontend visual journeys folded into design qa (single card page, both states, 5 viewports via render-375 + desktop).
