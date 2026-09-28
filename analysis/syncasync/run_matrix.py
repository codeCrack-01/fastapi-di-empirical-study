"""run_matrix.py — the full 16-condition grid, or a 5-rep smoke of it.

One driver for both. The only difference is --reps, and the smoke runs are
tagged and written to a separate directory so they can never be mistaken for
measurements or pooled with them.

    smoke:  16 conditions x 5 reps  = 80 cells
    main:   16 conditions x 40 reps = 640 cells

Each cell is a fresh server process on the server's cores, k6 on its own core,
a fixed rate, and a DB hash checked before and after. The whole grid is
randomised across conditions, so a drift in box state over the 12+ hours does not
land systematically on one arm.

Smoke data is written but never analysed: the pre-registration discards it, and
analyze.py refuses to read a smoke directory.

Run:
    python run_matrix.py --smoke
    python run_matrix.py --main
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from runner import (  # noqa: E402
    ARM, REPS, WARMUP_S, WINDOW_S, COOLDOWN_S, WORKERS,
    assert_disjoint, run_ramp, sha256_db,
)

PATTERNS = ["p1_direct", "p2_depends", "p3_middleware", "p4_container"]
MODELS = ["sync", "async"]
LOADS = ["capacity", "overload"]

SMOKE_REPS = 5
SEED = 20260928

FIELDS = [
    "condition", "pattern", "model", "load", "rep", "rate",
    "window_p50", "window_p95", "window_mean", "window_max",
    "window_requests", "window_errors", "window_error_rate",
    "achieved", "check_fails",
    "cpu_seconds", "cpu_seconds_per_req", "rss_peak_mb", "startup_ms",
    "db_sha256_before", "db_sha256_after", "db_unchanged", "returncode",
]


def load_rates(knee_file: Path) -> dict:
    """{arm: (capacity_rate, overload_rate)} from the knee medians."""
    if not knee_file.exists():
        raise SystemExit(
            f"FATAL: {knee_file} not found. Every app needs its own knee before the "
            "grid can run: 1.0x and 1.5x of a shared rate would not be 'capacity'."
        )
    out = {}
    for pattern in PATTERNS:
        for model in MODELS:
            f = knee_file / f"knee_{pattern}_{model}.json"
            if not f.exists():
                raise SystemExit(f"FATAL: missing knee result {f}")
            k = json.loads(f.read_text()).get("knee_median")
            if not k:
                raise SystemExit(f"FATAL: {f} has no knee_median (probe failed)")
            out[f"{pattern}/{model}"] = (float(k), float(k) * 1.5)
    return out


def build_plan(rates: dict, reps: int) -> list[dict]:
    cells = []
    for pattern in PATTERNS:
        for model in MODELS:
            arm = f"{pattern}/{model}"
            cap, over = rates[arm]
            for load, rate in (("capacity", cap), ("overload", over)):
                for rep in range(reps):
                    cells.append({
                        "condition": f"{arm}@{load}",
                        "pattern": pattern, "model": model,
                        "load": load, "rep": rep, "rate": rate,
                    })
    return cells


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--smoke", action="store_true", help=f"{SMOKE_REPS} reps, discarded")
    g.add_argument("--main", action="store_true", help=f"{REPS} reps, measured")
    ap.add_argument("--knee-dir", type=Path, default=HERE / "results")
    ap.add_argument("--port0", type=int, default=8900)
    ap.add_argument("--only", default=None, help="substring filter on condition")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    assert_disjoint()

    smoke = args.smoke
    reps = SMOKE_REPS if smoke else REPS
    tag = "smoke" if smoke else "main"
    outdir = HERE / "results" / tag
    outdir.mkdir(parents=True, exist_ok=True)

    rates = load_rates(args.knee_dir)
    cells = build_plan(rates, reps)
    if args.only:
        cells = [c for c in cells if args.only in c["condition"]]

    random.Random(SEED).shuffle(cells)

    print(f"run  tag={tag}  reps={reps}  cells={len(cells)}")
    print(f"out  {outdir}")
    if smoke:
        print("NOTE: smoke data is written for provenance and NEVER analysed")

    if args.dry_run:
        for c in cells:
            print(f"  {c['condition']:34s} rep={c['rep']:2d} rate={c['rate']:8.1f}")
        return 0

    csv_path = outdir / "cells.csv"
    done = set()
    if csv_path.exists():  # resume support: skip cells already recorded
        with open(csv_path) as fh:
            for row in csv.DictReader(fh):
                done.add((row["condition"], row["rep"]))
        print(f"resume: {len(done)} cells already recorded")

    fh = open(csv_path, "a", newline="")
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    if not done:
        writer.writeheader()
        fh.flush()

    db_before_first = sha256_db()
    t_start = time.time()
    n = 0
    for cell in cells:
        key = (cell["condition"], str(cell["rep"]))
        if key in done:
            continue
        res = run_ramp(ARM(cell["pattern"], cell["model"]), args.port0,
                       cell["rate"], WINDOW_S, WARMUP_S, COOLDOWN_S,
                       tag=f"{tag}-{cell['condition']}")
        w = res.window or {}
        e = res.extra or {}
        row = {
            "condition": cell["condition"], "pattern": cell["pattern"],
            "model": cell["model"], "load": cell["load"], "rep": cell["rep"],
            "rate": round(cell["rate"], 2),
            "window_p50": w.get("p50"), "window_p95": w.get("p95"),
            "window_mean": w.get("mean"), "window_max": w.get("max"),
            "window_requests": e.get("window_requests"),
            "window_errors": e.get("window_errors"),
            "window_error_rate": e.get("window_error_rate"),
            "achieved": round(res.achieved, 4),
            "check_fails": (res.checks or {}).get("fails"),
            "cpu_seconds": res.cpu_seconds,
            "cpu_seconds_per_req": e.get("cpu_seconds_per_req"),
            "rss_peak_mb": res.rss_peak_mb, "startup_ms": res.startup_ms,
            "db_sha256_before": res.db_sha256_before,
            "db_sha256_after": res.db_sha256_after,
            "db_unchanged": res.db_unchanged, "returncode": res.returncode,
        }
        writer.writerow(row)
        fh.flush()
        n += 1

        if not res.db_unchanged:
            print("FATAL: database hash changed mid-run; stopping", file=sys.stderr)
            fh.close()
            return 2
        if n % 10 == 0 or n == 1:
            el = time.time() - t_start
            eta = (el / n) * (len(cells) - n)
            print(f"  [{n}/{len(cells)}] {row['condition']} p95={row['window_p95']}ms "
                  f"ach={row['achieved']:.3f} elapsed={el / 60:.1f}m eta={eta / 60:.0f}m",
                  flush=True)

    fh.close()
    db_after = sha256_db()
    print(f"\ndone  {n} cells in {(time.time() - t_start) / 3600:.2f}h")
    print(f"db    {db_before_first[:16]} -> {db_after[:16]} "
          f"unchanged={db_before_first == db_after}")
    print(f"csv   {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
