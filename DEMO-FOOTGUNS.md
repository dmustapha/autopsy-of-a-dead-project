# DEMO-FOOTGUNS — Autopsy of a Dead Project
Generated: 2026-11-01 | Live URL: https://autopsy.132-145-100-81.sslip.io

All footguns below are VERIFIED against the live deploy + state files (not re-discovered from scratch).
coldStranger gate = **PASS** (99s < 120s budget) — the non-acknowledgeable cold-hero override does NOT fire.
No sentinel hits, no auth gaps, no privacy mirrors (`.wire-state.json`: all empty/null).

## Footgun Table

| id | source | description | severity | workaround | fixable |
|----|--------|-------------|----------|-----------|---------|
| FG-001 | `.livetest-state.json → latency.fresh_cold_leftpad_seconds=99.2`; `app/cache.py:8 ttl=3600` | COLD latency on any non-cached repo is **>90s** (two live 0G Compute calls + cold TabPFN load). CACHED examples are **<1s**. | HIGH | Film ONLY the 3 pre-cached examples (bower, caprine, fastapi). Never type a fresh repo. | ACCEPT-ONLY (inherent to 0G reasoning latency; cached path is the designed demo path) |
| FG-002 | `app/cache.py:8` TTL=3600s in-memory; `main.py:157 _prewarm` fire-and-forget on startup | The example cache **expires 1h after last access** and is **cleared on any service restart**. At rehearsal (Nov 1) the cache was already COLD — examples took >30s, confirming expiry. | HIGH | **WARM all 3 examples SERIALLY (one POST at a time, each finishing before the next) within the hour BEFORE recording,** then confirm each returns <2s. **Do NOT restart the service** near demo (~3min cold saturation on the 681MB box). | ACCEPT-ONLY (by-design 1h TTL; serial pre-warm is the mitigation) |
| FG-002b | rehearsal live finding: single-worker 681MB box | **Concurrent cold requests saturate the box.** A parallel 3-example warm batch hung ALL THREE past 200s at rehearsal; serialized, each completes (bower confirmed 200 + valid card once isolated). | HIGH | Warm examples **one at a time**, never in parallel. Never issue a cold POST while another is in flight. | ACCEPT-ONLY (micro box; serial discipline is the mitigation) |
| FG-003 | `app/static/app.js:210` | Narration badge falls back to the literal string **"Gemma"** if `narration_engine` is null on a card. | LOW | Cached example cards render **"deepseek-v4.1-flash · 0G Compute"** correctly (verified live in livetest VF-L3). Only edge/old-shape cards show "Gemma" — avoided by showing only cached examples. | YES (null-safe default could be corrected post-demo; not demo-blocking) |
| FG-004 | `app/templates/index.html:42-45` (repo input + "Perform the autopsy" CTA) | The prominent input box invites typing a live repo on camera, which triggers the 99s cold path (FG-001). | HIGH | On camera, **only click the example chips** under the input. Do not type or focus the input field during recording. | ACCEPT-ONLY (input is a real product surface; discipline is the mitigation) |

## Severity summary
- CRITICAL: 0
- HIGH: 4 (FG-001, FG-002, FG-002b, FG-004 — all the SAME root: cold-latency / cache / single-worker box; all mitigated by the cached-examples-only + SERIAL pre-warm discipline)
- LOW: 1 (FG-003)

## Acknowledgement state
No CRITICAL footguns → no hard block. The three HIGH footguns are the **known, PRD-documented demo footguns** (PRD §"Honest latency", livetest P1 #1). They require the operator to follow the pre-warm + cached-only staging discipline in DEMO-SCRIPT.md. `footguns_acknowledged` is set honestly per the exit gate (no CRITICAL, so acknowledgement is not a blocker — but the staging discipline is MANDATORY and is encoded in the Pre-Recording checklist).
