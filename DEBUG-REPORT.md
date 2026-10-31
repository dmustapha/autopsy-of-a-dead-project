# DEBUG-REPORT — Autopsy of a Dead Project

**Phase:** debug (hackathon-debug, 6-phase quality gate) · **Mode:** fresh · **Date:** 2026-10-30
**Adaptation:** per `docs/context/ADAPTATION-PLAYBOOK.md` §debug (sha8 `1689ac95` git / `7a69d9c5` sha256, 591 lines)
**Verdict:** `complete_with_blockers` (the two blockers are the deploy-gated model happy-paths — by design)
**CONFIDENCE-SCORE: 92 / 100**

Full 6-phase depth pointed at the **core forensic loop** (not breadth), per the governing ruling.
Contract/gas/heavy-frontend budget RE-DIRECTED onto (a) fallback-honesty labeling and (b) grounding-regex
hardening — the two surfaces the post's thesis and the $200 categories live on. Core never thinned.

---

## Phase 1 — Baseline

| Check | Result |
|---|---|
| Test suite | **14/14 pass** (0.27s) at entry; **24/24 pass** after debug hardening (14 + 4 debug-p5 + 6 debug-p2) |
| App imports | all 9 `app/*` modules import clean (schemas, validators, github, features, classifier, narrator, cache, ratelimit, main) |
| Offline loop | real repo → features → `engine=rules` verdict → grounded/templated eulogy → `AutopsyResult` executes |

Baseline is GREEN. (2 warnings remain: deprecated `@app.on_event("startup")` — see Phase 5.)

---

## Phase 2 — KNOWN-RISKS triage (9 INVARIANTS survivors)

Each survivor from `INVARIANTS.md` gets a disposition + (where mechanical) a gated test in
`tests/debug-p2-invariant-survivors.py`.

| # | Survivor | Disposition | Evidence |
|---|---|---|---|
| 1 | bus_factor alone can't separate burned_out from healthy 2–3 person repo | **ACCEPTED** (statistical, reported honestly) | joint signal used; LOO 31% reported in post as the honest ceiling |
| 2 | velocity_ratio≈0 doesn't separate abandoned/pivoted; lifespan_days must | **ACCEPTED** (statistical) | seed carries short-life pivoted exemplars; LOO honesty covers it |
| 3 | commit_cadence_decay biased when COMMIT_WINDOW truncates early history | **ACCEPTED** (documented in LIMITATIONS) | windowed-tail signal; `COMMIT_WINDOW=1000` env-set |
| 4 | healthz `tabpfn_reachable` is a token-presence proxy, not a model probe | **ACCEPTED** (documented) | `test_healthz_is_token_presence_proxy_only` asserts no fit/predict in healthz; real proof deferred to livetest |
| 5 | grounding `_numbers()` is 2+-digit substring match, not semantic | **HARDENED** (see Phase 5) | cross-field smuggle closed; `tests/debug-p5-grounding-registers.py` |
| 6 | Features lacks total_commits/is_archived → two §16 rules can't fire | **CLEARED** | `test_classifier_references_no_missing_feature_fields` — classifier references neither field; no silently-dead rule ships |
| 7 | TabPFN re-fit every request (only seed CSV cached) | **ACCEPTED** (cheap at ~48 rows) | response cache + 3 prewarm examples keep demo instant; cache present |
| 8 | seed_list.txt placeholders must be filled before B0 | **CLEARED** | seed shipped: 48 rows, balanced (VF-1) — precondition satisfied |
| 9 | PRE-BUILD token check must source .env or passes vacuously | **CLEARED** | build already ran with sourced .env; irrelevant post-build |

---

## Phase 4 — Security (keyless/local posture)

| Check | Result |
|---|---|
| Hard-coded secrets in core modules | **NONE** — `test_no_hardcoded_secrets_in_core_modules` (no `sk-`/`gsk_` literals in classifier/narrator/github/main) |
| `.env` posture | git-ignored; only `.env.example` tracked (names, no values); zero tracked secrets (`git grep` clean) |
| `GITHUB_TOKEN` / `TABPFN_TOKEN` | read only via `os.environ`; absence degrades gracefully (labeled rules / unauth 60/hr) |
| `openai` placeholder `api_key="ollama"` | **HARMLESS** — non-secret placeholder + localhost base_url (keyless Gemma); `test_placeholder_api_key_is_harmless` |
| SSRF | `validators.parse_repo_url` allow-lists `github.com/owner/repo`; URL rebuilt from parsed parts |

Security posture CLEARED for the stated scope (stateless public read-only app). Residuals (distributed
rate-abuse, Oracle firewall misconfig) are documented in `SECURITY.md` "Not defended against".

---

