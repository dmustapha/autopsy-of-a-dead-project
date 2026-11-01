# Autopsy Depth Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make both open-weight models do real, defensible work on *this* repo — TabPFN classifies content-enriched features and beats a 1-NN baseline, and the live 0G adjudicator reads what the project *was* and quotes its own death-signals — all shown honestly on the frozen certificate.

**Architecture:** `github.py` surfaces more already-fetched raw meta fields; `features.py` derives new honest features into `Features`/`FEATURE_ORDER` (which both TabPFN and the 1-NN fallback read automatically); the seed CSV is regenerated through the prod extractor (train==serve) and grown to ≥100 balanced, labeled rows; a LOO script proves TabPFN LOO > 1-NN LOO on the same enriched features; the `extractor.py` adjudicator is re-enabled and widened to also return a factual `project_summary`, wired additively through `main.py` → `AutopsyResult`; the certificate (`app.js`) surfaces the summary + quoted evidence + content-read badge in the existing amber style.

**Tech Stack:** Python, FastAPI, local TabPFN (tabpfn + torch), 0G Compute (OpenAI-compatible) via httpx/openai, pandas/numpy, pytest

**Spec:** /Users/MAC/dev-ghost/docs/superpowers/specs/2026-10-31-autopsy-depth-upgrade-design.md

## Global Constraints
- **Honesty invariant:** offline / parse-fail / failed-fetch → labeled-empty (`llm_offline`, seed-median impute, `""`), NEVER a fabricated value. New fields obey this exactly as the existing ones do.
- **Anti-goal — never fake the number:** do not hand-edit the LOO result or pick features/labels to manufacture a TabPFN win. If TabPFN still loses after honest enrichment, report it truthfully and invoke the spec's reframe clause (calibrated 5-class posterior + content tie-break).
- **Don't break the live deploy:** every change stays backward-safe; the offline test suite must stay green before any redeploy.
- **Don't touch co-resident prod LEASH:** deploy only within `/home/ubuntu/autopsy`; never edit leash blocks; re-check `api.leash.ink/healthz==200` after redeploy.
- **train==serve:** the seed is rebuilt via the production extractor (`fetch_repo` + `build_features`), never a parallel fetcher.
- **Box env is already 0G deepseek:** `LLM_BASE_URL=https://router-api.0g.ai/v1`, `LLM_MODEL=deepseek-v4.1-flash`, `LLM_MAX_TOKENS=2000` are already set; re-enabling `EXTRACTOR_LLM_DISABLE=0` runs the adjudicator on 0G. Do not hard-code a model.
- **Keep the frozen card aesthetic:** add new fields only in the existing amber/Spectral/IBM-Plex-Mono style; no visual redesign.

## Review Focus
These are the input/failure classes most likely to bite; each is pinned to the task that owns a test for it (verified present in the self-review pass).

1. **0G adjudicator returns garbage / empty content mid-autopsy** (deepseek is a reasoning model; low token budget → empty content → silent parse-fail). → honesty guard must yield labeled-empty + `project_summary=""`, never fabricate. *(Task 5)*
2. **Repo with empty / missing README** (adjudicator has nothing to read; `readme=None`). → adjudicator returns empty summary + no signals; `_death_note` stays `None`; cert degrades gracefully. *(Tasks 5, 7)*
3. **A seed row whose enriched fetch fails** (404 / rate-limit / partial meta during rebuild). → seed-median impute for the new numeric columns, labeled 0/1 flags default honestly, row still written or skipped deterministically. *(Tasks 2, 3)*
4. **Repo with no topics / no license / no description** (new raw fields absent from GitHub meta). → `topics=[]`, flags `0.0`, `github.py` returns them as honest empties, `build_features` emits a valid full vector. *(Tasks 1, 2)*
5. **Cache serving a pre-upgrade result shape** (in-memory `TTLCache`; a warm entry predates `project_summary`). → `AutopsyResult.project_summary` is an additive optional field (defaults safe); `app.js` null-checks it so an old-shape result renders without error. *(Tasks 6, 7)*

---

## Task 1 — Surface new raw fields in `github.py` meta

**Files**
- Modify: `app/github.py` — the `fetch_repo` return `meta={…}` dict (lines ~133–144).
- Modify: `tests/test_github_meta.py` — **Create** (no existing github test file).

