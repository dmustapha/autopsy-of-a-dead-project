# Depth Upgrade Plan — "Autopsy of a Dead Project"
Date: 2026-10-31 · Source: 4 parallel research spikes (Tier A/B/C architecture + codebase integration map)
Status: **PLAN — awaiting go/no-go. No code written yet.**

## The problem this fixes
Current build is **single-organ forensics**: all 6 features derive from the commit stream (dates+authors). The LLM (Gemma) is **garnish** — it writes prose over numbers a rules `if`-ladder already decided. The taxonomy (abandoned/pivoted/completed) out-runs the evidence: those deaths look identical in commit-cadence space. Signal is fetched and thrown away (commit *messages* discarded; `is_archived` fetched but unused).

## Deadline reality (binding)
Post published by **18:00 WAT today**. Full A+B+C ≈ 9.5h build + tests + re-verify + deploy + write-up. **Not all shippable today.** This plan is tiered so the highest-EV, lowest-risk slice ships and the rest is staged (built if time remains, else written as "where this goes next" in the post).

## Locked architecture decisions (from spikes)
1. **Tier A = LLM-as-adjudicator** (not feature-provider, not parallel). TabPFN stays the primary classifier (protects the $200 TabPFN category). Gemma fires **only in the tie-zone** (`max(probs) − 2nd < 0.25`) to adjudicate the top-2 using commit messages + README. Surface `tabpfn_probs` AND `llm_hint` separately so judges see TabPFN doing real work.
2. **Tier B** = add `is_archived` (0 API calls, already fetched) + `days_since_last_release`/`release_count` (1 call) + `open_issue_ratio` (1 call) to the feature vector → activates the already-built posterior/differential UI. **Requires `GITHUB_TOKEN`** (rate limits). Seed corpus backfilled by re-running the extractor against the 48 known repos (automatable, ~2 min with token).
3. **Tier C** = Oracle VM persistent disk (Render is moot per ADR-005a). SQLite memorial wall + cohort via extended k-NN.

## Honesty invariant (preserve in EVERY change)
- LLM offline → `engine` stays `tabpfn`/`rules`, no tie-break, narration appends "(Text analysis offline — verdict from commit cadence only.)". `death_note=None`, never fabricated.
- New TabPFN features missing (no token / 404) → impute from seed median, never crash, label.
- TabPFN offline → existing `engine="rules"` path unchanged.

