# Hacktoberfest Wk4 "Ghost in the Machine" — Ideas
## Selected: [AWAITING WARROOM DELIBERATION]

## Pool Stats
- Raw generated: 34 (G1:6 G2:6 G3:8 G4:6 G5:8)
- Hybrids: 2 (H1 Autopsy×Eulogy, H2 Autopsy×Resurrect) | Late entrants: [SEED] 0, [HISTORY] 0
- Killed — kill list/saturated: 1 (F Haunted Repo) | concerns: 0 extra | demo test: 1 (H2 scope) | score floor: 0 | anti-attractor: 0
- Cluster-duplicates merged (not killed): ~27 (11→A, 6→B, 4→C, 7→E, folded)
- Brief levers: ~12/12 mapped | Regeneration rounds: 0 | Rescued: 0
- Presented: 4
- injection: lint pass, quota 2/1/2/7

## Presented Pool

### #1: Autopsy of a Dead Project — "I ran an autopsy on my dead side-projects; a tabular AI told me what killed each one"
**Score:** 25/25 — Ship [5] | Demo [5] | Sponsor [5] | Novel [5] | Memorable [5]
**Mechanism:** Paste any GitHub repo URL. It pulls the REAL git history (commit cadence, time-between-commits, branch-death, issue-close rate, contributor churn, final-month diff-churn) into a TABLE, feeds that table to TabPFN-3.5 which zero-shot CLASSIFIES the death-mode (burnout / scope-creep / dependency-rot / lost-interest / blocked) with a calibrated confidence + feature attributions, then an open-weight LLM (Qwen/Llama via Groq) narrates the autopsy as a coroner's report / séance — ending (warm-eulogy framing from hybrid H1) with what the project gave you.
**Why this ecosystem (U6):** TabPFN is the beating heart — death-MODE classification from a small per-repo signal table is a zero-shot tabular-FM task no LLM can do honestly (an LLM would hallucinate a cause) and no solo dev can train in a day. Remove TabPFN → a git-stats page. Grand-slam tri-track: Overall + Render + TabPFN (blue-ocean sponsor field).
**3-min demo shape:** paste repo URL → real commit sparkline renders → TabPFN returns death-mode + confidence bars + top-3 killing features (red) → LLM coroner's report types out ("time of death 2024-03; cause: dependency-rot, 81%") → toe-tagged autopsy card export. WOW (20-sec GIF): the confidence bar snapping to a verdict + the typed coroner's line. TABLE: TabPFN death-mode accuracy/calibration vs an LLM-guess baseline on a held-out set. COVER: a graveyard of repo-tombstones under fog.
**TASTE lines satisfied:** U1 (real git data), U2 (paste any repo, see it), U3 (coroner séance hook), U4 (not the ghost-story herd), U6 (TabPFN load-bearing), U7 (earned — real verdict), C-AI1 (remove AI = no diagnosis).
**Primitive(s) adapted:** F02 tabular post-mortem oracle + F03 TabPFN-3.5 prediction-agent + MO1, remixed so the TABLE is git-history features and the narration is forensic-with-a-eulogy (H1 warmth).
**Law-check:** AI load-bearing (TabPFN classifies + LLM narrates); question-shifted off the herd (git-history → tabular FM death-mode, blue-ocean); writes up as the proven confessional-with-data winning structure; solo-shippable live on Render in a day (git API + one TabPFN call + one Groq call).
**Origin:** merged cluster A (G1/G2/G3/G4/G5 all converged) × H1 hybrid (warm eulogy).

