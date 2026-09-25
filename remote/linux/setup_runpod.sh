#!/usr/bin/env bash
# remote/linux/setup_runpod.sh — one-shot run of the pinned qwen3:14b judge job
# on a rented single-GPU box (RTX 3090 / CUDA runtime; provider-agnostic).
#
# Usage (after extracting the handoff zip into the job dir, e.g. /opt/judge):
#   ./remote/linux/setup_runpod.sh [MODEL]      (MODEL defaults to qwen3:14b)
#
# What it does:
#   0. install missing CLI tools (curl/unzip/tmux/python3-pip) on lean images
#   1. verify python3 + install `requests` (only non-stdlib driver dep)
#   2. ensure the ollama binary exists (installs via official script if missing)
#   3. ensure `ollama serve` is answering on OLLAMA_HOST (starts it if down)
#   4. pull MODEL (idempotent when already cached)
#   5. snapshot the executor for the paper (env_snapshot.txt; incl. power.limit)
#   6. run the fully-resumable driver: remote/run_judge_job.py --job job.json
#   7. print the MUST-DOWNLOAD-before-terminate checklist
set -uo pipefail

# Rootless / per-user installs (and some Lium images) put bins in $HOME/.local/bin.
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

JobDir="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$JobDir"
MODEL="${1:-qwen3:14b}"
Endpoint="${OLLAMA_HOST:-http://localhost:11434}"

echo "[runpod] job dir: $JobDir"

# 0. required CLI tools (lean base images ship none) ---------------------------
# Rootless installs skip this; the whole step is idempotent and best-effort.
if ! command -v curl >/dev/null 2>&1 || ! command -v unzip >/dev/null 2>&1 \
   || ! command -v tmux >/dev/null 2>&1 || ! command -v pip3 >/dev/null 2>&1; then
    echo "[runpod] installing curl unzip tmux python3-pip (apt-get) ..."
    apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        curl unzip tmux ca-certificates python3-pip || {
        echo "[runpod] WARN: apt-get install failed; continuing with whatever exists."
        }
fi

# 1. python + requests -------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "[runpod] ERROR: python3 not found on this image." >&2
    exit 1
fi
python3 -m pip install --quiet requests 2>/dev/null \
    || echo "[runpod] WARN: 'pip install requests' failed; driver will not import (it needs requests)."

# 2. ollama binary -----------------------------------------------------------
if ! command -v ollama >/dev/null 2>&1; then
    echo "[runpod] ollama not found; installing official binary ..."
    curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh || {
        echo "[runpod] ERROR: could not fetch ollama installer" >&2; exit 1; }
    sh /tmp/ollama-install.sh || { echo "[runpod] ERROR: ollama install failed" >&2; exit 1; }
fi

# 3. server up ---------------------------------------------------------------
if ! curl -fsS "$Endpoint/api/tags" >/dev/null 2>&1; then
    echo "[runpod] starting ollama serve ..."
    (nohup ollama serve >/tmp/ollama-serve.log 2>&1 &)
    for _ in $(seq 1 60); do
        curl -fsS "$Endpoint/api/tags" >/dev/null 2>&1 && break
        sleep 2
    done
fi
curl -fsS "$Endpoint/api/tags" >/dev/null 2>&1 \
    || { echo "[runpod] ERROR: ollama not reachable at $Endpoint" >&2; exit 1; }
echo "[runpod] ollama reachable at $Endpoint"

# 4. pull --------------------------------------------------------------------
echo "[runpod] pulling $MODEL (idempotent) ..."
ollama pull "$MODEL"

# 5. executor snapshot (paper provenance) -------------------------------------
{
    date -u +"snapshot_utc=%Y-%m-%dT%H:%M:%SZ"
    echo "host=$(hostname) | $(uname -srm)"
    echo "cpu_threads=$(nproc)"
    grep -m1 "model name" /proc/cpuinfo || true
    grep -E "MemTotal|MemAvailable" /proc/meminfo || true
    nvidia-smi --query-gpu=name,memory.total,driver_version,power.limit --format=csv,noheader || true
    echo "ollama=$(ollama --version 2>/dev/null || echo '?')"
    echo "model=$(ollama show "$MODEL" | tr '\n' ';')"
} | tee "$JobDir/env_snapshot.txt"

echo
echo "[runpod] ===== driver start: python3 remote/run_judge_job.py --job job.json (model=$MODEL) ====="
set +e
python3 remote/run_judge_job.py --job job.json 2>&1 | tee -a "$JobDir/job.log"
RC=${PIPESTATUS[0]}
set -e

echo
echo "[runpod] driver exit=$RC"
echo "chunks=$(wc -l < "$JobDir/remote/results/journal.jsonl" 2>/dev/null || echo 0) journal entries; model outputs in $JobDir/remote/results/"
echo
echo "!! BEFORE TERMINATING THIS POD, download everything from:"
echo "    $JobDir"
echo "  run on ANOTHER terminal (or download via web console file manager):"
echo "    tar -C \"$JobDir\" -czf results.tar.gz remote/results env_snapshot.txt job.log"
echo "  copy results.tar.gz back, verify it extracts, THEN terminate the pod."
echo "  If the driver exited !=0 (e.g. pod rebooted), re-run this script: it resumes."
exit "$RC"