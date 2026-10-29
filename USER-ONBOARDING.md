# USER-ONBOARDING — Autopsy of a Dead Project (LAW#7 user-first)

The product is scoped from real users, not dev convenience. The real user path and the demo path are
the SAME single loop (paste a repo → certificate); there is no simulate-only shortcut that diverges
from what a real user does.

## USER CLASSES

### DEV judge (primary)
- WHO: a DEV.to engineer / community reviewer skimming many Hacktoberfest entries, deciding in seconds whether a post is worth a full read and a reaction.
- GENESIS: arrives from the dev.to post's embedded demo link or the repo README; lands on a warm live page with a clear title and three example graves.
- ONBOARDING: zero setup — clicks an example chip and instantly sees a death-certificate card (verdict + confidence + evidence table + eulogy + the "classified by TabPFN" badge). Value is delivered in one click, no account, no config.
- INTEGRATION: the honest engine badge + the live <2s response are the trust signals that make the judge believe the open-source-AI claim without reading code.

### Reader-dev (secondary)
- WHO: a developer who clicks through from the post out of curiosity about their own abandoned repos.
- GENESIS: reads the post, feels the "I have a graveyard too" pull, clicks the live link.
- ONBOARDING: pastes their own repo URL (or an example), gets a verdict + eulogy, and is invited to share the certificate — the reaction loop (reactions are the published tiebreaker).
- INTEGRATION: the shareable certificate id + the "autopsy your own graveyard" closing line turn a reader into a reactor/sharer.

## COLD-STRANGER GENESIS
A cold stranger with no prior setup, no account, and no API keys reaches product value in one action:
land on the warm live URL → click a pre-warmed example chip (or paste any public repo) → receive a
full death-certificate (TabPFN verdict + grounded eulogy) in <6s. No signup, no install, no
configuration gates the first value. The genesis→value path is: **live link → one click → a verdict
they want to screenshot.** (For the fully-local/offline enthusiast, the documented Ollama mode is a
secondary genesis requiring `ollama pull`, but it is never on the critical first-value path.)
