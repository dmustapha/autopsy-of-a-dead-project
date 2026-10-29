# Oracle + Ollama/Gemma deploy runbook (ADR-005b / ARCHITECTURE PART III)

Authoritative deploy for "Autopsy of a Dead Project". Supersedes `render.yaml` (NOT used).
Host EVERYTHING on the Oracle Always-Free VM; narration = **Gemma (open weights) via Ollama**, co-located.
$0, no card, no spin-down, keyless narration.

> This runbook is the build phase's artifact. The conductor's **deploy** phase RUNS it against the
> real Oracle VM. Build does NOT provision remote infra.

## 0. Prereqs
- Oracle Always-Free VM (Ubuntu), reachable via the `oci` CLI / SSH already configured.
- Ingress 80/443 opened in BOTH the OCI security list AND the instance firewall (the classic Oracle
  gotcha — default-deny on both layers).

## 1. System deps
```bash
sudo apt-get update && sudo apt-get install -y python3-venv nginx
```

## 2. Ollama + Gemma (open weights, no key)
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma2:2b          # ~1.6GB; CPU-fine for short eulogies. (gemma2:9b if the box has RAM.)
# Ollama serves OpenAI-compatible at http://localhost:11434/v1 via `ollama serve` (systemd unit from installer).
systemctl enable --now ollama
```

## 3. App
```bash
git clone <repo> /opt/autopsy && cd /opt/autopsy
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
```

## 4. Env — `/opt/autopsy/.env`
```
TABPFN_TOKEN=...                       # the $200 TabPFN core (re-activates engine="tabpfn" automatically when Prior Labs is up)
LLM_BASE_URL=http://localhost:11434/v1 # Ollama, co-located
LLM_MODEL=gemma2:2b                    # the $200 Gemma core (non-reasoning; max_tokens=320 is fine)
LLM_API_KEY=ollama                     # placeholder; Ollama ignores it
GITHUB_TOKEN=...                       # optional; lifts the 60/hr unauth limit to 5000/hr
```

## 5. systemd units
- `deploy/autopsy.service` → `/etc/systemd/system/autopsy.service`
- Ollama unit is created by the installer; ensure it is enabled (step 2).
```bash
sudo cp deploy/autopsy.service /etc/systemd/system/autopsy.service
sudo systemctl daemon-reload && sudo systemctl enable --now autopsy
```

## 6. nginx reverse proxy
```bash
sudo cp deploy/nginx-autopsy.conf /etc/nginx/sites-available/autopsy
sudo ln -sf /etc/nginx/sites-available/autopsy /etc/nginx/sites-enabled/autopsy
sudo nginx -t && sudo systemctl reload nginx
# TLS: sudo certbot --nginx -d <host>   (or Caddy for auto-TLS)
```

## 7. Verify (the live V.B5 gate)
```bash
curl -s https://<host>/healthz                      # {ok:true, seed_rows:~48, tabpfn_reachable:true}
curl -s -X POST https://<host>/autopsy \
  -H 'content-type: application/json' \
  -d '{"repo_url":"bower/bower"}' -w '\n[%{http_code}] %{time_total}s\n'
```
Expected: `/healthz` 200 warm < 2s; `/autopsy` 200 with a full AutopsyResult. No spin-down → no warm-ping needed.

## Deploy-phase MUST re-verify (deferred from build, NOT faked here)
1. **Gemma-via-Ollama narration** — the build host had no Ollama, so every local eulogy used the
   labeled templated fallback. On the VM, confirm `/autopsy` returns a real Gemma-written eulogy
   (120–200 words, coroner register, grounded — no fabricated numbers). This is the Best-Use-of-Gemma proof.
2. **TabPFN happy path** — Prior Labs returned HTTP 503 "Service is disabled" during build, so every
   verdict fell back to `engine="rules"`. On deploy, re-run a classify; if the service is back the badge
   reads `engine=tabpfn` (the Best-Use-of-TabPFN proof) and you can finally measure the real LOO separability.
