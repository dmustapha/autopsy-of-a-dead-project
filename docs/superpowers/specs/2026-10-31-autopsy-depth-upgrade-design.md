# Autopsy of a Dead Project — Depth Upgrade (design)

Written 2026-10-31. Owner: Dami. Builder: this is a project-sized design; a plan follows.
Hard floor: submission in by **2026-11-01 06:59 UTC** (= 07:59 WAT). Direction: **full depth, time no object**, but if the floor is reached, ship the best honest state.

## Intent & the why
The live app classifies a repo's "death mode" from **10 numeric git/metadata features** and narrates a eulogy. Two problems a judge will see:
1. **Thin classification.** TabPFN (the Prior Labs $200 partner model) scores **LOO 36.2%, *below* a trivial 1-NN at 42.6%** on the 47-row seed. The sponsor model loses to a naive baseline — a visible liability for the "Best Use of TabPFN" category, which is judged on the model *earning its place*.
2. **No understanding of what the project *is*.** The content layer (the "evidence adjudicator" that reads README + commit messages) exists in code but is disabled live (`EXTRACTOR_LLM_DISABLE=1`). So nothing reads the project's purpose; the eulogy is grounded only in numbers.

**North Star (derived from the judging rubric — writing > theme > creativity > technical > partner-tech):** a judge opening the live autopsy must see **both open-weight models doing real, specific, defensible work on *this* project** — 0G Compute actually *reads* what the project was and quotes its own death-signals; TabPFN's verdict is *earned* because it now classifies **content-enriched features** and **beats the naive baseline**. A memorial should read the life, not just the death stats. The dev.to post then tells exactly that story.

## Goals
- G1. **TabPFN earns its keep:** on content-enriched features, TabPFN LOO > 1-NN LOO on the *same* features (the model beats the naive baseline). Measured, honest, reported.
- G2. **The app understands the project:** the adjudicator is live and extracts (a) a one-line factual "what this project was" summary, (b) ≥1 verbatim death-signal quote from the repo's own README/commits, (c) a content-based mode hint + confidence — with the honesty guard intact (no fabricated signals; offline/parse-fail → labeled empty, never invented).
- G3. **The certificate SHOWS the understanding:** "what this project was", the quoted evidence, a content-engine badge (0G read the content), and the existing cohort line ("died like N of 5 similar repos") are visible on the card.
- G4. **Honest end-to-end:** honesty-invariant tests stay green; the POST's numbers are re-derived from the new system; live deploy updated + 3 examples re-cached + livetest re-passes.

## Non-goals / anti-goals
- NOT changing the card's visual design / aesthetic (owner-frozen) beyond adding the new content fields in the existing style.
- NOT changing the stack choices (local TabPFN + 0G Compute narration stay).
- **Anti-goal: faking the number.** If, after honest feature engineering + a bigger seed, TabPFN still does not beat 1-NN, we report that truthfully and reframe TabPFN's value (calibrated 5-class posterior + content tie-break), never fabricate a win.
- Anti-goal: letting the LLM arbitrarily override TabPFN (breaks the "TabPFN is load-bearing" claim). The adjudicator *enriches and tie-breaks within principled bounds*; TabPFN stays primary.
- Anti-goal: breaking the live deploy or touching co-resident prod LEASH.

## Constraints
- Tiny 2-core Oracle micro; each LLM round-trip adds latency. With the adjudicator on, a fresh autopsy makes **2** 0G calls (adjudicate + narrate). Cached examples hide this for the demo; disclose the real fresh/cold latency honestly in the POST.
- GitHub REST only; the enrichment features must come from the **already-fetched** repo meta + readme + a topics field (no heavy new API cost).
- Deploy = `/home/ubuntu/autopsy` on the box; redeploy must not disturb prod LEASH; after redeploy, re-warm the 3 examples.
- Must stay within unauthenticated/token'd GitHub rate limits when rebuilding the seed.

## The four levers (how far each goes)

### Lever 2 — Enrich the classifier features (the core of "not thin")
Add honest, cheap, separating features to `FEATURE_ORDER`, derived from data we already fetch:
- `log_stars`, `log_forks`, `log_watchers` (popularity, log-scaled)
- `topics_count` (fetch the `topics` array — curation signal)
- `readme_size` (len of fetched README — documentation effort)
- `description_present` (0/1), `license_present` (0/1), `has_wiki`/`has_pages` (0/1)
- `is_fork` (0/1)
- `primary_language_freq` (frequency-encode language from the seed, not one-hot — keeps the vector small)
- keep the existing 10.
Builder picks the final set empirically (keep those that improve LOO; drop noise). Surface the needed raw fields in `github.py` meta (forks_count, watchers_count, topics, size, has_wiki, has_pages, fork, license, description).

### Lever 3 — Grow + rebalance the seed (so the enriched features have signal)
- Expand the seed from **47 → ~100+** labeled repos, balanced across the 5 modes (abandoned/burned_out/completed/pivoted/alive).
- Build `scripts/build_seed.py` enrichment so every seed row carries the NEW columns (re-fetch features for each repo through the real extractor — same code path as prod, so train==serve).
- **Labeling** is the risk. Use defensible, documented criteria (archived+released→completed; long-dead+no releases→abandoned; single-maintainer cadence-collapse→burned_out; short-life pivot signals→pivoted; actively-maintained→alive) + a human spot-check. Labels are the builder's documented calls; a labeling rubric lives next to the seed.

