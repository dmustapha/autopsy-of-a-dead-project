# STRESS-RESULTS.md

status: complete

## What Just Happened
We exhaustively attacked the one surface a judge actually touches — the `/autopsy` endpoint — by
pasting empty, malformed, nonexistent, path-traversal, oversized, XSS, and missing-field inputs, plus
a giant repo and five concurrent requests. Every input now returns its themed friendly 4xx with no
uncaught 500; we found and fixed one real P0 security/robustness bug where `../../etc/passwd` slipped
past the slug validator (which allowed `.`) and crashed the GitHub fetch into a 500 — it is now a
dignified 422. More importantly, we made the project's headline honesty claims *falsifiable*: two new
self-falsification tests feed the system a lie (a fallback pretending TabPFN ran; a eulogy citing a
fabricated 99999) and assert it refuses them, and a no-op ablation proves those guards are
load-bearing — no-op the grounding check and the fabrication test goes red; no-op the engine label
and the honesty test goes red. This matters because the dev.to post leans its whole credibility on
"nothing is faked, every verdict carries an honest engine badge" — stress makes that a *proven*
claim, not a hope, which is exactly what the writing and the TabPFN category writeup will cite. Deploy
and the demo now ride on a core that can't silently go hollow.

## Honest Gaps
- **Gemma live-narration consistency is unverified here** — it is OUT_OF_SLICE for stress (a
  deploy/livetest concern, DEV-004). Stress only exercised the labeled template-fallback path, which
  is correct behavior; proving a *real* Gemma eulogy renders consistently is deploy/livetest's job.
- **No load/soak test** — only a 5×-concurrent smoke was run (all 200). A dev.to post isn't judged on
  throughput, so sustained-load behavior under hundreds of concurrent autopsies is unmeasured.
- **Frontend visual journeys were folded into design qa** rather than re-run here — justified because
  the UI is a single card page already verified in real Chromium (both states, contrast, 375px), but
  it means stress did not independently re-screenshot the 5-viewport matrix.
