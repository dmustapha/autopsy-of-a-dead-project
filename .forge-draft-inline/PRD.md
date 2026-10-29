# PRD — Autopsy of a Dead Project

**DEV Hacktoberfest Wk4 "Ghost in the Machine" · SPRINT · 1-day build · entry = a dev.to post**

## 1. One-liner
Paste a public GitHub repo URL. An open tabular foundation model performs a forensic **autopsy** — classifying *how* the project died — and an open-weight language model reads the **coroner's report** aloud. You leave with a shareable death certificate.

## 2. Why it wins (judged axes, heaviest first)
- **Writing quality (heaviest):** the build is a four-beat story — feature-engineering → classification → narration → artifact — that writes up as a gripping first-person post ("I performed an autopsy on my dead side-projects").
- **Theme:** "Ghost in the Machine" read literally — the ghosts of dead code. Spooky (a séance over a commit DAG) + functional (a real verdict) + memorial (an optional eulogy — the Día-de-los-Muertos remembrance note).
- **Creativity:** nobody is turning git forensics into a tabular-ML autopsy; question-shifted off the ghost-story/haunted-terminal herd.
- **Technical:** two distinct open-source AI roles — TabPFN classifies, Groq-served open-weight model narrates.
- **Partner tech:** Render (live durable host) + TabPFN (load-bearing classifier). Tri-track.

## 3. Core user story
> As a developer, I paste a repo URL and in <15s get: a death-mode verdict with confidence, the forensic evidence (the feature table that drove it), and a eulogy I want to share.

## 4. Functional requirements (MUST)
| # | Requirement | Acceptance |
|---|---|---|
| F1 | Accept a public GitHub repo URL (owner/repo or full URL) | Valid URL parsed; bad input → friendly error, no crash |
| F2 | Fetch commit history + contributors via GitHub REST API (public, no auth needed; optional token raises rate limit) | Returns ≥1 commit; handles 404 / empty / archived |
| F3 | Compute a feature table (recency, commit-cadence decay, bus-factor, contributor count, lifespan, commit-velocity trend) | Numeric feature row produced for any repo |
| F4 | **TabPFN** classifies death-mode ∈ {abandoned, pivoted, completed, burned-out, alive} with calibrated confidence, conditioned on the shipped ~50-repo labeled seed dataset | Returns a class + probability vector; seed set is the in-context train data |
| F5 | **Groq open-weight model** narrates a coroner's report / eulogy grounded in the verdict + features | 120–200 word narration that cites the real features (no hallucinated stats) |
| F6 | Render a "death certificate" card (verdict, confidence, cause-of-death, dates, eulogy) with a typing animation | Card visible; screenshot-ready for the post |
| F7 | Deploy live on Render, durable + warm | Public URL responds <2s during judging week |

## 5. Non-goals (explicit scope cuts — Sonnet review)
- ❌ Issues/PR half-life features (paginated, slow) — commit+contributor signals only.
- ❌ Server-side image rendering of the card — DOM card + screenshot.
- ❌ Multi-repo comparison — one URL → one certificate.
- ❌ User accounts, history, persistence — stateless single-shot.
- ❌ Private repos / OAuth.

## 6. The linchpin artifact (MUST build first)
A hardcoded **~50-repo labeled seed dataset** (`seed_repos.csv`): rows = known dead/alive repos, columns = the F3 features, label = death-mode. TabPFN is a few-shot in-context learner — this seed set IS its training data at inference. Without it the classifier is decoration. It doubles as a describable post artifact ("I hand-labeled 50 dead repos").

## 7. Open-innovation narrative (for the post)
Core is open-source AI: **TabPFN** (open weights, Prior Labs) + an **open-weight LLM** (Llama/Qwen) served by Groq. The post shows an **Ollama + Gemma/Qwen fully-local/offline mode** as the open-innovation payoff — anyone can run the autopsy with zero closed dependencies.

## 8. Success metric
A published dev.to post (tags `devchallenge` + `hf26challenge`) with a cover image, embedded demo video/GIF, ≥1 table, first-person title, linking a live Render URL and a public repo — by Oct 31, 18:00 WAT.

---

## 9. The five death-modes (definitions the classifier + narration use)
| Mode | Meaning | Signature in the features | Coroner's framing |
|------|---------|---------------------------|-------------------|
| **abandoned** | Work simply stopped; no closure | high `days_since_last_commit`, `velocity_ratio`≪1 | "left to the dust; the lights were never turned off" |
| **burned_out** | A sole maintainer ran out of energy | `bus_factor`=1, steep negative `commit_cadence_decay` | "one pair of hands carried it until they couldn't" |
| **pivoted** | Short life, then the team moved on | short `lifespan_days`, early-stop | "the idea migrated; this body was left behind" |
| **completed** | Finished its purpose; intentional rest | archived or stable then quiet, decent lifespan | "it did what it came to do, and rested" |
| **alive** | Still breathing | `velocity_ratio`≥~0.8, recent commits | "not dead — merely sleeping; a pulse remains" |

`insufficient_history` is a non-verdict for <2 commits (honest: "no body to examine").

## 10. Detailed acceptance criteria (per functional requirement)
- **F1 URL input** — accepts `https://github.com/owner/repo`, `github.com/owner/repo`, `owner/repo`, trailing slashes, `.git` suffix. Rejects non-GitHub hosts, gists, and malformed input with an inline message. No uncaught exception on any string.
- **F2 GitHub fetch** — returns commits (windowed to `COMMIT_WINDOW`) + contributors + repo meta. Distinguishes 404 (no repo), 403 (rate limit → actionable message), empty repo, archived. Async; total fetch budget ≤4s typical.
- **F3 features** — produces all six numeric features for any repo with ≥2 commits; deterministic given the same commit set; unit-tested against a synthetic series with a known decay slope and bus factor.
- **F4 classify** — returns a class ∈ the 5 modes + a confidence in [0,1] + a full posterior; `engine` flag set; falls back transparently when the client is unreachable.
- **F5 narrate** — 120–200 words, grounded (no number absent from the evidence block), spooky-but-reverent register, one retry on a grounding-check failure.
- **F6 card** — renders verdict, confidence meter, dates, the six-row evidence table, the typed eulogy, and the engine badge; screenshot-clean at 1200×630 (OG size).
- **F7 deploy** — public Render URL, warm (<2s first byte), `/healthz` green, env vars set.

## 11. User journey (happy path)
1. Judge lands on the page (warm, instant). Reads a one-line hook and sees three example graves.
2. Clicks an example (or pastes their own dead repo). Button: "Perform the autopsy."
3. A tasteful "exhuming the commit history…" state (~3–6s).
4. The death-certificate card animates in: cause of death + certainty, born/last-seen dates, the forensic evidence table, and a coroner's report that types itself out.
5. The engine badge reads "classified by TabPFN." The footer links the open-source / Ollama-local mode.
6. The judge screenshots it, or pastes another repo. The story ("an AI performed an autopsy on my dead side-project") is self-evident.

