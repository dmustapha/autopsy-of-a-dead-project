# Hacktoberfest Open-Source AI Challenge — Week 4 "Ghost in the Machine" — Research Brief
**Compiled:** 2026-10-28
**Intel Depth:** ID 6 (Standard — deliberate SPRINT dial-down for a $250 challenge; Dami ruling)
**Sources:** Web research (14 sources). Social intel: NOT gathered (autonomous run — see Social Intel).

---

## Overview

| Field | Value |
|-------|-------|
| Name | Hacktoberfest Open-Source AI Challenge — Week 4: Ghost in the Machine |
| Organizer | DEV Community (dev.to) |
| Platform | dev.to (the submission IS a blog post) |
| Deadline | Oct 31, 2026, 11:59 PM **PDT** (winners wk of Nov 2). Internal cutoff: published Oct 31 18:00 WAT |
| Tracks | Overall $250; partner categories $200 each (Render, TabPFN, Tinker, Backboard, .tech) |
| Chain | n/a (not a crypto hackathon) |
| Team | Solo (one entry per participant; only the FIRST entry is judged) |

### Submission Requirements
- A published DEV post using the official **submission template**.
- **Required tags: `devchallenge` AND `hf26challenge`** (hard rule — wrong/missing tag = not a valid submission).
- A **brand-new** open-source AI project, **created + completed within the challenge window** (no pre-existing code; no PRs to existing projects).
- Post sections: **What I Built** (theme interpretation), **Demo** (deployed link OR video), **Code** (repo), **How I Built It** (which open-source AI tools), **Why Does Open Innovation Matter?**. Optional: **My Agent Session** (DevRelay), **The Spirit of It**, **Prize Categories**.

---

## Demo Video Requirements (E1)

| Field | Value |
|-------|-------|
| Max length | None published |
| Formats | YouTube / Loom / Vimeo / embedded GIF / live deployed link |
| Platform | Embedded in the DEV post |
| Content notes | Deployed link OR video required. **Winners embed a demo video 2x as often as losers (42% vs 21%)** — a GIF/video is close to mandatory for a winning post. |

---

## Submission Form Fields (E2)
The post itself is the form. The template scaffolds: Title · Cover image · Tags (`devchallenge`,`hf26challenge`) · What I Built · Demo · Code · How I Built It · Why Does Open Innovation Matter? · (opt) My Agent Session · (opt) The Spirit of It · (opt) Prize Categories.

---

## Disqualifiers (E3)
- Project/repo **not created within the challenge window** (pre-existing code → ineligible). *This binds `concept_origin: standalone-fresh` — nothing may be reused from the Qloo/other parallel builds; build net-new in-window.*
- A **PR to an existing project** (must be a standalone new project).
- **More than one entry** — only the first submitted is judged. Submit once, submit right.
- **Missing the required tags.**
- Core AI not open-source (a closed model as the core = fails the prompt).

---

## Prizes

| Track | Prize | Field size |
|-------|-------|-----------|
| Overall | **$250** + DEV++ + badge | Thickest (all entries) |
| Best Use of Render | **$200** + badge | **Thin** — requires a live Render deploy |
| Best Use of TabPFN | **$200** + badge | **Thinnest** — tabular angle rare under a spooky theme |
| Tinker / Backboard / .tech | $200 each + badge | Varies |

---

## Judging Criteria (derived weights — order is official, weights are estimated)

| Criterion | Est. weight | What it means | How to score high |
|-----------|:---:|---|---|
| **Writing Quality** | ~40% | The post as a craft object | Long, structured, first-person build-story; cover image; tables; demo video |
| Relevance to Prompt & Theme | ~20% | Genuine Ghost-in-the-Machine / Halloween / Día-de-los-Muertos fit | Lean into memorial/spooky *meaningfully*, not as a skin |
| Creativity | ~18% | Fresh angle | Avoid the ghost-story-generator herd (see Kill List) |
| Technical Execution | ~15% | Working code + functional demo | Live deployed app beats a local-only screenshot |
| Use of Partner Tech | ~7% | Optional, gates partner $200s | Load-bearing Render + (if natural) TabPFN |

**Tiebreaker (official):** highest number of positive reactions on the DEV post. → a shareable, well-titled post with a cover image has a real edge.

---

