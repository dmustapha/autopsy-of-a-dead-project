# INVARIANTS — Autopsy of a Dead Project (build-agent law)

Laws the build MUST hold at every phase. A change that violates any of these is a regression,
not a feature — stop and fix before proceeding. (INV-1 / 2.3 P0.)

## I1 — Open-source AI is the core, always
The death-mode verdict MUST come from TabPFN (open weights) and narration MUST come from an
open-weight model (Groq-served Llama/Qwen or Ollama-local). A closed model MUST NOT enter the core
path. Violation = disqualification from the challenge premise.
- Check: `requirements.txt` + `app/classifier.py` + `app/narrator.py` contain no closed-model SDK in the verdict/narration path.

## I2 — TabPFN stays load-bearing (substitution test)
Removing TabPFN MUST degrade the product to a non-AI heuristic page — i.e. the verdict is TabPFN's
`predict_proba`, never a hand-rule dressed up as the model. The seed dataset is TabPFN's in-context
train data and MUST ship in-repo.
- Check: `classify()` calls the TabPFN client on the happy path; the only non-TabPFN path is the explicitly-labeled `engine="rules"` fallback.

## I3 — Honesty: never fake the model
Every verdict MUST carry an `engine` flag (`tabpfn` | `rules`) surfaced verbatim in the UI. A
fallback MUST be labeled as an estimate. The app MUST NOT present a heuristic verdict as the model's.
- Check: the card renders the engine badge; `_forensic_rules` sets `engine="rules"`.

## I4 — Narration is grounded (no hallucinated facts)
The narration MUST NOT contain any number/date/name absent from the evidence block. The model never
receives raw repo text (anti-injection). A failed grounding check retries once, then falls back to a
labeled templated eulogy.
- Check: `test_narration_grounding.py` green; the narrator passes only the evidence block.

## I5 — Deploy is durable + warm
The live deploy MUST be a durable Render tier (Starter, `numInstances=1`), NOT free. A judge landing
during the Nov-2 week MUST get a warm response (<2s), never a cold-start/spun-down link.
- Check: `render.yaml` plan=starter, numInstances=1, healthCheckPath=/healthz; warm-ping configured.

## I6 — No uncaught failure reaches the user
Every external dependency (GitHub, TabPFN, Groq) MUST have a defined degradation path. Bad input,
404, empty repo, rate limit, and model-down MUST all produce a friendly, in-voice state — never a 500.
- Check: the error-handling matrix (ARCHITECTURE §11) is implemented; manual edge-case pass.

## I7 — Scope is frozen to the one loop
The build MUST NOT add: accounts, persistence/DB, multi-repo compare, issue/PR analysis, server-side
image render, private repos, or background jobs (PRD §34). Each costs time the post needs.
- Check: no new subsystem appears that isn't in ARCHITECTURE §3.

## I8 — The post is protected (heaviest axis)
App work MUST NOT consume the reserved post-writing block. If the day compresses, app polish is cut,
never the write-up. Observation capture (`data/NOTES.md`) happens during build, not retrofitted.
- Check: day-of timeline hard stops honored; NOTES.md grows during B0–B6.

## I9 — Originality: brand-new, in-window
All code MUST be written in-window; no pre-existing project reused (standalone-fresh, CP1). The repo
is created fresh and public.
- Check: git history starts in-window; no imported prior project.

## I10 — Secrets never leak
API keys live only in env (Render dashboard / local `.env`), never in the repo, client HTML, or logs.
- Check: `.env` git-ignored; `.env.example` empty; request log carries no secrets/PII/repo-text.

## I11 — Response contract is stable
The `AutopsyResult` shape (PRD §23) is the contract the frontend binds to. A model swap (`LLM_MODEL`)
or engine fallback MUST NOT change the response shape.
- Check: `schemas.py` unchanged across model swaps; frontend binds to the documented fields.

---

## Survivors from the A-G4 critical review (build MUST honor — distinct-model Sonnet review, 2026-10-29)
Two ARCHITECTURE BLOCKERS the review found were FIXED in the source of truth during forge (TabPFN token
now set via `set_access_token`; the `_forensic_rules` else-branch now calls `_nearest_mode`, not a
hard-coded `"completed"`). The findings below SURVIVED — they are real residual risks the build phase must
carry. Each is a falsifiable statement recorded verbatim so the build/verify loop checks it (see
`.forge-critical-review.json` for predicates).

PRD (feature-separability survivors):
- bus_factor alone cannot separate burned_out from a healthy 2-3 person repo — rely on the joint
  signal (bus_factor + commit_cadence_decay), and never claim more certainty than the TabPFN posterior.
- velocity_ratio ~= 0 does not separate abandoned from pivoted; lifespan_days must — ensure the seed set
  has sharp short-life pivoted exemplars so TabPFN can lean on lifespan_days for that pair.
