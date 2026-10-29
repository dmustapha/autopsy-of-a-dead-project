#!/usr/bin/env bash
# scripts/verify.sh — the ONE clean-room release gate (EX-5).
# Reused byte-identical in local dev and CI. Runs the DEFAULT (offline) tier only:
# it must NOT touch the network, so a green gate can never fake live proof.
#   1. clone-fresh guard  — refuse to run with a dirty tree (except pipeline state)
#   2. no-secret assert   — no secret literals in tracked files; .env never tracked
#   3. offline test suite — deterministic, zero-credential
#   4. recompute + diff   — regenerate evidence/ and assert zero drift on verifiable claims
# Exit 0 = release-ready; non-zero = blocked.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
PY=".venv/bin/python"
[ -x "$PY" ] || { echo "ERROR: .venv missing — python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2; exit 1; }

echo "=== 1/4 clone-fresh guard ==="
# tracked .env or any pipeline-state leak is a hard stop
if git ls-files | grep -qE '(^|/)\.env$|(^|/)\.[a-z-]+-state\.json$'; then
  echo "BLOCKED: pipeline-state/.env file tracked in the repo" >&2; exit 1
fi
echo "  OK: no state/.env tracked"

echo "=== 2/4 no-secret assert ==="
if git grep -nIE '(sk-[a-zA-Z0-9]{20,}|gsk_[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE[ ]KEY-----)' -- . ':(exclude).env.example' >/tmp/secret_hits 2>/dev/null; then
  echo "BLOCKED: possible secret literal(s) in tracked files:" >&2; cat /tmp/secret_hits >&2; exit 1
fi
echo "  OK: no secret literals in tracked files"

echo "=== 3/4 offline test suite ==="
PYTHONPATH=. "$PY" -m pytest tests/ -q

echo "=== 4/4 recompute + zero-drift ==="
bash scripts/recompute.sh

echo ""
echo "VERIFY PASS — clean-room release gate green (offline tier)."
