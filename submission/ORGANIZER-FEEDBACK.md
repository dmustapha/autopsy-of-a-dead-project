# Organizer Feedback: Autopsy of a Dead Project on the Hacktoberfest Open-Source AI stack

_Built during DEV Hacktoberfest Week 4 (Ghost in the Machine). Field notes from actually shipping on your stack, sent in the spirit of making it better. No blame, just what a build hit._

## What Worked Well
- **TabPFN auth and the token flow were instant and correct first try.** `set_access_token` succeeded in 1545ms with a freshly minted token; zero credential friction (evidence: `evidence/wire/model-integrations.json`).
- **TabPFN is genuinely runnable as an open-weight local model.** Once we stopped depending on the hosted inference endpoint, the local path gave us a real posterior and a re-derivable held-out number. That is exactly the property the challenge rewards.
- **The 0G Compute open-weight inference produced a real, honest result surface.** The engine field is env-derived, so our certificate badge ("deepseek-v4.1-flash on 0G Compute") reflects what actually ran, not a hardcoded string.
- **dev.to's Basic Markdown (v1) editor with front matter is elegant** once you find it: paste one markdown document and title, tags, cover, and draft state all parse from the `---` block.

## Friction & Suggestions

_Ordered by cost-to-discover: the items that ate the most build time come first._

### SDK / API
**What we hit:** Prior Labs' hosted TabPFN **inference** endpoint returned 503 on `fit`, while the auth service was up. It persisted from build day through the wire phase.
**Cost to discover:** high. It recurred across three phases (build DEV-002, wire re-probe, and it was still the only open deploy-time variable), so we designed the whole classifier around a labeled fallback before confirming the local path.
**Delta:** `set_access_token` returns SUCCESS (auth up), but a real `TabPFNClassifier.fit(...)` call returns HTTP 503 from the inference service. The failure is in inference availability, not credentials or client code.
**Impact:** the app ran on a labeled `engine="rules"` fallback until we moved to running TabPFN locally. A team that only tried the hosted API and gave up would have shipped without the foundation model at all.
**Evidence:** `evidence/wire/tabpfn-inference-503.log`, `WIRE-REPORT.md` DEV-002, `evidence/wire/model-integrations.json`.
**Suggestion:** surface hosted-inference status separately from auth status (a status page or a clear 503 body that says "inference capacity, retry / run locally"), and lead new users to the local open-weight path in the first code sample, since that is the reliable one.
_Severity: BLOCKER (forced a fallback until the local path was wired)_

### Infrastructure
**What we hit:** cold inference latency on 0G Compute is high enough to make interactive first-request UX hard. A never-seen repo means two live model calls and ran ~99s cold.
**Cost to discover:** medium. It surfaced at livetest and again at demo rehearsal, and it reshaped the whole demo (cached examples only, serial pre-warm, never type a fresh repo on camera).
**Delta:** deploy-time estimate was 20 to 40s; measured fresh-cold was 99.2s, with 0G reasoning dominating the budget. Concurrent cold requests on a small single-worker box compounded it (a parallel three-example warm hung past 200s).
**Impact:** we had to add an in-memory cache, a serial pre-warm step, and a cached-examples-only demo discipline. The live product is honest about it ("slow on a cold case") but it is a real UX tax.
**Evidence:** `LIVETEST-V3-REPORT.md` line 32 and line 52, `.demo-rehearsal-state.json` FG-001 / FG-002b.
**Suggestion:** a lower-latency or warm-pool tier for interactive apps, or first-token streaming so a cold request shows progress instead of a 90s blank. Even a documented "expect N seconds cold" would help teams budget their UX.
_Severity: FRICTION_

### Developer Experience (dev.to editor)
**What we hit:** driving the post editor programmatically, the editor never mounted its body/tags field. The page was served as a cached, logged-out HTML shell (no `csrf-token` meta, no `data-user` element) even though the session was authenticated, so `articleForm.js` threw "Couldn't find user data on page."
**Cost to discover:** ~20 minutes, across both editor versions, before reading the console error pinned it to the cached shell.
**Delta:** on an authenticated `/new` (and even the home page) in this context, `document.body.dataset.user` and the CSRF meta were absent, while `window.currentUser` was hydrated client-side. The editor bootstraps from the server-embedded user data, which the cached response lacked.
**Impact:** we could not automate the paste and fell back to a manual paste in a normal browser session, where it mounts fine.
**Evidence:** first-hand this session (console error `Failed to load article form: Error: Couldn't find user data on page` from `articleForm-*.js`).
**Suggestion:** have the article form hydrate user data and CSRF from the client session it already has (`window.currentUser`) rather than hard-requiring the SSR-embedded element, so a cached shell does not brick the editor. A clearer in-editor error ("reload to refresh your session") would also help.
_Severity: FRICTION (worked around manually)_

**Minor (POLISH):** the v1 and v2 editors handle a pasted full-markdown document differently (v1 parses `---` front matter into title/tags/cover; v2 treats it as literal body text). A one-line hint in the editor about which mode parses front matter would save a confused paste.

## Contributions
Each friction, with the fix we used, offered back so the next team skips the discovery cost:
- **TabPFN hosted 503:** wire the client to a **labeled** rules fallback that never silently pretends to be the model, and move the real path to **local open-weight TabPFN** (`TabPFNClassifier` loaded in-process). The 503 becomes a non-event and the verdict stays honest. Pattern in `app/classifier.py`.
- **0G cold latency:** an in-memory cache plus a **serial** pre-warm (one cold request finishes before the next starts, because a single-worker box saturates under concurrent cold calls). This turns a 99s first hit into sub-second repeat hits and keeps a small box alive. Discipline encoded in `DEMO-SCRIPT.md`.
- **dev.to editor mount failure:** switch to the **Basic Markdown (v1)** editor and paste the whole document including front matter in one shot; it sidesteps the un-mounting rich editor and parses title/tags/cover from the `---` block.

## At a Glance
| Category | BLOCKER | FRICTION | POLISH |
|---|---|---|---|
| SDK / API | 1 | 0 | 0 |
| Documentation | 0 | 0 | 0 |
| Infrastructure | 0 | 1 | 0 |
| Developer Experience | 0 | 1 | 1 |
| Sponsor Integration | 0 | 0 | 0 |

## Shareable Summary
Shipping an open-weight AI project on your stack, two things cost us real time and one was a pleasure. Prior Labs' TabPFN auth was flawless, but the hosted **inference** endpoint 503'd across three days while auth stayed up; leading new users to the local open-weight path first (which is also the reliable one) would save a lot of confusion. 0G Compute's open-weight inference gave us an honest result, but ~99s cold latency per fresh request forced a cache-and-pre-warm UX; a warm tier or token streaming would make interactive apps feasible. And the dev.to Basic Markdown editor plus front-matter paste is genuinely nice once you find it. Thanks for a challenge that rewarded doing the open-weight thing properly.
