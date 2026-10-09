#!/usr/bin/env bash
# sync_to_box.sh — push the Tier-2 study tree (repos + runner + locks) and
# rebuild the four app venvs on the box.
#
# Venvs are NOT shipped: they embed absolute interpreter paths (uv-managed
# CPython under ~/.local/share/uv) and break across machines. Instead each
# app's exact package set is frozen in locks/<app>.txt and reinstalled on the
# box with uv, pinned to the same Python minor (3.12 for johnsonhk88 /
# vstorm-co / ciiceronee, 3.14 for azure-samples). Two locks contain editable
# installs (-e file://<laptop path>); those lines are rewritten to the box
# repo path before install.
#
# The repo path contains an apostrophe (Fall'26), so the transfer goes
# through a tar pipe, same as ../syncasync/sync_to_box.sh.
#
#   BOX=study_box  ./sync_to_box.sh
#
set -euo pipefail
REPO="/home/zain_khan/Documents/Fall'26/research_fastapi"
SRC="$REPO/analysis/tier2_transform"

BOX="${BOX:-study_box}"
IP="$(cat "/tmp/opencode/${BOX}_ip")"
echo "target  BOX=$BOX  ip=$IP"
KEY=~/.ssh/reviewgate_vultr
SSH="ssh -i $KEY -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 -o BatchMode=yes root@$IP"

$SSH 'mkdir -p /root/study_tier2'

tar czf - \
  --exclude='repos/*/.venv' \
  --exclude='repos/*/*/.venv' \
  --exclude='repos/*/node_modules' \
  --exclude='repos/*/*/node_modules' \
  --exclude='results' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='.ruff_cache' \
  --exclude='.mypy_cache' \
  --exclude='.next' \
  --exclude='dist' \
  --exclude='build' \
  -C "$SRC" . | $SSH 'tar xzf - -C /root/study_tier2'

$SSH "set -e
export PATH=\"\$HOME/.local/bin:\$PATH\"
cd /root/study_tier2

# tar preserves the sending machine's uids, so the extracted repos are owned
# by a foreign uid; git refuses them as 'dubious ownership' until excepted.
git config --global --add safe.directory '*'

mkvenv() {  # name pyversion
  local name=\"\$1\" py=\"\$2\"
  echo \"=== \$name (python \$py) ===\"
  uv venv --allow-existing --python \"\$py\" \"repos/\$name/.venv\" >/dev/null 2>&1
  # rewrite editable installs to the box path
  sed \"s|-e file://.*|-e /root/study_tier2/repos/\$name|\" \"locks/\$name.txt\" > \"/tmp/lock_\$name.txt\"
  uv pip install --no-deps --python \"repos/\$name/.venv/bin/python\" -r \"/tmp/lock_\$name.txt\" 2>&1 | tail -1
}

# johnsonhk88 lives under repos/johnsonhk88/api
mkvenv_pkgs() {  # name subdir pyversion
  local name=\"\$1\" sub=\"\$2\" py=\"\$3\"
  echo \"=== \$name/\$sub (python \$py) ===\"
  uv venv --allow-existing --python \"\$py\" \"repos/\$name/\$sub/.venv\" >/dev/null 2>&1
  sed \"s|-e file://.*|-e /root/study_tier2/repos/\$name|\" \"locks/\$name.txt\" > \"/tmp/lock_\$name.txt\"
  uv pip install --no-deps --python \"repos/\$name/\$sub/.venv/bin/python\" -r \"/tmp/lock_\$name.txt\" 2>&1 | tail -1
}

mkvenv_pkgs johnsonhk88 api 3.12
mkvenv vstorm-co 3.12
mkvenv ciiceronee 3.12
mkvenv azure-samples 3.14

echo \"=== verify ===\"
for py in repos/johnsonhk88/api/.venv/bin/python repos/vstorm-co/.venv/bin/python \
          repos/ciiceronee/.venv/bin/python repos/azure-samples/.venv/bin/python; do
  \"\$py\" -V
done
(cd repos/johnsonhk88/api && .venv/bin/python -c 'import app.main' && echo '  jhk import OK')
(cd repos/azure-samples && PYTHONPATH=src .venv/bin/python -c 'import backend.app' && echo '  azure import OK')
(cd repos/vstorm-co && PYTHONPATH=src .venv/bin/python -c 'import pydantic_ai_backends.remote.server' && echo '  vstorm import OK')
(cd repos/ciiceronee && .venv/bin/python -c 'import ciicerone.api.main' && echo '  ciiceronee import OK')
k6 version | head -1
docker info >/dev/null 2>&1 && echo '  docker OK'
echo 'SYNC OK'
"