## Event Class & Judge Reading
- **Event class:** `open_buildathon` (derived). DEV editorial team judges the Overall prize; sponsor engineers judge partner categories.
- **Why this class:** organizer-run, rubric-scored (no public vote decides it; reactions are only the tiebreaker).
- **Judge reading:** The Overall panel rewards the POST as a piece of writing — the munim study (below) is the empirical rubric. Partner judges (Render, Prior Labs) reward *load-bearing* integration and penalize bolt-ons.
- **Sponsor vintage (last ~90 days):** TabPFN-3.5 (2026, docs changelog); DevRelay agent-session embed (2026, devrelay.com). Both are fresh — using a just-shipped partner primitive is an L5 podium signal.

---

## Winning-Post Anatomy (PRIMARY FINDING — #1 priority)

**BOTTOM LINE:** DEV challenge winners are long, structured, visual, first-person build-stories. This is measured, not folklore.
**EVIDENCE [B2 — munimtechnologies/devchallenge-study, 323 winners vs 8,320 entries across 55 challenges, Jan 2025–Oct 2026]:**
- **Length:** winners sit at the **0.78 percentile for word count — 86% are longer** than the typical entry. (0.75 reading-time, 0.67 heading-count, 0.60 code-blocks.) A good target: **~1,500–2,500 words** (the live PhantomTerminal competitor post is ~2,000).
- **Cover image:** **80% of winners vs 61%** of others. Near-mandatory.
- **Demo video:** **42% of winners vs 21%.** The single biggest separator after length.
- **Tables:** **29% of winners vs 12%** — a table signals "I measured something."
- **Images:** 0.66 percentile image count — show, don't tell.
- **Title:** **27% use a number** (vs 18%); **31% use first-person** "I/my/we" (vs 24%). Colons/dashes don't matter.
- **AI disclosure helps:** in the Oct-2026 "Build for a Friend" week, **8 of 17 winners declared "some AI" help vs ~15%** of other entries (≈3x). For an *open-source-AI* challenge, being transparent about your build process (and a DevRelay embed) aligns with what wins.
- **Timing is neutral** (0.49 percentile) — posting early/late gives no edge. Quality, not speed.
**CONFIDENCE:** High — large N, DEV's own public API, author flags it as correlation-not-cause but the signal is consistent and directly actionable.
**SO WHAT:** The build exists to generate screenshots, a GIF/demo-video, a measured table, and a first-person story. Budget real time for the post — it is the deliverable, not the afterthought. Top-5 patterns to hard-enforce: (1) cover image, (2) ~2k words with clear headings matching the template, (3) embedded demo video/GIF, (4) at least one table, (5) first-person, number-in-title.

---

## Tech Deep Dive — Open-Source-AI Core Options

**BOTTOM LINE:** For a 1-day Render-deployable build, **Groq's free API running an open-weight Llama/Qwen model** is the fastest, cheapest, most Render-friendly open-source-AI core. Local Ollama is the stronger *narrative* but heavier to deploy.
**EVIDENCE:**
- **Groq free tier [B2]:** OpenAI-compatible; open-weight Llama 3.1 8B / 3.3 70B / Qwen3-32B; ~85ms TTFB, 280–660 tok/s (fastest of Groq/Together/Fireworks); no credit card; 30–60 RPM free. Keeps the Render service tiny (no weights/GPU to host). *The open-weight requirement is satisfied by the model being open-weight — Groq is just the host.*
- **Ollama local [B2]:** Gemma 2/3, Qwen 2.5, Phi-4-mini run fully offline — best "open innovation / privacy / local-first" story and the dominant competitor stack. But even a 2–4B Q4 model needs ~2–4GB RAM → exceeds Render free (512MB) and Starter (512MB); needs the **$25/mo 2GB** tier, or ship local-only + deploy only a thin UI.
- **Credentials note:** ANTHROPIC/FAL/ELEVENLABS keys exist but **must not be the core** (closed). FAL (image) / ElevenLabs (TTS) are fine as *non-core garnish* (e.g. a generated cover image, a spoken ghost voice) layered on an open-weight core.
**CONFIDENCE:** High.
**SO WHAT:** Default core = **open-weight model via Groq free**, deployed on a durable Render tier. Mention Ollama as the local-first path in the post for the open-innovation narrative (and optionally ship a `docker run ollama` local mode) to win the "Why open innovation matters" section without paying for a 2GB tier.

---

## Render — "Best Use of Render" ($200) (#3 priority)

