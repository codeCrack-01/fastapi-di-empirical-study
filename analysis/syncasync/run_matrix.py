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
import re
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

# ---- host-drift reference cells (amendment 4d) ------------------------------
# The study is a single session on one host. If the host itself drifts over the
# session -- neighbouring load, thermal throttling, a noisy neighbour, provider
# migration -- then condition effects measured at different times are confounded
# with time, and the whole single-session design is quietly weakened. Measuring
# that directly is cheap, so the grid repeats ONE fixed cell at fixed positions.
#
# The reference is p1_direct/sync at 25% of its own capacity knee: the simplest
# arm, comfortably in the linear region, so a change in its latency is far more
# likely to be the host than the application. It is a diagnostic, not a result:
# analyze.py excludes these rows, and they are never used to set a rate.
DRIFT_REF_ARM = "p1_direct/sync"
DRIFT_REF_FRACTION = 0.25
DRIFT_REF_COUNT = 5
DRIFT_REF_CONDITION = f"driftref/{DRIFT_REF_ARM}@capacity"

FIELDS = [
    "condition", "pattern", "model", "load", "rep", "rate", "rate_exact",
    "is_drift", "drift_index", "after_cell", "steal_jiffies",
    "window_p50", "window_p95", "window_mean", "window_max",
    "window_requests", "window_errors", "window_error_rate",
    "achieved", "check_fails",
    "cpu_seconds", "cpu_seconds_per_req", "rss_peak_mb", "startup_ms",
    "db_sha256_before", "db_sha256_after", "db_unchanged", "returncode",
]


def load_rates(knee_file: Path, smoke: bool) -> dict:
    """{arm: (capacity_rate, overload_rate)} from the knee medians.

    `smoke` is the run's own mode, and is enforced against the knee source: the
    640-cell main run may never use single-probe smoke knees, and the smoke may
    never silently use the 3-probe study knees without saying so.
    """
    if not knee_file.exists():
        raise SystemExit(
            f"FATAL: {knee_file} not found. Every app needs its own knee before the "
            "grid can run: 1.0x and 1.5x of a shared rate would not be 'capacity'."
        )
    # The primary guard. Directory name is the mode tag written by knee.py.
    if not smoke and knee_file.name == "smoke_knees":
        raise SystemExit(
            f"FATAL: refusing to run the MAIN grid from {knee_file}. Those are "
            "single-probe SMOKE knees; the main run requires the 3-probe medians "
            "the pre-registration defines. Run the 24 study knees first."
        )
    out = {}
    for pattern in PATTERNS:
        for model in MODELS:
            f = knee_file / f"knee_{pattern}_{model}.json"
            if not f.exists():
                raise SystemExit(f"FATAL: missing knee result {f}")
            doc = json.loads(f.read_text())
            k = doc.get("knee_median")
            if not k:
                raise SystemExit(f"FATAL: {f} has no knee_median (probe failed)")
            # Second guard: the per-file mode tag must agree with the directory.
            # Catches a knee file copied between directories by hand.
            mode = doc.get("mode", "study")
            if knee_file.name == "smoke_knees" and mode != "smoke":
                raise SystemExit(
                    f"FATAL: {f} is mode={mode!r} but lives in smoke_knees/"
                )
            if mode == "smoke" and knee_file.name != "smoke_knees":
                raise SystemExit(
                    f"FATAL: {f} is a single-probe SMOKE knee and may not be used "
                    "as a study knee. Move it to results/smoke_knees/ for smoke use."
                )
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
                        "load": load, "rep": rep,
                        # k6's arrival-rate stages take an INT64 target; a
                        # fractional rate makes k6 fail to parse its options,
                        # exit immediately, and yield a cell with zero requests
                        # and no error. A study knee is a median of 3 probes and
                        # can be odd, which makes knee*1.5 fractional, so the
                        # rate is rounded to the nearest whole rps here and the
                        # exact value is kept for provenance.
                        "rate": int(round(rate)), "rate_exact": rate,
                    })
    return cells


