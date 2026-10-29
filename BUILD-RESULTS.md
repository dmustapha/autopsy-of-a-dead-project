# BUILD-RESULTS.md

status: complete

## What Just Happened
We transcribed the entire app from ARCHITECTURE.md into a running FastAPI service and proved the full
loop locally: a real GitHub repo is fetched, reduced to six forensic features, classified into a
death-mode, and given a grounded coroner's eulogy, rendered as a death-certificate card. The seed
dataset — the linchpin, because TabPFN is a few-shot in-context learner that needs labeled exemplars
at inference — was built from 50 hand-labeled real repos into a 48-row CSV balanced across all five
death-modes (two repos were genuine 404s; six more were recovered by teaching the fetcher to follow
GitHub's 301 redirects for repos that moved orgs, including the flagship `facebook/react`). This
matters to the thesis because the whole entry is a blog post whose soul is "I autopsied my dead
projects and an open-weight AI told me how they died" — the app is the evidence, and every number in
the post (the graveyard census, the feature table, the honest separability figure) now comes from a
real run, not a mock. The next phases ride on this: design screenshots the real certificate card,
demo records the real loop, deploy stands the stack up on Oracle with Ollama/Gemma co-located, and
package writes the post from the captured material in POST-DRAFT.md and data/NOTES.md.

The single most important honest finding: the **open-weight TabPFN core we built the project around
was down on build day** (Prior Labs returned HTTP 503 "Service is disabled"). The app did exactly
what its honesty invariant (I3) designed it to do — it fell back to the labeled `engine="rules"` path
and *said so on the certificate*. An autopsy tool that hid its own dead organ would be a fraud; the
engine badge is the feature, and the outage became the strongest live demonstration of it.

## Honest Gaps
- **TabPFN happy path (`engine="tabpfn"`) is UNTESTED (DEV-002)** — the Prior Labs hosted inference
  endpoint returned HTTP 503 on every `fit` call (the token authenticated fine; the service itself is
  disabled server-side). The real leave-one-out separability number is therefore UNMEASURABLE this
  build; the only separability figure we can honestly report is the 1-NN proxy LOO of 31% (chance 20%),
  which is a floor, not TabPFN's ceiling. Must be re-verified at deploy/livetest when Prior Labs is back.
- **Gemma-via-Ollama narration is UNVERIFIED locally (DEV-004)** — the build host has no Ollama daemon,
  so every local eulogy used the labeled templated fallback. The grounding + retry + fallback machinery
  IS proven (the grounding test rejects a fabricated 99999), but the actual Gemma-written register/quality
  is unverified until the Oracle deploy phase where Ollama is co-located.
- **Certificate screenshots are not produced** (claims.json: `pending`) — that is the `design` phase's
  deliverable (build boundary DP-7); build only proved the card renders (HTTP 200 on `/` and `/static`).
- **Live deploy is not performed** (claims.json: `pending`) — out of build scope by instruction. All
  deploy assets are committed (systemd unit, nginx conf, RUNBOOK, CI); the conductor's `deploy` phase runs
  the live V.B5 gate against the Oracle VM.
- **abandoned↔completed separability is weak** on the 1-NN proxy (9 confusions) because the discriminating
  `is_archived` boolean is deliberately absent from the feature row (a documented limitation, not a bug);
  whether TabPFN separates the pair better is unverified due to the outage.