### #2: Ofrenda / Voicekeeper — a local-first Día-de-los-Muertos memorial that preserves a real person's stories
**Score:** 20/25 — Ship [4] | Demo [4] | Sponsor [3] | Novel [4] | Memorable [5]
**Mechanism:** Record/paste a relative or mentor's stories; an open-weight model (local Ollama for privacy, or Groq) STRUCTURES the raw recollections — extracting people, places, dates, recurring phrases — into a searchable, question-answerable memorial that answers ONLY from their real words with citations, refusing to fabricate ("they never spoke of this"). Renders a Día-de-los-Muertos ofrenda/altar page + exportable keepsake.
**Why this ecosystem (U6):** the open-weight model is the preservation engine (extraction + grounded Q&A), and local-first is load-bearing BOTH technically and thematically — you do not send a dead loved one's words to a closed corporate API. Grounded-only answering (anti-hallucination) is the trust feature.
**3-min demo shape:** paste a transcript → timeline/people/places extracted into an altar card → ask a question → grounded answer with quoted source lines, or honest "they never spoke of this" → export keepsake. WOW: the honest refusal (shows it's real, not a hallucinating chatbot). COVER: a glowing marigold altar. TABLE: grounded-answer rate / fabrication rate (measured anti-hallucination).
**TASTE lines satisfied:** U1 (answers only from real words), U2 (paste + ask), U3 (memorial over gimmick), U6 (local open-weight core), U7, C-AI1.
**Primitive(s) adapted:** F01 memorial oral-history keeper + F06 open-weight local-first privacy narrative + MO2.
**Law-check:** AI load-bearing (extraction + grounded Q&A); question-shifted into the LOW-density memorial lane (W1); strongest emotional narratability (~40% writing weight); solo-shippable (Ollama/Groq + small RAG + Next.js). TabPFN not natural → skip it (do not bolt on).
**Origin:** merged cluster B (G1 Voicekeeper, G3 Last-Words, G5 Séance/Ofrenda, G4 Memorial-Loom, G2 Día-de-los-Commits).

### #3: The Necromancer — resurrect a dead/deprecated API into a working, runnable compat shim
**Score:** 19/25 — Ship [4] | Demo [4] | Sponsor [3] | Novel [4] | Memorable [4]
**Mechanism:** Paste code calling a dead/deprecated function (e.g. `request()`, a removed library method, Python-2 idioms). An open-weight code model (Qwen2.5-Coder via Groq) reads the old + new signatures and the real deprecation record, GENERATES a working compatibility shim that revives the dead call on a modern runtime, and runs it live, plus a one-paragraph "obituary" of why it died.
**Why this ecosystem (U6):** signature-diff → adapter-code is a precise code-gen task where open-weight coder models shine, and the output is instantly verifiable (it runs or it doesn't — earned demo, U7). Remove the model → nothing to resurrect.
**3-min demo shape:** paste deprecated-call code → "raising the dead…" → shim appears → RUNS live and executes → obituary line. WOW: the resurrected call actually executing. COVER: a flatlining monitor spiking back. TABLE: shims generated / runnable-on-first-try rate across N real deprecations.
**TASTE lines satisfied:** U1, U2, U3, U5 (builder-fast utility), U6, U7 (it actually runs), C-AI1.
**Primitive(s) adapted:** F04 deprecation-graveyard resurrector + F06, remixed to a REAL working-code generator (not a story).
**Law-check:** AI load-bearing; question-shifted (useful resurrection vs fictional haunting); narratable ("I built a necromancer for dead APIs"); solo-shippable (one Groq code route + a sandbox runner). Risk: the sandbox runner is the one build-risk; TabPFN not natural → optional.
**Origin:** merged cluster C (G1 Deprecation-Séance, G3 Necromancer, G2/G3 Deprecation-Oracle).

### #4: Haunted Dependency — which packages you ship are already dead and don't know it
**Score:** 17/25 — Ship [4] | Demo [3] | Sponsor [4] | Novel [3] | Memorable [3]
**Mechanism:** Parse `package.json`/`requirements.txt`, pull each dependency's real registry signal (last-publish date, open-issue ratio, maintainer count, archived flag) into a TABLE; TabPFN-3.5 zero-shot scores each dep P(abandoned) → surfaces the "zombie dependencies" you're shipping that are already dead upstream; open-weight LLM writes the risk summary.
**Why this ecosystem (U6):** TabPFN over a per-dependency feature table is a genuine zero-shot tabular scoring; load-bearing. Grand-slam eligible (Overall+Render+TabPFN).
**3-min demo shape:** upload package.json → dep table with registry signals → TabPFN flags zombies → haunted-package cards with abandonment probability + last-heartbeat date. COVER: node_modules as a graveyard. TABLE: predicted-abandoned vs actually-archived accuracy.
**TASTE lines satisfied:** U1, U2, U3, U5, U6, U7.
**Primitive(s) adapted:** F02 + F03 + F04, remixed onto the dependency graph.
**Law-check:** AI load-bearing; question-shifted (supply-chain forensics vs fiction); narratable ("the zombies in my node_modules"); solo-shippable. STRIKE: dep-health scanners (Snyk/socket.dev) exist — the "ghost" framing is a skin over a known category (weaker C3 uniqueness + theme-is-skin).
**Origin:** merged cluster E (G3 Haunted-Dependency + G2 variants).

## Brief-Utilization Map
| Lever | Idea(s) |
|-------|---------|
| open-weight core | A, B, C, E |
| TabPFN-3.5 (sponsor-newest) | A, E |
| Render durable | A, B, C, E |
| DevRelay | capture during build (all) |
| memorial theme | B, (A warm-eulogy) |
| spooky theme | A, C, E |
| question-shift off herd | A, C (F killed for failing it) |
| cover-image + demo-video craft | A, B, C, E |
| writing-narratability | A, B |
| MO1 why-did-my-project-die | A |
| MO2 preserve-a-voice | B |
| MO3 deprecated-function | C |

## Killed Ideas
| Idea | Origin | Gate | Cause |
|------|--------|------|-------|
| F Haunted Repo (ghost of previous dev over your legacy code) | G5 + G3 stack-trace | Gate 1/1b | saturated + critical_concern_C3 (haunted-terminal herd collision — the exact shape the brief says to question-shift OFF) |
| H2 Autopsy + Resurrect (two products) | hybrid A×C | Gate 2 | demo_test (two-product scope, not 1-day/3-min demoable) |
| ~27 cluster-duplicates | G1-G5 | synthesis merge | merged into A/B/C/E (not killed — deduped) |

### #5: Haunted Repo — a terminal that "haunts" you with the ghosts of your abandoned repos [KILLED]
Generated, then KILLED at pool_gates (cause: saturated_C3_herd_collision — collides with the 9+ haunted-terminal/ghost-story clones and competitor PhantomTerminal; its single failure is an un-fixable identity problem).

### #6: Autopsy + Resurrect — autopsy a dead project AND auto-generate a revival PR [KILLED]
Generated as an Autopsy hybrid, then KILLED at pool_gates (cause: demo_test_scope — autopsy + resurrection = two full products; neither lands cleanly in a 3-min demo for a 1-day solo build).