def make_drift_cell(idx: int, after_cell: int, n_study: int, rates: dict) -> dict:
    """Build one host-drift reference cell.

    Same app, same load, every time. Only its position in the run changes, so
    any trend across the drift cells is a property of the host, not of the
    application.
    """
    pattern, model = DRIFT_REF_ARM.split("/")
    cap = rates[DRIFT_REF_ARM][0]
    exact = cap * DRIFT_REF_FRACTION
    return {
        "condition": DRIFT_REF_CONDITION, "pattern": pattern, "model": model,
        "load": "capacity", "rep": idx,
        # integer for the same k6 reason as build_plan(); 25% of a knee is
        # frequently fractional (e.g. 0.25 * 950 = 237.5) and k6 rejects it
        "rate": int(round(exact)), "rate_exact": exact,
        "is_drift": 1, "drift_index": idx, "after_cell": after_cell,
        "n_study": n_study,
    }


def check_rate_is_usable(cell: dict) -> None:
    """Fail loudly on a rate k6 cannot run.

    A fractional or non-positive rate is not an error k6 reports usefully: it
    exits during option parsing, the cell records zero requests and a null
    window, and the failure only surfaces later as a mysterious missing result.
    Refuse it up front instead.
    """
    rate = cell.get("rate")
    if not isinstance(rate, int) or rate <= 0:
        raise ValueError(
            f"unusable rate {rate!r} for cell {cell.get('condition')!r} "
            f"(rep {cell.get('rep')}): k6 arrival-rate stages require a "
            f"positive integer rps; exact value was {cell.get('rate_exact')!r}"
        )