## 12. The post (the actual deliverable) — outline
Working title: **"I performed an autopsy on my dead side-projects. An open-weight AI told me how they died."**
1. Hook — the graveyard of unfinished repos every dev has.
2. The idea — turn git forensics into a tabular-ML autopsy + a coroner's eulogy; the "Ghost in the Machine" reading.
3. How it works — the feature table (a table, the craft element), TabPFN as the classifier, the open-weight coroner.
4. The seed dataset — hand-labeling 50 dead repos, what surprised me (`data/NOTES.md`), class balance.
5. Why open-source AI mattered — TabPFN open weights + open-weight LLM + a fully-local Ollama mode (no keys, runs offline).
6. Building on Render — the live demo, the durable-tier lesson.
7. Demo (embedded GIF/video) + the live link + the repo.
Craft elements present: cover image, embedded demo video, ≥1 table, first-person number-in-title.

## 13. Metrics / definition of done
- The post is published under `devchallenge` + `hf26challenge` by Oct 31 18:00 WAT.
- It contains: cover image, embedded demo video/GIF, ≥1 table, first-person title, live Render link, public repo link, the open-source-AI explanation, the open-innovation paragraph.
- The live app performs a full autopsy on a pasted repo in <15s warm.
- Three demo repos (one each of abandoned / burned_out / alive) are pre-warmed.

## 14. Competitive differentiation
Leading competitor PhantomTerminal (~2k words) ships NO cover image and NO demo video — the two biggest winner-correlated elements. Our post ships both, plus a load-bearing TabPFN story no ghost-story clone has. We question-shift off the haunted-terminal herd into git forensics.

---

## 15. Non-functional requirements
- **Performance:** warm first-byte <2s; full autopsy <15s typical (GitHub fetch + TabPFN + Groq). Example repos are cached → instant.
- **Availability (judging window):** the live URL must respond through the week of Nov 2. Render Starter + `numInstances=1` + an external warm-ping; no free-tier spin-down.
- **Reliability:** every external dependency (GitHub, TabPFN, Groq) has a defined degradation path; no unhandled exception reaches the user.
- **Security:** no secrets client-side; repo-URL allow-listing; narration grounded on numeric evidence only (no repo-text injection surface). See SECURITY.md.
- **Accessibility:** WCAG-minded — semantic landmarks, `aria-live` verdict region, `prefers-reduced-motion` honored, non-color signals, labeled inputs. See §18.
- **Cost:** ≤ $7/mo (Render Starter); TabPFN + Groq on free tiers; GitHub unauth or a free PAT.
- **Portability:** a documented fully-local mode (Ollama + open weights) with zero paid dependencies.

## 16. The seed-dataset labeling rubric (how each repo gets its mode)
The ~50-row `data/seed_repos.csv` is labeled by this rubric so labels are consistent and defensible:
- **alive** — a commit in the last 60 days AND `velocity_ratio` ≥ ~0.8. Pick well-known active repos.
- **completed** — explicitly archived OR a stable library that reached maturity (decent lifespan, deliberate quiet, docs/releases present).
- **abandoned** — no commit in >12 months, no archive flag, `velocity_ratio` ≪ 1, issues left open.
- **burned_out** — single dominant author (`bus_factor`=1), a once-high cadence that decayed steeply to zero.
- **pivoted** — short lifespan (<~4 months of real activity) then a hard stop, often with a README pointing elsewhere or a successor repo.
Target balance: ~10 rows per class (±3). `note` records the human reason — this is the raw material for the post and `data/NOTES.md`. Separability is validated with a quick TabPFN leave-one-out before any UI work (if classes bleed, refine features/labels at B0, not mid-build).

## 17. Edge-case catalog
| Input / condition | Expected behavior |
|---|---|
| Empty repo (0 commits) | `insufficient_history`, honest "no body to examine" copy |
| 1 commit | `insufficient_history` |
| Monorepo with 200k commits | windowed to last `COMMIT_WINDOW`; card notes the window |
| Repo renamed/moved (301) | follow one redirect; else 404 copy |
| Fork with little own history | classify on the fork's own commits; note low signal |
| Private/404 | "couldn't exhume this grave — is it public?" |
| Non-GitHub URL / gist | 422 inline, no fetch attempted |
| GitHub 403 (rate limit) | actionable message; suggest a token; cached examples still work |
| Unicode / emoji repo names | handled (REST returns them; rendered safely) |
| TabPFN timeout | forensic-rules fallback, labeled |
| Groq timeout | cached narration or terse labeled summary |

## 18. Accessibility requirements (acceptance)
- All interactive elements keyboard-reachable; visible focus states.
- The result card is an `aria-live="polite"` region so screen readers announce the verdict.
- Typing animation disabled under `prefers-reduced-motion` (instant text).
- Confidence shown as a number, not only a bar; death-mode is text, not only color.
- Contrast ≥ 4.5:1 for body text on the parchment/dark theme.

## 19. Analytics / success signal (lightweight)
Server logs `{engine, verdict, latency_ms}` per request (no PII). For the post, the interesting
numbers are: how often TabPFN vs fallback served, the death-mode distribution across the demo
repos, and median latency. These become a small results table in the write-up.

## 20. Risks accepted (not mitigated, by choice)
- Death-mode is an inference, not ground truth — stated plainly in UI + post (not a correctness bug).
- Small hand-labeled seed → approximate boundaries — acceptable for a demo; disclosed.
- Commit-only signal misses issue-tracker death — acceptable 1-day scope cut, disclosed in LIMITATIONS.

## 21. Open questions (resolve at build day)
- Exact Wk4 theme prompt text (secret until the live page — DS-1): confirm the framing matches.
- Final narration model: `llama-3.3-70b-versatile` vs a `qwen` variant — pick on output quality at B3.
- Whether to show the full posterior (all 5 probabilities) or just the top verdict — decide on card legibility at B4.