**BOTTOM LINE:** Render wins on a **live, functioning, durable deployment** — and the free tier will sabotage you.
**EVIDENCE [B2 — temps.sh render-pricing-2026, agentdeals render vendor]:** Free web service = 512MB/0.1CPU, **spins down after 15 min idle** (first request after sleep 30–60s), 750 instance-hrs/mo then **suspended**. Always-on starts at **Starter $7/mo (512MB)**; **$25/mo (2GB)** for anything hosting a local model. Qualifying use: Render as the AI runtime, agent frontend host, or to run Hermes/OpenClaw.
**CONFIDENCE:** High.
**SO WHAT (dl-1 durable-tier rule, binding):** A judge clicking a sleeping free-tier link during the Nov-2 judging week sees a 30–60s hang or a suspended service → dead demo. **Deploy on Render Starter ($7/mo) minimum, kept warm through the judging window.** Size the tier to the build: Groq-core → $7/mo 512MB is plenty; local-model core → $25/mo 2GB. This is the +EV category (thin field) — do it, and make Render *load-bearing* (it IS the app host), not a bolt-on.

---

## TabPFN / Prior Labs — "Best Use of TabPFN" ($200) (#4 priority)

**VERDICT: viable-but-forced for the obvious concepts — pursue ONLY if the concept has a genuine tabular-prediction core.**

**BOTTOM LINE:** TabPFN is a real, easy-to-use open-weight tabular foundation model, but it predicts over *tables of historical data* — it has zero natural fit for the ghost-story/chatbot concepts the theme invites.
**EVIDENCE [A1 — docs.priorlabs.ai, HF Prior-Labs/tabpfn_3_5]:** `pip install tabpfn` (local, open weights on HF, **non-commercial license**, GPU-friendly) OR `tabpfn-client` (hosted API, managed GPU). One checkpoint does classification + regression in a single forward pass, no training. Prior Labs recommends **TabPFN-3.5**, and explicitly **favors projects that use it inside a wider prediction agent**. Local weights require an interactive browser login to accept the license (awkward headless).
**CONFIDENCE:** High on the capability; medium on theme-fit (depends entirely on concept).
**SO WHAT:** Only reach for TabPFN if a concept *naturally* needs to forecast/classify/anomaly-spot over a table. The thinnest, highest-EV path to the $200 is to invent a concept where tabular prediction IS the ghost — e.g. a "séance" that reads a dead project's git/commit history table and *predicts* what killed it, or an ofrenda that forecasts a memory from a person's life-events table. If the concept is text-only, **skip TabPFN** rather than bolt it on (sponsor engineers penalize bolt-ons).

---

## Capability Map

| Primitive | Can (proven) | Can't / not-yet | Maturity | Evidence | Load-bearing for |
|-----------|--------------|-----------------|----------|----------|------------------|
| dev.to platform | MD post, cover, tables, code, GIF/video, GitHub + `{% agent_session %}` embeds; tags gate submission; reactions = tiebreaker | Can't host a running app; no originality auto-check; theme prompt secret until launch | GA | challenge page + Wk1 rules + munim study | THE submission — writing quality is the heaviest axis |
| Render | Public web service / Docker; host agent frontend + OSS runtime | Free spins down 15min; 512MB too small for LLM weights; 750hr/mo cap | GA | temps.sh/agentdeals render 2026 | Best Use of Render $200 + live demo — **needs durable Starter $7/mo min** |
| Groq free API | Hosted open-weight Llama/Qwen; ~85ms TTFB; no card | Rate-limited free; hosted not local | GA | eesel groq-pricing + ml+ benchmark | the open-source-AI **core** via a Render-tiny path |
| Ollama + small OSS model | Gemma/Qwen/Phi local & offline; best open-innovation story; competitor-dominant | 2–4B needs 2–4GB RAM > Render free/Starter; slow cold-pull | GA | localaimaster/morphllm VRAM 2026 | the offline/privacy narrative — load-bearing only if local or 2GB+ tier |
| TabPFN-3.5 | pip/local open weights OR hosted client; classify+regress, no training | needs tabular data; non-commercial local license; interactive license login | GA | docs.priorlabs.ai + HF | Best Use of TabPFN $200 — **NOT load-bearing for a pure text/story build (bolt-on risk)** |
| DevRelay | Embed agent-session transcript; judges appreciate it | optional, not directly scored; capture needs Cursor/CLI mid-build | beta | devrelay.com + organizer post | NOT load-bearing — free credibility boost; capture during build |

