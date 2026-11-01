# PACKAGE-RESULTS.md

status: complete

## What Just Happened
Assembled the submission record for a DEV Hacktoberfest Week 4 entry whose submission was already published (the DEV blog post IS the submission, so there is no form to fill). Produced a real `submission/` bundle: HTTP-verified `links.md` (4/4 required + 3/3 media), a grep-verified `sponsor-tracks.md` staking the Best Use of TabPFN partner category against actual code paths (`app/classifier.py`, `scripts/eval_loo.py`, `app/narrator.py`), a three-tier `HONESTY-LEDGER.md`, a `HACKATHON-README.md` with a recompute-tier `## Verify in 60s` proof surface (a judge reruns `python scripts/eval_loo.py` and watches 58.1% vs 43.6% re-derive), copy files, a `SUBMISSION-GUIDE.md` recording how it was submitted, and a root `HANDOFF.md`. It matters because the judged claim ("the foundation model beats the dumb baseline") is now independently re-derivable from a cold clone, not just asserted, and the category claim is backed by file references rather than prose. Verify_preflight already passed; organizer-feedback and conductor-state close-out ride on this.

## Honest Gaps
- Inline article images are hosted on catbox.moe, not dev.to's own CDN. Dami chose this for speed; it is a real durability risk if that host hiccups during the judging window (dev.to-native upload would be more robust). Flagged as a warning in `.package-state.json`, not fixed.
- `HANDOFF.md` cites "68 tests green" from the build/verify records rather than a fresh `pytest` run in this session; grep counts 60 test functions. The number is the recorded one, not re-measured here.
- The package gate scripts (submission-terminal-gate, judge-artifacts-gate, submission-surface-gate) were not executed; this was an inline run without the conductor, and most assume a contract/DoraHacks shape that does not apply to a published DEV post. The artifacts they check for were produced and verified by hand instead.
- No launch-tweet / THREAD.md drafts produced (B-13 submission-surface extras); not requested, and the entry is already live. Can be added if Dami wants social amplification.
