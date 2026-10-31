# SCORECARD — dev-ghost "Autopsy of a Dead Project" · good-era design cycle · 2026-10-30

Register: dark forensic / memorial (axon's lane). Signature: **the flatline** ("the last heartbeat").
Hero artifact: the death certificate card (the dev.to post's screenshot). Bars: chit + leash + axon + whopays.

## THE LADDER (the engine — real iteration, fresh critic each round, scored beside the bars)

| Round | Felt-density | Fresh critic (lens) | Verdict | Key defects named |
|-------|-------------|---------------------|---------|-------------------|
| R1 | 6.3 | code-reviewer | ELEVATE (substantive) | signature **wallpapered/split**: flatline mechanism good BUT 6 progress bars = chart clip-art doing the same verb; field thinner than leash; cert strip static; numeral tie |
| R2 | 6.6 | general-purpose | ELEVATE (substantive) | flatline appears **4× on the card** (strip + ghost-traces + watermark) = motif-monotony (amp reject); cause/certainty **hierarchy tie**; under-charged lamp; templated evidence table; **mode-color truth broken** (3 modes share amber; pivoted blue-text/green-trace) |
| R3 | 8.4 | ui-frontend-craftsman | **ONLY NITS** (holds beside bars) | de-wallpapered (one flatline + guilloche watermark + typographic differential); hierarchy fixed; field sculpted; color-truth per mode; evidence driver-ticks. Nit: completed/alive share green |
| R4 | 8.4 | architect (confirming) | **CONFIRMED: only nits, holds beside the bars** | 4 nits, all cosmetic; no substantive defect; not FLAT/CROWDED/AIRY/MOTIF-MONOTONY/STATIC/BORING |

**Ladder stop condition MET:** two consecutive independent fresh critics (R3 ui-craftsman, R4 architect)
found ONLY NITS **and** both judged it holds its own beside chit + leash. No self-certification; each
round surfaced NEW defects anchored on OWNER-VERDICTS; fixes went FAIL→fix→re-score with a fresh lens.

## WHAT EACH ROUND CHANGED (FAIL→fix)
- **R1→R2:** killed the 6 progress bars → fused the posterior into **ghost-traces**; cert strip now
  performs (flatten-on-reveal + seal stamp); field thickened (dust motes + extended grid + underglow);
  lower-hero grounded with a forensic signal band; cause 40→54px hero, certainty demoted.
- **R2→R3:** de-wallpapered — ONE flatline performance (strip); **guilloche rosette** watermark (not the
  motif); differential reborn as a typographic **differential-diagnosis list** (dotted leaders, no chart);
  evidence table given forensic teeth (uppercase mono + amber **driver-row** emphasis showing *why*);
  **color-truth** per mode (cause word + trace agree): abandoned clay-red, burned_out ember, pivoted blue,
  completed sage, alive green; sculpted lamp (hot core + halo).
- **R3→R4 (nit):** split `completed` off `alive`'s green (sage #6f9f7a) so all 5 modes read distinct at
  thumbnail scale; lamp breathe deepened; guilloche alpha lowered + repositioned.

## VERIFICATION (real Chrome, cache-busted — the coldspot lesson)
- **Motion proven live** (getAnimations + canvas-pixel probe, cache-busted): dust rAF moving; cert strip
  flatten animates (635 pixel-cells over ~950ms); seal `stamp` keyframe fires; cause-word reveal (2
  CSSTransitions); lamp breathes. `bodyBg = rgb(12,11,9)` warm near-black; abandoned cause = clay-red.
- **Real app verified** (own instance :3300, live `/autopsy`): renders the HONEST current backend state
  (engine=rules, templated narration) with dignity — the "single determination" note replaces a fabricated
  posterior; both honesty badges (`FORENSIC-RULES ESTIMATE · MODEL OFFLINE` + `TEMPLATED CORONER · LLM
  OFFLINE`) shown first-class. Alive repo (fastapi) flips to `CERTIFICATE OF LIFE` + green + "still beating".
- **Responsive** held at 390px (certificate stacks as a legible document).

## HONEST GAPS / NOTES
- The real deployed backend currently returns **rules + templated narration** (TabPFN hosted 503 despite
  token set; Ollama not running locally). The design is built to show BOTH engine states with equal dignity;
  the `tabpfn` + `gemma` visual (full ghost-differential + "classified by TabPFN"/"narrated by Gemma") is
  proven in the proto captures and activates automatically when those services return — nothing fabricated.
- Two fonts (Spectral + IBM Plex Mono) do three jobs; chit uses three distinct faces. Deliberate (document
  authenticity); a nit, not a defect.

## ARTIFACTS
- Locked design: `RUN-dev-ghost/proto/index.html` (self-contained, all states switchable).
- Ported to the REAL app: `dev-ghost/app/templates/index.html`, `app/static/card.css`, `app/static/app.js`.
- Captures: `caps/` (proto states + bars side-by-side) and `caps/real/` (live-app deliverable screenshots).
- Terminal gate: **owner eye** (pending Dami).
