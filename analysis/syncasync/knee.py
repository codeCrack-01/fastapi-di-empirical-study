"""knee.py — operational knee measurement for one ReviewGate-R app.

Knee is defined in advance, per the pre-registration:

    reference : 30 s steady window at 10 req/s -> p95_ref
    knee      : highest offered rate r such that, at r,
                    p95 <= 3 * p95_ref
                    error rate <= 1%
                    achieved / offered >= 0.98

A rate qualifies or it does not. The search is a ramp whose stages are
geometric, then a binary search between the last passing and first failing
stage, so the estimate does not depend on stage granularity.

Each app is probed 3 times; the reported knee is the MEDIAN of the 3.

The ramp runs one process and one k6 invocation, so all requests in a probe go
to the same fresh server process. `ramp.js` reports per-stage aggregates;
`knee.py` reads them back.

Run:  python knee.py --pattern p1_direct --model sync
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from runner import ARM, DB_PATH, RampResult, run_ramp, sha256_db  # noqa: E402

REF_RPS = 10.0
REF_WINDOW_S = 30
P95_MULT = 3.0
MAX_ERR = 0.01
MIN_ACHIEVED = 0.98
REPS = 3

# geometric ramp ladder, doubling: fine enough near the knee, cheap overall
LADDER = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 3200]


def qualifies(r: RampResult, p95_ref: float) -> tuple[bool, str]:
    if r.window is None or r.window.get("count", 0) == 0:
        return False, "no window samples"
    if r.checks and r.checks["fails"] > 0:
        return False, f"check failures {r.checks['fails']}"
    if r.http_error_rate is not None and r.http_error_rate > MAX_ERR:
        return False, f"error rate {r.http_error_rate:.4f} > {MAX_ERR}"
    if r.achieved < MIN_ACHIEVED:
        return False, f"achieved {r.achieved:.3f} < {MIN_ACHIEVED}"
    p95 = r.window["p95"]
    if p95_ref > 0 and p95 > P95_MULT * p95_ref:
        return False, f"p95 {p95:.2f} > {P95_MULT}x ref {p95_ref:.2f}"
    return True, "ok"


def probe_once(pattern: str, model: str, port: int, verbose: bool) -> dict:
    ref = run_ramp(
        ARM(pattern, model), port,
        rate=REF_RPS, window_s=REF_WINDOW_S, warmup_s=5, cooldown_s=0,
        ramp=False, tag="knee-ref",
    )
    if ref.window is None or ref.window.get("count", 0) == 0:
        return {"knee": None, "reason": "reference run produced no samples", "ref": None}
    p95_ref = ref.window["p95"]
    if verbose:
        print(f"    ref 10rps: p50={ref.window['p50']:.2f} p95={p95_ref:.2f} "
              f"achieved={ref.achieved:.3f}")

    passing, failing, trace = None, None, []

    def try_rate(rate: float) -> bool:
        nonlocal passing, failing
        res = run_ramp(
            ARM(pattern, model), port,
            rate=rate, window_s=30, warmup_s=10, cooldown_s=12,
            ramp=True, ramp_max=rate, ramp_ms=8000, tag=f"knee-{int(rate)}",
        )
        ok, why = qualifies(res, p95_ref)
        trace.append({"rate": rate, "p95": (res.window or {}).get("p95"),
                      "achieved": res.achieved, "ok": ok, "why": why})
        if verbose:
            print(f"    {rate:7.0f} rps  p95={(res.window or {}).get('p95', float('nan')):8.2f}"
                  f"  achieved={res.achieved:.3f}  {'PASS' if ok else 'FAIL: ' + why}")
        if ok:
            passing = rate if passing is None else max(passing, rate)
        else:
            failing = rate if failing is None else min(failing, rate)
        return ok

    for rate in LADDER:
        if try_rate(float(rate)):
            if rate == LADDER[-1]:
                # right-censored: every ladder stage qualified
                passing = float(LADDER[-1])
                failing = None
        else:
            break

    # binary refine between last pass and first fail
    if passing is not None and failing is not None:
        lo, hi = passing, failing
        while hi - lo > max(1.0, lo * 0.02):
            mid = (lo + hi) / 2
            if try_rate(mid):
                lo = mid
            else:
                hi = mid
        passing = lo

    if passing is None:
        return {"knee": None, "reason": "no rate qualified, including 10 rps",
                "ref": p95_ref, "trace": trace}
    return {"knee": passing, "reason": "ok", "ref": p95_ref, "trace": trace,
            "censored": failing is None}


def measure(pattern: str, model: str, port: int, reps: int = REPS,
            verbose: bool = True) -> dict:
    out = {"pattern": pattern, "model": model, "reps": reps, "probes": []}
    for i in range(reps):
        if verbose:
            print(f"  probe {i + 1}/{reps}")
        t0 = time.time()
        probe = probe_once(pattern, model, port, verbose)
        probe["index"] = i
        probe["seconds"] = round(time.time() - t0, 1)
        out["probes"].append(probe)
    knees = [p["knee"] for p in out["probes"] if p.get("knee") is not None]
    out["knee_median"] = statistics.median(knees) if knees else None
    out["knees"] = knees
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True)
    ap.add_argument("--model", required=True, choices=["sync", "async"])
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--port", type=int, default=8900)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    before = sha256_db()
    print(f"knee probe {args.pattern}/{args.model}  reps={args.reps}")
    print(f"  db sha256 before {before[:16]}")

    result = measure(args.pattern, args.model, args.port, args.reps)

    after = sha256_db()
    result["db_sha256_before"] = before
    result["db_sha256_after"] = after
    result["db_unchanged"] = before == after
    print(f"  db sha256 after  {after[:16]}  unchanged={before == after}")
    print(f"  knee median      {result['knee_median']}")

    out = args.out or (HERE / "results" / f"knee_{args.pattern}_{args.model}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"  written {out}")
    return 0 if result["knee_median"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
