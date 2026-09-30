#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-http://127.0.0.1:8000}"
curl --fail --silent --show-error "$BASE_URL/health" | grep -q '"status":"ok"'
curl --fail --silent --show-error "$BASE_URL/" | grep -q 'GAINT Academy API'
echo "GAINT Academy smoke test passed: $BASE_URL"
