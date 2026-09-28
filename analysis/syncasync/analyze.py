"""analyze.py — the pre-registered statistics. Nothing else is permitted.

Fixed in advance, and this file is covered by the config hash:

  1. Per condition (8 arms x 2 loads), the MEDIAN of the 40 reps, with a
     bootstrap 95% CI over reps. 10,000 resamples, percentile method, seed
     pinned. The CI is on the median, not the mean.
  2. Per pattern per load, the PAIRED sync-minus-async difference of the medians,
     with a paired bootstrap 95% CI that resamples REPS, keeping each rep index
     together across the two arms, because the two arms share box state at that
     index. This is the primary comparison.
  3. A CI spanning zero is reported as UNRESOLVED AT N=40. It is never reported
     as "no difference" and never as "no effect".

Explicitly not done, because the pre-registration does not include them:
no p-values, no interaction or 2x2 tests, no multiplicity correction, no
per-rep outlier removal, no cross-pattern ranking into a single league table.
Per-rep distributions go to the appendix; nothing is trimmed.

The paired difference is AT-CAPACITY-RELATIVE. The sync and async arms of a
pattern have different knees, so 1.0x is each arm's own capacity, not a shared
absolute rate. That is stated in the pre-registration and repeated in the
output, because reading it as equal-rate would be wrong.

Run:  python analyze.py            (refuses to read a smoke directory)
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent

REPS = 40
BOOT = 10000
SEED = 20260928

METRICS = ["window_p50", "window_p95", "window_error_rate",
           "achieved", "cpu_seconds_per_req", "rss_peak_mb"]
# lower is better for these; a positive paired difference then means async worse
LOWER_IS_BETTER = {"window_p50", "window_p95", "cpu_seconds_per_req", "rss_peak_mb"}
HIGHER_IS_BETTER = {"achieved"}
NEUTRAL = {"window_error_rate"}

PATTERNS = ["p1_direct", "p2_depends", "p3_middleware", "p4_container"]
LOADS = ["capacity", "overload"]


def read_cells(path: Path) -> list[dict]:
    with open(path) as fh:
        rows = list(csv.DictReader(fh))
    out = []
    n_drift = 0
    for r in rows:
        # Host-drift reference cells (amendment 4d) are diagnostics. They are
        # dropped here so they cannot reach a result even if the condition-name
        # filter below were ever widened.
        if r.get("is_drift", "0") not in ("0", "", None):
            n_drift += 1
            continue
        rec = {
            "condition": r["condition"], "pattern": r["pattern"], "model": r["model"],
            "load": r["load"], "rep": int(r["rep"]), "rate": float(r["rate"]),
        }
        for m in METRICS:
            v = r.get(m, "")
            rec[m] = float(v) if v not in ("", None) else None
        rec["db_unchanged"] = r.get("db_unchanged") == "True"
        out.append(rec)
    if n_drift:
        print(f"excluded {n_drift} host-drift reference cells (diagnostic only)")
    return out


def median_ci(values: list[float], boot: int = BOOT, seed: int = SEED) -> dict:
    """Median with a percentile bootstrap CI, resampling the observed reps."""
    vals = [v for v in values if v is not None]
    if not vals:
        return {"n": 0, "median": None, "ci95": None}
    rng = random.Random(seed)
    n = len(vals)
    meds = []
    for _ in range(boot):
        meds.append(statistics.median(rng.choices(vals, k=n)))
    meds.sort()
    lo = meds[int(0.025 * boot)]
    hi = meds[int(0.975 * boot) - 1]
    return {"n": n, "median": statistics.median(vals), "ci95": [lo, hi]}


def paired_ci(sync_vals: list[float], async_vals: list[float],
              boot: int = BOOT, seed: int = SEED) -> dict:
    """Paired sync-minus-async difference of medians.

    Resamples REP INDICES, carrying each index across both arms, so the pairing
    survives: a rep index is the same slot in the randomised grid for both arms,
    and any drift in box state at that slot is shared rather than attributed to
    the execution model.
    """
    pairs = [(s, a) for s, a in zip(sync_vals, async_vals) if s is not None and a is not None]
    if not pairs:
        return {"n_pairs": 0, "diff_median": None, "ci95": None, "verdict": "no data"}
    n = len(pairs)
    observed = statistics.median([s for s, _ in pairs]) - \
               statistics.median([a for _, a in pairs])
    rng = random.Random(seed)
    boots = []
    for _ in range(boot):
        idx = [rng.randrange(n) for _ in range(n)]
        ms = statistics.median([pairs[i][0] for i in idx])
        ma = statistics.median([pairs[i][1] for i in idx])
        boots.append(ms - ma)
    boots.sort()
    lo = boots[int(0.025 * boot)]
    hi = boots[int(0.975 * boot) - 1]
    if lo <= 0 <= hi:
        verdict = "unresolved at n=40"
    else:
        worse = "async" if lo > 0 else "sync"
        better = "sync" if lo > 0 else "async"
        verdict = f"{worse} higher than {better}"
    return {
        "n_pairs": n,
        "sync_median": statistics.median([s for s, _ in pairs]),
        "async_median": statistics.median([a for _, a in pairs]),
        "diff_median": observed,
        "ci95": [lo, hi],
        "verdict": verdict,
    }


def by_condition(rows: list[dict]) -> dict:
    out = {}
    for pattern in PATTERNS:
        for model in ("sync", "async"):
            for load in LOADS:
                cond = f"{pattern}/{model}@{load}"
                sel = [r for r in rows if r["condition"] == cond]
                if not sel:
                    continue
                sel.sort(key=lambda r: r["rep"])
                out[cond] = {
                    "n_reps": len(sel),
                    "rate": sel[0]["rate"],
                    "reps": [r["rep"] for r in sel],
                    "db_unchanged_all": all(r["db_unchanged"] for r in sel),
                    "metrics": {m: median_ci([r[m] for r in sel]) for m in METRICS},
                }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", type=Path, default=HERE / "results" / "main" / "cells.csv")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--allow-smoke", action="store_true",
                    help="refused by default: smoke data is never analysed")
    args = ap.parse_args()

    if "smoke" in str(args.cells) and not args.allow_smoke:
        print("REFUSING: the pre-registration discards smoke data. It exists to "
              "verify the harness, not to estimate anything.", file=__import__("sys").stderr)
        return 2

    if not args.cells.exists():
        print(f"missing {args.cells}", file=__import__("sys").stderr)
        return 2

    rows = read_cells(args.cells)
    n_short = [c for c, v in by_condition(rows).items() if v["n_reps"] != REPS]

    conds = by_condition(rows)
    paired = {}
    for pattern in PATTERNS:
        for load in LOADS:
            key = f"{pattern}/{load}"
            s = conds.get(f"{pattern}/sync@{load}")
            a = conds.get(f"{pattern}/async@{load}")
            if not s or not a:
                continue
            entry = {"note": "at-capacity-relative: each arm at 1.0x of its OWN knee"}
            for m in METRICS:
                entry[m] = paired_ci([r[m] for r in
                                      sorted([x for x in rows if x["condition"] == f"{pattern}/sync@{load}"],
                                             key=lambda r: r["rep"])],
                                     [r[m] for r in
                                      sorted([x for x in rows if x["condition"] == f"{pattern}/async@{load}"],
                                             key=lambda r: r["rep"])])
                entry[m]["direction"] = (
                    "lower is better" if m in LOWER_IS_BETTER
                    else "higher is better" if m in HIGHER_IS_BETTER else "target 0"
                )
            paired[key] = entry

    payload = {
        "config": {
            "reps_per_condition": REPS, "bootstrap": BOOT, "seed": SEED,
            "ci_method": "percentile bootstrap on the median",
            "pairing": "rep index carried across arms",
            "power_note": "at n=40 the overload arm resolves only roughly 30%+ differences",
        },
        "conditions_short_of_40": n_short,
        "conditions": conds,
        "paired": paired,
    }

    out = args.out or (HERE / "results" / "analysis.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))

    print("=" * 78)
    print("p95 (ms), median of 40 reps, bootstrap 95% CI")
    print("=" * 78)
    for load in LOADS:
        print(f"\n-- {load} --")
        print(f"{'pattern':16s} {'sync':>26s}   {'async':>26s}")
        for pattern in PATTERNS:
            s = conds.get(f"{pattern}/sync@{load}", {}).get("metrics", {}).get("window_p95")
            a = conds.get(f"{pattern}/async@{load}", {}).get("metrics", {}).get("window_p95")
            def fmt(d):
                if not d or d["median"] is None:
                    return "n/a"
                return f"{d['median']:.1f} [{d['ci95'][0]:.1f},{d['ci95'][1]:.1f}]"
            print(f"{pattern:16s} {fmt(s):>26s}   {fmt(a):>26s}")
        print("paired (sync - async), p95 ms, at-capacity-relative:")
        for pattern in PATTERNS:
            d = paired.get(f"{pattern}/{load}", {}).get("window_p95")
            if not d or d["diff_median"] is None:
                continue
            print(f"  {pattern:16s} {d['diff_median']:+.2f} "
                  f"[{d['ci95'][0]:+.2f},{d['ci95'][1]:+.2f}]  {d['verdict']}")

    if n_short:
        print(f"\nWARNING: conditions without 40 reps: {n_short}")
    print(f"\nwritten {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
