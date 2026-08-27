#!/usr/bin/env bash
# scripts/retry_clone_failed.sh — resilient driver for corpus/filter.py --retry.
#
# Re-runs the clone_failed retry until exclusion_log.json has no clone_failed
# entries left (or MAX_ATTEMPTS is exhausted). Before each attempt it probes
# actual GitHub reachability over HTTPS (git ls-remote, not just DNS) and
# waits out network outages, so a dropped connection does not burn the
# retry rounds on 300s clone timeouts.
#
# Usage: scripts/retry_clone_failed.sh [max_attempts]   (default: 5)
# Monitor: tail -f logs/filter_retry.log

set -u
cd "$(dirname "$0")/.."

LOG=logs/filter_retry.log
MAX_ATTEMPTS="${1:-5}"
PROBE_URL="https://github.com/octocat/Hello-World.git"
PROBE_TIMEOUT=20

log() { echo "[runner $(date '+%H:%M:%S')] $*" >> "$LOG"; }

clone_failed_count() {
  python3 - <<'PY'
import json
try:
    d = json.load(open("corpus/exclusion_log.json"))
    print(sum(1 for e in d["excluded"] if e["reason"] == "clone_failed"))
except Exception:
    print(-1)
PY
}

probe_ok() {
  timeout "$PROBE_TIMEOUT" git ls-remote --heads "$PROBE_URL" >/dev/null 2>&1
}

attempt=0
while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
  n=$(clone_failed_count)
  if [ "$n" -le 0 ]; then
    log "no clone_failed entries remaining; corpus filtering complete"
    exit 0
  fi
  attempt=$((attempt + 1))
  log "attempt ${attempt}/${MAX_ATTEMPTS}: ${n} clone_failed pending"

  cycles=0
  until probe_ok; do
    cycles=$((cycles + 1))
    if [ "$cycles" -ge 30 ]; then
      break
    fi
    log "github unreachable; waiting 60s before re-probe (cycle ${cycles}/30)"
    sleep 60
  done

  if ! probe_ok; then
    log "network down >30min; spending this attempt, cooling off 10min"
    sleep 600
    continue
  fi

  log "github reachable; launching filter.py --retry"
  uv run python corpus/filter.py --retry >> "$LOG" 2>&1
  log "filter.py exited rc=$?"
done

n=$(clone_failed_count)
log "runner finished after ${MAX_ATTEMPTS} attempts; clone_failed remaining: ${n}"
