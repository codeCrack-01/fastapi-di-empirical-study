"""phaseB.py — revised Tier-2 Phase B runner (per user brief, POST-A preflight).

Per app (invoked as  `python phaseB.py <repo>`, e.g. ciiceronee):

  1. S2 arm only: 3-probe knee discovery. Every ladder rung is probed 3 times
     and qualified on the MEDIAN (tier-1 protocol: p95 <= 3*p95_ref, err <= 1%,
     fidelity >= 0.98); knee = last qualifying rung.
  2. Matched absolute-rate grid for ALL FOUR arms at
        S2knee x {0.75: K=3, 1.0: K=5, 1.25: K=5, 1.5: K=5}
     pinned (offset via TIER2_PIN/TIER2_SERVER_CORES/TIER2_K6_CORES). Reps are
     min-max only.

Plus a one-cell probe for the S3@2560 pinned-vs-unpinned comparison:

    TIER2_PIN=1 python phaseB.py <repo> --probe2560 <arm>
    TIER2_PIN=0 python phaseB.py <repo> --probe2560 <arm>

Run pinned/unpinned as TWO back-to-back processes (constants bind at import).

azure: report S1/S2/S3 only on its bench route (/api/health does not cross the
container); if a route DOES cross, include S4.

Rows written to results/v2/bench/<app>/raw.tsv (append; header on first run)
plus knee.json. Every cell records both processes' /proc/<pid>/status
Cpus_allowed_list as pinning evidence.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
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
    arm_env,
    boot,
    load_plan,
    resolve_auth,
    venv_python,
)

# Matched absolute-rate grid: S2knee x {frac: K}
MULT = [(0.75, 3), (1.0, 5), (1.25, 5), (1.5, 5)]
LADDER = KNEE.LADDER
REF_RPS = KNEE.REF_RPS  # 10.0
P95_MULT = KNEE.P95_MULT  # 3.0
MAX_ERR = KNEE.MAX_ERR
MIN_FID = KNEE.MIN_ACHIEVED

HEADER = [
    "repo", "arm", "stage", "rate", "probe",
    "p50_ms", "p95_ms", "p99_ms", "cell_s",
    "achieved_rate", "fidelity", "window_errors", "window_requests",
    "cpus_allowed_server", "cpus_allowed_k6",
]


class CellFailed(Exception):
    pass


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
    def med(key, pick=None):
        vals = sorted(pick(c) if pick else (c.get("window") or {}).get(key) for c in cells)
        return vals[len(vals) // 2]
    return {
        "p95": med("p95"),
        "err": med("window_errors", lambda c: (c["window_errors"] or 0) / max(1, c["window_requests"] or 1)),
        "fid": med("load_fidelity"),
        "ref_p95": med("p95"),
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


def discover_s2_knee(arm, repo_dir, workdir, out):
    py = venv_python(arm, repo_dir)
    env = {**os.environ, **arm_env(arm)}
    rows = []
    probes_by_rate = {}
    with boot_ctx(arm, repo_dir, workdir) as (pro, pid, base, route, auth, header, sall):
        # reference: 3 probes @10 rps, median p95
        ref_cells = []
        for i in range(3):
            row, s = run_one(K6, base, route, REF_RPS, workdir, auth, header, "ref", i, sall)
            row_f = [arm["repo"], arm["arm"], "ref", REF_RPS, i] + row[0][1:]
            rows.append(row_f)
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
                rows.append([arm["repo"], arm["arm"], "knee", rate, i] + row[0][1:])
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


def run_grid(arm, repo_dir, workdir, s2knee, out, print_prefix=""):
    py = venv_python(arm, repo_dir)
    env = {**os.environ, **arm_env(arm)}
    rows = []
    with boot_ctx(arm, repo_dir, workdir) as (pro, pid, base, route, auth, header, sall):
        for frac, k in MULT:
            rate = int(round(s2knee * frac))
            for probe in range(k):
                try:
                    row, _ = run_one(K6, base, route, rate, workdir, auth, header, "grid", probe, sall)
                except CellFailed:
                    rows.append([arm["repo"], arm["arm"], "grid", rate, probe,
                                 "", "", "", "", "", "", "ERRk6", "", sall, ""])
                    print(f"   !! grid cell {rate} probe {probe} failed (k6 error)", flush=True)
                    continue
                rows.append([arm["repo"], arm["arm"], "grid", rate, probe] + row[0][1:])
        print(f"   grid {len(rows)} cells done", flush=True)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("app", help="repo key e.g. ciiceronee")
    ap.add_argument("--probe2560", metavar="ARM", default=None,
                    help="run the single cell rate=2560 for ARM once (pinned or unpinned per TIER2_PIN env); boots the arm and exits")
    a = ap.parse_args()

    plan = load_plan()
    arms = [x for x in plan["arms"] if x["repo"] == a.app]
    if not arms:
        print(f"no arms for repo {a.app}")
        return 1
    repo_dir = HERE.parent / "repos" / a.app
    out = HERE.parent / "results" / "v2" / "bench" / a.app
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
            print(f"   {arm['arm']} @2560 [{pin}] p50={row[0][2]} p95={row[0][3]} p99={row[0][4]} "
                  f"err={row[0][8]} reqs={row[0][9]} fid={row[0][7]} "
                  f"server_cpus={row[0][10]} k6_cpus={row[0][11]}", flush=True)
            full = [a.app, arm["arm"], f"probe2560_{pin}", 2560, 0] + row[0][1:]
        write_rows(out / f"probe2560_{pin}_raw.tsv", [full])
        return 0

    # main design: S2 3-probe knee, then matched grid for all four arms
    s2 = next(x for x in arms if x["arm"] == "S2")
    workdir = out / "S2"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "server.log").unlink(missing_ok=True)
    print(f"  -- S2 knee (3-probe) --", flush=True)
    s2knee, ref_p95, knee_rows, by_rate = discover_s2_knee(s2, repo_dir, workdir, out)
    print(f"  S2 knee = {s2knee} rps (ref_p95={ref_p95:.2f} ms)", flush=True)
    (out / "knee.json").write_text(json.dumps({
        "app": a.app, "box_plan": "voc-c-8c-16gb-150s-amd",
        "instance_id": "e8cd6321-daa8-4f44-9ad6-da6adedc114a",
        "s2_knee_rps": s2knee, "ref_p95_ms": ref_p95,
        "ladder_probes": {str(k): v for k, v in by_rate.items()},
        "grid": [{"frac": f, "K": k} for f, k in MULT],
        "pinning": pin, "server_cores": os.environ.get("TIER2_SERVER_CORES", "0,2,4"),
        "k6_cores": os.environ.get("TIER2_K6_CORES", "6")},
        indent=1))

    all_rows = list(knee_rows)
    for arm in arms:  # S1..S4 in plan order
        print(f"  -- {arm['arm']} matched grid @ S2knee={s2knee} --", flush=True)
        arm_work = out / arm["arm"]
        arm_work.mkdir(parents=True, exist_ok=True)
        (arm_work / "server.log").unlink(missing_ok=True)
        try:
            all_rows += run_grid(arm, repo_dir, arm_work, s2knee, out)
        except CellFailed as e:
            print(f"   !! cell failed at {e}", flush=True)

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