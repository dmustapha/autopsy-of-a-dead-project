# DESIGN HANDOFF → dev-ghost main chat · 2026-10-31

The good-era design cycle for "Autopsy of a Dead Project" is DONE and already ported into the
real app files. This chat should adopt it, verify, and carry it into the dev.to submission.
Do NOT re-design — the design passed the ladder (two independent fresh-critic "only nits"
verdicts, holds beside chit+leash). Owner (Dami) eye is the only gate left.

## WHAT CHANGED (the revamp is in these 3 files — this is the git diff)
- `app/templates/index.html` — new structure (constructed amber field, flatline hero, forensic
  grounding band, cert container, loading/error states). No mock data; wired to `/examples` + `/autopsy`.
- `app/static/card.css` — the full dark-forensic/memorial design system (amber lamp field, the
  certificate document, differential list, driver-row evidence, honesty badges, responsive).
- `app/static/app.js` — renders the REAL `/autopsy` response; the signature flatline (canvas,
  per-mode, animated flatten + seal stamp), drifting dust, guilloche watermark.
Backend (`app/*.py`, schemas, classifier, narrator) is UNCHANGED.

## HONESTY (built in — do not "fix" it)
- Engine badge: `tabpfn` vs `rules (fallback)` + narration badge `Gemma` vs `templated · LLM offline`,
  both first-class, detected from the real response (narration fallback detected via its marker text).
- Current backend returns rules + templated (TabPFN 503, Ollama off): the card shows a dignified
  "single determination — no posterior" note instead of fabricating a distribution. When TabPFN/Gemma
  return, the full ghost-differential + live badges activate automatically. Nothing is faked.

## VERIFY BEFORE YOU TRUST IT (run your own instance; :3200 is another session's — leave it)
    cd /Users/MAC/dev-ghost && .venv/bin/python -m uvicorn app.main:app --port 3300 --host 127.0.0.1
Open http://127.0.0.1:3300/ , paste a repo or click an example. Confirm: certificate renders, the
flatline flattens + seal stamps, badges read honestly, alive repos flip to "CERTIFICATE OF LIFE".
(A design-owned instance may already be running on :3300 — `lsof -ti:3300` ; kill/restart as needed.)

## DELIVERABLE SCREENSHOTS (real app, ready for the dev.to post)
`/Users/MAC/pipeline-audit/skill-audit/win-audit/REFERENCE-TEARDOWN/RUN-dev-ghost/caps/real/`
- `hero.png`, `cert-bower.png` (CERTIFICATE OF DEATH — the hero artifact), `cert-fastapi.png`
  (CERTIFICATE OF LIFE), `cert-caprine.png` (Burned Out). Proto has the tabpfn+full-differential
  state at `caps/card-abandoned-tabpfn.png` if you want to show that path too.
The POST-DRAFT (`POST-DRAFT.md`) cover should be the bower death-certificate card.

## FULL RECORD
`…/REFERENCE-TEARDOWN/RUN-dev-ghost/` — CALIBRATION.md, SELECTION.md, AUDIENCE-CONTRACT.md,
SCORECARD.md (the R1→R4 ladder + verification), LEDGER-ENTRY.md, proto/index.html (all states).

## WHAT'S LEFT (gated)
1. Dami's terminal eye on the design (does it hold beside chit + leash?).
2. Commit the 3 changed files (design revamp) — on Dami's go.
3. Deploy + the dev.to post — Dami decides; do NOT publish without his explicit go-ahead.
   Deadline: post published 2026-10-31 by 18:00 WAT.