## 22. Glossary (product terms)
- **Autopsy** — the full flow: fetch → features → classify → narrate → certificate.
- **Death certificate** — the shareable result card (the post's hero image).
- **Coroner's report** — the open-weight-LLM narration.
- **Engine badge** — the `tabpfn`/`rules` honesty label on the card.
- **Grave** — a (dead) repository, in the product's voice.

---

## 23. Data contract — `AutopsyResult` (the exact API response)
```json
{
  "owner": "someuser",
  "repo": "abandoned-thing",
  "meta": {
    "stars": 142, "primary_language": "Python",
    "created_at": "2021-03-02", "last_commit_at": "2022-08-14",
    "is_archived": false
  },
  "features": {
    "days_since_last_commit": 806.0,
    "commit_cadence_decay": -3.4,
    "lifespan_days": 530.0,
    "contributor_count": 2.0,
    "bus_factor": 1.0,
    "velocity_ratio": 0.04
  },
  "verdict": {
    "mode": "abandoned",
    "confidence": 0.81,
    "probs": {"abandoned":0.81,"burned_out":0.11,"pivoted":0.05,"completed":0.02,"alive":0.01},
    "engine": "tabpfn"
  },
  "narration": "Here lies abandoned-thing, born in the spring of 2021...",
  "certificate_id": "a1b2c3"
}
```
The frontend binds directly to this shape; `verdict.engine` drives the honesty badge; `probs`
may be shown as a faint secondary breakdown under the headline verdict.

## 24. Why these six features (feature-selection reasoning)
The classifier must separate five modes from *commit-shaped* evidence only (Issues cut). Each
feature earns its place by discriminating at least one mode boundary the others can't:
- `days_since_last_commit` — the single strongest *dead-vs-alive* axis, but blind to *how* it died.
- `velocity_ratio` — normalizes recent vs lifetime rate, so a big old repo that slowed isn't mistaken for a small new one; separates `alive` from `completed`/`fading`.
- `commit_cadence_decay` (slope) — captures the *shape* of the decline; a steep cliff suggests `burned_out`/`abandoned`, a gentle plateau suggests `completed`.
- `lifespan_days` — short life + stop ⇒ `pivoted`; long life ⇒ `completed`/`abandoned`. Disambiguates early death from late death.
- `bus_factor` — the `burned_out` signal: a single author carrying ≥50% share is the burnout shape.
- `contributor_count` — context for bus_factor (bus_factor=1 of 1 vs 1 of 20 mean different things).
Collinearity is acceptable for TabPFN (it is robust to correlated tabular features and small N);
we deliberately keep the set to six for interpretability in the evidence table (the post's craft element). Rejected features: lines-changed (noisy, requires per-commit diffs), stars-over-time (API-expensive), issue half-life (scope cut).

## 25. Narration spec (prompt + grounding check)
System prompt (verbatim intent): a forensic coroner writing a 120–200 word report/eulogy — spooky,
literary, Día-de-los-Muertos reverence — where **every factual claim comes from the evidence block**.
The evidence block passed to the model is a compact factual rendering: repo name, born/last-seen
dates, the verdict + confidence, and the six features with plain-language labels. The model never
sees raw repo text (anti-injection, SECURITY). **Grounding check:** after generation, extract every
integer/float/year token from the narration; if any is absent from the evidence block, retry once
with an explicit "use only these numbers" reminder; if it fails twice, fall back to a templated
non-LLM eulogy labeled as such. Temperature 0.7 for voice, capped at 320 output tokens.

## 26. Personas
- **The judge (primary):** a DEV engineer/community reviewer skimming many posts. Wants to *get it*
  in 10 seconds (the certificate card does that) and to see a real, honest technical story.
- **The builder-reader (secondary):** a dev who clicks through, pastes their own dead repo, feels
  the "oof, mine's abandoned too" moment, and reacts/shares (reactions are the tiebreaker).

## 27. Assumptions & dependencies
- GitHub REST is reachable and public repos are readable unauth (rate-limited) — optional PAT lifts it.
- `tabpfn-client` hosted inference is available with a token; else the labeled fallback serves.
- Groq free tier serves `llama-3.3-70b-versatile`; else Ollama-local or templated eulogy.
- Render Starter credits (hacktoberfest promo) or $7/mo available.

## 28. Self-scoring against the judging rubric
| Axis (weight) | How this entry scores high |
|---|---|
| Writing (heaviest) | First-person autopsy narrative, NOTES.md observations, a results table, cover+video |
| Theme | "Ghost in the Machine" = ghosts of dead code; coroner/eulogy + DdlM remembrance |
| Creativity | Git forensics → tabular-FM autopsy; nobody in the herd does this |
| Technical | Two open-source AI roles; honest fallback; live on Render |
| Partner | Render (live durable) + TabPFN (load-bearing) — tri-track |

## 29. Future work (v2, out of scope now)
Issue/PR-tracker signals; multi-repo graveyard comparison; a "revival prescription" (what it would
take to bring it back); an org-wide graveyard scan; fine-grained per-file decay heatmap.

## 30. The three example repos (pre-warmed, one-click)
Curated so a judge sees contrast instantly without pasting anything:
| Slot | Repo profile | Expected mode | Why chosen |
|---|---|---|---|
| 1 | A famously abandoned once-popular repo | `abandoned` | the archetypal grave; high confidence |
| 2 | A single-maintainer project that stalled | `burned_out` | shows bus_factor=1 story |
| 3 | A currently-thriving well-known repo | `alive` | the contrast case — "not dead, merely sleeping" |
Exact repos are chosen at B0 from the seed set (never a repo whose result would embarrass a living maintainer — prefer archived/clearly-inactive or giant-active). Results are cached at startup so the demo never cold-calls.

## 31. User-facing copy (error + edge states)
| State | Exact message (voice-consistent) |
|---|---|
| bad URL | "That doesn't look like a GitHub grave. Try `owner/repo`." |
| 404 / private | "Couldn't exhume this grave — is the repository public?" |
| empty / <2 commits | "No body to examine — this repo has almost no history." |
| rate limited | "The gatekeeper (GitHub) is rate-limiting us. Try again shortly, or add a token." |
| model unavailable | "Classified by forensic rules (the model is resting). Verdict is an estimate." |
| success | (the certificate card; no banner) |

## 32. Card voice & copy guidelines
The product speaks as a gentle, literary coroner — reverent, never mocking a maintainer. Deaths are
described with dignity (Día-de-los-Muertos remembrance, not ridicule). Verbs: *exhume, rest, pulse,
linger, remember*. The eulogy closes on a note of respect, even for `abandoned`. This voice is the
post's emotional texture and must be consistent across UI strings and narration.

## 33. Definition of "done" for the app (gate into package)
A pasted public repo returns a correct-shaped `AutopsyResult` with `engine="tabpfn"` on the happy
path, renders the full certificate (verdict + confidence + dates + six-row evidence table + typed
eulogy + engine badge), live on a warm Render URL, with the three examples pre-warmed and
screenshotted into `evidence/`. Only then does package write the post.

## 34. Out-of-scope confirmations (explicit, to prevent scope creep mid-build)
Not building: authentication, user accounts, saved autopsy history, a database, multi-repo
comparison, issue/PR-tracker analysis, server-side image generation, private-repo support,
payment, email, or any background job system. Each is a deliberate cut; revisit only in v2 (§29).

## 35. Dependency & version pins (product-visible)
Python 3.11; `tabpfn-client` (hosted inference, pinned minor); Groq model `llama-3.3-70b-versatile`
(swap target `qwen-2.5-72b` if quality/latency favors it at B3); Tailwind via CDN (no pinned build).
Any model swap is a one-line env change (`LLM_MODEL`) and must not change the response contract (§23).

## 36. Theme-interpretation statement (for the post's theme section)
"Ghost in the Machine" is read literally: every repository that stops is a ghost left in the
machine — unfinished intent, haunting its own commit history. The app is a séance that lets the
ghost speak once more: a forensic verdict on *how* it died, and a coroner's eulogy that remembers
it. The Día-de-los-Muertos layer is the reverence — we do not mock dead code, we hold a vigil for
it. This is the honest answer to the challenge prompt, not a spooky skin: the mechanism (git
forensics → tabular classification → remembrance) only makes sense *as* a meditation on death.

## 37. The results table the post will report (measurement plan)
The post needs ≥1 table (winner-correlated craft element). Beyond the evidence table in the card,
the write-up reports measured run data captured via the §19 request log across the demo + seed repos:
| Metric | Source | Why it's in the post |
|---|---|---|
| TabPFN vs fallback mix | `engine` field counts | proves the model actually served (honest) |
| Death-mode distribution | `verdict.mode` counts over the seed+demo set | the "graveyard census" hook |
| Median / p90 latency (warm) | `latency_ms` | shows it's genuinely live, not a mockup |
| LOO classifier separation | B0 validation | evidence the seed set is real signal, not noise |

## 38. Reactions strategy (the published tiebreaker)
Reactions break ties on DEV. The design optimizes for the "paste my own dead repo → oof" moment that
makes a reader react: a one-click example to lower friction, a shareable certificate with a permalink
id, and a closing line in the post inviting readers to autopsy their own graveyard and share the verdict.

---

# PART II — DETAILED PRODUCT SPECIFICATION

## 40. Detailed user flows (step-by-step)

### Flow A — happy path (dead repo)
1. User lands on `/` (warm). Sees title, subtitle, a paste field, and three example chips.
2. User pastes `owner/deadrepo` and clicks "Perform the autopsy" (or presses Enter).
3. Client validates non-empty; POSTs `{repo_url}` to `/autopsy`; shows the "exhuming…" state.
4. Server parses URL → fetches commits/contributors → builds features → TabPFN classifies → Groq narrates.
5. Server returns `AutopsyResult`. Client hides loading, reveals the certificate card.
6. Card shows cause of death, confidence, born/last-seen, the six-row evidence table.
7. The coroner's report types out (or appears instantly under reduced-motion).
8. Engine badge reads "classified by TabPFN". User screenshots / pastes another repo.

### Flow B — example chip (one-click)
1. User clicks an example chip. Client sets the input + submits.
2. Result is cached (pre-warmed at startup) → returns instantly. Same render as Flow A.

### Flow C — alive repo (the twist)
1. User pastes an active repo. Verdict = `alive`; eulogy reads "not dead, merely sleeping."
2. Reinforces that the model discriminates, not just declares everything dead.

### Flow D — bad input
1. User pastes a non-GitHub URL / gibberish. Client POSTs; server raises `BadRepoURL` → 422.
2. Client shows inline "That doesn't look like a GitHub grave. Try `owner/repo`." No crash, field retained.

### Flow E — private/404
1. Server `fetch_repo` → 404. Client shows "Couldn't exhume this grave — is the repository public?"

### Flow F — empty/insufficient history
1. `build_features` raises `insufficient_history` → 422 "No body to examine — too little commit history."

### Flow G — model unavailable
1. TabPFN client down → classifier returns `engine="rules"`. Card badge reads "forensic-rules estimate — model unavailable." Verdict still renders; honesty preserved.

### Flow H — GitHub rate limit
1. `fetch_repo` → 403 rate-limited → 422 "The gatekeeper (GitHub) is rate-limiting us. Try again shortly." Cached examples still work.

## 41. UI state spec (every screen state)
| State | Visible elements | Transitions |
|---|---|---|
| Idle | header, form, example chips, footer | submit → Loading |
| Loading | "exhuming the commit history…" (pulse), form disabled | success → Result; error → Error |
| Result | certificate card (verdict, confidence, dates, evidence table, typed eulogy, engine badge) | new submit → Loading |
| Error | inline red box with the in-voice message; form re-enabled | new submit → Loading |
| Reduced-motion | identical but eulogy appears instantly; no pulse animation | — |

## 42. Wireframe (textual)
```
┌───────────────────────────────────────────┐
│          Autopsy of a Dead Project          │
│   Every repo that stops is a ghost…         │
│  ┌─────────────────────────┐ [Perform ▸]   │
│  │ owner/repo or URL        │                │
│  └─────────────────────────┘                │
│  try: react · flask · <dead> (chips)        │
│                                             │
│  ┌── Certificate of Death ──── No.a1b2c3 ──┐│
│  │ Deceased:  owner/repo                    ││
│  │ Cause:     abandoned        [███░░] 81%  ││
│  │ Born:      2021-03-02                    ││
│  │ Last seen: 2022-08-14                    ││
│  │ ── Forensic evidence ──                  ││
│  │  Days since last commit        806       ││
│  │  Commit-cadence decay         -3.4       ││
│  │  Lifespan (days)               530       ││
│  │  Contributors                    2       ││
│  │  Bus factor                      1       ││
│  │  Velocity ratio               0.04       ││
│  │ "Here lies owner/repo, born in the…"     ││
│  │ classified by TabPFN                     ││
│  └──────────────────────────────────────────┘│
└───────────────────────────────────────────┘
```

## 43. Full risk register
| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|----|------|:---:|:---:|-----------|-------|
| R1 | TabPFN not load-bearing w/o labeled rows | Med | High | ship ~50-repo seed; B0-first; validate LOO | build |
| R2 | Render free spins down → dead judging demo | High | High | Starter + numInstances=1 + warm-ping | deploy |
| R3 | GitHub Issues API pagination burns time | Med | Med | cut from core features (commits only) | build |
| R4 | Server-side card render adds deploy complexity | Med | Med | DOM card + screenshot | build |
| R5 | Death-mode labels not separable from features | Med | High | validate LOO at B0; refine features/labels | build |
| R6 | Groq rate limit during demo | Med | Med | cache narration; pre-warm examples | build |
| R7 | TabPFN client/token friction headless | Med | Med | hosted client w/ token; pre-build verify | build |
| R8 | Theme reads as a spooky skin, not genuine | Med | Med | coroner/eulogy narrative; read live page DS-1 | package |
| R9 | Writing (heaviest axis) starved by app overrun | Med | High | timeboxed day; reserved post block | package |
| R10 | Large repos slow git fetch | Low | Med | COMMIT_WINDOW cap + loading state | build |
| R11 | RAM >512MB on Starter | Low | Med | lazy imports; bump tier w/ credits | deploy |
| R12 | Narration hallucinates a number | Med | Med | grounding check + retry + templated fallback | build |
| R13 | A demoed repo embarrasses a living maintainer | Low | Med | only demo archived/giant-active repos | demo |
| R14 | dev.to tags wrong → invalid entry | Low | High | checklist: devchallenge + hf26challenge both | package |

## 44. Metrics & instrumentation (detail)
- Per request, log `{owner_repo_hash, engine, verdict, confidence, latency_ms}` (no PII, no repo text).
- Derive for the post: engine mix (tabpfn vs rules), death-mode distribution, median/p90 latency, LOO accuracy.
- A simple counter of autopsies performed (for the "N graves examined" line in the post, if notable).

## 45. Competitive analysis (detail)
- **PhantomTerminal** (leading competitor): ~2k-word polished post, but NO cover image and NO demo video — the two strongest winner-correlated elements. We ship both.
- **Ghost-story generators / haunted terminals (the herd, 9+):** generative-text toys; AI is decoration, no measurable artifact, heavy theme-overlap collision. We question-shift into git forensics with a load-bearing tabular model.
- **Our moat:** two distinct open-source AI roles + a shareable forensic artifact + a first-person build-story with real numbers (the NOTES.md observations). Hard to clone in the remaining window.

## 46. Release criteria (go / no-go for publishing the post)
GO when: the live app completes a real autopsy <15s warm with `engine="tabpfn"`; three examples pre-warmed + screenshotted; the post has all craft elements (cover, video, table, first-person title), both tags, live link, repo link, the open-source explanation; internal cutoff Oct 31 18:00 WAT not breached. NO-GO (fix first) if the live URL is cold, the engine badge shows `rules` on the happy path (token/seed issue), or any craft element is missing.

## 47. The post — full working draft (the deliverable; package refines)
Target ~1,800 words. Title: **"I performed an autopsy on 50 of my dead side-projects. An open-weight AI told me how each one died."**

### §1 Hook (~150 words)
Every developer has a graveyard. Mine is a GitHub profile full of repos that started with a burst of
commits and then — nothing. A half-built game engine. A "this time I'll finish it" note-taking app.
I never knew *why* each one died, or whether they died the same way. So for the DEV "Ghost in the
Machine" challenge I built a coroner for dead code: paste a repo, and an open tabular AI performs an
autopsy — classifying *how* it died — while an open-weight language model reads the eulogy.

### §2 The idea & the theme (~200 words)
"Ghost in the Machine," read literally: a repository that stops is a ghost — unfinished intent
haunting its own commit history. The app is a séance that lets the ghost speak once: a forensic
verdict and a remembrance. The Día-de-los-Muertos layer is reverence — we hold a vigil for dead
code, we don't mock it. [screenshot: the death-certificate card]

### §3 How it works (~350 words, includes the evidence table)
Three steps. (1) I pull a repo's commit history from the GitHub API and compute six forensic
features — days since last commit, commit-cadence decay, lifespan, contributor count, bus factor,
and a velocity ratio. (2) I feed that feature row to **TabPFN**, Prior Labs' open-weight tabular
foundation model, which classifies the death-mode against a seed set of 50 repos I hand-labeled.
(3) An **open-weight Llama model** (served by Groq) writes the coroner's report, grounded strictly
in the evidence so it never invents a number. [table: the six features for an example repo]
Why TabPFN and not a rules engine? Because the whole point is that the *model* decides — remove it
and you have a git-stats page, not an autopsy.

### §4 The seed dataset (~300 words — the human story)
TabPFN is a few-shot in-context learner: it needs examples at inference. So I spent an afternoon
hand-labeling 50 dead (and a few living) repos. [weave in 3–5 real observations from data/NOTES.md —
the ones that surprised me]. The labeling itself taught me the taxonomy: abandoned, pivoted,
completed, burned_out, alive. [screenshot/table: the class distribution — the "graveyard census"]

### §5 Why open-source AI mattered (~300 words)
Both models are open: TabPFN's weights are public, and the narration runs on an open-weight LLM. To
prove it, there's a fully-local mode — point it at Ollama and it runs on your laptop with zero API
keys, offline. [code block: the one env change]. Open weights meant I could reason about the model,
swap it, and ship a version with no closed dependency in the core — exactly the "open innovation"
the challenge asks for.

### §6 Building & shipping on Render (~250 words)
It's one small Python service — FastAPI, server-rendered, no build step — which made Render deploy
trivial. One lesson worth sharing: the free tier spins down after 15 minutes idle, so a judge
landing during judging week would hit a dead link. I deployed on a durable warm tier and added a
health-check ping. [screenshot: the live app]

### §7 Try it / close (~150 words + embeds)
[embedded demo GIF/video] Live: [link]. Code: [repo]. Go autopsy your own graveyard — and tell me
how yours died. [closing line inviting reactions — the tiebreaker]

Craft-element audit: cover image ✓ (the certificate card), demo video ✓, ≥1 table ✓ (evidence +
census), first-person number-in-title ✓.

## 48. Seed-dataset labeling guide (detailed, per-mode decision rules)
For each candidate repo, apply in order; record the deciding reason in `note`:
- **alive** — a commit within ~60 days AND velocity_ratio ≥ ~0.8. Examples: large active frameworks. Pick repos that are unambiguously thriving so the class anchor is clean.
- **completed** — explicitly archived with a "done/maintenance" README, OR a mature library with a long lifespan that reached a deliberate, stable quiet (tagged releases, low but non-zero recent activity). The key discriminator vs abandoned: *intentional* rest, usually archived or clearly finished.
- **abandoned** — no commits >12 months, NOT archived, open issues ignored, velocity_ratio ≪ 1. The archetype: a once-active repo that simply stopped with loose ends.
- **burned_out** — a single dominant author (bus_factor=1) whose once-high cadence decayed steeply to zero. Discriminator vs abandoned: the *shape* (a cliff driven by one person) and the single-maintainer signature.
- **pivoted** — short real lifespan (<~4 months active) then a hard stop, often with a README pointing to a successor or the team's new direction. Discriminator vs abandoned: *early* death + a redirect.
Balance target: ~10 per class (±3). Avoid small living personal repos whose "abandoned" label could embarrass an author; prefer famous archived or giant-active repos. If two classes bleed in the LOO check, add 2–3 sharper exemplars to the bleeding pair rather than relabeling arbitrarily.

## 49. Data dictionary (every field)
| Field | Type | Range/units | Meaning |
|---|---|---|---|
| repo_url | str | — | user input; parsed to owner/repo |
| days_since_last_commit | float | days ≥0 | recency of the last commit |
| commit_cadence_decay | float | slope | monthly-commit-count trend over lifespan (neg = declining) |
| lifespan_days | float | days ≥1 | first→last commit span |
| contributor_count | float | ≥1 | distinct commit authors |
| bus_factor | float | ≥1 | authors making up ≥50% of commits |
| velocity_ratio | float | ≥0 | recent-90d rate ÷ lifetime rate |
| verdict.mode | enum | 5 modes + insufficient | the death-mode |
| verdict.confidence | float | 0..1 | top-class posterior probability |
| verdict.engine | enum | tabpfn/rules | honesty flag |
| meta.is_archived | bool | — | GitHub archive flag |
| certificate_id | str | 6 hex | shareable card id |

## 50. Accessibility spec (detailed acceptance)
- Keyboard: form reachable + submittable by keyboard; example chips are `<button>`s; visible focus rings.
- Screen reader: the certificate is `aria-live="polite"` so the verdict is announced on arrival; the evidence `<table>` has a `<caption>`.
- Motion: typewriter effect gated on `prefers-reduced-motion` (instant text fallback); no essential info conveyed only by animation.
- Color: death-mode is text (not only color); confidence is a number (not only a bar); contrast ≥4.5:1 on the dark theme.
- Content: error messages are specific and actionable, never color-only.

## 51. Day-by-day (PRD-level; PLAN has the hour-level)
Single build day: PRE-BUILD (tokens, live-page read) → B0 seed → B1 features → B2 classify → B3
narrate → B4 UI → B5 deploy → B6 demo-prep → **reserved post block**. Buffer: if the day compresses,
app polish is cut, never the post. Publish by Oct 31 18:00 WAT.

## 52. Sample coroner narrations (quality target per death-mode)
These are the bar the narration must hit — grounded, reverent, literary. Build tunes the prompt until output is in this register.

**abandoned** (days_since=806, velocity=0.04):
> Here lies owner/repo, who drew its first commit in the spring of 2021 and its last on an August
> afternoon in 2022. For 806 days the cursor has not blinked. Two hands once tended it; one did most
> of the work, and then that one went quiet. The issues remain open, small doors left ajar in an
> empty house. Cause of death: abandonment — not a dramatic end, just a slow turning-away. Rest now.

**burned_out** (bus_factor=1, decay=-3.4):
> A single pair of hands carried owner/repo from its first commit to its last. The cadence tells the
> story: a steep, lonely decline, the graph of someone running out of evenings. There was no second
> maintainer to catch it when it fell. Cause of death: burnout. It was loved hard by one person, and
> that is its own kind of eulogy.

**pivoted** (lifespan=90, successor noted):
> owner/repo lived a brief, bright ninety days. Then the commits simply moved — the idea survived,
> but in another body. This grave is not a failure; it is a chrysalis. Cause of death: pivot.

**completed** (archived, stable):
> owner/repo did what it came to do and was laid to rest on purpose — archived, finished, at peace.
> Cause of death: completion. The rarest and happiest verdict a project can receive.

**alive** (velocity=1.1):
> Not dead. owner/repo still breathes — a commit only days ago, a steady pulse across many hands.
> We came for an autopsy and found a living thing. Put down the scalpel; this one is merely sleeping.

## 53. Judge/user FAQ (anticipated)
- **Is the death-mode "true"?** No — it's an inference from commit-shaped evidence, stated as "likely cause." Honesty is a product invariant (I3).
- **What makes the AI open-source?** TabPFN has open weights; narration runs on an open-weight LLM (and a fully-local Ollama mode exists). No closed model in the core path.
- **Why TabPFN and not a classifier I trained?** No time to train/tune in a 1-day build, and TabPFN's strength is exactly small-N tabular in-context learning — the seed set is its training data.
- **Does it store my repo / data?** No. Stateless, single-shot; only an anonymized request log for the post's metrics.
- **Will it work during judging?** Yes — durable warm Render tier + health-ping; cached examples are instant.
- **Can I run it without API keys?** Yes — the documented Ollama-local mode.

## 54. Expanded per-feature acceptance (test-mapped)
| Feature | Acceptance test | Lives in |
|---|---|---|
| F1 URL parsing | 5 valid forms → (owner,repo); 5 invalid → BadRepoURL | test_validators.py |
| F2 fetch | 404/empty/rate-limit each mapped to a RepoError kind | (manual + github.py) |
| F3 features | synthetic series → known decay-slope, bus-factor, velocity within tol | test_features.py |
| F4 classify | class in set, confidence∈[0,1], posterior sums≈1, engine set; fallback labeled | test_classifier_shape.py |
| F5 narrate | no number absent from evidence survives (grounding) | test_narration_grounding.py |
| F6 card | all fields + engine badge render; 1200×630 screenshot-clean | manual |
| F7 deploy | /healthz ok:true, tabpfn_reachable:true, warm <2s | manual + livetest |

## 55. Demo narration script (what I say over the clip)
"Every dev has a graveyard of dead side-projects. This one tells you how each died. I paste a repo…
it pulls the commit history, computes six forensic features, and an open tabular model — TabPFN —
classifies the death-mode. Abandoned, 81% confident. Here's the evidence that drove it. And an
open-weight model reads the eulogy. Here's one that burned out — single maintainer, steep decline.
And one that's still alive — not dead, merely sleeping. All open-source AI, live on Render, runs
fully local on Ollama too."

## 56. Constraints
- **Time:** one build day + a reserved post block before Oct 31 18:00 WAT.
- **Platform:** must deploy live on Render (partner category) as one web service.
- **Model:** core AI must be open-source (rule) — TabPFN + open-weight LLM.
- **Originality:** brand-new in-window, no pre-existing code (rule).
- **Budget:** ~$7/mo Render; free tiers elsewhere.

## 57. Dependencies (external services the product relies on)
- GitHub REST API (public, rate-limited; optional PAT).
- TabPFN hosted inference (`tabpfn-client`, token).
- Groq API (open-weight model; free tier) OR Ollama-local.
- Render (durable Starter hosting).

## 58. Roadmap (post-submission, non-blocking)
v1.1: issue/PR-tracker signals; v1.2: a "revival prescription" (what it'd take to resurrect);
v1.3: org-wide graveyard scan + a shareable leaderboard of death-modes; v2: fine-tuned death-mode
model trained on a larger labeled corpus.

## 59. What a judge sees in the first 10 seconds (the bar)
A clear title that states the concept; a one-click example that instantly shows a death-certificate
card with a real verdict, a confidence number, an evidence table, and a literary eulogy; and an
"open-source AI" footer. If a judge gets the whole idea without reading the post, the card has done
its job — and that card is the post's cover image.

---

# PART III — THESIS & FORGE ARTIFACTS

## 60. Thesis (the winning argument, formalized)
**WINNING ARGUMENT:** On a platform where the post is judged hardest, the entry that wins pairs a
genuinely load-bearing open-source-AI mechanism with a first-person build-story that has real
numbers and a shareable artifact. "Autopsy of a Dead Project" is that entry: TabPFN's verdict is the
product (substitution test passes), and the write-up — hand-labeling 50 dead repos, a graveyard
census, a coroner's eulogy — is a story only this build can tell.

### 60.1 Five strategic invariants (the bets that must hold for the thesis)
1. **TabPFN carries the verdict.** If classification ever becomes a rules engine dressed up as the model, the whole premise collapses. (Enforced: INVARIANTS I2.)
2. **The post is the product.** App scope never grows at the post's expense. (I8.)
3. **Honesty is the voice.** Every fallback is labeled; the coroner never invents. Judges trust an honest build. (I3, I4.)
4. **The artifact is shareable.** The death-certificate card must be screenshot-worthy — it is the cover image and the reaction magnet. (F6.)
5. **The core is open.** TabPFN open weights + open-weight LLM + a local mode. No closed model in the core. (I1.)

### 60.2 Six drift tripwires (if any fires, stop and re-plan)
1. The classifier's happy-path badge reads `rules` (TabPFN not actually serving) → the TabPFN story is dead; fix tokens/seed before anything else.
2. B0 slips past its timebox → the linchpin is at risk; cut to a smaller separable seed, don't abandon it.
3. App polish is eating the reserved post block → stop polishing, write.
4. Render demo link is cold when tested → durability failed; fix tier/warm-ping before demo.
5. Narration starts citing numbers not in the evidence → grounding check broken; fix before demo.
6. The concept starts reading as a generic ghost-story (theme-skin) → re-anchor on forensics + remembrance; re-read the live challenge page.

## 61. [C] Concerns register (open concerns carried into build)
| ID | Concern | Status / resolution path |
|----|---------|--------------------------|
| C1 | Will 50 seed rows give TabPFN enough signal? | Validate LOO at B0; TabPFN is designed for small-N; add sharper exemplars if bleeding. |
| C2 | Is "death-mode" a defensible construct? | Framed as inference, not fact (I3); the labeling rubric is published; the post owns the caveat. |
| C3 | Groq model availability/limits on the day | Cache + pre-warm; Ollama-local fallback; templated eulogy last resort. |
| C4 | Render Starter RAM headroom | Spot-check at B5; lazy imports; bump tier on credits if needed. |
| C5 | Exact Wk4 theme prompt unknown pre-launch | DS-1: read the live page build day; the concept fits "Ghost in the Machine" strongly regardless. |
| C6 | Picking demo repos that won't embarrass a maintainer | Only archived/giant-active; rule in the demo runbook. |

## 62. Safety / content architecture
- **No PII, no persistence:** stateless; only anonymized request logs (hashed repo key).
- **Reverent voice:** the coroner never mocks a maintainer; deaths are described with dignity (DdlM remembrance). This is a content-safety choice, not just tone — a public tool that ridiculed real people's abandoned work would be a reputational and ethical failure.
- **Input safety:** repo-URL allow-listing; GitHub calls only to parsed owner/repo; narration grounded on numeric evidence (no repo-text → no injection surface).
- **Opt-out of embarrassment:** examples are archived/giant repos; the tool classifies what the user chooses to paste; nothing is published or shared without the user's action.

## 63. Technical-spike source pins (what was verified, with pointers)
- **TabPFN usage:** `tabpfn-client` provides `TabPFNClassifier` with sklearn-style `fit`/`predict_proba`; small-N in-context is the designed use (Prior Labs docs). Pin: `tabpfn-client==0.1.6`.
- **Groq OpenAI-compatibility:** `base_url=https://api.groq.com/openai/v1` with the `openai` SDK; `llama-3.3-70b-versatile` available on the free tier (Groq docs). Pin: `openai==1.54.4`.
- **GitHub REST:** `/repos/{o}/{r}`, `/commits` (paginated, `per_page=100`), `/contributors`; unauth 60/hr, PAT 5,000/hr (GitHub docs).
- **Render:** Starter plan, `numInstances`, `healthCheckPath`, env `sync:false` secrets (Render blueprint docs). Free tier spins down at 15 min idle (dl-1, verified).
- **FastAPI/Uvicorn:** server-rendered Jinja2 + static mount; `on_event("startup")` pre-warm hook.

## 64. Success criteria scoring (detailed, against the five judged axes)
| Axis | Weight | Target evidence | Self-assessment |
|---|---|---|---|
| Writing | heaviest | ~1,800-word first-person build-story, NOTES.md observations, results table, cover + video | strong — the whole plan protects this |
| Theme | high | literal "ghosts of dead code" + DdlM remembrance; not a skin | strong — mechanism IS a meditation on death |
| Creativity | high | git forensics → tabular-FM autopsy; off-herd | strong — unique in the field |
| Technical | med | two open-source AI roles, honest fallback, live on Render, tests green | strong |
| Partner | med | Render (live durable) + TabPFN (load-bearing) | strong — tri-track |

## 65. Open questions carried to build (resolve build-day)
- Final narration model (`llama-3.3-70b-versatile` vs a `qwen` variant) — pick on B3 output quality.
- Whether to surface the full 5-class posterior or just the headline verdict — decide on card legibility at B4.
- Exact three example repos — choose at B0 from the seed set (safe repos only).
- Exact live challenge-page framing (DS-1) — confirm build-day before locking the theme section.

## 66. Observability / analytics events (spec)
| Event | Fields (no PII) | Purpose |
|---|---|---|
| `autopsy_requested` | repo_key_hash, ts | volume; "N graves examined" line |
| `autopsy_completed` | engine, verdict_mode, confidence_bucket, latency_ms | engine mix, census, latency for the results table |
| `autopsy_error` | kind (bad_url/404/empty/rate/model_down) | reliability picture |
| `example_clicked` | slot | which example lands best |
| `startup_prewarm` | ok/failed per example | demo-readiness signal |
Logs are structured JSON lines, no secrets, no raw repo text; retention is ephemeral (process-local).

## 67. Comparison to the organizer's example prompts (why ours is distinct)
The brief suggests haunted terminals, virtual ofrenda builders, offline chatbots, oral-history
tools, ghost-story generators. These cluster into "generative-text toy" (AI as decoration) or
"memorial UI." Ours is neither: it is a **forensic classifier** where the AI produces a *measurable
verdict* over real data, with the generative layer as the eulogy on top. The "ghost" is literal
(dead code), the mechanism is honest (a tabular model), and the artifact is shareable (a certificate).
That distinctness is the anti-collision moat (warroom kill-list: avoid the herd).

## 68. Non-functional acceptance checklist
- [ ] Warm first-byte <2s (measured on the live Render URL).
- [ ] Full cold autopsy <15s (new repo, not cached).
- [ ] No unhandled 500 across the Flow A–H matrix.
- [ ] No secret in repo/client/logs (grep check).
- [ ] WCAG checks (keyboard, aria-live, reduced-motion, contrast) pass.
- [ ] Runs fully local via Ollama with no API keys (documented mode works).
- [ ] Four unit tests green in CI.

## 69. Post craft checklist (the winner-correlated elements — cross-ref SUBMISSION_STATUS)
- [ ] Cover image = the death-certificate card (1200×630).
- [ ] Embedded demo GIF/video near the top.
- [ ] ≥1 table (evidence table + graveyard-census results table).
- [ ] First-person, number-in-title.
- [ ] ~1,500–2,500 words.
- [ ] Both tags `devchallenge` + `hf26challenge`.
- [ ] Live link + public repo link.
- [ ] Open-source-AI explanation + open-innovation (Ollama-local) paragraph.
- [ ] A closing line inviting readers to autopsy their own graveyard (reactions = tiebreaker).

## 70. Stakeholder map
| Stakeholder | Interest | How the product serves it |
|---|---|---|
| DEV judge | a well-written, honest, on-theme build | the post + the honest engine badge + the live demo |
| Render (partner) | a real, live, durable deployment | warm Starter deploy with a health check |
| Prior Labs / TabPFN (partner) | a genuine, load-bearing use of TabPFN | classification IS the verdict (substitution test) |
| The builder (Dami) | a shippable 1-day win + a reusable pattern | small scope, reserved post block, a clean repo |
| The reader-dev | a relatable "oof, mine's dead too" moment | paste-your-own-repo + a shareable certificate |

## 71. Glossary (full)
- **Autopsy** — the end-to-end flow: fetch → features → classify → narrate → certificate.
- **Death certificate** — the result card; the post's hero image.
- **Coroner's report** — the open-weight-LLM narration (the eulogy).
- **Death-mode** — abandoned / pivoted / completed / burned_out / alive (+ insufficient_history).
- **Engine badge** — the `tabpfn`/`rules` honesty flag on the card.
- **Seed dataset** — `data/seed_repos.csv`, the ~50 labeled rows that are TabPFN's in-context train set.
- **Velocity ratio** — recent-90d commit rate ÷ lifetime rate; the primary alive/fading signal.
- **Bus factor** — the number of authors making up ≥50% of commits; =1 is the burnout signature.
- **Substitution test** — remove TabPFN; if only a rules page remains, TabPFN was load-bearing (it is).
- **Grounding check** — the post-generation test that the narration cites no number absent from the evidence.
- **Ollama-local mode** — the zero-closed-dependency path proving the core is genuinely open-source.
- **Grave** — a (dead) repository, in the product's voice.

## 72. Document control
Product intent lives here (PRD). System design + all code → ARCHITECTURE.md. Build order + commands
→ PLAN.md. Build-agent law → INVARIANTS.md. Decisions → DECISIONS.md. Honest gaps → LIMITATIONS.md.
Threat model → SECURITY.md. Submission requirements → SUBMISSION_STATUS.md. Winner rationale →
warroom/WINNER-BRIEF.md + FINAL-VERDICT-V1.md. This PRD is authoritative for *what* and *why*; the
ARCHITECTURE is authoritative for *how*.

## 73. Content & voice style guide (for every user-facing string + narration)
- **Register:** a gentle, literary coroner at a Día-de-los-Muertos vigil. Reverent, never flippant.
- **Allowed verbs:** exhume, rest, linger, pulse, remember, lay to rest, draw its last commit.
- **Forbidden:** mockery ("lol dead"), blame of a named maintainer, hype words ("revolutionary", "game-changing"), emoji in the narration body.
- **Length:** narration 120–200 words; UI strings one short sentence.
- **Honesty markers:** when the model is unavailable, the string says so ("the model is resting").
- **Capitalization:** death-modes shown capitalized in the UI (Abandoned), lowercase in the API enum.
- **Second person vs third:** the eulogy speaks *of* the repo (third person, "here lies"), not *to* the user.

## 74. Manual QA script (run before deploy + before demo recording)
1. Start the app locally (`make dev`); open `/`.
2. Idle state: title, subtitle, form, three example chips, footer all present.
3. Click example #1 (dead) → loading → certificate with verdict + confidence + evidence table + typed eulogy + `tabpfn` badge.
4. Click example #3 (alive) → `alive` verdict, "not dead, merely sleeping" register.
5. Paste a bad URL (`not a repo`) → inline 422 message, no crash, input retained.
6. Paste a private/nonexistent repo → "couldn't exhume this grave" message.
7. Paste a 1-commit repo → "no body to examine".
8. Unset `TABPFN_TOKEN`, restart, repeat #3 → `rules` badge, verdict still renders.
9. Keyboard-only: tab to the field, type, Enter → works; focus rings visible.
10. Toggle OS reduced-motion → eulogy appears instantly (no typewriter).
11. `curl /healthz` → `{ok:true, seed_rows:~50, tabpfn_reachable:true}`.
12. Screenshot the card at 1200×630 → clean, legible, no overflow.
All twelve pass = ready to deploy/record.

## 75. Test data & fixtures
- **Unit fixtures:** synthetic commit series (code-generated in `test_features.py`) with known decay/bus-factor — no network.
- **Classifier fixture:** a `Features` instance with abandoned-shaped values (`test_classifier_shape.py`).
- **Narration fixture:** a monkeypatched Groq client returning a fabricated-number string (`test_narration_grounding.py`).
- **Live smoke set (manual):** three real repos (one each abandoned / burned_out / alive) — the example chips, chosen at B0 from the seed set.
- **No fixture mocks the GitHub/TabPFN/Groq network in unit tests except the narration grounding monkeypatch** — live integration is covered by the manual smoke + the livetest phase (documented gap, intentional).

## 76. Failure-injection drills (demo-rehearsal)
- Kill the TabPFN token → confirm the `rules` badge appears and the app still returns a verdict.
- Point `LLM_BASE_URL` at a dead host → confirm the templated eulogy fallback and no crash.
- Paste a 50k-commit repo → confirm the COMMIT_WINDOW cap keeps latency bounded.
- Hit `/autopsy` 20× fast → confirm the soft rate limit + cache keep quotas safe.

## 77. Acceptance sign-off (the single gate into package)
The app is accepted for the post when the Manual QA script (§74) passes all twelve, the live Render
URL is warm, the three examples are pre-warmed + screenshotted into `evidence/`, and `claims.json`
rows point to real artifacts. Only then does the package phase write and publish the post.

## 78. What-if scenarios (product decisions pre-made so build doesn't stall)
- **What if a repo has commits but all from bots?** Bot authors still count as contributors; the velocity/decay signal still classifies. Acceptable; noted in LIMITATIONS as a known edge.
- **What if two death-modes tie in the posterior?** Show the argmax; the confidence number communicates the closeness (a 0.34 top means "uncertain" honestly).
- **What if the repo is a fork?** Classify on the fork's own commit history; if it has little, `insufficient_history`. No special-casing.
- **What if the user pastes their OWN alive repo hoping for a scare?** They get `alive` + the "merely sleeping" eulogy — a pleasant twist, shareable.
- **What if TabPFN returns a class not in our 5?** It can't — it only predicts labels present in the seed (`y_train`); the seed only contains the 5 modes.
- **What if Groq returns an empty string?** Treated as a grounding failure → templated eulogy.

## 79. Post-launch monitoring (judging week)
- The external warm-ping on `/healthz` also serves as an uptime check; a non-200 is the signal to redeploy/rollback.
- Spot-check the live URL once a day through the Nov-2 week: a warm load <2s, a fresh autopsy works, the engine badge is `tabpfn`.
- If TabPFN or Groq has an outage, the labeled fallbacks keep the app honest and functional — no action needed beyond noting it.

## 80. Decision-log summary (full rationale in DECISIONS.md)
D1 FastAPI single page · D2 hosted TabPFN · D3 Groq open-weight narration · D4 seed-dataset-first ·
D5 GitHub REST (no clone) · D6 Render Starter warm · D7 scope cuts (no Issues/card-render/compare) ·
D8 transparent never-fake fallback. Each is traceable to a PRD requirement or invariant and to a
risk it retires.

## 81. Final definition of done (product-level)
The product is DONE when: a judge can paste any public repo and receive, in <15s on a warm live
Render URL, an honest death-mode verdict from TabPFN (engine badge `tabpfn`), the six-feature
forensic evidence, and a grounded open-weight eulogy on a screenshot-worthy certificate card — AND
the dev.to post that tells this build-story (with cover image, demo video, a table, a first-person
number-in-title, both required tags, live + repo links, and the open-source/open-innovation
explanation) is published under `devchallenge` + `hf26challenge` by Oct 31, 18:00 WAT. The post is
the deliverable; everything above exists to make it true and evidenced.

## 82. Inputs this PRD was derived from (provenance)
- `warroom/WINNER-BRIEF.md` + `warroom/FINAL-VERDICT-V1.md` — the CP2-selected winner + thesis.
- `research/research-brief.md` — DEV Wk4 rules, winning-post anatomy, Render/TabPFN partner reqs, the Groq inference path.
- The independent Sonnet feasibility review (recorded in the cross-model ledger) — the ~50-repo seed-dataset requirement, the scope cuts, the NOTES.md capture.
- `PULSE.md` Active Facts / Decisions / Downstream Items (DS-1 live-page read, DS-2 durable Render, DS-3 post craft elements).
- The brief: `~/.claude/skills/hackathon-briefs/dev-hacktoberfest.md`.

## 83. Review & ratification
- Thesis (THESIS-1..5) + the feasibility claim reviewed by a distinct model (Sonnet) → AGREE, with the seed-dataset caveat folded into B0 and the two pre-build/RAM fixes folded into PLAN.
- CP1 (manifest) + CP2 (idea selection) answered by the user; this PRD implements the ratified winner at the ratified scope (standalone-fresh, TabPFN-if-natural → natural here).
- Open items (§65) are build-day resolutions, not blocks.

## 84. Versioning
This is PRD v1 for the `v1-submission` tag. Any post-submission change is a branch; the submitted
commit the dev.to post links to stays pinned so judges see exactly what was described.

## 85. Closing note
This PRD is deliberately thorough because the build is deliberately small: a one-page, one-loop app
whose job is to be the evidence behind a gripping post. Depth here is what lets the build be
transcription (ARCHITECTURE carries every line) and the post be written from captured, real
observations (NOTES.md). Nothing above adds runtime surface; it adds certainty. Build with momentum;
protect the write-up; keep the coroner honest.
