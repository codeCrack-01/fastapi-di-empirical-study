"""phaseB.py — revised Tier-2 Phase B runner (per user brief, POST-A preflight).

Protocol v1 (default for the grid, `--freshboot`):
  * FRESH server process for EVERY measured grid cell (no single-boot sequence),
  * randomised cell order (fixed seed), and
  * per cell record: time since boot, TIME_WAIT count, Cpus_allowed_list.

Knee (S2 only): 3 probes per ladder rung, qualified on the MEDIAN
(tier-1 protocol: p95 <= 3*p95_ref, err <= 1%, fidelity >= 0.98); knee = last
qualifying rung. Pass `--knee N` to reuse a previously measured knee and skip
discovery (used when re-running an app whose knee is known).

Matched absolute-rate grid for ALL FOUR arms at
    S2knee x {0.75: K=3, 1.0: K=5, 1.25: K=5, 1.5: K=5}
pinned via TIER2_PIN/TIER2_SERVER_CORES/TIER2_K6_CORES. Reps are min-max only.

S3 @ 2560 pinned-vs-unpinned one-cell probe (BACK-COMPAT, fresh boot):
    TIER2_PIN=1 python phaseB.py <repo> --probe2560 <arm>
    TIER2_PIN=0 python phaseB.py <repo> --probe2560 <arm>
Run pinned/unpinned as TWO back-to-back processes (constants bind at import).

azure: report S1/S2/S3 only on its bench route (/api/health does not cross the
container); if a route DOES cross, include S4.

Rows -> results/<TIER2_OUTDIR>/<app>/raw.tsv (append; header on first run) plus
knee.json. S4 rows carry the label "container instantiated per call, as
transformed" in `arm_label`.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import knee as KNEE  # noqa: E402
from bench import (  # noqa: E402
    K6,
    OUTDIR_REL,
    arm_env,
    boot,
    load_plan,
    resolve_auth,
    venv_python,
)

# Matched absolute-rate grid: S2knee x {frac: K}
MULT = [(0.75, 3), (1.0, 5), (1.25, 5), (1.5, 5)]
if os.environ.get("TIER2_FAST") == "1":
    MULT = [(0.75, 1), (1.0, 1)]  # smoke only
LADDER = KNEE.LADDER
REF_RPS = KNEE.REF_RPS  # 10.0
P95_MULT = KNEE.P95_MULT  # 3.0
MAX_ERR = KNEE.MAX_ERR
MIN_FID = KNEE.MIN_ACHIEVED

ARM_LABEL = {
    "S4": "container instantiated per call, as transformed",
}

HEADER = [
    "repo", "arm", "stage", "rate", "probe",
    "p50_ms", "p95_ms", "p99_ms", "cell_s",
    "achieved_rate", "fidelity", "window_errors", "window_requests",
    "cpus_allowed_server", "cpus_allowed_k6",
    "time_since_boot_s", "timewait_start", "timewait_end", "arm_label",
]


class CellFailed(Exception):
    pass


def timewait_count() -> int:
    """Count sockets in TCP TIME_WAIT (state 06) across IPv4 + IPv6."""
    n = 0
    for p in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            for line in open(p):
                parts = line.split()
                if len(parts) > 3 and parts[3] == "06":
                    n += 1
        except OSError:
            pass
    return n


def proc_age_s(pid: int) -> float | None:
    """Age of the server process (seconds since exec), from /proc/<pid>/stat
    starttime + system uptime. This is the per-cell 'time since boot'."""
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().split()
        start_ticks = int(fields[21])
        hz = os.sysconf("SC_CLK_TCK")
        uptime = float(Path("/proc/uptime").read_text().split()[0])
        return round(uptime - start_ticks / hz, 3)
    except (OSError, IndexError, ValueError):
        return None


def run_one(k6p, base, route, rate, workdir, auth, auth_header, stage, probe, server_allowed):
    sf = workdir / f"{stage}_{int(rate)}_{probe}.json"
    sf.unlink(missing_ok=True)
    t0 = time.monotonic()
    s = KNEE.run_cell(k6p, base, route, rate, sf, auth, auth_header)
    tok = time.monotonic() - t0
    if s is None:
        raise CellFailed(rate)
    win = s.get("window") or {}
    return [
        [rate, probe,
         win.get("p50"), win.get("p95"), win.get("p99"), tok,
         s.get("achieved_rate"), s.get("load_fidelity"),
         s.get("window_errors") or 0, s.get("window_requests") or 0,
         server_allowed, s.get("cpus_allowed_k6", "")], s
    ]


def median_summary(cells) -> dict:
    def med(vals):
        vals = sorted(vals)
        return vals[len(vals) // 2]

    def p95(c):
        return (c.get("window") or {}).get("p95")

    def err(c):
        return (c.get("window_errors") or 0) / max(1, c.get("window_requests") or 1)

    return {
        "p95": med(p95(c) for c in cells),
        "err": med(err(c) for c in cells),
        "fid": med(c.get("load_fidelity") for c in cells),
        "ref_p95": med(p95(c) for c in cells),
    }


def qualifies(med, ref_p95) -> bool:
    return (med["p95"] <= P95_MULT * max(ref_p95, 0.001)
            and med["err"] <= MAX_ERR
            and med["fid"] >= MIN_FID)


@contextlib.contextmanager
def boot_ctx(arm, repo_dir, workdir):
    pro, auth, auth_header = boot(arm, repo_dir, workdir)
    server_allowed = KNEE.read_allowed(pro.pid)
    base = f"http://127.0.0.1:{arm['port']}"
    try:
        yield pro, pro.pid, base, arm["route"], auth, auth_header, server_allowed
    finally:
        pro.terminate()
        try:
            pro.wait(timeout=20)
        except subprocess.TimeoutExpired:
            pro.kill()
            pro.wait(timeout=10)


def discover_s2_knee(arm, repo_dir, workdir):
    rows = []
    probes_by_rate = {}
    with boot_ctx(arm, repo_dir, workdir) as (pro, pid, base, route, auth, header, sall):
        ref_cells = []
        for i in range(3):
            row, s = run_one(K6, base, route, REF_RPS, workdir, auth, header, "ref", i, sall)
            rows.append([arm["repo"], arm["arm"], "ref"] + row)
            ref_cells.append(s)
        ref_p95 = median_summary(ref_cells)["ref_p95"]
        print(f"   ref_p95 (median of 3 @ {REF_RPS} rps) = {ref_p95:.2f} ms", flush=True)
        knee = REF_RPS
        for rate in LADDER:
            cells = []
            failed = False
            for i in range(3):
                try:
                    row, s = run_one(K6, base, route, rate, workdir, auth, header, "knee", i, sall)
                except CellFailed:
                    failed = True
                    break
                rows.append([arm["repo"], arm["arm"], "knee"] + row)
                cells.append(s)
            if failed:
                print(f"   rung {rate}: FAIL (k6 cell error — treated as non-qualifying)", flush=True)
                break
            med = median_summary(cells)
            if not qualifies(med, ref_p95):
                print(f"   rung {rate}: FAIL (p95 med {med['p95']:.1f} err {med['err']:.4f} fid {med['fid']:.4f})", flush=True)
                break
            print(f"   rung {rate}: ok (p95 med {med['p95']:.1f})", flush=True)
            knee = rate
            probes_by_rate[rate] = {"med_p95": med["p95"], "med_err": med["err"], "med_fid": med["fid"]}
    return knee, ref_p95, rows, probes_by_rate


def run_grid_fresh(arms, repo_dir, out, s2knee, seed) -> list[list]:
    """Protocol v1: fresh server process per cell, randomised order."""
    rng = random.Random(seed)
    cells = []
    for arm in arms:
        for frac, k in MULT:
            rate = int(round(s2knee * frac))
            for probe in range(k):
                cells.append((arm, rate, probe))
    rng.shuffle(cells)
    rows: list[list] = []
    total = len(cells)
    for idx, (arm, rate, probe) in enumerate(cells, 1):
        label = ARM_LABEL.get(arm["arm"], "")
        workdir = out / arm["arm"] / f"fresh_{rate}_{probe}"
        workdir.mkdir(parents=True, exist_ok=True)
        (workdir / "server.log").unlink(missing_ok=True)
        pro = None
        try:
            pro, auth, header = boot(arm, repo_dir, workdir)
            sall = KNEE.read_allowed(pro.pid)
            base = f"http://127.0.0.1:{arm['port']}"
            boot_age = proc_age_s(pro.pid)
            tw0 = timewait_count()
            try:
                row, _ = run_one(K6, base, arm["route"], rate, workdir, auth, header, "grid", probe, sall)
            except CellFailed:
                rows.append([arm["repo"], arm["arm"], "grid", rate, probe,
                             "", "", "", "", "", "", "ERRk6", "", sall, "",
                             boot_age, tw0, tw0, label])
                print(f"   [{idx}/{total}] {arm['arm']}@{rate} p{probe}: ERRk6 tw={tw0}", flush=True)
                continue
            tw1 = timewait_count()
            rows.append([arm["repo"], arm["arm"], "grid"] + row + [boot_age, tw0, tw1, label])
            print(f"   [{idx}/{total}] {arm['arm']}@{rate} p{probe}: p95={row[3]} fid={row[7]} "
                  f"cell={row[5]:.1f}s age={boot_age}s tw0={tw0} tw1={tw1}", flush=True)
        except Exception as exc:  # noqa: BLE001 — one bad boot must not kill the run
            rows.append([arm["repo"], arm["arm"], "grid", rate, probe,
                         "", "", "", "", "", "", "ERRboot", "", "", "", "", "", "", label])
            print(f"   [{idx}/{total}] {arm['arm']}@{rate} p{probe}: ERRboot {exc}", flush=True)
        finally:
            if pro is not None:
                pro.terminate()
                try:
                    pro.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    pro.kill()
                    pro.wait(timeout=10)
    return rows


def run_grid_single_boot(arms, repo_dir, out, s2knee) -> list[list]:
    """Legacy single-boot ascending grid (kept for reference only)."""
    rows = []
    for arm in arms:
        workdir = out / arm["arm"]
        workdir.mkdir(parents=True, exist_ok=True)
        (workdir / "server.log").unlink(missing_ok=True)
        label = ARM_LABEL.get(arm["arm"], "")
        with boot_ctx(arm, repo_dir, workdir) as (pro, pid, base, route, auth, header, sall):
            for frac, k in MULT:
                rate = int(round(s2knee * frac))
                for probe in range(k):
                    try:
                        row, _ = run_one(K6, base, route, rate, workdir, auth, header, "grid", probe, sall)
                    except CellFailed:
                        rows.append([arm["repo"], arm["arm"], "grid", rate, probe,
                                     "", "", "", "", "", "", "ERRk6", "", sall, "", "", "", "", label])
                        continue
                    rows.append([arm["repo"], arm["arm"], "grid"] + row + ["", "", "", label])
        print(f"   {arm['arm']} single-boot grid done", flush=True)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("app", help="repo key e.g. ciiceronee")
    ap.add_argument("--freshboot", action="store_true", help="protocol v1: fresh process per grid cell + randomised order")
    ap.add_argument("--knee", type=int, default=None, help="reuse this S2 knee (skip discovery)")
    ap.add_argument("--seed", type=int, default=20261009)
    ap.add_argument("--probe2560", metavar="ARM", default=None,
                    help="run the single cell rate=2560 for ARM once (pinned/unpinned per TIER2_PIN); boots the arm and exits")
    ap.add_argument("--arms", metavar="ARMS", default=None,
                    help="comma list of arm ids to run, e.g. S1,S2,S3 (default: all arms for the app)")
    a = ap.parse_args()

    plan = load_plan()
    arms = [x for x in plan["arms"] if x["repo"] == a.app]
    if not arms:
        print(f"no arms for repo {a.app}")
        return 1
    if a.arms:
        arms = [x for x in arms if x["arm"] in set(a.arms.split(","))]
        if not arms:
            print(f"no matching arms for {a.app}: {a.arms}")
            return 1
    repo_dir = HERE.parent / "repos" / a.app
    out = HERE.parent / "results" / OUTDIR_REL / a.app
    out.mkdir(parents=True, exist_ok=True)
    raw_f = out / "raw.tsv"
    pin = "pinned" if (os.environ.get("TIER2_PIN", "1") != "0") else "unpinned"
    print(f"=== {a.app} [{pin}] ===", flush=True)

    if a.probe2560:
        arm = next(x for x in arms if x["arm"] == a.probe2560)
        workdir = out / f"probe2560_{pin}" / arm["arm"]
        workdir.mkdir(parents=True, exist_ok=True)
        (workdir / "server.log").unlink(missing_ok=True)
        with boot_ctx(arm, repo_dir, workdir) as (pro, pid, base, route, auth, header, sall):
            row, _ = run_one(K6, base, route, 2560, workdir, auth, header, "probe2560", 0, sall)
            print(f"   {arm['arm']} @2560 [{pin}] p50={row[2]} p95={row[3]} p99={row[4]} "
                  f"err={row[8]} reqs={row[9]} fid={row[7]} "
                  f"server_cpus={row[10]} k6_cpus={row[11]}", flush=True)
            full = [a.app, arm["arm"], f"probe2560_{pin}"] + row + ["", "", "", ARM_LABEL.get(arm["arm"], "")]
        write_rows(out / f"probe2560_{pin}_raw.tsv", [full])
        return 0

    all_rows: list[list] = []
    if a.knee is not None:
        s2knee, ref_p95, by_rate = a.knee, None, {}
        print(f"  reusing S2 knee = {s2knee} rps (--knee)", flush=True)
    else:
        s2 = next(x for x in arms if x["arm"] == "S2")
        workdir = out / "S2"
        workdir.mkdir(parents=True, exist_ok=True)
        (workdir / "server.log").unlink(missing_ok=True)
        print(f"  -- S2 knee (3-probe) --", flush=True)
        s2knee, ref_p95, knee_rows, by_rate = discover_s2_knee(s2, repo_dir, workdir)
        all_rows += knee_rows
        print(f"  S2 knee = {s2knee} rps (ref_p95={ref_p95:.2f} ms)", flush=True)

    (out / "knee.json").write_text(json.dumps({
        "app": a.app, "box_plan": "voc-c-8c-16gb-150s-amd",
        "instance_id": "e8cd6321-daa8-4f44-9ad6-da6adedc114a",
        "s2_knee_rps": s2knee, "ref_p95_ms": ref_p95,
        "ladder_probes": {str(k): v for k, v in by_rate.items()},
        "grid": [{"frac": f, "K": k} for f, k in MULT],
        "protocol": "fresh-boot-per-cell, randomised order" if a.freshboot else "single-boot ascending",
        "seed": a.seed if a.freshboot else None,
        "s4_label": ARM_LABEL["S4"],
        "pinning": pin, "server_cores": os.environ.get("TIER2_SERVER_CORES", "0,2,4"),
        "k6_cores": os.environ.get("TIER2_K6_CORES", "6")},
        indent=1))

    if a.freshboot:
        print(f"  -- fresh-boot randomised grid (seed={a.seed}), arms={[x['arm'] for x in arms]} --", flush=True)
        all_rows += run_grid_fresh(arms, repo_dir, out, s2knee, a.seed)
    else:
        all_rows += run_grid_single_boot(arms, repo_dir, out, s2knee)

    write_rows(raw_f, all_rows)
    print(f"  wrote {len(all_rows)} rows to {raw_f}", flush=True)
    return 0


def write_rows(path: Path, rows: list[list]) -> None:
    existed = path.exists()
    with open(path, "a") as f:
        if not existed:
            f.write("\t".join(HEADER) + "\n")
        for row in rows:
            row = list(row) + [""] * (len(HEADER) - len(row))
            f.write("\t".join("" if v is None else str(v) for v in row) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
