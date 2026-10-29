# SECURITY — Autopsy of a Dead Project

Scope: a stateless public web app that reads PUBLIC GitHub data and calls two AI APIs. Low attack surface; no user data, no auth, no persistence.

| Area | Risk | Control |
|------|------|---------|
| Secrets | GROQ_API_KEY / TABPFN_TOKEN / GITHUB_TOKEN leakage | Env vars only (Render dashboard); never in repo; `.env` git-ignored; no secrets in client HTML or logs |
| Input | Malicious/malformed repo URL (SSRF, injection) | `validators.parse_repo_url` allow-lists `github.com/owner/repo` only; all GitHub calls go to api.github.com with the parsed owner/repo — no arbitrary-URL fetch |
| Rate/abuse | Public endpoint spammed → Groq/GitHub quota burn | Per-IP soft rate limit; narration cached per (repo,verdict); GitHub unauth read is already rate-limited; graceful 429 handling |
| Output | LLM narration echoing injected repo content | Narration is grounded on the numeric feature row + verdict only, not raw repo text → no prompt-injection surface from repo contents |
| Transport | — | HTTPS terminated by Render |
| Dependencies | Supply chain | Pinned `requirements.txt`; minimal dep set |

Not in scope (stateless app, no accounts): session mgmt, CSRF, PII handling.

## Not defended against

- **Rate-abuse beyond the soft per-IP limiter** — the limiter (`slowapi` per-IP, 10 req/min by default) is a best-effort soft guard; a distributed attack across many IPs, or any attacker that spoofs/rotates IPs via a proxy, will still burn through the GitHub API quota, the hosted TabPFN token, and the Ollama endpoint budget. No hard auth wall, no token-level quota, no IP blocklist.
- **SSRF via crafted `repo_url`** — mitigated by `validators.parse_repo_url` which allow-lists `github.com/<owner>/<repo>` only and re-constructs the URL from parsed components. However: only `github.com` is in the allowlist; if the validation regex is bypassed (e.g. by a future change) the HTTP client would follow any host. No additional network-egress firewall on the host enforces the allow-list at the OS level.
- **GitHub API token abuse** — an attacker who can trigger many `/autopsy` calls (within rate-limit windows) can exhaust the `GITHUB_TOKEN` quota and cause 403s for all subsequent users. No per-token budget cap or circuit-breaker beyond GitHub's native rate limits.
- **Hosted Ollama/TabPFN endpoint exposure** — the Ollama endpoint (`LLM_BASE_URL`) and the TabPFN client secret (`TABPFN_TOKEN`) are env-vars on the Oracle VM; they are not accessible from the web app's client bundle. However, if the Oracle VM's firewall is misconfigured, the Ollama HTTP port may be reachable directly from the internet, with no auth. No mTLS or network-level auth on those internal services.
- **DoS via huge repositories** — the GitHub REST extractor fetches `/commits`, `/pulls`, and `/issues` with pagination (page-size capped). A repo with tens of thousands of issues/PRs will cause many paginated requests and slow responses; the per-request timeout (`httpx` default) is the only guard. No hard cap on total pages fetched, and no async concurrency limit on parallel GitHub calls.
- **Log injection / sensitive-data in logs** — repo URLs and verdict strings are logged at INFO level. A crafted repo slug containing newlines or ANSI escape sequences would appear in the systemd journal unescaped. Structured logging / sanitization is not implemented.