def interleave_drift(cells: list[dict], rates: dict) -> list[dict]:
    """Splice DRIFT_REF_COUNT reference cells into the shuffled study order.

    Called AFTER the shuffle, so the study cells keep exactly the randomised
    order fixed by SEED. Reference cells are added at evenly spaced positions
    from the first to near the last study cell.
    """
    if DRIFT_REF_COUNT <= 0 or not cells:
        return cells
    n = len(cells)
    step = max(1, n // DRIFT_REF_COUNT)
    out: list[dict] = []
    d = 0
    # the last reference is placed after the final study cell, so the session is
    # bracketed by reference measurements at both ends rather than trailing off
    for i, c in enumerate(cells):
        if i % step == 0 and d < DRIFT_REF_COUNT - 1:
            out.append(make_drift_cell(d, i, n, rates))
            d += 1
        out.append(c)
    if d < DRIFT_REF_COUNT:
        out.append(make_drift_cell(d, n, n, rates))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--smoke", action="store_true", help=f"{SMOKE_REPS} reps, discarded")
    g.add_argument("--main", action="store_true", help=f"{REPS} reps, measured")
    ap.add_argument("--knee-dir", type=Path, default=HERE / "results")
    ap.add_argument("--port0", type=int, default=8900)
    ap.add_argument("--only", default=None, help="substring filter on condition")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-drift", action="store_true",
                    help="disable the host-drift reference cells (amendment 4d)")
    args = ap.parse_args()

    assert_disjoint()

    smoke = args.smoke
    reps = SMOKE_REPS if smoke else REPS
    tag = "smoke" if smoke else "main"
    outdir = HERE / "results" / tag
    outdir.mkdir(parents=True, exist_ok=True)

    rates = load_rates(args.knee_dir, smoke)
    cells = build_plan(rates, reps)
    if args.only:
        cells = [c for c in cells if args.only in c["condition"]]

    random.Random(SEED).shuffle(cells)

    n_study = len(cells)
    if not args.no_drift:
        cells = interleave_drift(cells, rates)
        _dr = make_drift_cell(0, 0, n_study, rates)
        print(f"NOTE: {DRIFT_REF_COUNT} host-drift reference cells added "
              f"({DRIFT_REF_CONDITION} @ {_dr['rate']} rps, i.e. "
              f"{DRIFT_REF_FRACTION:.0%} of the {_dr['rate_exact']:.2f} rps exact "
              f"quarter-knee), interleaved into {n_study} study cells; "
              f"diagnostics only, never analysed and never used to set a rate")

    print(f"run  tag={tag}  reps={reps}  study_cells={n_study} total={len(cells)}")
    print(f"out  {outdir}")
    print(f"knees {args.knee_dir}")
    if smoke:
        print("NOTE: smoke data is written for provenance and NEVER analysed")
        if args.knee_dir.name != "smoke_knees":
            print("NOTE: smoke rates are not necessarily single-probe; record the "
                  "knee source in the run log", file=sys.stderr)

    if args.dry_run:
        for c in cells:
            ex = c.get("rate_exact")
            note = "" if ex is None or float(ex) == float(c["rate"]) else \
                   f"  (exact {float(ex):.2f} rounded)"
            print(f"  {c['condition']:34s} rep={c['rep']:2d} "
                  f"rate={c['rate']:8d}{note}")
        return 0

    # provenance: the rates this run used, and where they came from
    (outdir / "rates.json").write_text(json.dumps({
        "knee_dir": str(args.knee_dir),
        "knee_mode": "smoke (1 probe)" if args.knee_dir.name == "smoke_knees"
                     else "study (median of 3)",
        "tag": tag, "reps": reps, "seed": SEED,
        "study_cells": n_study,
        "drift_ref": {
            "enabled": not args.no_drift,
            "condition": DRIFT_REF_CONDITION,
            "count": DRIFT_REF_COUNT,
            "fraction_of_capacity": DRIFT_REF_FRACTION,
            "role": "host-drift diagnostic only; excluded from analysis",
        } if not args.no_drift else {"enabled": False},
        "workers": WORKERS, "warmup_s": WARMUP_S, "window_s": WINDOW_S,
        "cooldown_s": COOLDOWN_S,
        "rates": {k: {"capacity": v[0], "overload": v[1]} for k, v in rates.items()},
    }, indent=2))

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
        # refuse a rate k6 cannot run, before a cell is spent on it
        check_rate_is_usable(cell)
        # condition is "<pattern>/<model>@<load>"; the slash would turn the log
        # path into a directory that does not exist
        safe = re.sub(r"[^A-Za-z0-9._@+-]", "-", cell["condition"])
        res = run_ramp(ARM(cell["pattern"], cell["model"]), args.port0,
                       cell["rate"], WINDOW_S, WARMUP_S, COOLDOWN_S,
                       tag=f"{tag}-{safe}")
        w = res.window or {}
        e = res.extra or {}
        row = {
            "condition": cell["condition"], "pattern": cell["pattern"],
            "model": cell["model"], "load": cell["load"], "rep": cell["rep"],
            "rate": cell["rate"], "rate_exact": cell.get("rate_exact", ""),
            "is_drift": cell.get("is_drift", 0),
            "drift_index": cell.get("drift_index", ""),
            "after_cell": cell.get("after_cell", ""),
            "steal_jiffies": e.get("steal_jiffies"),
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
        if n % 10 == 0 or n == 1 or row["is_drift"]:
            el = time.time() - t_start
            eta = (el / n) * (len(cells) - n)
            if row["is_drift"]:
                # printed at full volume: this is the drift time series
                print(f"  [{n}/{len(cells)}] DRIFT-REF #{row['drift_index']} "
                      f"after_cell={row['after_cell']} p50={row['window_p50']}ms "
                      f"p95={row['window_p95']}ms ach={row['achieved']:.3f} "
                      f"steal={row['steal_jiffies']} elapsed={el / 60:.1f}m",
                      flush=True)
            else:
                print(f"  [{n}/{len(cells)}] {row['condition']} "
                      f"p95={row['window_p95']}ms ach={row['achieved']:.3f} "
                      f"elapsed={el / 60:.1f}m eta={eta / 60:.0f}m", flush=True)

    fh.close()
    db_after = sha256_db()
    print(f"\ndone  {n} cells in {(time.time() - t_start) / 3600:.2f}h")
    print(f"db    {db_before_first[:16]} -> {db_after[:16]} "
          f"unchanged={db_before_first == db_after}")
    print(f"csv   {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