**Interfaces**
- Produces (in `RepoData.meta`): `forks_count: int | None`, `watchers_count: int | None`, `topics: list[str]`, `size: int | None`, `has_wiki: float`-ready `bool`, `has_pages: bool`, `fork: bool`, `license_present: bool`, `description: str | None`.
- Consumes: the already-fetched `meta = meta_r.json()` from `GET /repos/{owner}/{repo}` (GitHub returns `forks_count`, `watchers_count`, `topics` [when `Accept: application/vnd.github+json` — already set], `size`, `has_wiki`, `has_pages`, `fork`, `license`, `description` all in that one response — **no new API call**).

**Steps**
- [ ] Write failing test `test_fetch_repo_surfaces_new_meta_fields` that monkeypatches the httpx repo-meta response with a fixture JSON containing `forks_count=12, watchers_count=30, topics=["cli","tool"], size=400, has_wiki=True, has_pages=False, fork=False, license={"spdx_id":"MIT"}, description="a thing"` and asserts the returned `RepoData.meta` carries `forks_count==12, watchers_count==30, topics==["cli","tool"], size==400, has_wiki==True, has_pages==False, fork==False, license_present==True, description=="a thing"`.
- [ ] Add `test_fetch_repo_missing_optional_meta_defaults_honestly`: meta JSON omits `topics`/`license`/`description` → `topics==[]`, `license_present==False`, `description is None` (Review-Focus 4). Keep `TABPFN_DISABLE`/network-mock pattern from existing tests.
- [ ] Run tests — confirm they FAIL (fields absent).
- [ ] Implement: extend the `meta={…}` dict in `fetch_repo` with the 9 fields, reading from the already-parsed `meta` JSON. `topics`: `meta.get("topics") or []`. `license_present`: `bool((meta.get("license") or {}).get("spdx_id"))`. Others `meta.get(k)` with honest `None`/`False` defaults. Do not add any new `client.get`.
- [ ] Run tests — confirm PASS.
- [ ] Commit: `feat(github): surface forks/watchers/topics/size/wiki/pages/fork/license/description in meta`.

---

## Task 2 — Extend `Features` + `FEATURE_ORDER` and compute the new derived features

**Files**
- Modify: `app/schemas.py` — `Features` model (lines 21–33) and `FEATURE_ORDER` (lines 54–59).
- Modify: `app/features.py` — add a `_tier_c(data, )` helper and call it in `build_features` (lines 96–154), analogous to the existing `_tier_b`.
- Modify: `tests/test_features.py` — extend `_repo` fixture meta + add assertions.

**Interfaces**
- Produces (new `Features` fields, all `float`, all defaulting `0.0` so existing `Features(...)` fixtures never break — mirror the Tier-B pattern in lines 28–33):
  `log_stars`, `log_forks`, `log_watchers`, `topics_count`, `readme_size`, `description_present`, `license_present`, `has_wiki`, `has_pages`, `is_fork`, `primary_language_freq`.
- Consumes: `data.meta` fields from Task 1 + `data.readme` (already on `RepoData`).
- `FEATURE_ORDER` is appended in the **same order** as the CSV columns (Task 3 writes them in this order).

**Definitions the signature/test do not determine:**
- Log scaling: `log_stars = round(math.log1p(stars), 4)` (log1p so 0 stars → 0.0, honest). Same for forks/watchers.
- `primary_language_freq`: frequency-encode from the **seed** — fraction of seed rows sharing this repo's `primary_language`; unknown/None language → `0.0`. Implement as a `functools.lru_cache`d `_language_freq()` reading `SEED_PATH` (mirror `_seed_medians`), looked up by `data.meta.get("primary_language")`. A `None`/empty readme → `readme_size=0.0`.
- **Bootstrap / chicken-and-egg (train==serve):** `_language_freq` reads the seed, but Task 3 rebuilds the seed via `build_features`. Resolve by sourcing the frequency map from the repo's own `primary_language` against a frequency table that does NOT require the derived feature column to pre-exist — compute it from the `owner_repo`→language the extractor already knows, cached per-process, and if `SEED_PATH` is missing/empty (first build) fall back to `0.0`. `build_seed.py` therefore produces the raw language per row; the frequency column is a pure post-pass over the finished rows OR `_language_freq` tolerates an absent seed. **Builder decision (pick one, documented in the commit):** (a) two-pass seed build — build raw rows, then compute `primary_language_freq` as a post-pass over the assembled frame; or (b) `_language_freq` guards on missing seed → `0.0` during build, real value at serve. (a) is cleaner for train==serve; prefer it.

