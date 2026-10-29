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

### hackathon-warroom (2026-10-29, SPRINT)

#### Done
Generated + deliberated the concept pool through 8 pool-gates + round_0 independent scoring (4 scorers: SCRIBE/MEDIUM/ORACLE/GRAVEDIGGER). Artifacts: warroom/{WARROOM-V1-BRIEF, concerns-snapshot-V1, deliberation-transcript, gap-map, primitives-sheet, round-scorecard}.md + .warroom-state.json. (Subagent socket-dropped at finalization; verdict re-read from disk — decisive, so confirmatory crowning rounds not re-run.)

#### Additions
Criteria-weighted scoring reflects the dev.to reality: Writing×0.40 + Theme×0.20 + Creativity×0.18 + Technical×0.15 + Partner×0.07 (writing is the heaviest axis).

#### Deviations
Finalized at scored-pool (round_0) rather than running fact_check→challenge→crowning: subagent died post-scoring and the #1 is UNANIMOUS (top on all 4 lenses, divergence 0.80), so later rounds would be confirmatory. selected_idea left null for CP2 (conductor human checkpoint).

#### Verified Facts
- Unanimous #1: **Autopsy of a Dead Project** — weighted 8.61, Gate-3 25/25. Substitution test PASSES (remove TabPFN → degrades to a git-stats page → TabPFN is load-bearing core, not a bolt-on). Zero dead-demo risk (git API + 1 TabPFN call + 1 Groq call; Render stays tiny).
- #2 Ofrenda/Voicekeeper 7.35 — HIGH divergence 2.40 (MEDIUM #1 "soul" vs GRAVEDIGGER last "local-Ollama>512MB dead-demo, value invisible on screen").
- #3 The Necromancer 7.18; #4 Haunted Dependency 6.83.
- Killed: F Haunted Repo (herd collision, un-fixable); H2 Autopsy+Resurrect (two-product scope for a 1-day solo build).

#### Assumptions
Autopsy's "death-mode" labels (abandoned/pivoted/completed/burned-out) are derivable from git-history features (commit cadence decay, bus-factor, issue/PR half-life) — to be validated at build when the feature table is built.

#### Blockers for Downstream
TabPFN access path (hosted tabpfn-client key vs local weights w/ browser license-accept) must be resolved at build. Groq key still needed.

#### Key Decisions
Recommend Autopsy of a Dead Project as the tri-track grand-slam (Overall + Render + TabPFN). Open-weight core = Groq-hosted Llama/Qwen for the coroner/eulogy narration; TabPFN = the forensic death-mode classifier. CP2 pending Dami's pick.

#### For Next Skill
If Autopsy confirmed at CP2 → forge scopes: (1) paste a public GitHub repo URL → fetch git/commit history, (2) build a feature table, (3) TabPFN classifies death-mode + confidence, (4) Groq open-weight model narrates a "coroner's report / eulogy" that types out, (5) shareable death-certificate card (cover-image + demo-video material). Keep it ONE page, one paste-field, live on Render Starter. Post hook/title candidate: "I performed an autopsy on my dead side-projects. An open-weight AI told me how they died."

### hackathon-forge (2026-10-29, SPRINT)

#### Done
Produced + brought to the forge STANDARD the planning suite for CP2-winner "Autopsy of a Dead Project": PRD.md (801), ARCHITECTURE.md (1512), PLAN.md (1018 — expanded from 487), INVARIANTS.md (I1-I11 + critical-review survivors), DECISIONS.md, SECURITY.md, LIMITATIONS.md, SUBMISSION_STATUS.md, .input-manifest.json. Ran the forge OWN completion gates to real GREEN: forge_doc_floor_gap CLEAN (800/1500/1000 all met), forge-critical-review exit OK (distinct-model, findings-not-scores, survivors→INVARIANTS, no hype-lint). Run INLINE (Dami ruling after 2 subagent failures).

