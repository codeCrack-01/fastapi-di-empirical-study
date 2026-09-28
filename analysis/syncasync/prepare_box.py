#!/usr/bin/env python3
"""prepare_box.py — one-time setup and topology capture for the study box.

Order matters and must not be rearranged:

  1. enable every cpu that is offline, and delete any stale topology cache
  2. capture the true SMT sibling map, while the machine is fully online
  3. verify the captured layout matches what the pre-registration specifies
  4. take the unused siblings offline
  5. re-verify: assert_disjoint() against the cached topology

Step 2 must precede step 4. Once a cpu is offline its topology directory
disappears, so a map read afterwards reports every cpu as its own physical core
and the "offline cpu is a sibling of a core in use" guard would pass on a
misconfigured layout instead of catching it.

Run as root, once, before any cell:

    .venv/bin/python prepare_box.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import runner  # noqa: E402


def main() -> int:
    print("== 1. restore all cpus and clear any stale cache ==")
    brought = runner.enable_all_cpus()
    print(f"   re-enabled: {brought or 'none were offline'}")
    runner.TOPOLOGY_CACHE.unlink(missing_ok=True)

    print("== 2. capture topology (machine fully online) ==")
    groups = runner.capture_topology()
    print("   " + json.dumps({str(k): v for k, v in groups.items()}))

    print("== 3. check the captured layout against the pre-registration ==")
    server = runner.expand_cores(runner.SERVER_CORES)
    k6 = runner.expand_cores(runner.K6_CORES)
    offline = runner.expand_cores(runner.OFFLINE_CORES)
    all_cpus = set(groups)

    def physical(cpus):
        out = set()
        for c in cpus:
            out.update(groups.get(c, [c]))
        return out

    # physical cores, as distinct physical cores
    server_phys = {min(groups.get(c, [c])) for c in server}
    k6_phys = {min(groups.get(c, [c])) for c in k6}
    print(f"   server {sorted(server)} -> physical cores {sorted(server_phys)}")
    print(f"   k6     {sorted(k6)} -> physical cores {sorted(k6_phys)}")
    print(f"   offline {sorted(offline)}")

    if server_phys & k6_phys:
        print(f"   FATAL: server and k6 share physical core(s) "
              f"{sorted(server_phys & k6_phys)}")
        return 1

    # The offline set must be EXACTLY the unused siblings: every offline cpu is a
    # sibling of a cpu in use, and every cpu not in use is offline. Anything else
    # means a cpu is left idle-but-online (contended) or a used cpu was offlined.
    used_phys = server_phys | k6_phys
    in_use_threads = {t for phys in used_phys for t in groups.get(phys, [phys])}
    expected_offline = sorted(in_use_threads - (server | k6))
    if sorted(offline) != expected_offline:
        print(f"   FATAL: offline set {sorted(offline)} != the unused siblings "
              f"{expected_offline}")
        return 1
    uncovered = sorted(all_cpus - server - k6 - offline)
    if uncovered:
        print(f"   FATAL: cpus {uncovered} are neither pinned nor offline; they would "
              "be left online and contended")
        return 1
    print(f"   layout OK: server on {len(server_phys)} physical cores, k6 on "
          f"{len(k6_phys)}, {len(offline)} siblings offline, nothing contended")

    print("== 4. take unused siblings offline ==")
    state = runner.take_siblings_offline()
    print("   changed: " + str(state["changed"]))
    print("   failed : " + str(state["failed"]))
    if state["failed"]:
        print("   FATAL: could not offline a listed sibling")
        return 1

    print("== 5. re-verify against the cached topology ==")
    runner.assert_disjoint()
    online = sorted(int(c) for c, v in state["online_after"].items() if v == "1")
    print(f"   online after offlining: {online}")
    print("\nBOX READY. Do not edit runner.py core constants without re-running this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
