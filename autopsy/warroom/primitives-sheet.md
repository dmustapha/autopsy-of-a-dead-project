---
event_class: open_buildathon
event_class_source: inferred
pack_version: 2
pack_date: 2026-09-28
gap_map: present
sponsor_vintage: present
---

# Working Primitives Sheet — Hacktoberfest Wk4 "Ghost in the Machine"

(Run-local families. The shipped MECHANISM-LIBRARY is crypto-ecosystem; this is a non-crypto open-source-AI writing challenge, so families are re-authored for this ecosystem per the open_buildathon lens — whitespace from the gap map, sponsor-newest re-anchored on TabPFN-3.5/DevRelay, question-shift as cross-pollination. Receipts cite the research-brief winner-anatomy study + competitor reads, not crypto profiles.)

### F01 — Memorial oral-history keeper [lane: whitespace]
**Mechanism:** An open-weight model turns a person's recorded/typed memories into a durable, replayable remembrance surface (an ofrenda) — the AI structures, voices, and preserves the story; the product is the act of preservation, not chatting. Día-de-los-Muertos frame, memorial not spooky.
**Receipts:** Gap-map W1/MO2 (memorial density LOW, 2–3 teams); winner anatomy rewards emotional first-person narratability (munim study, research-brief Winning-Post Anatomy). Theme's memorial half is nearly empty.
**Adaptation axes:** input modality (typed vs spoken-via-ElevenLabs garnish); subject (a deceased person vs a retired project vs a shuttered community); output (a static ofrenda page vs an interactive remembrance vs a printable keepsake).
**Saturation:** warm — memorial is low-density but 2–3 teams are in it; differentiate on craft + a non-obvious subject.
**Loss-twin:** a generic "chat with your dead relative" bot — ghoulish, low-taste, and collapses into the chatbot herd; memorial must preserve, not impersonate.

