# POST-DRAFT — living draft (fill [CAPTURE] hooks during build; package finalizes)
Title: I performed an autopsy on 50 of my dead side-projects. An open-weight AI told me how each one died.
Tags: devchallenge, hf26challenge · Cover: the death-certificate card · Embed: demo GIF/video

## §1 Hook
[the graveyard-of-dead-repos opening — see PRD §47.1]

## §2 Idea & theme (Ghost in the Machine = ghosts of dead code; DdlM remembrance)
[PRD §47.2] — [CAPTURE B4: screenshot of the certificate card]

## §3 How it works (+ evidence table)
[PRD §47.3] — CAPTURED B4 (hero repo `bower/bower`, a real `/autopsy` response):
| Signal | Value |
|---|---|
| Days since last commit | 745 |
| Commit-cadence decay | -0.239 |
| Lifespan (days) | 4089 |
| Contributors | 161 |
| Bus factor | 1 |
| Velocity ratio | 0.0 |
| **Verdict** | **abandoned** (engine: rules — see §5 honesty) |

## §4 The seed dataset (the human story)
[PRD §47.4] — CAPTURED B0 (full observations in `data/NOTES.md`, 6 blocks):
- Django reads "old" but came back velocity ratio **4.3** — age tells you nothing, recent cadence vs itself tells you everything.
- `abandoned` vs `completed` is the hardest pair (9 of the proxy's 33 misses) — the one boolean that separates them (`is_archived`) is deliberately absent from the feature row (documented limitation).
- `facebook/react` + 5 others 404'd on build-1: they hadn't died, they'd *moved orgs* (GitHub 301). One line, `follow_redirects=True`, resurrected all six.
- `burned_out` has a fingerprint: bus factor 1 **and** a steep negative cadence slope — neither alone catches it.

**Graveyard census (48 real repos, hand-labeled):**
| Death mode | Count |
|---|---|
| alive | 10 |
| abandoned | 10 |
| pivoted | 10 |
| completed | 9 |
| burned_out | 9 |

**Separability, honest (critique E-2):** On build day the Prior Labs TabPFN hosted endpoint returned HTTP `503 "Service is disabled"` — so the real TabPFN leave-one-out number is UNMEASURABLE this build. The 1-NN proxy LOO on standardized features is **15/48 = 31%** (chance 20%). The app therefore shipped its labeled `engine="rules"` path as primary and said so on every certificate. An autopsy tool that hid its own dead organ would be a fraud.

## §5 Why open-source AI mattered
[PRD §47.5] — The core is open-weight end to end: **TabPFN** (open-weight tabular foundation model) reads the death-mode posterior; **Gemma** (open weights) writes the eulogy, served by **Ollama** on our own box — keyless, offline-capable, zero paid APIs. The one-line local switch: `LLM_BASE_URL=http://localhost:11434/v1` + `LLM_MODEL=gemma2:2b`. Because narration is self-hosted, the whole thing runs with no closed dependency and no API bill — which is also exactly why, when the hosted TabPFN went dark, the app degraded honestly instead of lying.

## §6 Hosting (Oracle Always-Free + Ollama)
[PRD §47.6] — Everything (FastAPI app + Ollama/Gemma) runs co-located on one Oracle Always-Free VM: $0, no card, no spin-down. Runbook in `deploy/RUNBOOK.md`. [CAPTURE deploy: the live URL + first-warm-latency number]

## §7 Try it / close
[CAPTURE demo: embedded demo GIF/video] · Live: [CAPTURE deploy url] · Code: [repo]
[closing line inviting readers to autopsy their own graveyard — reactions = tiebreaker]

## Results table (graveyard census — critique E-2, honest numbers)
- **Engine mix this build:** 100% `rules` (TabPFN hosted service was down — HTTP 503); `tabpfn` re-activates automatically on deploy when the service returns.
- **Death-mode seed distribution:** alive 10 · abandoned 10 · pivoted 10 · completed 9 · burned_out 9 (48 total).
- **1-NN proxy LOO:** 31% (chance 20%). Real TabPFN LOO: pending service recovery.
- **Local loop latency:** `/healthz` ready < 2s; `/autopsy` (cold, real GitHub fetch + rules + templated narration) ~1–3s. [CAPTURE demo: median on live Gemma]