**Steps**
- [ ] Write failing `test_build_features_emits_full_enriched_vector`: build `_repo` with meta carrying stars=100, forks_count=10, watchers_count=50, topics=["a","b"], size=200, has_wiki=True, has_pages=False, fork=False, license_present=True, description="x", and a 300-char readme; assert each new feature equals its spec value (`log_stars==round(log1p(100),4)`, `topics_count==2.0`, `readme_size==300.0`, `description_present==1.0`, `license_present==1.0`, `has_wiki==1.0`, `has_pages==0.0`, `is_fork==0.0`) and that `[getattr(f,k) for k in FEATURE_ORDER]` has no missing/None entries.
- [ ] Add `test_enriched_features_empty_inputs_are_zero_not_crash` (Review-Focus 4): meta with no topics/license/description and `readme=None` → `topics_count==0.0, readme_size==0.0, description_present==0.0, license_present==0.0`, vector still full-length.
- [ ] Run — confirm FAIL.
- [ ] Implement `Features` fields + `FEATURE_ORDER` appends + `_tier_c` + `_language_freq`; spread `**tc` into the `Features(...)` call like `**tb`.
- [ ] Run `tests/test_features.py` AND `tests/test_classifier_shape.py::test_feature_order_includes_tier_b` (it constructs `Features(...)` with only the base 6 — new fields MUST stay defaulted). Confirm PASS.
- [ ] Commit: `feat(features): add log-popularity/topics/readme/flags/language-freq to FEATURE_ORDER`.

---

## Task 3 — Regenerate + expand the seed CSV with new columns + a labeling rubric

**Files**
- Modify: `scripts/build_seed.py` — write ALL `FEATURE_ORDER` columns (already does via `FEATURE_ORDER` loop — verify it picks up the new ones) and carry the new feature columns; drop the stale `tabpfn_client` LOO block (Task 4 owns LOO via local TabPFN).
- Modify: `scripts/seed_list.txt` — expand from 47 → ≥100 labeled repos, balanced ~20/class across abandoned/burned_out/completed/pivoted/alive.
- Create: `data/seed_repos.csv` (regenerated output; header carries the new columns between `velocity_ratio` and `is_archived_flag`… existing Tier-B … then new Tier-C … then `death_mode,note`). **Decision:** append Tier-C columns AFTER the Tier-B block, before `death_mode,note`, matching `FEATURE_ORDER` order.
- Create: `data/LABELING_RUBRIC.md` — the documented, falsifiable labeling criteria (from spec §Lever 3: archived+released→completed; long-dead+no releases→abandoned; single-maintainer cadence-collapse→burned_out; short-life pivot-signal→pivoted; actively-maintained→alive).
- Create: `scripts/validate_seed.py` — the validation "test" for this task.

**Interfaces**
- `scripts/validate_seed.py` Produces: exit 0 + printed summary, exit 1 on any violation. Consumes: `data/seed_repos.csv` via pandas + `FEATURE_ORDER`.
- `build_seed.py` Consumes: `scripts/seed_list.txt` lines `slug, mode, note`; Produces: `data/seed_repos.csv` with columns `["owner_repo", *FEATURE_ORDER, "death_mode", "note"]`.

