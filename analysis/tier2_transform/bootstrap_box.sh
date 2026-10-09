#!/usr/bin/env bash
# bootstrap_box.sh — Tier-2 study host tooling (k6 + docker + git + uv).
#
# Tier-2 needs everything tier-1 needed (pinned k6, uv) plus Docker (two
# Postgres containers: johnsonhk88's alembic gate and azure-samples' pgvector)
# and git (bench.py checks out each arm branch per run). Same pinning rules
# as ../syncasync/bootstrap_box.sh: k6 is checksum-verified against the
# published GitHub release digest, never a floating URL.
#
# IDEMPOTENT. Safe to re-run.
#
# Run ON THE BOX as root:  bash bootstrap_box.sh
set -euo pipefail

K6_VERSION="${K6_VERSION:-v2.2.0}"
say() { printf '  %s\n' "$*"; }

[ "$(id -u)" -eq 0 ] || { echo "FATAL: must run as root"; exit 1; }

echo "=== base packages ==="
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq curl ca-certificates tar util-linux git >/dev/null
say "git $(git --version | awk '{print $3}')"
say "taskset $(command -v taskset >/dev/null && echo present || echo MISSING)"

echo "=== docker (PG containers for johnsonhk88 + azure-samples) ==="
if ! command -v docker >/dev/null; then
  apt-get install -y -qq docker.io >/dev/null 2>&1 || {
    # docker.io can be missing on newer Ubuntu; fall back to the CE repo.
    curl -fsSL https://get.docker.com | sh >/dev/null 2>&1
  }
fi
systemctl enable --now docker >/dev/null 2>&1 || service docker start >/dev/null 2>&1 || true
say "docker $(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',' || echo MISSING)"

echo "=== uv (Python toolchain manager) ==="
if ! command -v uv >/dev/null && [ ! -x "$HOME/.local/bin/uv" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
fi
export PATH="$HOME/.local/bin:$PATH"
say "uv $(uv --version 2>/dev/null || echo MISSING)"

echo "=== k6 $K6_VERSION (load generator, pinned) ==="
have_k6="$(k6 version 2>/dev/null | head -1 || true)"
case "$have_k6" in
  *"$(echo "$K6_VERSION" | tr -d v)"*) say "already present: $have_k6" ;;
  *)
    asset="k6-${K6_VERSION}-linux-amd64.deb"
    url="https://github.com/grafana/k6/releases/download/${K6_VERSION}/${asset}"
    say "fetching $asset"
    tmp="$(mktemp -d)"
    curl -sSL -o "$tmp/$asset" "$url"
    digest="$(curl -sSL "https://api.github.com/repos/grafana/k6/releases/tags/${K6_VERSION}" \
      | python3 -c "
import json, sys
asset = sys.argv[1]
for a in json.load(sys.stdin).get('assets', []):
    if a.get('name') == asset:
        d = a.get('digest') or ''
        print(d.split('sha256:')[-1] if d.startswith('sha256:') else '')
        break
" "$asset")"
    if [ -n "$digest" ]; then
      actual="$(sha256sum "$tmp/$asset" | awk '{print $1}')"
      [ "$actual" = "$digest" ] || { echo "FATAL: k6 digest mismatch"; exit 1; }
      say "sha256 verified against published digest"
    else
      say "WARNING: no published digest found; version pin only"
    fi
    dpkg -i "$tmp/$asset" >/dev/null
    rm -rf "$tmp"
    ;;
esac
say "k6 $(k6 version 2>/dev/null | head -1 || echo MISSING)"

echo "=== verify ==="
fail=0
command -v git >/dev/null || { say "FAIL git"; fail=1; }
command -v docker >/dev/null || { say "FAIL docker"; fail=1; }
command -v uv >/dev/null || { say "FAIL uv"; fail=1; }
command -v k6 >/dev/null || { say "FAIL k6"; fail=1; }
docker info >/dev/null 2>&1 || { say "FAIL docker daemon not running"; fail=1; }
[ "$fail" -eq 0 ] && echo "BOOTSTRAP OK" || { echo "BOOTSTRAP FAILED"; exit 1; }