## Design-risk gate (CRITICAL)
The 3 UI files (`index.html`, `app.js`, `card.css`) were **verified in Chrome today and owner-approved.**
- **Tier A + Tier B = ZERO UI file touches** (backend Python + CSV only). SAFE.
- **Tier C = touches all 3** → HIGH RISK. Additive-only CSS, no `:root` edits, no duplicate DOM IDs (don't break `seal → typeOut → drawTrace`). Requires Chrome re-verification + re-screenshot.

---

## PHASE 1 — Tier A (adjudicator) · ~4h · backend-only · SHIP TODAY
| File | Change | UI risk | Honesty-fallback | Tests |
|---|---|---|---|---|
| `app/github.py` | Keep `commit.message` (cap 200 chars, last ~20); fetch README (`/readme`, raw, cap 2000) → `RepoData.readme` | N | README 404 → `None` | `test_features.py` `_commit()` helper gains `message` key |
| `app/extractor.py` **(new)** | Gemma structured JSON call (`format=json`, temp 0, max_tokens 200): `{death_signals[], classification_hint, hint_confidence, evidence_quote}`; offline guard → `hint="none", llm_offline=True` | N | parse-fail/offline → `hint=none` | new: returns none when Ollama offline |
| `app/classifier.py` | Tie-zone check; if `hint_confidence=high` & hint ∈ top-2 → override, `engine="tabpfn+llm"`; else keep TabPFN | N | offline → argmax stands, `engine=tabpfn` | `test_classifier_shape.py` (constructor) |
| `app/schemas.py` | `Verdict.engine` += `"tabpfn+llm"`; `AutopsyResult.death_note: str\|None=None`, `llm_hint` optional; `RepoMeta.readme_excerpt` | N | None defaults = honest "not extracted" | new optional fields, no break |
| `app/narrator.py` | Pass `evidence_quote` into evidence string; `_template()` never sets `death_note` | N | template path unchanged marker | grounding `_METRIC_NOUNS` if new nouns |
| `app/main.py` | Wire extractor after classify; attach `death_note`, `llm_hint` | N | field absent if None | new smoke test |

**Note:** Gemma is only live where Ollama runs (Oracle VM deploy — ties to existing DEV-004). Locally the honest fallback shows; adjudicator logic is unit-tested with a mocked LLM. Real tie-break proven at deploy.

## PHASE 2 — Tier B (richer vector + live posterior) · ~2.5h · backend+CSV · SHIP TODAY (needs token)
| File | Change | UI risk | Honesty | Tests |
|---|---|---|---|---|
| `app/github.py` | `is_archived` (have it) + `/releases?per_page=1` (recency+count) + closed-issue count (`/issues?state=closed&per_page=1` Link header) | N | failure → `None`, not 0 | new meta-field None test |
| `app/features.py` | +`is_archived_flag`, `release_recency_days`, `has_releases`, `open_issue_ratio`; extend `FEATURE_ORDER` | N | None → seed-median impute | extend fixtures |
| `app/schemas.py` | New `Features` floats **all `=0.0` defaults** (or `test_classifier_shape` breaks); `RepoMeta` +counts | N | defaults | constructor fix |
| `data/seed_repos.csv` | +columns; backfill 48 rows via one-off extractor script (token, ~2 min) | N | — | indirect |
| `app/classifier.py` | `FEATURE_ORDER` auto-extends; optional `is_archived` rule branch | N | `engine=rules` unchanged | shape test |
| `app/narrator.py` | New metric nouns in `_evidence()` + `_METRIC_NOUNS` (grounding must cover them) | N | grounding gate intact | extend grounding test |

**Cheapest-first within P2 if time-squeezed:** `is_archived` (2 lines, 0 calls) → releases (1 call) → open-issue ratio. Each independently shippable.

## PHASE 3 — Tier C (theme) · cohort ~0.5h (safe) + wall ~3h (UI-RISK) · STAGE
| File | Change | UI risk | Notes |
|---|---|---|---|
| `app/classifier.py` | `nearest_k(f,k=5)` from existing `_nearest_mode` → "died like N of 5 similar repos" | N (backend) | cheap, strong narrative |
| `app/main.py` | cohort surfaced in `AutopsyResult`; **wall:** `POST /offerings` + `GET /offerings/{o}/{r}` | N (endpoints) | reuse `parse_repo_url`, existing per-IP `rate_limit` |
| `app/ofrenda_store.py` **(new)** | SQLite at `/opt/autopsy/data/offerings.db` (repo,text,created_at); `html.escape`, ≤280 chars | N | Oracle persistent fs |
| `app/static/app.js` | **HIGH RISK** — cohort line in cert; "add offering" + wall render inside `render()` literal | **Y** | don't dup IDs / break anim |
| `app/templates/index.html` | **HIGH RISK** — `<section id="ofrenda-wall">` after `<article id="cert">` | **Y** | structural |
| `app/static/card.css` | **HIGH RISK** — additive `.ofrenda-wall` rules only; no `:root`/selector redefine | **Y** | visual regression |

---

## Recommended ship line (my call)
**SHIP TODAY:** Phase 1 (Tier A full) + Phase 2 (is_archived + releases + open-issue-ratio). Both **backend-only → zero risk to the verified design**, directly kill the "garnish AI" critique, AND light up the dormant posterior/differential UI. Re-run 24-test suite + mocked adjudicator test; no Chrome re-verify needed (no UI change).
**STAGE:** Phase 3 — do cohort (0.5h backend + 1 cert line) if time; hold the memorial wall unless there's clear runway (it reopens the verified-design gate: Chrome re-verify + re-screenshot). If not built, write both as "where this goes next" in the post.

## Blockers / decisions needed
1. **`GITHUB_TOKEN`** — required for Tier B (and to re-shoot the stale `cert-fastapi.png` past the 60/hr limit). Do you have one to drop in `.env`? If not, Tier B is blocked and Tier A still ships.
2. **Ambition line** — A+B only (safe, backend) vs A+B+cohort vs all-including-wall (UI re-verify cost)?
3. **Pipeline implication** — this reopens BUILD scope after `design` completed. On ship we re-run tests + (if UI touched) re-verify in Chrome + re-screenshot, then deploy, then the post. Noted, not blocking.

## Known limitations
- `open_issue_ratio` is a **weak signal**: it sits near-flat (~0.98) across abandoned / completed / alive in the seed corpus, so it adds little discriminative power. Retained (not dropped) to avoid re-backfill churn; treated as a soft input, not a driver.

## Test/verify tail (all paths)
`PYTHONPATH=. .venv/bin/python -m pytest -q` (24 green baseline) + new tests per phase → local smoke on :3300 → (if UI) Chrome re-verify both cert states → re-screenshot deliverables → deploy (Oracle, activates Gemma+TabPFN) → write post.
