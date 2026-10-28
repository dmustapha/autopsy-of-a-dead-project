# PULSE — Pipeline Rolling Context

## Active Facts
| Fact | Source | Phase |
|------|--------|-------|
| Required tags: `devchallenge` + `hf26challenge` (both; missing = invalid) | Wk4 page + Wk1 rules | intel |
| Deadline Oct 31 11:59 PM **PDT**; internal cutoff Oct 31 18:00 WAT | Wk1 contest rules | intel |
| Project must be NEW, built in-window; no pre-existing code; no PRs → binds standalone-fresh | Wk1 rules | intel |
| One entry only; FIRST submitted is judged; reactions = tiebreaker | Wk1 rules | intel |
| Writing quality is the heaviest judged axis; the POST is the deliverable | challenge page | intel |
| Winner anatomy (N=323): 86% longer, 80% cover image, 42% demo video, 29% tables, first-person titles | munim study | intel |
| Render free tier spins down 15min → dead demo; need Starter $7/mo min, kept warm (dl-1) | Render pricing 2026 | intel |
| Field crowded on ghost-story/haunted-terminal + Ollama/Gemma; whitespace = memorial + TabPFN tabular | live competitor posts | intel |

## Decisions Log
| Decision | Rationale | Phase |
|----------|-----------|-------|
| Default open-source-AI core = open-weight model via **Groq free API** | Fastest, cheapest, Render-tiny; satisfies open-weight req without hosting weights | intel |
| Deploy on **Render Starter $7/mo** (durable), not free tier | dl-1: free spins down inside judging window | intel |
| TabPFN = pursue ONLY if concept has a genuine tabular-prediction core (else skip, don't bolt on) | sponsor judges penalize bolt-ons; thinnest field = highest EV if natural | intel |
| Question-shift OFF the organizer examples (ghost-story/haunted terminal are the collision map) | 9+ live clones; PhantomTerminal already shipped the altar concept | intel |

## Downstream Items
<!-- Owner-routed, non-blocking deferred work. Every skill reads on entry, actions rows it owns. See PULSE-PROTOCOL § Downstream Items. -->
| ID | Raised by | Owner phase | Pri | Item | Acceptance | Status |
|----|-----------|-------------|:---:|------|-----------|:------:|
| DS-1 | intel | build | 🔴 | Read the LIVE Wk4 challenge page on build day for exact theme/example prompt text (secret pre-launch) | exact prompt quoted in post | open |
| DS-2 | intel | deploy | 🔴 | Render MUST be a durable paid tier (Starter $7/mo min), kept warm through Nov-2 judging week | live URL responds <2s during judging | open |
| DS-3 | intel | package | 🟡 | Post MUST have: cover image + embedded demo video/GIF + ≥1 table + first-person number-in-title | all four present before publish | open |
| DS-4 | intel | build | 🟢 | Capture a DevRelay agent session during build for the optional embed (credibility boost) | `{% agent_session %}` embeddable | open |

## Skill Sections

### hackathon-intel (2026-10-28, ID 6 Standard)

#### Done
 Researched DEV Wk4 rules, winning-post anatomy (323-winner study), Render + TabPFN partner categories, open-weight inference paths. 14 sources. research-brief.md (20KB), config.json, intel-state.json written; capability-map gate clean (exit 1).

#### Additions
 Capability map (6 primitives: dev.to-platform, Render, Groq open-weight inference, TabPFN, Ollama-local, ElevenLabs-garnish) + organizer_feedback seam (3 DX frictions). 3–5 themed concept seeds incl a TabPFN grand-slam angle.

#### Deviations
 Ran Standard depth (ID 6, ~14 searches) not MAXIMAL (ID 9) — deliberate SPRINT / 1-day-build sizing per conductor dispatch. Social intel (Phase 2) skipped (autonomous run, no user).

#### Verified Facts
- Required tags: `devchallenge` + `hf26challenge` (both; missing = invalid). [A1]
- Hard rules: brand-new build within window, ONE entry (first-submitted judged), core AI must be open-source. Deadline Oct 31 11:59 PM PDT; tiebreaker = post reactions. [A1]
- Writing quality judged HEAVIEST, then theme, creativity, technical, partner-tech. Winning posts: ~1,500–2,500 words, cover image (80%), embedded demo video/GIF (42% vs 21%), ≥1 table, first-person/number-in-title. [B2]
- Render free tier spins down after 15 min idle → dead demo during Nov-2 judging week. Need Starter $7/mo kept warm. [A1/dl-1]
- Groq free API serves open-weight Llama/Qwen, OpenAI-compatible, ~85ms TTFB, no card — keeps Render service tiny. [B2]

#### Assumptions
 Exact Week-4 theme prompt text stays secret on the live page until launch — must read live challenge page on build day (org-fb #1). [ASSUMED pending live-page read]

#### Blockers for Downstream
 None hard. TabPFN local weights need a browser license-accept (awkward headless) — hosted tabpfn-client sidesteps with an API key.

#### Key Decisions
 Open-weight core via Groq; durable Render Starter tier (not free); TabPFN only if tabular is genuinely the concept's core (blue-ocean $200, near-zero field); standalone-fresh concept; question-shift OFF the ghost-story/haunted-terminal herd toward memorial/functional whitespace.

#### For Next Skill
 Pick a concept that is open-weight-at-core + themed (memorial/functional preferred over clichéd spooky) + Render-deployable + writes up beautifully. Strongest seed = "Autopsy of a dead project" (TabPFN predicts what killed a repo from its git-history table + open-weight model narrates the post-mortem as a séance) — genuine tri-track (Overall + Render + TabPFN), tabular is the core not a bolt-on. Leading competitor to beat: PhantomTerminal (~2k words but NO cover image, NO demo video).
