# Autopsy field notes — the human story behind the seed dataset

Harvested live during the B0 build (2026-10-29). Each block is a real observation from watching
50 real repositories get exhumed, classified, and separated. This is the soul of the write-up —
it cannot be invented at write-time, only collected.

## The one I was sure had died — and it is wide awake
`pallets/flask` and `django/django` both read "old." I half-expected the decade-old frameworks to
look abandoned. They do not: Django's velocity ratio came back at **4.3** (its recent 90-day commit
rate is over four times its lifetime average — a release crunch), and its bus factor is 6. A repo's
age tells you nothing; its *recent cadence relative to itself* tells you everything.

## `abandoned` and `completed` are the hardest pair to tell apart
The 1-NN proxy confused `abandoned` with `completed` 9 times out of its 33 misses — more than any
other pair. It makes sense: a deliberately-finished library (`google/leveldb`, archived) and a
quietly-dead one (`bower/bower`, deprecated) both show the same surface signature — no commits for
years, velocity near zero. The thing that actually separates them — *was it archived on purpose* —
is a single boolean (`is_archived`) that the forensic feature row deliberately does not carry.
That omission is a real, documented limitation, not an accident (see LIMITATIONS.md).

## `facebook/react` taught the fetcher a lesson about ghosts that moved house
Six of the original 50 seeds 404'd on the first build — including the flagship `facebook/react`,
`zeit/next.js`, and `twitter/bootstrap`. They had not died; they had *moved orgs*. GitHub answers a
renamed repo with a `301 Moved Permanently` to the canonical path, and the fetcher was calling
`raise_for_status()` on it. One line — `follow_redirects=True` — resurrected all six. A ghost that
moved house is not a ghost.

## `burned_out` has a fingerprint: one hand, falling
`sindresorhus/caprine` and `tj/commander.js` are the archetype — a single maintainer whose cadence
decays toward zero. Bus factor 1, a steep negative commit-cadence slope. The forensic-rules path
keys off exactly this joint signal (`commit_cadence_decay < -2 and bus_factor == 1`), because no
single feature catches it: a healthy solo project also has bus factor 1; only the *decay* alongside
it says "burning out."

## The model we built the project around went dark mid-autopsy
The whole point was to let **TabPFN**, an open-weight tabular foundation model, read the posterior.
On build day its hosted inference endpoint returned `503 Service Unavailable — Service is disabled`
on every call. The token authenticated fine; the model simply was not serving. So the app did
exactly what it was designed to do when a dependency dies: it fell back to the labeled
`engine="rules"` forensic path and *said so on the certificate*. An autopsy tool that hides its own
dead organ would be a fraud. The honesty badge is the feature.

## Velocity ratio is a liar for very short lives
The `pivoted` class (`angular/angular.js`, `yarnpkg/yarn`) overlaps `abandoned` on velocity alone —
both can read ~0. What separates a pivot from an abandonment is that a pivot has a *successor*
(angular.js → Angular; yarn classic → berry) and usually a shorter decisive lifespan. The feature
that should carry this is `lifespan_days`; the seed set leans on it to keep the two apart.
