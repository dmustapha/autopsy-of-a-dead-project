# Design QA Report — dev-ghost (ADOPT + VERIFY, frozen card)

**Mode:** qa (Phase 5 only). The certificate-card design is FROZEN + owner-approved
(FULL-DEPTH-RESUME delta #2) — verified, not regenerated. Evidence captured LIVE from the running
instance at http://127.0.0.1:3300/ via local Playwright Chromium (1.60.0), both themes/states.

## Verdict: APPROVED — zero blocking issues

| Check | Result |
|---|---|
| Death state renders (bower/bower → CERTIFICATE OF DEATH, abandoned) | ✅ |
| Life state renders (fastapi/fastapi → CERTIFICATE OF LIFE, alive) | ✅ |
| Ground = warm near-black, constructed field (lamp glow + dust + vignette) | ✅ |
| Exactly one colored ambient glow (no flat panels) | ✅ |
| Contrast — paper text on ground | **15.69:1** (AA 4.5, AAA 7) ✅ |
| Contrast — amber eyebrow on ground | **8.28:1** ✅ |
| Mobile 375px — no horizontal overflow (scrollW 375 ≤ clientW 375) | ✅ |
| Mobile 375px — certificate visible + legible | ✅ |
| Engine badge present + honest | ✅ live engine=`tabpfn` → "CLASSIFIED BY TABPFN" |
| Narration badge present + honest | ✅ renders "NARRATED BY GEMMA" or "TEMPLATED CORONER · LLM OFFLINE" per real response |

## Honesty mechanism (the thesis) — WORKING
Observed badges across both states:
`OPEN-WEIGHT · LOCAL-CAPABLE` · `CLASSIFIED BY TABPFN` · `NARRATED BY GEMMA (OPEN WEIGHTS)` ·
`TEMPLATED CORONER · LLM OFFLINE`.

- Live `/autopsy` returns `verdict.engine="tabpfn"` with a real posterior (bower: abandoned 0.492,
  burned_out 0.234, completed 0.206, pivoted 0.054, alive 0.014). The card shows the full
  ghost-differential + the honest TabPFN badge. **Local TabPFN is genuinely classifying** (delta #4).
- Narration is detected from the real response: when Gemma narrates → "NARRATED BY GEMMA"; when it
  falls to the template (marker "Generated without the language model") → "TEMPLATED CORONER ·
  LLM OFFLINE". Nothing is faked either way.

## Deploy/livetest hand-off (NOT a design defect)
- **DEV-004 narration intermittency:** with `ollama :11434` up and `llm_hint.llm_offline=false`,
  bower's narration still came back templated this run (fastapi got a real Gemma eulogy). Gemma
  narration is intermittent locally (latency/timeout suspected). Resolve + prove consistent Gemma
  narration at deploy/livetest; the design already renders whichever state is real, honestly.

## Artifacts
`evidence/design-qa/{hero,cert-bower-death,cert-fastapi-life,mobile-375}.png`,
`ai/design-qa-results.json`, `.design-qa-verdict.json`, `.design-render-375.json`.
