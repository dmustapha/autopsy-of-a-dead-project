# Seed Labeling Rubric

Labels are the builder's documented, falsifiable calls — not cherry-picked for class separation.
Each label should be defensible by a third party reading the repo's public history.

---

## Label Criteria

### `alive`
**Criteria (all must hold):**
- Commits within the last 6 months (from labeling date ~2026-10-31)
- Multiple contributors (bus_factor ≥ 2 in recent history), OR solo author with continuous cadence
- No "end-of-life" / "deprecated" / "archived" signals in README or GitHub metadata
- Issues are being triaged and/or PRs merged

**Falsifiable disqualifiers:** last commit > 6 months ago; README says "deprecated"; GitHub archived flag set.

**Example:** `facebook/react` — GitHub shows commits this week, 1000+ contributors, active issue triage. Clearly alive.

---

### `completed`
**Criteria (at least 2 must hold):**
- GitHub `is_archived = true`, OR last commit > 2 years ago, OR README explicitly says "complete / stable / no longer maintained"
- The project reached a logical end-point: released stable versions, the problem space was solved, or the project was deliberately finished
- No "abandoned" signals — no maintainer burnout language, no sudden drop-off, no issue pile-up

**Falsifiable disqualifiers:** maintainer said "burned out" or "no time"; issues piled up with no response; sudden activity cliff without a release.

**Example:** `google/leveldb` — archived on GitHub, shipped v1.23 as a clean final state, README points to upstream. Purpose served.

---

### `abandoned`
**Criteria (all must hold):**
- Last commit > 1 year ago (and preferably > 2 years)
- No formal "this project is done" declaration or stable final release
- Was actively used (stars > 100 or notable prior traction)
- Issues open, PR backlog, or maintainer went silent without handoff

**Falsifiable disqualifiers:** repo is archived with a final release note (→ completed); README explicitly redirects to a successor (→ pivoted).

**Example:** `request/request` — formally deprecated with a note "no longer maintained", issues piled up, last meaningful commit years ago. Huge traction, then abandoned.

---

### `burned_out`
**Criteria (all must hold):**
- Single maintainer (bus_factor = 1 in commit history) or very small team (2–3)
- Commit cadence decline is visible in git log: active periods followed by steep falloff
- No deliberate EOL announcement — project just slowly stopped
- Maintainer may have been prolific but activity trailed off over 12–24 months

**Falsifiable disqualifiers:** project had a large team (contributor_count > 10 in active period); maintainer posted explicit "this is done" (→ completed or abandoned).

**Example:** `petkaantonov/bluebird` — solo author wrote a major promise library, active for ~2 years, then a clear cliff in commit frequency. No successor, no announcement. Classic burnout pattern.

---

### `pivoted`
**Criteria (at least 2 must hold):**
- Short active life (< 3 years of real activity), OR successor/replacement explicitly named in README/issues
- A successor project exists that absorbed the purpose (new org, rewrite, separate package)
- The original repo is quiet/archived but the successor is active
- Maintainers themselves redirected users elsewhere

**Falsifiable disqualifiers:** project is simply dead with no successor (→ abandoned); project ran for many years before stopping (→ completed or burned_out).

**Example:** `angular/angular.js` — AngularJS had a clear EOL announcement, README points to Angular 2+, the successor (`angular/angular`) is actively maintained. Classic pivot pattern.

---

## Ambiguous Cases — Drop Rule

If a repo genuinely fits two labels equally, **drop it** rather than guess.
A clean ≥100 rows beats a murky 130.

Common ambiguities:
- "Is this abandoned or burned_out?" → If solo maintainer + gradual decline → `burned_out`; if multi-person + no announcement → `abandoned`
- "Is this completed or abandoned?" → If there is a clear final version + README says stable → `completed`; if issues piled up with no response → `abandoned`
- "Is this pivoted or completed?" → Successor still active and README redirects → `pivoted`; no living successor → `completed`
