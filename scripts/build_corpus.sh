#!/usr/bin/env bash
# scripts/build_corpus.sh — one-command corpus build: discover + filter 5,000
# candidates from GitHub into corpus/manifest.json + corpus/reports/.
#
# Flow:
#   1. corpus/finder.py   --target 5000   scrapes GitHub's dependents list of
#      fastapi/fastapi until 5,000 unique candidate repos are gathered and
#      enriches them via the REST API (resumable; use --include-topic to add
#      the topic:fastapi seed as a secondary source).
#   2. corpus/filter.py   --delta --keep-clones accepted   processes ONLY
#      candidates not yet decided (idempotent across re-runs: already-decided
#      repos are preserved verbatim), keeps clones of accepted repos, deletes
#      rejected clones, and retries transient clone failures.
#
# Result: the candidate pool grows toward 5,000; accepted repos are whatever
# clears E1-E6 (~7-8% historically). All downstream analyses
# (analysis/aggregate.py --scope all, usage_patterns, e2/e6, build_pptx) then
# read from corpus/manifest.json + corpus/reports/.
#
# Usage:
#   GITHUB_TOKEN=... scripts/build_corpus.sh
# Real-time conjugate monitoring:
#   tail -f logs/build_corpus.log
#
# NOTE: set env or accept defaults from corpus/settings.py.

set -euo pipefail
cd "$(dirname "$0")/.."

LOG=logs/build_corpus.log
mkdir -p logs

log() { echo "[build_corpus $(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

if [ -z "${GITHUB_TOKEN:-}" ]; then
  # allow token to come from .env (loaded by finder itself)
  log "GITHUB_TOKEN not set in shell; finder will source it from .env if present"
fi

log "--- phase 1: finder (target: ${TARGET_CANDIDATES:-5000} candidates) ---"
uv run python corpus/finder.py --target "${TARGET_CANDIDATES:-5000}" 2>&1 | tee -a "$LOG"

log "--- phase 2: filter (--delta, keep accepted clones) ---"
uv run python corpus/filter.py --delta --keep-clones accepted 2>&1 | tee -a "$LOG"

log "--- done ---"
uv run python - <<'PY' 2>&1 | tee -a "$LOG"
import json
m = json.load(open("corpus/manifest.json"))
print(f"[build_corpus] candidates -> accepted: {m['accepted_count']} accepted repos",
      f"(manifest config: {m.get('config')})")
PY