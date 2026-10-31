# Livetest V3 Report — Autopsy of a Dead Project

**4 PASS / 0 FAIL / 2 SKIP (adversarial N/A fields) — no P0 blockers**
**Mode:** Web | **URL:** https://autopsy.132-145-100-81.sslip.io | **Tested:** 2026-10-31T20:42:49Z
**Overall: PASS** (2 P1 warnings for demo/publish)

## Baseline
- `GET /` → 200 (1.6s). `GET /healthz` → `{"ok":true,"seed_rows":47,"tabpfn_reachable":true}`. `GET /examples` → 3 examples.

## V1 functional / V2 exact-value — Engine is genuinely TabPFN LIVE

| Repo | engine | mode | top prob | probs sum | latency |
|------|--------|------|----------|-----------|---------|
| bower/bower | **tabpfn** | abandoned | 0.4908 (claim ~0.49 ✓) | 1.0 | 0.72s |
| sindresorhus/caprine | **tabpfn** | burned_out | 0.4020 (claim ~0.40 ✓) | 1.0 | 0.77s |
| fastapi/fastapi | **tabpfn** | alive | 0.5785 (claim ~0.58 ✓) | 1.0 | 0.73s |
| stevemao/left-pad (FRESH) | **tabpfn** | completed | 0.299 | 1.0 | 99.2s |

Posteriors are a real 5-class distribution, sum to 1.0, and **differ per repo** — proves a live model, not a constant/rules. bower full posterior: abandoned 0.4908, burned_out 0.2349, completed 0.2064, pivoted 0.0541, alive 0.0138.

## Numbers recompute — TabPFN LOO
- **Claim: 17/47 = 36.2%.** Recomputed live with the **local tabpfn** (same engine prod uses), leave-one-out over `data/seed_repos.csv` (47 rows, balanced 10/10/9/9/9): **17/47 = 36.2% — EXACT MATCH.**
- Chance (5-class majority) = 10/47 = 21.3%; TabPFN beats chance.
- ⚠️ 1-NN baseline recomputed here (raw standardized Euclidean LOO) = **20/47 = 42.6%**, not the 31% the POST cites. The 1-NN comparison method differs — the load-bearing TabPFN number is exact, but the "beats 1-NN 31%" line should be re-derived or rephrased before publishing.

## Real 0G eulogy + latency
Narration engine badge (API `narration_engine`, honest, env-derived): **"deepseek-v4.1-flash · 0G Compute"**. Card renders it as `narrated by deepseek-v4.1-flash · 0G Compute (open weights)` (app.js:210, not hardcoded). Classifier badge `classified by TabPFN` (app.js:21).

Quoted bower eulogy (grounded — quotes real features: bus_factor=1, velocity→0, not archived):
> Bower was born and lived long, gathering stars at its windows while a crowd of contributors passed through its rooms. Releases went out like letters from a busy post office, and open issues remained at the table like unlit candles. Yet the bus factor was one: a single keeper carried the whole house on weary shoulders. The cadence of change decayed; velocity fell to nothing. Then came the silence—a last seen, a long idleness, and the verdict of abandonment, spoken with modest confidence...

**Latency:** cached 0.72–0.77s (instant ✓); fresh cold (left-pad) **99.2s** — higher than the deploy's 20–40s estimate; 0G reasoning dominates.

## V3 adversarial / honesty gate
| Input | Result |
|-------|--------|
| empty repo_url | 422 string_too_short |
| malformed JSON | 422 json_invalid |
| missing field | 422 missing |
| `../../etc/passwd` | 422 "invalid owner/repo" (traversal blocked) |
| non-github host | 422 "not a github.com URL" |
| gist | 422 "invalid owner/repo" |
| 600-char owner | 422 string_too_long (max 200) |
| nonexistent repo | 422 "Couldn't exhume this grave - is the repository public?" |

All bad input → **422, friendly message, zero 500s, zero stack traces.** No secret/key material in `GET /` HTML or any response. Zero console errors; no undefined/NaN/[object Object] in DOM.

## Cold-stranger hero gate — PASS
Fresh Playwright context (no storageState, no creds): cold judge clicks an example / pastes a repo → receives TabPFN verdict + 0G eulogy on the deployed URL. Fresh repo mutation (left-pad) executed live, engine=tabpfn, 99s (budget 120s). Free pre-money proof surface = POST /autopsy, zero setup, runs the real engine.

## P1 warnings (for demo + package)
1. **Fresh cold latency ~99s** — demo must use the 3 cached examples (instant); never type a fresh repo live; never restart the service near demo.
2. **1-NN 31% claim** doesn't reproduce (got 42.6%) — rephrase/recompute before publishing the comparison line.
