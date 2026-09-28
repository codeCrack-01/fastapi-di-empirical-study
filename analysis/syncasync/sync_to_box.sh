#!/usr/bin/env bash
# sync_to_box.sh — push the study tree to the box and set up the runtime.
#
# The repo path contains an apostrophe (Fall'26), which breaks naive quoting
# over ssh, so the transfer goes through a tar pipe assembled here.
#
# Box env must match the pre-registration: Python 3.12, k6 v2.2.0.

set -euo pipefail
REPO="/home/zain_khan/Documents/Fall'26/research_fastapi"
SRC="$REPO/analysis/syncasync"
IP="$(cat /tmp/opencode/study_box_ip)"
KEY=~/.ssh/reviewgate_vultr
SSH="ssh -i $KEY -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 -o BatchMode=yes root@$IP"

tar czf - \
  --exclude='results/cells' \
  --exclude='results/smoke' \
  --exclude='results/main' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  -C "$SRC" . | $SSH 'tar xzf - -C /root/study'

# the read-only db is rebuilt on the box by build_db.py, not shipped as a binary;
# build_db verifies the rebuilt file matches the hash in the pre-registration.
$SSH 'chmod 0644 /root/study/results/reviewgate_ro.db 2>/dev/null || true'

$SSH 'set -e
export PATH="$HOME/.local/bin:$PATH"
cd /root/study
# --allow-existing: uv venv recreates the venv and drops the console scripts on
# every run, which broke the venv on a repeat sync. The venv is disposable; the
# pinned package versions below are what make it reproducible.
uv venv --allow-existing --python 3.12 .venv >/dev/null 2>&1
uv pip install --python .venv/bin/python -q \
  "fastapi==0.141.1" "starlette==1.6.0" "pydantic==2.13.2" "uvicorn==0.52.4" \
  "aiosqlite==0.22.1" "dependency-injector==4.49.1" "httpx" 2>&1 | tail -2
echo "  python: $(.venv/bin/python -V)"
echo "  k6:     $(k6 version | head -1)"
.venv/bin/python -c "
import fastapi, starlette, pydantic, uvicorn, aiosqlite, dependency_injector
print(\"  fastapi\", fastapi.__version__, \"| starlette\", starlette.__version__,
      \"| pydantic\", pydantic.__version__, \"| aiosqlite\", aiosqlite.__version__)
"
'