#### Additions
- PLAN expanded +531 lines to clear the ≥1000 floor with REAL buildable depth (not padding): PART IV file-by-file transcription order + per-file landing checks; PART V per-phase verification protocol with exact expected transcripts + decision trees; PART VI deploy/post walkthroughs; PART VII a complete worked end-to-end trace (one dead repo, real intermediate values, incl. a "wrong-trace" catcher list); PART VIII env/troubleshooting/CI runbook + commit-ledger + decision-provenance.
- A-G4 critical review RAN: three fresh-context DISTINCT-model (claude-sonnet) per-doc reviews (PRD/ARCH/PLAN), recorded in .forge-critical-review.json with falsifiable predicates; survivors folded verbatim into INVARIANTS.md.
Locked stack unchanged: Python FastAPI single server-rendered page + TabPFN (tabpfn-client) + Groq open-weight LLM + GitHub REST, on Render Starter. Linchpin = a shipped ~50-repo labeled seed dataset.

#### Deviations
Forge ran IN-CONTEXT, not as the SPRINT profile-gated fresh subagent (fresh-dispatch-boundary deviation) — earlier subagent dispatch socket-dropped/timed out; Dami ruled inline for reliability. The per-doc critical review, however, WAS run as genuine distinct-model fresh-context subagents (producer opus → reviewers sonnet), satisfying the D-1 distinct-model gate honestly. Scope deliberately sized to a 1-day build.

#### Verified Facts
- Gate verdicts are REAL, read off disk: PRD 801 / ARCH 1512 / PLAN 1018 lines (all ≥ floor); forge-critical-review.sh exit → OK.
- Stack is Render-tiny: one Python process, no JS bundler, no git clone (GitHub REST only), no local model weights (both AI models hosted).
- TabPFN is load-bearing: in-context classify over seed_repos.csv; substitution test → remove it leaves a heuristic rules page. [ARCHITECTURE.md]
- Two distinct open-source AI roles: TabPFN classifies death-mode; Groq open-weight LLM narrates.
- Two ARCHITECTURE BLOCKERS found by the review were FIXED in the source of truth: (1) TabPFN was never authenticated — II.6 now calls set_access_token(TABPFN_TOKEN) before fit() (else labeled rules, honest) — this is what makes I2 load-bearing real not aspirational; (2) _forensic_rules else-branch now calls _nearest_mode (II.26), not a dead hardcoded "completed".

#### Assumptions
Death-mode ∈ {abandoned,pivoted,completed,burned-out,alive} is separable from ~6 commit/contributor features — VALIDATED at B0 exit before UI wiring (R5). Exact Wk4 theme prompt still secret until live page (DS-1).

#### Blockers for Downstream
- Required inputs still unresolved: GROQ_API_KEY (blocks B3+deploy), TABPFN_TOKEN (blocks B2+deploy), RENDER_ACCOUNT (blocks B5). GITHUB_TOKEN optional. DEVTO login deferred to package.
- Nine SURVIVING critical-review findings the build MUST carry (in INVARIANTS.md "Survivors" + .forge-critical-review.json predicates): bus_factor alone can't separate burned_out; velocity_ratio~=0 can't separate abandoned/pivoted (lean on lifespan_days); commit_cadence_decay is biased by COMMIT_WINDOW on long repos; healthz tabpfn_reachable is a token-presence proxy not a probe (prove via live /autopsy engine=tabpfn); grounding _numbers() is substring-match not semantic; Features lacks total_commits/is_archived so two §16 rules can't fire; TabPFN re-fits per request (keep the cache); seed_list.txt placeholders are a build-day precondition; PRE-BUILD token check must source .env.

#### Key Decisions
See DECISIONS.md D1-D8. Headline: FastAPI single page (D1), hosted TabPFN (D2), Groq open-weight narration (D3), seed-dataset-first (D4), Render Starter warm (D6), scope cuts (D7), transparent fallback never-fake (D8). Forge-run addendum: fixed the two code BLOCKERS in ARCHITECTURE (token-set + nearest-mode) rather than defer them, because shipping a known-dead TabPFN path would void the load-bearing premise.

#### For Next Skill
critique: grade this STAGE-0/1 scope against the §12 parts + N2 floor — is the scope genuinely 1-day-buildable, is TabPFN honestly load-bearing, does the plan protect the heaviest axis (the post)? Note the 9 critical-review survivors are already recorded — critique should pressure-test, not re-discover them. Then build: start at B0 (seed dataset) — do NOT skip it; it is the linchpin; fill seed_list.txt placeholders FIRST. Read the LIVE challenge page first (DS-1).