### F02 — Tabular post-mortem oracle [lane: whitespace]
**Mechanism:** Feed a TABLE of historical signals (git/commit cadence, issue velocity, contributor churn, star decay) into an open-weight tabular foundation model to PREDICT/CLASSIFY an outcome (did/why this project die), then an open-weight LLM narrates the verdict. Tabular prediction IS the beating heart — not a bolt-on.
**Receipts:** Gap-map W2/MO1 (BLUE OCEAN, ~0 competitors; TabPFN under a spooky theme near-unseen); research-brief TabPFN section ("invent a concept where tabular prediction IS the ghost"); grand-slam tri-track (Overall+Render+TabPFN).
**Adaptation axes:** the table's domain (dead repos / churned SaaS users / abandoned issues / stale PRs); the predicted label (cause-of-death class vs survival-probability regression); narration voice (séance medium vs coroner vs eulogy).
**Saturation:** fresh — no competitor seen doing tabular prediction as the core under this theme.
**Loss-twin:** stapling TabPFN onto a text-only story app — sponsor engineers penalize the bolt-on (research-brief Kill List #4); the table must be load-bearing or TabPFN is dropped.

### F03 — TabPFN-3.5 prediction-agent [lane: sponsor-newest]
**Anchored on:** TabPFN-3.5 (shipped 2026, docs.priorlabs.ai/changelog/tabpfn-3.5 — the sponsor's newest primitive; `config.sponsor_vintage`). Prior Labs explicitly favors projects that use TabPFN inside a wider PREDICTION AGENT.
**Mechanism:** A thin agent loop wraps the TabPFN forward pass: assemble the feature table → single-pass classify/regress → open-weight LLM explains the prediction in plain language → surface a confidence + the top contributing features. One checkpoint, no training, demoable on the real model.
**Receipts:** sponsor-newest primitive <1 season old (L5 podium signal, research-brief Sponsor-vintage); Prior Labs' stated preference for prediction-agent framing (research-brief TabPFN section).
**Adaptation axes:** hosted `tabpfn-client` (API key, headless-clean) vs local open weights (license login); classification vs regression head; which 5–12 features become the table.
**Saturation:** fresh — a just-shipped tabular FM under a Halloween theme is essentially an empty lane.
**Loss-twin:** local-weights-in-headless-CI → blocked by the interactive license login (research-brief org-feedback DX seam); use the hosted client or accept locally first.

### F04 — Deprecation-graveyard resurrector [lane: cross-pollination]
**Mechanism:** Forced axis-shift (L9 — keep the "haunting" venue, shift the SUBJECT): from *a ghost haunts a chat* → *dead CODE haunts a living codebase*. An open-weight model mines a repo's git history for removed/deprecated functions and "resurrects" them — voicing what each dead function did, why it was killed, and what replaced it.
**Receipts:** gap-map W3/MO3 (functional dev-tool twist, unoccupied); question-shift class is the open_buildathon winner template (L9, EVENT-CLASS-LENSES open_buildathon). Spooky-but-useful writes up as a gripping dev build-story.
**Adaptation axes:** subject (deprecated functions / deleted files / closed-wontfix issues / dead feature flags); output (a narrated graveyard tour vs a changelog séance vs a "what would it say" monologue).
**Saturation:** fresh — the deprecation graveyard is unvoiced; adjacent to PhantomTerminal's code-séance but SUBJECT-shifted off it.
**Loss-twin:** drifting back into "a trapped spirit in your terminal" chat — that is the occupied haunted-terminal herd; the shift must stay on dead-code-as-subject.

### F05 — Changelog séance [lane: cross-pollination]
**Mechanism:** Forced axis-shift (L9 — shift the INTERFACE/ACTIVITY): from *generate a spooky story* → *reconstruct a true history as a ritual*. An open-weight model reads a real artifact's timeline (a repo's releases, a package's version history, an abandoned project's commits) and stages a "séance" that reconstructs what happened, as narrated history rather than fiction.
**Receipts:** gap-map W3; organizer-brief-inversion template (Pacifica: every winner question-shifted OFF the brief, EVENT-CLASS-LENSES open_buildathon L6/L9). Grounded in a REAL timeline → not a gimmick.
**Adaptation axes:** the artifact (repo / npm package / a person's life-events / a shuttered startup's blog); the ritual framing (séance / autopsy / eulogy / ofrenda); fiction-free history vs light dramatization.
**Saturation:** warm — adjacent to story generators; survives only if the history is REAL and verifiable (fiction-free), else it collapses into the ghost-story herd.
**Loss-twin:** a "spooky story from your commits" generator that fabricates events — fabricated history violates TASTE U7 (earned state) and lands in the red-ocean generator cluster.

### F06 — Open-weight local-first privacy narrative [lane: core]
**Mechanism:** The core AI is an open-weight model (Groq-hosted for the live demo; `docker run ollama` local mode shipped for the "your data never leaves your machine" story). The openness is load-bearing for the post's mandatory "Why open innovation matters" section — not a closed API behind a curtain.
**Receipts:** research-brief Tech Deep Dive (Groq free open-weight core = fastest Render-tiny path) + Broader Market Context (open-weight + local-first is the native fit for the open-innovation prompt); C-AI1 (AI is the product, fails if removed).
**Adaptation axes:** Groq-hosted vs Ollama-local vs both (demo hosted, ship local); which open-weight family (Llama 3.3 70B / Qwen3-32B / Gemma 3 / Phi-4-mini); whether a local mode is shipped as a differentiator.
**Saturation:** warm — every competitor uses an open-weight model; the openness is table stakes, so it must be made load-bearing in the WRITEUP, not just the stack.
**Loss-twin:** quietly using a closed model (GPT/Claude) as the engine → instant fail of the open-source-AI prompt (research-brief Kill List #4).

### F07 — Post-anatomy craft layer [lane: core]
**Mechanism:** Treat the DEV post as the product. Hard-enforce the five measured winner separators: cover image, ~1,500–2,500 words with template-matching headings, embedded demo video/GIF, ≥1 measured table, first-person number-in-title. Capture a DevRelay agent session during the build for the optional `{% agent_session %}` embed.
**Receipts:** research-brief Winning-Post Anatomy (munim study, N=323 winners vs 8,320 entries — writing quality ~40% of the rubric); PhantomTerminal (the leader) lacks BOTH a cover image and a demo video (gap-map W4 — the opening to beat it).
**Adaptation axes:** which number headlines the title; GIF vs Loom vs YouTube; how the table "measures something" (a prediction accuracy, a latency, a before/after); whether DevRelay is embedded.
**Saturation:** fresh-as-advantage — the craft layer is where the field under-invests; the leader skips two of the five separators.
**Loss-twin:** a great app with a thin, image-less, table-less writeup — it loses the heaviest-weighted axis regardless of code quality (research-brief: the post is the deliverable, not the afterthought).
