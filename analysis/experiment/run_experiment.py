"""run_experiment.py — orchestrator for the ReviewGate S0-S3 matrix.

Per protocol (§7 of docs/experiment_proposal.md):

  fresh uvicorn process -> health wait (startup clock) -> warm-up 10 s
  -> measurement window 30 s (k6 steady at cell rate) -> cooldown >= 10 s
  -> terminate. Sampler subprocess pinned off-core records CPU/RSS.

Run matrix: strategies x modes x levels x R=5, order randomized within
superblocks (one repetition of every cell), interleaved across the day.

Usage (from analysis/experiment, in .venv):
    python run_experiment.py --dry-run            # print plan only
    python run_experiment.py                       # full matrix
    python run_experiment.py --cell s1 A sub        # single cell, for debugging
    python run_experiment.py --levels 'A:80,160,240; B:60,120,180'
    python run_experiment.py --reps 5 --port0 8200 --server-core 2 --sampler-core 3 --k6core 4
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
K6 = "k6"

from core import db  # noqa: E402  (import after HERE/RESULTS setup)

WARMUP_S = 10.0
WINDOW_S = 30.0
COOLDOWN_S = 12.0
STARTUP_REPS = 5


def fresh_db(label: str) -> Path:
    """Create and return a path to a pristine, unshared seed database.

    Each cell gets its own database file (initialized from nothing, seeded
    exactly once by core.db.init_database), so every run sees byte-identical
    schema + seed regardless of how many earlier runs wrote. This removes
    DB-size drift from the measurement.
    """
    p = RESULTS / "db" / f"{label}.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    db.init_database(p)
    return p


def start_server(strategy: str, mode: str, port: int, core: str, seed_db: Path) -> tuple[subprocess.Popen, float]:
    cfg = ["taskset", "-c", core, HERE / ".venv/bin/python", "-m", "uvicorn",
           f"straights.{strategy}.app:app", "--host", "127.0.0.1", "--port", str(port),
           "--workers", "1", "--log-level", "warning"]
    env = dict(os.environ, REVIEWGATE_MODE=mode, PYTHONHASHSEED="0",
               REVIEWGATE_DB=str(seed_db))
    proc = subprocess.Popen(cfg, cwd=HERE, env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    return proc, time.monotonic()


def wait_ready(port: int, timeout: float = 30.0) -> None:
    import httpx
    end = time.monotonic() + timeout
    last = None
    while time.monotonic() < end:
        try:
            r = httpx.get(f"http://127.0.0.1:{port}/health", timeout=1.0)
            if r.status_code == 200:
                return
        except Exception as e:
            last = e
        time.sleep(0.05)
    raise RuntimeError(f"server :{port} not ready: {last}")


def start_sampler(pid: int, out: Path, core: str) -> subprocess.Popen:
    cfg = ["taskset", "-c", core, sys.executable, str(HERE / "sampler.py"),
           str(pid), str(out), "0.1"]
    return subprocess.Popen(cfg, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)


def run_k6(port: int, rate: float, summary_file: Path, csv_file: Path, core: str,
           scenario: str = "steady") -> dict:
    cmd = [K6, "run", "--quiet",
           f"--out=csv={csv_file}", "-e", f"TARGET_URL=http://127.0.0.1:{port}",
           "-e", f"SCENARIO={scenario}", "-e", f"RATE={rate}",
           "-e", f"WARMUP_MS={int(WARMUP_S * 1000)}", "-e", f"DURATION_MS={int(WINDOW_S * 1000)}",
           "-e", f"COOLDOWN_MS={int(COOLDOWN_S * 1000)}",
           "-e", f"RAMP_MAX_RPS={int(rate * 3)}",
           "-e", f"SUMMARY_FILE={summary_file}", str(HERE / "k6" / "harness.js")]
    if core:
        cmd = ["taskset", "-c", core] + cmd
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=1200)
    return {"rc": r.returncode, "stderr_tail": r.stderr[-400:]}


def run_cell(strategy: str, mode: str, rate: float, port: int, server_core: str,
             sampler_core: str, k6_core: str, run_dir: Path, seed_db: Path) -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    proc, t_start = start_server(strategy, mode, port, server_core, seed_db)
    meta = {"strategy": strategy, "mode": mode, "rate": rate, "run_dir": str(run_dir)}
    try:
        wait_ready(port)
        startup_ms = (time.monotonic() - t_start) * 1000.0
        s = start_sampler(proc.pid, run_dir / "sampler.csv", sampler_core)

        summ = run_k6(port, rate, run_dir / "run.json", run_dir / "run.csv", k6_core)
        proc.terminate()
        proc.wait(timeout=20)
        s.terminate()
        s.wait(timeout=10)

        try:
            summary = json.loads((run_dir / "run.json").read_text())
        except Exception:
            summary = {"_parse_error": True}
        sampler = (run_dir / "sampler.csv").read_text() if (run_dir / "sampler.csv").exists() else ""
        cpu, rss = summarize_sampler(sampler)
        meta.update({
            "startup_ms": round(startup_ms, 1),
            "k6_rc": summ["rc"],
            "window_p50": summary.get("window_p50"),
            "window_p95": summary.get("window_p95"),
            "window_p99": summary.get("window_p99"),
            "window_mean": summary.get("window_mean"),
            "window_count": summary.get("windowCount"),
            "http_avg": (summary.get("http_req_duration") or {}).get("avg"),
            "http_p95": (summary.get("http_req_duration") or {}).get("p95"),
            "http_count": (summary.get("http_req_duration") or {}).get("count"),
            "check_failures": summary.get("checkFailures"),
            "http_error_rate": summary.get("httpErrors"),
            "cpu_usr_pct": cpu[0], "cpu_sys_pct": cpu[1],
            "rss_avg_mb": rss[0], "rss_peak_mb": rss[1],
            "stderr_tail": summ["stderr_tail"],
        })
        return meta
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=20)


def summarize_sampler(text: str) -> tuple[tuple[float, float], tuple[float, float]]:
    rows = []
    peak = 0.0
    for line in text.splitlines():
        if line.startswith("#peak"):
            peak = float(line.split("=")[1])
            continue
        p = line.split(",")
        if len(p) == 6 and p[0] != "ts_ms":
            try:
                rows.append((float(p[2]), float(p[3]), float(p[4])))
            except ValueError:
                pass
    if not rows:
        return (0.0, 0.0), (0.0, peak)
    usr = sum(r[0] for r in rows) / len(rows)
    sys_ = sum(r[1] for r in rows) / len(rows)
    rss = sum(r[2] for r in rows) / len(rows)
    return (round(usr, 2), round(sys_, 2)), (round(rss, 2), round(max(peak, max(r[2] for r in rows)), 2))


def cell_label(cell) -> str:
    s, m, lvl = cell
    return f"{s}.{m}.{lvl}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cell", help="single cell: s0|s1|s2|s3 A|B sub|at|over")
    ap.add_argument("--levels", default=None,
                    help="levels per mode: 'A:80,160,240; B:60,120,180' (overrides --rates)")
    ap.add_argument("--sub-frac", type=float, default=0.5,
                    help="sub-knee fraction of knee (default 0.5 -> overridden by explicit levels)")
    ap.add_argument("--over-frac", type=float, default=1.5)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--port0", type=int, default=8200)
    ap.add_argument("--server-core", default="2")
    ap.add_argument("--sampler-core", default="3")
    ap.add_argument("--k6-core", default="4")
    ap.add_argument("--no-knee", action="store_true",
                    help="use --levels directly without knee json")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)

    modes = ["A", "B"]
    strategies = ["s0", "s1", "s2", "s3"]

    # --- resolve levels ----------------------------------------------------
    if args.levels:
        levels = {}
        for spec in args.levels.split(";"):
            m, rates = spec.strip().split(":")
            levels[m.strip()] = [float(x) for x in rates.split(",") if x.strip()]
    else:
        levels = {}
        for m in modes:
            knee_json = RESULTS / f"knee_{m}.json"
            if args.no_knee or not knee_json.exists():
                # fallback defaults
                knee = 160.0 if m == "B" else 900.0
            else:
                knee = json.loads(knee_json.read_text()).get("knee_rps") or 160.0 if m == "B" else 900.0
                if not knee:
                    knee = 160.0 if m == "B" else 900.0
            levels[m] = [round(knee * args.sub_frac), round(knee), round(knee * args.over_frac)]
    print(f"[orchestrator] levels: {levels}")

    cells = [(s, m, lvl) for s in strategies for m in modes for lvl in levels[m]]

    if args.dry_run:
        for rep in range(args.reps):
            block = cells[:]
            random.Random(rep + 1).shuffle(block)
            print(f"superblock {rep}: " + ", ".join(cell_label(c) for c in block))
        print(f"total steady runs: {len(cells) * args.reps}; est. wall: "
              f"{len(cells) * args.reps * (WARMUP_S + WINDOW_S + COOLDOWN_S) / 3600:.1f} h")
        return 0

    if args.cell:
        cell = args.cell.split(" ")
        cells = [(cell[0], cell[1], float(cell[2]))]

    # --- startup timing (STARTUP_REPS, all strategies, both modes) ---------
    startup_rows = []
    for s in strategies:
        for m in modes:
            for i in range(STARTUP_REPS):
                port = args.port0 + i
                sdb = fresh_db(f"startup-{s}-{m}-{i}")
                try:
                    proc, t0 = start_server(s, m, port, args.server_core, sdb)
                    try:
                        wait_ready(port)
                        startup_rows.append({"strategy": s, "mode": m, "rep": i,
                                             "startup_ms": round((time.monotonic() - t0) * 1000, 1)})
                    finally:
                        proc.terminate(); proc.wait(timeout=20)
                finally:
                    sdb.unlink(missing_ok=True)
    with open(RESULTS / "startup.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["strategy", "mode", "rep", "startup_ms"])
        w.writeheader(); w.writerows(startup_rows)

    if args.cell:
        sdb = fresh_db(f"cell-{cell_label(cells[0])}")
        try:
            run_cell(*cells[0], args.port0, args.server_core, args.sampler_core,
                     args.k6_core, RESULTS / "cell", sdb)
        finally:
            sdb.unlink(missing_ok=True)
        print("[orchestrator] single-cell done")
        return 0

    # --- full matrix --------------------------------------------------------
    runs_meta = []
    run_i = 0
    for rep in range(args.reps):
        block = cells[:]
        random.Random(rep + 1).shuffle(block)
        print(f"[orchestrator] superblock {rep} ({len(block)} runs)", flush=True)
        for i, (s, m, lvl) in enumerate(block):
            run_dir = RESULTS / "steady" / f"{rep:02d}-{cell_label((s, m, lvl))}"
            sdb = fresh_db(f"run-{rep:02d}-{cell_label((s, m, lvl))}")
            try:
                meta = run_cell(s, m, lvl, args.port0, args.server_core, args.sampler_core,
                                args.k6_core, run_dir, sdb)
            finally:
                sdb.unlink(missing_ok=True)
            runs_meta.append(meta)
            run_i += 1
            print(f"  [{rep}.{i}] {cell_label((s, m, lvl))} p50={meta.get('window_p50')}ms "
                  f"p95={meta.get('window_p95')}ms rc={meta.get('k6_rc')}", flush=True)

    with open(RESULTS / "runs.csv", "w", newline="") as f:
        cols = ["strategy", "mode", "rate", "startup_ms", "window_p50", "window_p95",
                "window_p99", "window_mean", "window_count", "http_avg", "http_p95",
                "http_count", "check_failures", "http_error_rate", "cpu_usr_pct",
                "cpu_sys_pct", "rss_avg_mb", "rss_peak_mb", "k6_rc", "run_dir"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(runs_meta)
    print(f"[orchestrator] done: {len(runs_meta)} steady runs, results/results/steady + runs.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())