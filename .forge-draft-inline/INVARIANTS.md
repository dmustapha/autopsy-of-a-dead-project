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
