# Design Progress: Autopsy of a Dead Project (dev-ghost)

Started: 2026-10-31 (conductor design phase — ADOPT + VERIFY of frozen design)
Style Config: ai/style.config.md (mapped from DESIGN_BRIEF.md, derived from owner-approved frozen design)
Mode: qa (adopt + verify — NOT generate; card is FROZEN per FULL-DEPTH-RESUME delta #2)

## Provenance
The good-era design cycle completed OUT-OF-CONDUCTOR (dedicated design chat) and was ported into
`app/templates/index.html`, `app/static/card.css`, `app/static/app.js`. It passed the R1→R4 ladder
with two independent fresh-critic "only nits" verdicts and the owner (Dami) eye — see
`DESIGN-HANDOFF.md` + `/Users/MAC/pipeline-audit/skill-audit/win-audit/REFERENCE-TEARDOWN/RUN-dev-ghost/`
(CALIBRATION.md, SELECTION.md, AUDIENCE-CONTRACT.md, SCORECARD.md). This conductor phase ADOPTS it.
agent_nonce: 903d8fe7abe90ecee4a8325e

## Phase 0: Pre-flight
color_mode: dark-only — dark forensic/memorial IS the product identity (coroner's bench)
states_reachable: 3/3 surfaced — death (abandoned/burned_out), life (alive), + error states;
  routes /, /examples, /autopsy, /healthz all reachable from the single card UI.

## Phase 2: Creative (3 Proposals)
Status: SKIPPED — design FROZEN, no regeneration (delta #2). Direction already selected + built
  (SELECTION.md in the REFERENCE-TEARDOWN record).

## Phase 3: Selection
Status: completed (out-of-band) — amber-forensic certificate direction, owner-approved.
Selected: the dark-forensic death-certificate card (amber #D4A017 accent, Spectral/IBM Plex Mono).

## Phase 4: Production Polish
Status: completed (out-of-band) — ported + ladder-passed; audit_result: pass (two fresh-critic "only nits").

## Phase 5: Final QA
Status: completed
QA Result: APPROVED (see .design-qa-verdict.json) — live Playwright verify on :3300, both states,
  contrast paper 15.69:1 / amber 8.28:1, mobile-375 overflow-free, engine+narration badges honest.
inputs_opened:
  - docs/context/ADAPTATION-PLAYBOOK.md §design (full-depth re-point applied)

## Hand-off to design_forge
Design is ADOPTED + QA-APPROVED. design_forge FORMALIZES this frozen card only (DESIGN_SYSTEM.md +
brand.json + real fal logo + favicon) — NO new proposals, NO ui-revamp. DP-3 self-heal must NOT fire
(this file + .design-state.json + .design-qa-verdict.json are the proof the design phase ran).
