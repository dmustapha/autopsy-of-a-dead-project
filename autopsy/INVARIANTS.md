# INVARIANTS — Build-Agent Law (Autopsy of a Dead Project)
> The build agent reads this as non-negotiable law. Violating any NON-NEGOTIABLE fails the hackathon gate.

## NON-NEGOTIABLES
1. **TabPFN is the SOLE source of the death-mode verdict.** — Test: `grep -rn` the classify path shows the verdict comes from `TabPFNClassifier.predict_proba`; no if/else rules engine produces a death_mode. — Judge-attack: a sponsor engineer deletes the TabPFN call and checks whether the app still produces a verdict. -> Defense: the classify module has NO fallback classifier; if tabpfn-client is unreachable the request returns the state token `CLASSIFIER_UNAVAILABLE` (fail-closed) and renders a "the coroner is unavailable" card, never a verdict. Removing TabPFN breaks the core feature — the substitution test passes.
2. **The open-source AI is the core, not a closed model.** — Test: the narration call targets an open-weight model id (`openai/gpt-oss-20b` / `qwen/qwen3.8-27b`) on Groq; no ANTHROPIC/OpenAI-GPT/Gemini key is on the core path. — Judge-attack: a judge greps the repo for closed-model API calls on the autopsy path. -> Defense: core modules import only `groq` + `tabpfn_client`; any closed key present is quarantined to non-core garnish (cover-image gen) and documented. A closed model on the verdict/narration path returns `OPEN_CORE_VIOLATION` in the build self-check.
3. **No fabricated verdicts or narration.** — Test: there is no hardcoded death_mode string or canned narration returned as if computed. — Judge-attack: a judge pastes an obscure repo the demo never pre-warmed and checks the verdict is genuinely computed. -> Defense: on any classifier/narrator failure the app returns the fail-closed token (`CLASSIFIER_UNAVAILABLE` / `NARRATION_UNAVAILABLE`) and an honest card, never a stored-success response.
4. **One URL -> one certificate.** — Test: the `/autopsy` route accepts exactly one repo URL and renders exactly one certificate; no multi-repo comparison surface exists. — Judge-attack: a judge tries to compare two repos. -> Defense: the input is a single URL field; multi-repo is explicitly out of scope (LIMITATIONS.md), the route rejects extra input.
5. **The live demo path EQUALS the real user path.** — Test: the demo pastes a real public repo into the same `/autopsy` route; no always-on simulate flag, no demo-only mock branch. — Judge-attack: a judge pastes a fresh URL instead of the demoed one and expects the same behavior. -> Defense: there is no `DEMO_MODE` branch in the loop; seeded landing certificates are real prior runs, labeled as such.

### MUST NOT CLAIM
- Do NOT claim "calibrated probabilities" — `predict_proba` is not documented as calibrated by default. Say "confidence distribution" unless `eval_metric` calibration is wired AND the hold-out check verifies it.
- Do NOT claim an accuracy figure not produced by `scripts/eval_seed.py` on a real hold-out of the seed dataset.
- Do NOT claim the model runs locally/offline in the deployed demo — it runs on Groq (hosted). The Ollama local mode is described as an *option*, not the deployed path.

## VERIFY-BEFORE-CLAIMING
Every headline number/figure in the post/README/demo (hold-out accuracy, seed-dataset size, number of death-modes, model id) must be RECOMPUTABLE from a committed source: `seed_dataset.csv` (size + labels), `scripts/eval_seed.py` output (accuracy), the narrate module (model id). No unbacked figure ships in the post.

## RESOLVED DECISIONS
| # | Question | Options considered | Chosen | Why not the others | Status |
|---|---|---|---|---|---|
| D-1 | Open-weight core host | Groq hosted / Ollama local on Render / local-only | Groq hosted | Ollama needs 2-4GB RAM (>512MB Starter); local-only can't be the live demo. Groq keeps the service tiny and satisfies open-weight via the model | RESOLVED |
| D-2 | TabPFN access path | local weights / tabpfn-client hosted | tabpfn-client hosted | Local weights need an interactive browser license-accept (awkward headless on Render); hosted uses a token, works in CI | RESOLVED |
| D-3 | Death-mode source | rules engine on features / TabPFN classification | TabPFN classification | A rules engine makes TabPFN a bolt-on and loses the sponsor track + the thesis (substitution test) | RESOLVED |
| D-4 | Card rendering | server-side puppeteer / DOM card + manual screenshot | DOM card + screenshot | Puppeteer on 512MB Starter is fragile and adds deploy complexity (R4); DOM card is simpler and the screenshot is the post hero anyway | RESOLVED |
| D-5 | Feature set | include Issues/PR half-life / commit+recency+contributors only | commit+recency+contributors only | Issues/PR API is paginated and slow — burns the 1-day budget (R3) for a bonus signal | RESOLVED |
| D-6 | Groq model id | llama-3.3-70b-versatile / openai/gpt-oss-20b | openai/gpt-oss-20b | The Llama id was decommissioned on Groq free tier 2026-08-16 — it 400s; gpt-oss-20b is free-tier-safe open-weight | RESOLVED |

## SOURCE LOCK
| External identifier | Version / pin | Verify command | Expected output | Status |
|---|---|---|---|---|
| tabpfn-client | 0.7.0 | `pip show tabpfn-client \| grep Version` | `Version: 0.7.0` (or compatible) | [VERIFIED-in-forge: PyPI 0.7.0 2026-10-28] |
| groq (SDK) | latest | `python -c "from groq import Groq"` | no ImportError | [VERIFIED-in-forge: shape] |
| Groq model id | `openai/gpt-oss-20b` | live `chat.completions.create` returns 200 | streamed content, not a 400 model-decommissioned error | [UNVERIFIED-build-gate: needs GROQ_API_KEY] |
| TabPFN auth | `set_access_token` / `TABPFN_TOKEN` | `python -c "from tabpfn_client import set_access_token, TabPFNClassifier"` + token fit | predict_proba shape (n,4) | [UNVERIFIED-build-gate: needs TABPFN_TOKEN] |
| GitHub REST | api v `2026-03-10` | `curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/torvalds/linux` | `200` | [VERIFIED-in-forge: docs HTTP 200, unauth read works] |

## ESCALATE, DON'T FABRICATE
On any gate/task failure: stop, record BLOCKED with the failing gate name, and NEVER substitute a mock, cached result presented as live, stored-success response, or fabricated count. Triage when over budget: cut the certificate polish and the `/demo` route first, then the eulogy flourish; NEVER cut the TabPFN-is-sole-source invariant, the open-core invariant, or the no-fabrication invariant. Escalate after 2 failures on the same gate. The hold-out accuracy and seed-dataset labels are `[HUMAN_REVIEW_REQUIRED]` for honesty, never a blocking build gate.
