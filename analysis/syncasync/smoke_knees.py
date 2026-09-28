#!/usr/bin/env python3
"""smoke_knees.py — one knee probe per arm, for the smoke's load rates.

These are NOT study knees. The pre-registration defines a knee as the median of
three probes; this runs exactly one, to get the smoke's capacity/overload rates
and to prove the harness works end to end on the box. Results are written to
results/smoke_knees/, and run_matrix.py is pointed at that directory with
--knee-dir, so a single-probe rate can never be substituted for a study knee.

    python smoke_knees.py                 # all 8 arms
    python smoke_knees.py --only p1_direct

Then:
    python run_matrix.py --smoke --knee-dir results/smoke_knees
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import knee  # noqa: E402
from runner import assert_disjoint, sibling_groups  # noqa: E402

PATTERNS = ["p1_direct", "p2_depends", "p3_middleware", "p4_container"]
MODELS = ["sync", "async"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="substring filter on the arm name")
    ap.add_argument("--port", type=int, default=8900)
    ap.add_argument("--outdir", type=Path, default=HERE / "results" / "smoke_knees")
    args = ap.parse_args()

    assert_disjoint()
    print(f"topology: {sibling_groups()}\n")

    arms = [f"{p}/{m}" for p in PATTERNS for m in MODELS]
    if args.only:
        arms = [a for a in arms if args.only in a]

    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    summary = []

    for i, arm in enumerate(arms, 1):
        pattern, model = arm.split("/")
        est = len(arms) * 8
        print(f"[{i}/{len(arms)}] {arm}  (elapsed {time.time() - t_start:.0f}s, "
              f"est total {est} min)")
        t0 = time.time()
        res = knee.measure(pattern, model, args.port, reps=1, verbose=True)
        res["mode"] = "smoke"
        res["arm"] = arm
        (outdir / f"knee_{pattern}_{model}.json").write_text(
            __import__("json").dumps(res, indent=2, default=str))
        dt = time.time() - t0
        summary.append((arm, res["knee_median"], round(dt)))
        print(f"  -> knee {res['knee_median']}  ({dt:.0f}s)\n")

    print("=" * 62)
    print(f"{'arm':32s} {'knee rps':>10s} {'secs':>7s}")
    for arm, k, dt in summary:
        print(f"{arm:32s} {str(k):>10s} {dt:>7d}")
    missing = [a for a, k, _ in summary if k is None]
    if missing:
        print(f"\nFAILED (no knee): {missing}")
    print(f"total {time.time() - t_start:.0f}s -> {outdir}")
    print("These are SMOKE rates. The study knee is the median of 3 probes.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
