# DEMO-SCRIPT — Autopsy of a Dead Project
Generated: 2026-11-01 | Duration target: 90s | Live URL: https://autopsy.132-145-100-81.sslip.io

Audio strategy: **separate** (silent screen capture; VO/TTS added in post). pacing_mode: **gap**.
Recording resolution: **1920x1080** (OffthreadVideo requirement).

## Pre-Recording Setup (MANDATORY — footgun mitigations)

- [ ] **WARM THE CACHE FIRST — SERIALIZED, one repo at a time.** Run these POSTs so each FINISHES before the next starts (~90-100s+ cold each the first time). **Do NOT fire them in parallel** — the box is a single-worker 681MB micro and concurrent cold requests saturate it (a parallel batch at rehearsal hung all three past 200s; serialized, each completes). This is the #1 footgun — the 1h cache was COLD at rehearsal:
  ```bash
  # SERIAL: the `;` and per-request --max-time 280 ensure one finishes before the next starts
  for r in bower/bower sindresorhus/caprine fastapi/fastapi; do
    echo "warming $r (cold ~90-200s, be patient)...";
    curl -s -o /dev/null -w "$r %{http_code} %{time_total}s\n" --max-time 280 \
      -X POST https://autopsy.132-145-100-81.sslip.io/autopsy \
      -H "Content-Type: application/json" -d "{\"repo_url\":\"$r\"}"; done
  ```
  Then CONFIRM warm (must be <2s each): re-run the same loop — all three should now return in <2s. Only start recording once all three confirm <2s.
- [ ] Record within **1 hour** of warming (TTL=3600s). If you overrun, re-warm.
- [ ] **Do NOT restart the autopsy service** (clears cache → ~3min cold saturation on the 681MB box).
- [ ] Do NOT touch the co-resident LEASH service (api.leash.ink).
- [ ] Browser zoom 100-125%; notifications disabled; DevTools closed (no console errors — livetest confirmed zero).
- [ ] Open the example chips are visible under the input (GET /examples returns bower/caprine/fastapi).
- [ ] **Never type in the repo input on camera** — only CLICK the example chips (typing a fresh repo = 99s cold path on screen).
- [ ] Exact example slugs (must match the chips): `bower/bower` (abandoned), `sindresorhus/caprine` (burned_out + last words), `fastapi/fastapi` (alive). NOTE: it is `fastapi/fastapi`, NOT `tiangolo/fastapi`.

## Filming Sequence (single 1920x1080 screen capture, ~90s)

### Step 1: [Screen: Landing / hero] — 0:00-0:12
Action: Open https://autopsy.132-145-100-81.sslip.io. Let the hero heartbeat canvas animate for a beat.
Show: Headline "Every repository that stops is a ghost in the machine." + lede "A tabular foundation model performs the autopsy; an open-weight coroner reads the report."
Say:
[SUB] Every repository that stops is a ghost in the machine.
[SUB] This is a forensic coroner for dead software.
[SUB] Paste a GitHub repo — it determines how the project died.
**DO NOT SHOW:** the repo input being typed into (cause: latency — would trigger the 99s cold path).

### Step 2: [Screen: bower death certificate] — 0:12-0:38
Action: CLICK the "bower" example chip (do not type). Card returns in <1s (pre-warmed).
Show: The death certificate — cause of death **ABANDONED**, the differential diagnosis (full TabPFN posterior, several causes with probabilities), the "evidence read by deepseek-v4.1-flash · 0G Compute" badge, "classified by TabPFN" badge, and the cohort line ("died like N of M similar repos").
Say:
[SUB] bower. Cause of death: abandoned.
[SUB] The verdict is TabPFN — an open tabular foundation model, classifying in one forward pass.
[SUB] It shows the full differential: every death mode it considered, with probabilities.
[SUB] The evidence was read by deepseek-v4.1-flash on 0G Compute — decentralized, open-weight.
**DO NOT SHOW:** any fresh-repo result (cause: latency / Gemma-label fallback).

### Step 3: [Screen: caprine death certificate — the last words] — 0:38-0:62
Action: CLICK the "caprine" example chip. Card returns <1s.
Show: Cause of death **BURNED_OUT**, "What this project was" (project_summary), and the **recovered last words** quote block: "Caprine is feature complete."
Say:
[SUB] caprine. Cause of death: burned out.
[SUB] It recovers the project's real last words from the repo itself —
[SUB] "Caprine is feature complete." Not an invented epitaph. A verbatim quote.
[SUB] The tool memorializes the dead by name — it never fabricates a death it can't defend.
**DO NOT SHOW:** nothing to hide here — this is the emotional wow moment.

### Step 4: [Screen: fastapi — certificate of LIFE] — 0:62-0:82
Action: CLICK the "fastapi" example chip. Card returns <1s.
Show: A certificate of **LIFE** (alive, ~0.58 posterior) — proving the tool doesn't just declare everything dead; living repos get a life certificate.
Say:
[SUB] fastapi. This one is alive — a certificate of life.
[SUB] The classifier isn't a death stamp; it reads the signal honestly either way.
[SUB] A tool that knows the edge of what it knows.

### Step 5: [Screen: back to a death cert / honesty badges hold] — 0:82-0:90
Action: Scroll to hold on the honesty badges + differential of one death cert (bower or caprine).
Show: Badges "classified by TabPFN" + "evidence read by deepseek-v4.1-flash · 0G Compute".
Say:
[SUB] Held-out proof: TabPFN beats a nearest-neighbour baseline by 14.5 points.
[SUB] Open weights end to end. It issues a verdict — and shows its uncertainty.

## Do NOT Show During Recording

| Footgun | Severity | Cause | Why | Workaround |
|---------|----------|-------|-----|-----------|
| Typing a fresh repo into the input | HIGH | latency | 99s cold path appears on camera as dead air | Only CLICK example chips |
| Any non-cached repo result | HIGH | latency | same 99s cold path | Cached examples only |
| A card showing "Gemma" in the narration badge | LOW | untested-feature | stale null-fallback label (app.js:210); never appears on cached cards | Show only cached examples |
| Service restart / cache-clear | HIGH | latency | ~3min cold saturation afterward | Never restart near demo; warm then record in the hour |

(No `cold-hero-unavailable` entry — forbidden per skill; coldStranger gate is PASS upstream in livetest.)

## Async Operation Timings

| Operation | Expected Wait (ON CAMERA) | What to Say During Wait |
|-----------|---------------------------|-------------------------|
| Click a pre-warmed example chip | <1s (0.72-0.77s measured) | nothing — it is instant; no dead air |
| (OFF CAMERA, pre-record only) warming a cold example | ~90-100s each | N/A — never on camera |

⚠ Sequence budget: steps sum to ~90s. If VO runs long, trim Step 5 narration to one [SUB] line.