---

## Organizer Feedback (DX seam)

| Area | Friction | Evidence |
|------|----------|----------|
| docs | Week-4 theme name + example-project prompt stay secret until launch; the hub post omits it → can't quote exact prompt pre-launch; must read the live page on build day | devteam Hacktoberfest-2026 overview ("each theme stays secret until the day it launches") |
| DX | TabPFN local weights need an interactive browser login to accept the license — awkward headless/CI; hosted client sidesteps but adds a key | docs.priorlabs.ai/models/accessing-model-weights |
| infra | Render free tier (512MB, 15-min spin-down) is unusable for a live judging demo and too small for local LLM weights — builders aren't warned they effectively need a paid tier to win the Render category | temps.sh render-pricing-2026 + agentdeals |

---

## Competitor Landscape

**BOTTOM LINE:** The field is already **crowded and converged** — ghost-story generators + haunted terminals, almost all on **Ollama + Gemma/Qwen + Streamlit/Gradio**. The whitespace is *memorial* (Día de los Muertos / oral-history), a *functional* twist, or a *tabular* angle.

### Competitor Registry (web-sourced, live DEV posts under `hf26challenge`)
| Project | Angle | Stack | Threat | Source | Confidence |
|---------|-------|-------|:---:|---|:---:|
| GhostWriter AI | horror story generator | Python + Ollama + Qwen2.5 + Streamlit | MED | dev.to/lavish_sheth | B2 |
| The Haunted Terminal | "trapped spirit" chat | Streamlit + Ollama + Llama 3 | MED | dev.to/shambhavichourasia | B2 |
| Phantom AI | ghostly oracle / debug assistant | HF transformers + Gradio + Colab GPU | MED | dev.to/naman_srivastava | B2 |
| PhantomTerminal AI | code-séance + DdlM altar (multi-tool) | Gemma 2 2B + Ollama + Render (free) + vanilla JS | **HIGH** | dev.to/dien | B2 |
| GhostLore AI | spooky story website | HTML/CSS/vanilla JS | LOW | dev.to/rishi_yadav | B2 |
| GhostScript / GhostWhisper / N-CODE GhostLog / Spiritus | memory-revival / log-to-story / ofrenda | Gemma local variants | MED | dev.to (hf26) | B2 |

**PhantomTerminal is the one to beat:** ~2,000-word polished post, live Render deploy + local mode, Gemma-2B/Ollama, a table, a Día-de-los-Muertos altar, zero-dependency local run. It is well-written but has **no cover image and no demo video** — both are proven winner separators and our opening to beat it.

### Competition Density Map
| Angle | Est. Teams | Density |
|-------|:---:|:---:|
| Ghost-story / horror generator | 9+ | **HIGH (red ocean)** |
| Haunted terminal / trapped-spirit chat | 5+ | HIGH |
| Virtual ofrenda / memorial / oral-history | 2–3 | **LOW (whitespace)** |
| Tabular-prediction "ghost" (TabPFN) | ~0 seen | **BLUE OCEAN** |

---

## Community Pain (Verbatim Quotes)
Social intel was NOT gathered (autonomous run — no user for Discord/X). Verbatim community complaints were not collected this run; the convergence evidence above is from reading live competitor posts directly. **Gap noted.** No fabricated quotes.

---

## Past Editions Analysis
This is a per-week 2026 Hacktoberfest challenge; the munim cross-challenge study (55 challenges, 323 winners, Jan 2025–Oct 2026) *is* the past-winner analysis — see Winning-Post Anatomy. Earlier 2026 weeks (Touch Grass, Build for a Friend) show the same pattern: long, visual, first-person, demo-video'd posts win; AI-help disclosure correlated 3x with winning.

---

## Broader Market Context
Open-weight small models (Gemma 3, Qwen 3, Phi-4-mini) + fast hosted inference (Groq/Cerebras) make a polished local-feeling AI app a 1-day build in 2026. The spooky/memorial theme + "open innovation matters" prompt rewards the *local-first / privacy / your-data-stays-yours* narrative — a natural fit for an open-weight core, and a clean contrast to closed APIs that the "Why open innovation matters" section explicitly asks for.

---

## Category Saturation (Grid Data)
Not applicable — Grid is a crypto-ecosystem tool; this is a non-crypto DEV challenge. Saturation is captured in the Competition Density Map above from direct post reads.

