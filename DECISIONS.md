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

## ADR-003a — Inference served by 0G Compute (supersedes the Groq default in ADR-003)
- **Status:** Accepted (2026-10-29, Dami-steered)
- **Context:** We already own a working 0G Compute key (`ZERO_G_COMPUTE_API_KEY`), and 0G Compute is an OpenAI-compatible decentralized inference network serving open-weight models.
- **Decision:** Narration is served by **0G Compute Router** (`https://router-api.0g.ai/v1`) using the open-weight model **`deepseek-v4-flash`** (verified end-to-end). `narrator.py` is unchanged — only `LLM_BASE_URL`/`LLM_MODEL`/key env differ. Groq (`openai/gpt-oss-120b`) is the documented fallback.
- **Rejected:** Groq as primary (generic cloud, a weaker open-source narrative, required a fresh key); Oracle self-hosted Ollama (more setup than value given 0G already works); any closed model on the 0G router (claude-* are proxied there but violate the open-source-core rule — deliberately avoided).
- **Consequences:** Stronger "decentralized open-weight AI" story for the post; no new signup; the Render service stays tiny (just an HTTP call). Honesty: 0G TEE-verifiability is opt-in per provider — we do NOT claim attested inference unless a TeeML provider is explicitly used. TabPFN remains the unambiguous open-weight core.

## ADR-005a — Deploy on Oracle Cloud (supersedes ADR-005 Render; Dami ruling 2026-10-29)
- **Status:** Accepted
- **Context:** We own an authenticated Oracle Always-Free VM (oci CLI v3.95 + config). Dami chose to host on infra we control rather than Render.
- **Decision:** The live app is hosted on **Oracle Cloud (Always-Free VM)** — full control, no spin-down, no PaaS RAM ceiling, can co-host services. Deploy via the VM (uvicorn behind nginx/caddy + a systemd unit or docker), not render.yaml.
- **Consequence (explicit):** FORFEITS the "Best Use of Render" $200 partner category. **Prize targeting drops to Overall ($250) + Best Use of TabPFN ($200)** — two tracks, not three. ARCHITECTURE render.yaml is now superseded by an Oracle deploy runbook (to be written at B5). The durable-tier concern (dl-1) is moot — our VM does not spin down.
- **Rejected:** Render (would keep the $200 but Dami prefers owned infra); the hybrid Render-primary (not chosen).

## ADR-005b — Host EVERYTHING on Oracle Always-Free; narration = Gemma via Ollama (supersedes ADR-003a inference + ADR-005a/the DO pick; Dami ruling 2026-10-29 "$0, no card")
- **Status:** Accepted (final)
- **Context:** Dami's hard constraint: zero out-of-pocket cost AND no credit card on file. DigitalOcean's free credit needs a card → excluded. Render's warm/promo tier is uncertain on cards; its 512MB can't run Gemma anyway.
- **Decision:** Host the FastAPI app AND run **Gemma (open weights) via Ollama** both on the **Oracle Always-Free VM** we already own + have authenticated (oci v3.95). Narration calls Oracle-local Ollama (`/v1/chat/completions`, OpenAI-compatible) — `narrator.py` unchanged, just LLM_BASE_URL→Ollama + LLM_MODEL=gemma2 (use `gemma2:2b` for CPU speed, cache narration). TabPFN classifier via its free token (the $200 core). 0G/deepseek becomes an optional fallback, not primary.
- **Prize targeting (final):** Overall ($250) + Best Use of TabPFN ($200) + Best Use of Gemma ($200) = **$650 potential, $0 cost**. We FORGO the hosting category (Render/DigitalOcean) — it is the one $200 that isn't reliably free/no-card.
- **Rejected:** DigitalOcean (card for the credit — Dami's hard no); Render (card risk + can't run Gemma); 0G/deepseek as primary (earns no category); Tinker (fine-tuning, bolt-on, heavy); Arduino (hardware, N/A).
- **Consequences:** One free box runs everything (no spin-down). Gemma-on-our-own-server is ALSO the strongest open-source narrative ("open weights, self-hosted, offline-capable, zero paid APIs"). Build adds: provision Oracle + install Ollama + pull gemma2:2b + expose the app (nginx/caddy + systemd, or a tunnel). render.yaml (ARCH II.13) is superseded by an Oracle deploy runbook (B5).