**Steps**
- [ ] Write `scripts/validate_seed.py` first (this is the task's test): assert (a) every `FEATURE_ORDER` column present, (b) `len(df) >= 100`, (c) each of the 5 modes has `>= 15` rows (balance), (d) no NaN/empty in any feature column, (e) `death_mode` ∈ the 5 training modes (no `insufficient_history`). Run it against the CURRENT 47-row CSV — confirm it FAILS on row-count/column checks.
- [ ] Write `data/LABELING_RUBRIC.md` with the criteria + one example repo per mode + the spot-check note (labels are the builder's documented, falsifiable calls).
- [ ] Expand `scripts/seed_list.txt` to ≥100 repos, ~balanced, per the rubric. Reuse the existing 47. Use only safe public repos (per the file's header rule). Review-Focus 3: pick repos resilient to fetch (famous/stable), and the builder re-runs on any 404.
- [ ] Update `build_seed.py`: confirm the `FEATURE_ORDER` loop now emits Tier-C columns; remove the `tabpfn_client` LOO tail (moved to Task 4). On a per-repo fetch error, print `ERR` and skip (existing behavior) — a skipped row must not silently unbalance classes, so the builder re-checks balance via `validate_seed.py` after.
- [ ] Run `python scripts/build_seed.py` (needs `GITHUB_TOKEN`) to regenerate `data/seed_repos.csv`.
- [ ] Run `python scripts/validate_seed.py` — confirm PASS (≥100 rows, balanced, all columns, no NaN).
- [ ] Update `scripts/recompute.sh` `EXPECTED_ROWS=48` → the new count (keep the drift-gate honest). Commit: `feat(seed): expand to ≥100 balanced labeled repos with enriched columns + rubric`.

---

## Task 4 — LOO evaluation: TabPFN LOO vs 1-NN LOO on the same enriched features

**Files**
- Create: `scripts/eval_loo.py`.
- Create: `tests/test_eval_loo.py` (smoke test the script runs and prints both numbers; guarded by `TABPFN_DISABLE` — see below).

**Interfaces**
- `scripts/eval_loo.py` Produces: `{"tabpfn_loo": float, "onenn_loo": float, "n": int, "tabpfn_beats_1nn": bool}` printed as JSON + a human line; exit 0. Consumes: `data/seed_repos.csv`, `FEATURE_ORDER`, local `tabpfn.TabPFNClassifier`, and the SAME standardized 1-NN as `classifier._nearest_mode` (import/reuse the standardization: `mu/sd` over `X`, argmin squared distance).
- 1-NN LOO MUST use the identical feature matrix + standardization as TabPFN LOO (spec G1: "the *same* features").

**Definitions the signature/test do not determine:**
- LOO loop: for each row i, fit on `df.drop(i)`, predict row i; TabPFN via `TabPFNClassifier().fit(tr[FEATURE_ORDER], tr["death_mode"]).predict`; 1-NN via standardized nearest-neighbor over `tr` (reuse the `_nearest_mode` math, not sklearn, to match serve). Accuracy = correct/n for each.

**Steps**
- [ ] Write failing `tests/test_eval_loo.py::test_eval_loo_reports_both_models`: run `eval_loo.main()` (or subprocess) and assert output JSON has keys `tabpfn_loo`, `onenn_loo`, `n`, and `n == len(seed)`. Because local TabPFN is ~GB, gate the heavy path: if `TABPFN_DISABLE=1`, the script still computes the 1-NN LOO and reports `tabpfn_loo=None` — the test asserts the 1-NN number is present and `n` correct. (Full TabPFN LOO is run by the builder manually / in the DoD gate, like the existing conftest TabPFN policy.)
- [ ] Run — confirm FAIL (script absent).
- [ ] Implement `scripts/eval_loo.py` with both LOO loops; make the TabPFN loop skip when `TABPFN_DISABLE=1`.
- [ ] Run test — confirm PASS.
- [ ] **DoD GATE (builder, real TabPFN, not in CI):** run `python scripts/eval_loo.py` on the box/local with TabPFN enabled. Record `tabpfn_loo` and `onenn_loo`. **Assert `tabpfn_loo > onenn_loo`.** If it holds → record the honest numbers for the POST. If NOT → STOP and apply the anti-goal clause: iterate features/seed (within honesty) OR, if still losing, write the truthful reframe (do not fabricate). Surface the result to Dami either way.
- [ ] Commit: `feat(eval): LOO script comparing TabPFN vs standardized 1-NN on enriched features`.

---

## Task 5 — Adjudicator: re-enable path + extend to `project_summary`, honesty-guarded

**Files**
- Modify: `app/extractor.py` — `SYSTEM` prompt (lines 10–19), `_OFFLINE` (21–27), `_normalize` (33–46), `extract_death_note` (49–76; `max_tokens=400` → env-driven).
- Modify: `tests/test_extractor.py` — add summary + garbage-input cases.

**Interfaces**
- Produces (new key in the returned dict, everywhere the dict is produced — `_OFFLINE` and `_normalize`): `project_summary: str` (one factual line of what the project was/did, strictly from README/description; `""` when absent/offline).
- Consumes: unchanged `messages`, `readme`; token budget now `int(os.environ.get("LLM_MAX_TOKENS", "400"))` (box sets 2000; deepseek reasoning model needs headroom — see Review-Focus 1 and narrator.py:133 precedent).

**Steps**
- [ ] Write failing `test_offline_returns_empty_project_summary`: with `EXTRACTOR_LLM_DISABLE=1`, `extract_death_note(...)["project_summary"] == ""` and `llm_offline is True`.
- [ ] Write failing `test_garbage_json_yields_empty_summary_no_fabrication` (Review-Focus 1): monkeypatch `_client` to return non-JSON / `{}` / a dict with `project_summary` as a non-string → normalized result has `project_summary == ""`, `classification_hint == "none"`, `hint_confidence == "low"` (never invents a summary).
- [ ] Write failing `test_valid_json_includes_normalized_summary`: model returns valid JSON with `project_summary="A CLI bundler for JS."` → normalized dict carries it (truncated to a sane length, e.g. `str(...)[:300]`).
- [ ] Run — confirm FAIL.
- [ ] Implement: add `"project_summary"` to the `SYSTEM` JSON key list with the "strictly from README/description, one factual line, no invention" instruction; add `"project_summary": ""` to `_OFFLINE`; in `_normalize` add `"project_summary": str(raw.get("project_summary"))[:300] if isinstance(raw.get("project_summary"), str) else ""`; change `max_tokens=400` → `int(os.environ.get("LLM_MAX_TOKENS", "400"))`.
- [ ] Run `tests/test_extractor.py` — confirm PASS.
- [ ] **Builder probe (honesty, measured not guessed — spec builder-check):** with the box 0G env, run a real `extract_death_note` against 2–3 example repos and confirm deepseek returns a non-empty, factual `project_summary` at `LLM_MAX_TOKENS=2000`. If empty → raise budget / adjust wording, re-measure. Do NOT ship a prompt validated only offline.
- [ ] Commit: `feat(extractor): add factual project_summary to adjudicator, env-driven token budget`.

---

## Task 6 — Wire `project_summary` + death signals through `/autopsy` → `AutopsyResult`

**Files**
- Modify: `app/schemas.py` — `AutopsyResult` (lines 41–52): add additive optional field.
- Modify: `app/main.py` — `autopsy` handler (91–125) and `_prewarm_one` (128–142): pass the new field through from `hint`.
- Create/Modify: `tests/test_autopsy_result.py` — handler-level test (may extend an existing test module if one asserts handler shape; none currently does, so Create).

**Interfaces**
- Produces: `AutopsyResult.project_summary: str | None = None` (additive, backward-safe for cached pre-upgrade entries — Review-Focus 5).
- Consumes: `hint.get("project_summary")` from `_adjudicate_evidence` (Task 5). When `hint["llm_offline"]` or empty → `project_summary=None` (honest empty), mirroring `_death_note`'s offline guard.

**Steps**
- [ ] Write failing `test_autopsy_result_accepts_project_summary`: construct `AutopsyResult(..., project_summary="A bundler.")` and also `AutopsyResult(...)` WITHOUT it (old cached shape) — both valid, latter `project_summary is None` (Review-Focus 5).
- [ ] Write failing `test_handler_populates_summary_from_live_hint` (or a `_summary_from_hint(hint)` helper mirroring `_death_note`): a live medium+ hint with `project_summary="X"` → result carries `"X"`; an offline hint → `None`.
- [ ] Run — confirm FAIL.
- [ ] Implement: add the schema field; add a small `_project_summary(hint)` helper in `main.py` next to `_death_note` (offline/empty → `None`); pass it in BOTH `AutopsyResult(...)` constructions (`autopsy` and `_prewarm_one`). No other handler change.
- [ ] Run new test + `recompute.sh`'s pytest set — confirm PASS.
- [ ] Commit: `feat(autopsy): thread project_summary through result, honesty-guarded`.

---

## Task 7 — Certificate UI: show "What this project was" + quoted evidence + content-read badge

**Files**
- Modify: `app/static/app.js` — `render(d)` (167–294): add the summary line, ensure the quoted-evidence block (`last-words` already renders `death_note`) and a content-read badge; null-safe for old-shape results.
- Modify: `app/static/card.css` — add minimal selectors for the new summary line in the existing amber style (reuse `.cohort-line`/`.last-words` tokens where possible; no new palette).
- Modify: `tests/test_cert_render.py` — **Create**: a lightweight JS-free DOM assertion is out of scope for pytest; instead this task's "test" is a documented manual Chrome check PLUS a static assertion that `app.js` references the new fields.

**Interfaces**
- Consumes: `d.project_summary` (Task 6), existing `d.death_note` (quoted evidence, already wired to `.last-words`), `d.narration_engine` / env-derived model for the content-read badge.
- Produces: in the frozen card — a "What this project was" line (when `project_summary` present), the existing quoted death-signal block, and a badge `evidence read by <model> · 0G Compute` (derive text from `d.narration_engine` which already resolves `deepseek-v4.1-flash · 0G Compute`).

**Steps**
- [ ] Write failing static check `tests/test_cert_render.py::test_appjs_surfaces_summary_and_content_badge`: read `app/static/app.js` and assert it references `project_summary`, renders a "What this project was" label, and emits a content-read badge; assert it null-guards `project_summary` (graceful-empty — Review-Focus 2 & 5). (This is a source-level guard that the wiring exists; the visual check is the manual step below.)
- [ ] Run — confirm FAIL (strings absent).
- [ ] Implement in `render(d)`: a `summaryHTML` block above `.coroner` (shown only when `d.project_summary` truthy), using `esc()`; a content-read badge appended in `.cert-foot` ONLY when the adjudicator actually ran (`!isTemplated` and `d.llm_hint && !d.llm_hint.llm_offline`), reading the model from `d.narration_engine`. Add minimal CSS in the existing style.
- [ ] Run static check — confirm PASS.
- [ ] **Manual Chrome check (documented, per spec Lever 4):** load the app in real Chrome, run the 3 examples, confirm the summary + quote + badge appear in both an adjudicator-on case and gracefully disappear for an offline/empty case. Capture a screenshot. (Use claude-in-chrome against the live box, not localhost — per MEMORY: claude-in-chrome can't reach localhost; use the deployed URL after Task 8, OR local Playwright Chromium for a pre-deploy loopback check.)
- [ ] Commit: `feat(cert): surface project summary, quoted evidence, and 0G content-read badge`.

---

## Task 8 — Full offline suite green + redeploy + re-warm + livetest

**Files**
- No code changes; this is the verification + deploy task. Touches only the box at `/home/ubuntu/autopsy` and its `.env`.

**Interfaces**
- Consumes: the green offline suite, the LOO DoD result (Task 4), the box 0G env.
- Produces: a live, re-warmed deploy with the new result shape; a passing livetest; recorded honest numbers for the POST.

**Steps**
- [ ] Run the FULL offline suite locally: `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` — confirm ALL green (new + existing honesty-invariant tests). Fix any regression before proceeding.
- [ ] Run `bash scripts/recompute.sh` — confirm zero drift (updated row count from Task 3).
- [ ] Deploy new code to the box `/home/ubuntu/autopsy` ONLY (rsync/git pull within that dir). Do NOT touch any leash block. Set `EXTRACTOR_LLM_DISABLE=0` in the box `.env` (0G env already present).
- [ ] Restart the autopsy service only. Verify co-resident prod unaffected: `curl -s https://api.leash.ink/healthz` → expect `200`.
- [ ] Re-warm the 3 examples (startup prewarm fires, or hit `/autopsy` for each of `bower/bower`, `sindresorhus/caprine`, `fastapi/fastapi`). Confirm each cached response now carries a real `project_summary` + ≥1 verbatim death-signal (for the dead ones) and returns `<2s` warm.
- [ ] Re-run livetest against the live box (V1/V2/V3 per the livetest skill); confirm it passes with the NEW numbers. Record the honest TabPFN-LOO / 1-NN-LOO figures and the adjudicator latency for the POST.
- [ ] Verify DoD checklist from the spec is fully met; report any partial state (hard floor 06:59 UTC clause).
- [ ] Commit any deploy-config notes; push is Dami-gated (hold origin/main push per standing rule until the whole upgrade is done).

---

## Definition of Done (from spec — final gate)
- [ ] TabPFN LOO > 1-NN LOO on enriched features, measured & script-reproducible (Task 4), or honest reframe.
- [ ] Seed ≥100 rows, balanced, documented rubric, train==serve (Task 3).
- [ ] Adjudicator live: 3 examples show real "what this project was" + ≥1 verbatim death-signal (Tasks 5–8).
- [ ] Honesty-invariant tests green + full offline suite green (Task 8).
- [ ] Live deploy updated, 3 examples re-cached <2s, livetest re-passes (Task 8).
- [ ] POST + demo reflect new honest numbers (downstream, after Task 8).