---

## Builder Project History (Copilot)
Not available — Copilot corpus is crypto/Colosseum projects, irrelevant to a DEV.to AI writing challenge. Omitted (not proof of absence).

---

## Key Links & Resources
| Resource | URL |
|----------|-----|
| Challenge page | https://dev.to/challenges/hacktoberfest-week4-2026-10-26 |
| Contest rules (Wk1, same terms) | https://dev.to/page/hacktoberfest-week1-2026-10-05-contest-rules |
| What-wins study (empirical rubric) | https://dev.to/munimv2/what-wins-dev-challenges-323-winners-compared-with-the-8320-entries-they-beat-2p8 |
| Hub (all hf26 submissions) | https://dev.to/challenges/hf26 |
| TabPFN quickstart | https://docs.priorlabs.ai/quickstart |
| TabPFN weights (HF) | https://huggingface.co/Prior-Labs/tabpfn_3_5 |
| Render pricing 2026 | https://temps.sh/blog/render-pricing-2026 |
| Groq pricing/free tier | https://www.eesel.ai/blog/groq-pricing |
| DevRelay | https://devrelay.com/ |
| Free credits | https://hacktoberfest.com/my/promos |

---

## Track Coverage Matrix (#1 winning pattern)

| Track | Prize | Judging Focus | Overlap | Est. Submissions |
|-------|-------|--------------|---------|-----------------|
| Overall | $250 | Writing quality + theme | — | HIGH |
| Best Use of Render | $200 | Live durable deploy | Overlaps Overall (same app, deployed) | MED |
| Best Use of TabPFN | $200 | Load-bearing tabular prediction | Overlaps Overall if concept is tabular | **LOW** |

**Multi-track target:** One project → **Overall + Render** is free (any live-deployed app). **Overall + Render + TabPFN** is the grand slam *if* a tabular prediction is the concept's beating heart.
**Low-competition tracks:** TabPFN (near-zero entrants) and Render (thinner than Overall) — both higher win-probability than Overall.

---

## Domain Knowledge Sources (#2 winning pattern)
| Source | URL | Covers | Essential? |
|--------|-----|--------|:---:|
| munim what-wins study | (above) | the empirical winning-post rubric | **YES** |
| Groq docs | https://console.groq.com/docs | open-weight inference, OpenAI-compat API | YES (if Groq core) |
| TabPFN quickstart | https://docs.priorlabs.ai/quickstart | tabular prediction integration | YES (if TabPFN) |
| Render docs | https://render.com/docs | deploy web service / Docker | YES |
| DevRelay | https://devrelay.com/ | agent-session embed | NO (optional boost) |

---

## Kill List

### 1. Saturated (dead on arrival — the herd)
- **Ghost-story / horror-story generator** (GhostWriter, GhostLore, GhostWhisper, …) — *organizer-suggested → collision magnet.* 9+ live.
- **Haunted terminal / "trapped spirit in your shell" chatbot** (Haunted Terminal, Phantom AI) — *organizer-suggested.* 5+ live.
- Generic **offline chatbot with a spooky system prompt** — the default everyone reaches for.
- *(All organizer example ideas — haunted terminals, ghost-story generators, offline chatbots — are the collision map, not a menu. Question-shift off them.)*

### 2. Broken Dependencies
- **Render free tier for the live demo** — spins down in 15 min, dead in the judging window (dl-1). Must pay Starter.
- **Local LLM weights on Render free/Starter (512MB)** — won't fit; needs $25/mo 2GB or stay local.
- **TabPFN local weights in a headless Render build** — interactive license-login blocks CI; use tabpfn-client or accept locally first.

### 3. Already Built
- Multi-tool "code séance + Día-de-los-Muertos altar" on Gemma/Ollama/Render — **PhantomTerminal already shipped this.** Don't rebuild it; out-write it on a different angle with a cover image + demo video.

### 4. Zero Alignment
- Any build whose **core AI is a closed model** (GPT/Claude/Gemini as the engine) — fails the open-source-AI prompt.
- A **TabPFN bolt-on** stapled to a text-only story app — sponsor judges penalize it; either make tabular the core or skip TabPFN.

---

## Social Intel
Not gathered (autonomous conductor run — Discord/X review requires a user). Competitor data above is web-sourced from live DEV posts. **Phase-2 gap noted.**
