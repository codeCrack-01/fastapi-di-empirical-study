#!/bin/bash
# Preflight: venv + install + baseline test for each Tier-2 pick.
# One row appended per repo to results/preflight.tsv:
#   repo  status  install_s  test_s  passed  failed  error  note
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$ROOT/results/preflight.log"
TSV="$ROOT/results/preflight.tsv"
mkdir -p "$ROOT/results"
[ -f "$TSV" ] || printf 'repo\tstatus\tinstall_s\ttest_s\tpassed\tfailed\terror\tnote\n' > "$TSV"

run_one() {
  local repo="$1" dir="$2" py="$3" install="$4" testcmd="$5" note="$6"
  local start end install_s test_s passed failed err status
  echo "=== [$repo] start $(date +%H:%M:%S)" | tee -a "$LOG"
  start=$(date +%s)
  ( cd "$dir" && eval "$install" ) >>"$LOG" 2>&1
  local rc=$?
  end=$(date +%s); install_s=$((end-start))
  if [ $rc -ne 0 ]; then
    printf '%s\tinstall_failed\t%s\t0\t0\t0\t0\t%s\n' "$repo" "$install_s" "$note" >> "$TSV"
    echo "=== [$repo] INSTALL FAILED ($install_s s)" | tee -a "$LOG"
    return 1
  fi
  echo "=== [$repo] installed in ${install_s}s; running tests" | tee -a "$LOG"
  start=$(date +%s)
  local out="$ROOT/results/${repo}_baseline.txt"
  ( cd "$dir" && eval "$testcmd" ) > "$out" 2>&1
  rc=$?
  end=$(date +%s); test_s=$((end-start))
  # parse pytest summary line
  passed=$(grep -oE '[0-9]+ passed' "$out" | tail -1 | grep -oE '[0-9]+')
  failed=$(grep -oE '[0-9]+ failed' "$out" | tail -1 | grep -oE '[0-9]+')
  err=$(grep -oE '[0-9]+ error' "$out" | tail -1 | grep -oE '[0-9]+')
  passed=${passed:-0}; failed=${failed:-0}; err=${err:-0}
  if [ "$rc" -eq 0 ] && [ "$err" = "0" ]; then status=green
  elif [ "$rc" -eq 0 ]; then status=green
  elif [ "$failed" != "0" ] || [ "$err" != "0" ]; then status=red
  else status=crashed; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$repo" "$status" "$install_s" "$test_s" "$passed" "$failed" "$err" "$note" >> "$TSV"
  echo "=== [$repo] $status passed=$passed failed=$failed error=$err (${test_s}s)" | tee -a "$LOG"
}

cd "$ROOT/repos"

# 1. vstorm — light, optional server+dev extras
run_one vstorm "$ROOT/repos/vstorm-co" 3.12 \
  "uv venv --python 3.12 -q --clear && uv pip install -q -e '.[server,dev]'" \
  ".venv/bin/python -m pytest -q -p no:cacheprovider" \
  "MIT/117s/1 DI file"

# 2. azure-samples — locked, mock-heavy unit tests (integration deselected by addopts)
run_one azure "$ROOT/repos/azure-samples" 3.12 \
  "uv sync -q --frozen" \
  "uv run -q pytest -p no:cacheprovider" \
  "MIT/1172s/central deps.py"

# 3. ciiceronee — poetry-era, requirements-dev
run_one ciiceronee "$ROOT/repos/ciiceronee" 3.12 \
  "uv venv --python 3.12 -q --clear && uv pip install -q -r requirements-dev.txt" \
  ".venv/bin/python -m pytest -q -p no:cacheprovider" \
  "MIT/544s/1 DI file"

# 4. shabti — self-contained sub-project (needs py3.14)
run_one shabti "$ROOT/repos/infosecinnovations/docker_containers/shabti_api" 3.14 \
  "uv sync -q" \
  "uv run -q pytest tests -p no:cacheprovider" \
  "Apache/197s/2 DI files"

# 5. blessedrebus — fallback
run_one krawl "$ROOT/repos/blessedrebus" 3.12 \
  "uv venv --python 3.12 -q --clear && uv pip install -q -r requirements.txt pytest pytest-asyncio" \
  ".venv/bin/python -m pytest tests -q -p no:cacheprovider" \
  "MIT/556s/fallback"

echo "=== preflight done $(date +%H:%M:%S)" | tee -a "$LOG"
cat "$TSV"
