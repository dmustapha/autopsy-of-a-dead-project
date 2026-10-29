# DECISIONS — Autopsy of a Dead Project

| # | Decision | Rationale | Alternatives rejected |
|---|----------|-----------|-----------------------|
| D1 | Python FastAPI single server-rendered page | TabPFN + git analysis are Python-native; one service, tiny Render footprint, no JS build | Next.js/React (adds bundler + a second runtime for no gain on a one-page app) |
| D2 | TabPFN via hosted `tabpfn-client` | Load-bearing classifier; hosted avoids local-weights browser license-accept + GPU/2GB tier on Render | Local TabPFN weights (headless license friction, heavy Render tier) |
| D3 | Groq-served open-weight Llama/Qwen for narration | Open-weight satisfies the "open-source AI core" rule; ~85ms TTFB, free, OpenAI-compatible | A closed model (would violate the open-source requirement); self-hosted LLM (too heavy for 1-day + Starter) |
| D4 | Ship a ~50-repo labeled seed dataset in-repo | TabPFN is few-shot in-context; the seed set IS its train data → makes classification honest + is a post artifact | Zero-shot TabPFN (collapses the load-bearing claim); training a conventional model (no time to tune) |
| D5 | GitHub REST API, no clone | No git binary / large checkout on Render; commits+contributors suffice for the feature table | git clone (slow, disk-heavy on Starter) |
| D6 | Render Starter $7, min-instances=1 (warm) | dl-1: free tier spins down 15min idle → dead demo during Nov-2 judging | Render free (dead-demo risk); other hosts (loses the Render partner category) |
| D7 | Scope cuts: no Issues API, no server-side card render, no multi-repo | Protects the 1-day timeline (Sonnet review) | Full feature set (blows the day; starves the post, which is the heaviest axis) |
| D8 | Transparent forensic-rules fallback if TabPFN unreachable | Never silently fake the model; demo stays honest | Faking a verdict (dishonest, and kills the TabPFN story if caught) |

---

# Architecture Decision Records (ADRs)

## ADR-001 — Python FastAPI single server-rendered page
- **Status:** Accepted
- **Context:** The app is a one-page, one-loop tool; TabPFN + git analysis are Python-native; it must deploy as one tiny Render service.
- **Decision:** FastAPI + Jinja2, server-rendered, Tailwind CDN + ~40 lines vanilla JS. No JS build step.
- **Rejected:** Next.js/React SPA — adds a bundler + a second runtime for zero gain on a one-page app and slows Render cold-start. A static site — can't run the Python classifier server-side.
- **Consequences:** Trivial deploy, tiny image; the "frontend" is one HTML file; no node toolchain.

## ADR-002 — TabPFN via hosted `tabpfn-client` (not local weights)
- **Status:** Accepted
- **Context:** TabPFN is the load-bearing classifier; Render Starter is 512MB with no GPU.
- **Decision:** Use the hosted `tabpfn-client` with `set_access_token(TABPFN_TOKEN)` before `fit`.
- **Rejected:** Local TabPFN weights — the browser license-accept is awkward headless and weights+torch blow the Starter image/RAM budget, forcing a larger instance.
- **Consequences:** A required `TABPFN_TOKEN`; a hosted dependency with a labeled forensic-rules fallback when unreachable (never silently faked).

## ADR-003 — Groq-served open-weight LLM for narration (not a closed model)
- **Status:** Accepted
- **Context:** The challenge requires open-source AI at the core; narration needs to be fast and free.
- **Decision:** `openai` SDK against Groq's OpenAI-compatible endpoint, model `llama-3.3-70b-versatile`; swappable to Ollama-local via `LLM_BASE_URL`.
- **Rejected:** A closed model (GPT/Claude) — would violate the open-source-core rule and void the premise. A self-hosted 70B — too heavy for a 1-day build on Starter.
- **Consequences:** Open-weight narration; a documented fully-local Ollama mode proves zero closed dependencies.

## ADR-004 — Ship a hand-labeled ~50-repo seed dataset, built first (B0)
- **Status:** Accepted
- **Context:** TabPFN is a few-shot in-context learner — it needs (X_train, y_train) at inference; it has no priors about repos.
- **Decision:** Curate `data/seed_repos.csv` (~50 labeled repos) as a shipped build artifact, built in B0 before anything downstream, validated by a leave-one-out separability check.
- **Rejected:** Zero-shot TabPFN — collapses the load-bearing claim. Training a conventional sklearn model — no time to tune in a 1-day build.
- **Consequences:** The seed set is the linchpin + a describable post artifact ("I hand-labeled 50 dead repos"); B0 is the critical path.

## ADR-005 — Render Starter ($7), kept warm (not the free tier)
- **Status:** Accepted
- **Context:** The free tier spins down after 15 min idle (dl-1); judging is a week out (Nov 2).
- **Decision:** Deploy on Starter with `numInstances=1` + an external warm-ping on `/healthz`.
- **Rejected:** Render free tier — a cold/dead link during judging is a lost demo and a lost partner category.
- **Consequences:** ~$7/mo (or promo credits); a reliably warm live URL through judging.

## ADR-006 — Scope cuts: no Issues API, no server-side card render, no multi-repo compare
- **Status:** Accepted
- **Context:** 1-day build; the dev.to post (not the app) is the heaviest-judged deliverable.
- **Decision:** Features from commits+contributors only; the certificate is a DOM card screenshotted for the cover; one URL → one certificate.
- **Rejected:** Issue/PR half-life features (paginated/slow), Puppeteer card rendering (heavy on Starter), multi-repo comparison (doubles UX surface) — each costs build time the post needs.
- **Consequences:** A complete, shippable loop; documented limitations; the post block is protected.

## ADR-007 — Transparent, never-faked fallback (engine flag)
- **Status:** Accepted
- **Context:** Hosted model dependencies can be unreachable; honesty is a judged and ethical must.
- **Decision:** Every verdict carries an `engine` flag (`tabpfn`|`rules`) surfaced verbatim in the UI; the rules path consults the seed via 1-NN and is labeled an estimate.
- **Rejected:** Silently serving a heuristic as "the model" — dishonest and fatal if caught.
- **Consequences:** The load-bearing claim is checkable; a demo on the fallback is still honest.
