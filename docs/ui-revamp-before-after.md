# UI-Revamp Before/After — dev-ghost death-certificate card

> This records the full production-polish (ui-revamp-equivalent) that elevated the card to ship
> quality. It was run as the **R1→R4 craft ladder** in the good-era design cycle (a FAIL→fix→re-score
> loop with a FRESH independent critic each round, scored beside the vouched bars chit/leash/axon/whopays)
> — a stronger discipline than a single 4-phase pass. Source: `SCORECARD.md` (in-repo) +
> `/Users/MAC/pipeline-audit/skill-audit/win-audit/REFERENCE-TEARDOWN/RUN-dev-ghost/`.

## The 4-phase arc (audit → plan → implement → validate), mapped to the ladder

| Phase | Round | Felt-density | Critic (lens) | Verdict |
|---|---|---|---|---|
| Audit (baseline) | R1 | 6.3 | code-reviewer | ELEVATE (substantive) |
| Plan + implement | R2 | 6.6 | general-purpose | ELEVATE (substantive) |
| Implement (converge) | R3 | 8.4 | ui-frontend-craftsman | **ONLY NITS** (holds beside bars) |
| Validate (confirm) | R4 | 8.4 | architect | **CONFIRMED: only nits** |

## BEFORE → AFTER (what each round changed, FAIL→fix)

- **R1 → R2 — signature de-cluttered.** BEFORE: the posterior shown as **6 progress bars** = chart
  clip-art doing the same verb as the flatline (wallpapered/split signature); field thinner than
  leash; static cert strip; cause/numeral hierarchy tie. AFTER: killed the 6 bars → fused the
  posterior into **ghost-traces** behind the flatline; cert strip gained a time-of-death tick row.
- **R2 → R3 — motif-monotony + color-truth fixed.** BEFORE: the flatline appeared **4× on one card**
  (strip + ghost-traces + watermark) = motif-monotony; 3 death-modes shared amber (mode-color truth
  broken); under-charged lamp; templated evidence table. AFTER: **de-wallpapered** to ONE flatline +
  a guilloche watermark + a typographic differential; per-mode color truth (abandoned #c9623f,
  burned_out #d98324, pivoted #6fa8c9, completed #6f9f7a, alive #8FB339); lamp charged; evidence
  driver-ticks.
- **R3 → R4 — confirmation.** 4 residual nits, all cosmetic (e.g. completed/alive both green); no
  substantive defect; not FLAT / CROWDED / AIRY / MOTIF-MONOTONY / STATIC / BORING.

## Stop condition (met)
Two consecutive independent fresh critics (R3 ui-craftsman, R4 architect) found **ONLY NITS** and
both judged it **holds its own beside chit + leash + axon + whopays**. No self-certification; each
round surfaced NEW defects anchored on owner-verdicts; fixes went FAIL→fix→re-score with a fresh lens.
Owner (Dami) eye then passed it. Ported into `app/templates/index.html`, `app/static/card.css`,
`app/static/app.js`.

## AFTER — live-verified this phase (qa)
Live Playwright on :3300 (both states): contrast paper 15.69:1 / amber eyebrow 8.28:1, mobile-375
overflow-free, engine + narration badges render honestly. See `ai/design-qa-report.md`.
