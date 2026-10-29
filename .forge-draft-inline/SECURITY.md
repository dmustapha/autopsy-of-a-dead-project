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
