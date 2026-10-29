# FINAL VERDICT V1 — DEV Hacktoberfest Wk4 "Ghost in the Machine"

Winner (recommended, pending CP2): **Autopsy of a Dead Project**
Deliberation: 5 generators → 34 raw ideas → 4 finalists + 2 hybrids; 8 pool-gates; round_0 (4 independent scorers); independent cross-model (Sonnet) feasibility review = AGREE.

## 1. The winning argument
In a field that is a red ocean of ghost-story generators and haunted terminals, "Autopsy of a Dead Project" is the one concept where (a) the open-source AI is genuinely load-bearing, (b) three prize tracks are unlocked honestly, and (c) it writes up into a gripping first-person developer build-story — the single heaviest-judged axis on dev.to. It was unanimous #1 across all four scoring lenses (weighted 8.61) with the lowest divergence (0.80).

## 2. Mechanism (what it is)
Paste a public GitHub repo URL → the app fetches git/commit history and builds a feature **table** → **TabPFN** (open tabular foundation model) classifies the repo's death-mode (abandoned / pivoted / completed / burned-out) with calibrated confidence → a **Groq-hosted open-weight model** (Llama/Qwen) narrates a spooky "coroner's report / eulogy" → output is a shareable "death certificate" card.

## 3. Why it beat the pool (scored discrimination)
Full generation was 34 ideas, dominated by clone-tier ghost-story/haunted-terminal duplicates (calibration distribution below: min 2.4, median ~3.8 — the kill floor was genuinely exercised). Only 4 cleared the pool-gates to the finalist round. Autopsy topped all four independent scorers; the nearest rival (Ofrenda) carried a 2.40 divergence from dead-demo risk (local-Ollama > Render 512MB, value invisible on screen).

## 4. Capability-surface / deep-integration analysis
The open-weight-AI core is load-borne across two distinct surfaces, not one bolt-on:
- **Surface 1 — tabular classification (TabPFN):** the death-mode verdict IS TabPFN's output. Substitution test PASSES — remove TabPFN and the product degrades to a git-stats page. Deep-integration: load-bearing, sole-provider for the classification, live-provable in the demo (paste repo → verdict + confidence bars).
- **Surface 2 — open-weight narration (Groq):** the coroner/eulogy narrative is the theme layer and the post's emotional payload. Load-bearing for the "Ghost in the Machine" interpretation.
- **Caveat (Sonnet review):** TabPFN is a few-shot in-context learner — load-bearing CONTINGENT on a hardcoded ~50-repo labeled seed dataset shipped as a build artifact. This is the single lock-before-coding decision.

## 5. Theme interpretation
"Ghost in the Machine" read literally: the ghosts of dead code. Spooky (a coroner's séance over a commit DAG) AND functional (a real forensic verdict) AND optionally memorial (a eulogy ending — the Día-de-los-Muertos remembrance note). Question-shifted off the herd; no collision with competitor PhantomTerminal.

## 6. Risks (see WINNER-BRIEF Risk Register for the full 10)
Top three: (R1) TabPFN seed-dataset is the linchpin — lock first; (R2) Render must be a durable warm Starter tier (free spins down → dead judging demo); (R9) timebox the app so the docs-writer-grade post (heaviest axis) is not starved.

## 7. Partner-track mapping
Overall ($250) — the build-story. Best Use of Render ($200) — live durable deploy. Best Use of TabPFN ($200) — load-bearing classification core. Tri-track grand-slam, all earned.

## 8. Calibration distribution (full 34-idea pool, criteria-weighted)
Finalists: Autopsy 8.61, Ofrenda 7.35, Necromancer 7.18, Haunted Dependency 6.83. Mid: Deprecation Oracle 6.0, Last Words 5.6, Flatline Detector 5.2, Oracle of Dead Languages 4.6, Ghostwriter's Confession 4.3. Weak/killed/clone-tier: Séance (chat-dead) 3.8, assorted merged ghost-story clones 3.0–3.5, Séance-for-a-Stack-Trace 3.4 (haunted-terminal herd), Haunted Repo [F, killed] 3.0, Cold Case 2.9, Possessed 2.4. Top−median spread ≈ 4.8 — real discrimination, kill floor exercised.