- commit_cadence_decay is biased when COMMIT_WINDOW truncates a long repo's early history — treat the
  slope as a recent-tail signal for windowed repos; document the window in LIMITATIONS.

ARCHITECTURE (code/design survivors):
- healthz tabpfn_reachable is a token-presence proxy, not a real TabPFN probe — a green `/healthz` does
  NOT prove the model path; the real proof is a live `/autopsy` returning `engine=tabpfn` (verify/livetest).
- grounding _numbers() is a 2+-digit substring match, not semantic grounding — it is a floor not a
  ceiling; the grounding test must keep the fabricated-number case, and narration stays short to limit risk.
- Features has no total_commits/is_archived, so two section-16 rules cannot fire — either carry those two
  context fields into the fallback or drop those rule rows; do not ship rules that silently never execute.
- TabPFN is re-fit every request (only the seed CSV is cached) — acceptable at ~50 rows, but the response
  cache + 3 pre-warmed examples are what keep the demo instant; never remove the cache.

PLAN (execution survivors):
- seed_list.txt placeholders must be filled on build day before B0 can run — the angle-bracket slots are
  a human-input precondition, not optional; B0 cannot reach separability without them.
- PRE-BUILD token check must source .env (or export) before asserting the key, else it passes vacuously —
  the credential gate only counts if it reads the real value, not a stale shell env.

---

## NON-NEGOTIABLES
The build MUST NOT ship a violation of any row below. Each names the judge's attack it defends against.

1. The death-mode verdict on the happy path is produced by TabPFN (`engine="tabpfn"`), never a heuristic dressed as the model. Judge-attack: "You call this a TabPFN project but the badge says `rules` — the model never ran." Defense: `set_access_token` before `fit`; the engine badge is rendered from the real engine field (I2, I3).
2. Every fallback is labeled as an estimate in the UI and the response. Judge-attack: "Your 'AI verdict' is actually an if/else — and you hid it." Defense: `engine="rules"` surfaced verbatim on the card (I3).
3. The narration contains no number/date absent from the evidence block. Judge-attack: "The eulogy invented stats — the AI is hallucinating." Defense: grounding check + retry + templated fallback (I4).
4. The core AI is open-source only (TabPFN open weights + open-weight LLM); no closed model in the verdict/narration path. Judge-attack: "This is an open-source-AI challenge and your core calls a closed API." Defense: requirements + narrator base_url; Ollama-local mode proves it (I1).
5. The live deploy is a durable, warm Render tier. Judge-attack: "I clicked your link during judging and got a dead/cold page." Defense: Starter + numInstances=1 + warm-ping (I5).
6. No input produces an uncaught 500. Judge-attack: "I pasted a weird URL and your app crashed." Defense: the Flow A–H error matrix + the catch-all handler (I6).
7. All code is brand-new, written in-window. Judge-attack: "This repo predates the challenge — it's not original." Defense: fresh public repo, in-window git history (I9).
8. The post ships with a cover image, embedded demo video, ≥1 table, first-person number-in-title, both tags. Judge-attack: "Great app, but the post is thin / missing the basics." Defense: the SUBMISSION_STATUS craft checklist, gated before publish (I8).

### MUST NOT CLAIM
- MUST NOT claim the death-mode is ground truth — it is an inference ("likely cause of death").
- MUST NOT claim a feature (e.g. issue-tracker death) that was scope-cut.
- MUST NOT present a `rules`-engine verdict as a TabPFN verdict.

## ESCALATE (escalate, don't fabricate)
If a required input or fact is missing at build time, STOP and escalate in one sentence — never
invent it. Specifically: a missing `TABPFN_TOKEN`/`GROQ_API_KEY`/Render account is a surfaced
blocker, not a reason to mock the model or fake a deploy. A seed set that won't separate is escalated
(ship rules-primary + log it in DECISIONS.md), never silently relabeled to force separation.

## SOURCE LOCK (verified source pins)
- `tabpfn-client==0.1.6` — `TabPFNClassifier.fit/predict_proba`, `set_access_token` (Prior Labs docs).
- `openai==1.54.4` against `https://api.groq.com/openai/v1`, model `llama-3.3-70b-versatile` (Groq docs).
- GitHub REST `/repos`, `/commits`, `/contributors` (GitHub docs; unauth 60/hr, PAT 5000/hr).
- Render Starter blueprint: `plan`, `numInstances`, `healthCheckPath`, `envVars sync:false` (Render docs).
Headline invariant enforcement: STRUCTURAL — the `engine` flag is part of the `Verdict` type, so a
verdict cannot exist without declaring its engine; a fabricated-as-tabpfn rules verdict is
unrepresentable, not merely checked.
