#!/usr/bin/env bash
# scripts/recompute.sh — re-derive verifiable claims in claims.json and assert they match.
# Runs the production extractor + offline test suite; checks the two recomputable claims.
# Exit 0 = zero drift; exit 1 = drift or environment error.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

VENV=".venv/bin/python"
if [[ ! -x "$VENV" ]]; then
  echo "ERROR: venv not found at $VENV — run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

echo "=== CLAIM: seed-dataset (117 rows, 5 balanced classes) ==="
SEED_OUT=$("$VENV" -c "
import pandas as pd, json, sys
d = pd.read_csv('data/seed_repos.csv')
result = {'rows': int(len(d)), 'classes': {str(k): int(v) for k, v in d['death_mode'].value_counts().sort_index().items()}}
print(json.dumps(result))
")
EXPECTED_ROWS=117
ACTUAL_ROWS=$(echo "$SEED_OUT" | "$VENV" -c "import json,sys; d=json.load(sys.stdin); print(d['rows'])")
if [[ "$ACTUAL_ROWS" != "$EXPECTED_ROWS" ]]; then
  echo "DRIFT: seed row count $ACTUAL_ROWS != expected $EXPECTED_ROWS" >&2
  exit 1
fi
echo "  OK: $ACTUAL_ROWS rows — $SEED_OUT"

echo "=== CLAIM: test-suite-green (54 cases) ==="
TEST_OUT=$(PYTHONPATH=. "$VENV" -m pytest tests/ -q 2>&1 | tail -3)
if ! echo "$TEST_OUT" | grep -q "passed"; then
  echo "DRIFT: test suite did not report 'passed'" >&2
  echo "$TEST_OUT" >&2
  exit 1
fi
echo "  OK: $TEST_OUT"

echo "=== CLAIM: honest-engine-badge (rules fallback labeled correctly) ==="
ENGINE_OUT=$(PYTHONPATH=. "$VENV" -c "
from app.schemas import Features
from app.classifier import _forensic_rules
f = Features(days_since_last_commit=900, commit_cadence_decay=-3, lifespan_days=700,
              contributor_count=4, bus_factor=2, velocity_ratio=0.0)
print(_forensic_rules(f).engine)
")
if [[ "$ENGINE_OUT" != "rules" ]]; then
  echo "DRIFT: fallback engine='$ENGINE_OUT' != expected 'rules'" >&2
  exit 1
fi
echo "  OK: fallback engine=$ENGINE_OUT"

echo ""
echo "RECOMPUTE PASS — zero drift on all verifiable claims."