### Lever 1 — Evidence adjudicator live + widened (0G reads content)
- Re-enable (`EXTRACTOR_LLM_DISABLE=0`), bump the prompt to ALSO return `project_summary` (one factual line: what the project was/did, strictly from README/description — no invention).
- Role: feeds the eulogy (evidence_quote already does), surfaces summary + signals on the cert, and keeps the principled tie-break in `_adjudicate` (high-confidence, top-2, within tie-zone). TabPFN stays primary; content hint can also become a *feature* fed to the classifier if it improves LOO (builder's empirical call, honesty-guarded).
- Honesty guard unchanged: offline/parse-fail → labeled-empty, never fabricated.

### Lever 4 — Cert shows the understanding
- Add to the card, in the existing amber style: a **"What this project was"** line (project_summary), the **quoted death-signal(s)** (evidence), a **content-read badge** ("evidence read by deepseek-v4.1-flash · 0G Compute"), and keep the cohort line. Degrade gracefully when content is empty (honest).

## Order of work
1. **Features + seed (Levers 2+3)** — surface raw fields → enriched extractor → rebuild+expand+relabel seed with new columns → validate **TabPFN LOO > 1-NN LOO**. This is the load-bearing proof.
2. **Adjudicator (Lever 1)** — re-enable + `project_summary` + wire to narration/cert; optional content-feature if it helps LOO.
3. **Cert UI (Lever 4)** — surface summary + evidence + badge.
4. **Redeploy** new code + flip `EXTRACTOR_LLM_DISABLE=0` on the box + **re-cache 3 examples** + **re-run livetest** (recompute all numbers).
5. Resume pipeline: demo-video → dev.to post (numbers re-derived) → verify. Publish Dami-gated.

## Definition of done
- [ ] TabPFN LOO > 1-NN LOO on the enriched feature set, **measured** (script-reproducible), reported honestly (or, if it still loses, the anti-goal clause: truthful reframe).
- [ ] Seed ≥ ~100 rows, balanced, with a documented labeling rubric; train==serve (seed built via the prod extractor).
- [ ] Adjudicator live: for the 3 examples, the cert shows a real "what this project was" + ≥1 verbatim death-signal from that repo's own content.
- [ ] Honesty-invariant tests green (fabrication rejected; offline → labeled-empty); full offline suite green.
- [ ] Live deploy updated, 3 examples re-cached (<2s), livetest re-passes with the new numbers.
- [ ] POST + demo reflect the new, honest numbers (no stale 36.2%/1-NN claims).

## Risks
- Seed labeling subjectivity → documented rubric + spot-check; labels are falsifiable (the rubric predicts them).
- TabPFN may still not beat 1-NN even enriched → anti-goal clause (honest reframe, never fake).
- Box latency with 2 LLM calls → caching hides it for demo; POST discloses real numbers; consider running adjudicate concurrently with feature-build.
- Redeploy risk to co-resident prod LEASH → deploy only within /home/ubuntu/autopsy; never touch leash blocks; re-check api.leash.ink/healthz==200 after.
- Hard floor 06:59 UTC → if reached mid-build, ship the best honest state and note what's partial.

## Builder-check resolutions (my calls — verified against code/box)
- **Feature propagation (train==serve):** the new features go into `schemas.Features` + `FEATURE_ORDER` + the seed CSV columns. The 1-NN fallback (`_nearest_mode`) and TabPFN both read `FEATURE_ORDER`, so they pick the new features up automatically. Existing test fixtures + the seed CSV get regenerated — expected work, not a blocker.
- **0G model is already wired:** the box `.env` already has `LLM_BASE_URL=https://router-api.0g.ai/v1`, `LLM_MODEL=deepseek-v4.1-flash`, `LLM_API_KEY=…`, `LLM_MAX_TOKENS=2000`. So re-enabling `EXTRACTOR_LLM_DISABLE=0` makes the adjudicator run on **0G deepseek** (the `gemma2:2b` in code is only a default). The cert badge derives from `LLM_MODEL`, so it reads "deepseek-v4.1-flash · 0G Compute" correctly. NOTE: `extractor.py` hardcodes `max_tokens=400`; deepseek is a reasoning model that returned empty content at low budgets — the builder bumps the adjudicator's token budget (align to `LLM_MAX_TOKENS`) and validates the `project_summary` prompt against deepseek with a real measured probe (not guessed).
- **Seed scaffolding exists:** `scripts/build_seed.py` + `scripts/backfill_seed_tier_b.py` + `scripts/seed_list.txt` already exist (the 47-row seed was built with them). The plan EXTENDS them — add the new columns + more labeled repos — rather than writing a fetcher from scratch.
- **Cache is in-memory TTL (1h):** `TTLCache` (app/cache.py). A redeploy restarts the service → cache cleared automatically → re-warm repopulates with the new `project_summary`/fields. No persistent clear needed. (This 1h TTL is also why the 3 examples cooled during the long gate work.) Adding `project_summary` to `AutopsyResult` is additive/backward-safe.

## Left to the builder
Final feature set (empirical), exact seed repos + labels (per the rubric), prompt wording for `project_summary` (measured, not guessed — honesty), the content-feature-or-not decision (keep only if it improves LOO), and the exact cert layout of the new fields within the frozen style.