## Phase 5 — Per-domain critique (backend, re-aimed at the two fallback paths)

**classifier.py (TabPFN fit/predict + rules fallback honesty):**
- Happy path authenticates via `set_access_token` BEFORE `fit` (required by tabpfn-client 0.1.6), reads
  `predict_proba`, stamps `engine="tabpfn"`. ✓
- EVERY non-TabPFN exit routes through `_forensic_rules`, which **ALWAYS** stamps `engine="rules"` across
  all 5 branches (abandoned/burned_out/pivoted/alive/1-NN else). Proven exhaustively
  (`test_rules_fallback_always_labeled`). **No silent fake-tabpfn is representable** — `engine` is a
  required `Verdict` field. Missing-token path proven to degrade to labeled rules
  (`test_missing_token_degrades_to_labeled_rules`). ✓ This IS the post's thesis, and it holds.

**narrator.py (grounding, retry, templated fallback):**
- **ROOT-CAUSE-CLASS BUG FOUND + FIXED (detective, 3+ attempts).** The original
  `_numbers(text) <= _numbers(evidence)` grounding check was **cross-field value-blind**: a 2+-digit run
  from ANY evidence field grounded the same token used in a DIFFERENT false context. 4 confirmed attacks:
  - `confidence 80%` → grounded a lie "80 stars" (real stars=10)
  - `Lifespan 530` → grounded "530 contributors" (real=2)
  - `Born: 2021-03-02` → grounded "survived 2021 days" (and injected stray 02/03)
  - single-digit numbers entirely ungrounded (ACCEPTED-by-design: low risk, dates contain them)
  - **Fix** (`app/narrator.py`): `_numbers()` strips date-strings + percentages before harvesting whole
    tokens; a new `_metric_values()` parses `Label: N` lines into a metric→value map; `_grounded()` adds a
    **binding gate** so a number attached to a metric noun ("530 contributors") must match the value
    evidence binds to THAT metric. Attacks 1–3 now rejected → templated fallback; the legit eulogy
    (800 days / 530-day lifespan / 10 stars / 2 contributors) still passes. The original fabricated-99999
    test still passes. Detective attempts: (1) `\b\d+\b` whole-token — insufficient (2021/80 are whole
    tokens); (2) non-digit-bounded lookaround — equivalent, insufficient; (3) strip dates/pct — partial
    (530 still smuggled); (4-final) strip + metric-noun binding gate — closes all three.
- Retry: 2 attempts (2nd re-instructs "use only evidence numbers"), then labeled template. ✓
- **Vacuous-gate hole caught + fixed:** the mandated `debug-p{phase}-*.py` test files were NOT collected
  by the default `pytest` glob, so CI's bare `pytest -q` would silently skip the hardening test (14
  collected, not 18). Added `pytest.ini` (`python_files = test_*.py debug-*.py`) — bare `pytest -q` now
  collects and passes 24/24, so the guarantee runs in CI, not just locally.

**Non-blocking note (deploy-gated):** `main.py` uses the deprecated `@app.on_event("startup")`
(FastAPI ≥0.95 prefers `lifespan`). Functional today (2 DeprecationWarnings); flagged for the deploy phase.

---

## Fix snapshot

| Fix | File | Proof |
|---|---|---|
| Grounding cross-field smuggle (root-cause-class, 3+ attempts) | `app/narrator.py` | `tests/debug-p5-grounding-registers.py` (5 tests) |
| Vacuous-CI-collection of debug tests | `pytest.ini` (new) | bare `pytest -q` → 24 collected/passed |
| Survivor dispositions gated | `tests/debug-p2-invariant-survivors.py` (new, 6 tests) | all green |

---

## Verified Facts (recomputable — see `debug-results/vf-recompute.txt`)

- **VF-1** seed corpus: **48 rows**, balance {abandoned 10, alive 10, pivoted 10, completed 9, burned_out 9} — matches POST-DRAFT §4.
- **VF-2** 1-NN proxy leave-one-out separability: **15/48 = 31.2%** (uniform chance 20%) — matches the post's "31% (chance 20%)".
- **VF-3** grounding rejects fabricated `99999` → templated fallback fires (`"99999" not in output == True`).

---

## Open gaps / blockers handed forward (expected)

- **DEV-002** — TabPFN happy-path (`engine="tabpfn"` + real LOO number). Prior Labs was HTTP 503 at build;
  rules fallback fires AND labels itself honestly. **Deploy-gated** (close on live Oracle box).
- **DEV-004** — Gemma-via-Ollama real eulogy. No local daemon here. **Deploy-gated.**
- Deprecated `@app.on_event("startup")` — functional; address at deploy with `lifespan`.

Core was NOT thinned at any point. The fallbacks fire AND label themselves honestly — that honesty is the deliverable.
