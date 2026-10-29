# USER-ONBOARDING — Autopsy of a Dead Project

## USER CLASSES

### The dev.to judge (primary)
- WHO: a DEV editorial judge or a Render/Prior-Labs sponsor engineer opening the live URL from the post.
- GENESIS: arrives cold from the post's Demo link, no account, no setup. First state: a pre-seeded death-certificate already rendered on the landing page.
- ONBOARDING: reads the one-line hero, sees a real certificate, pastes any public repo URL to try it within 60s.
- INTEGRATION: none required — the app needs nothing from the judge but a URL.

### The curious developer (secondary)
- WHO: a dev who found the post and wants to autopsy their own dead side projects.
- GENESIS: same cold-arrival path; no login wall.
- ONBOARDING: pastes their own repo URL, gets a verdict + narration, screenshots the certificate to share (tiebreaker: reactions).
- INTEGRATION: optionally sets a GITHUB_TOKEN if self-hosting for higher rate limits (documented, not required).

## COLD-STRANGER GENESIS
A cold stranger with no prior setup reaches a real death-certificate by: opening the live Render URL (seeded certificate visible immediately) → pasting any public GitHub repo URL → clicking Autopsy → watching the full loop run. No login wall, no API key entry, no install.

## USER PATH (not the demo's)
- REAL: open URL → paste public repo URL → autopsy runs → death certificate.
- DEMO: EQUALS the real path exactly. The demo pastes a real public repo and runs the same live loop — no always-on simulate button, no manual-paste shortcut, no pre-faked verdict. The seeded landing certificates are real outputs of the same loop run in advance, not a demo-only mock.
