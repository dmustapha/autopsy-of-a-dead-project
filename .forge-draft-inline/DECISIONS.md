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
