"""analyze.py -- Amendment 7 statistics for the shared offered-load ladder.

Reads results/main/cells.csv (written incrementally by run_matrix.py) and reports
the two comparisons the study exists to make:

  A. execution model  -- async minus sync, within each DI pattern, at each rate
  B. pattern          -- each pattern minus s1_direct (the direct baseline),
                         within each execution model, at each rate

Both are paired on the repetition index, so any host drift at a given slot is
shared by both arms of a pair instead of being charged to one of them.

INTERVALS. The percentile bootstrap is retained as a SENSITIVITY analysis only,
because at the repetition counts this design actually uses it is degenerate: for
n=5 the bootstrap resample cannot produce a median outside the observed range,
so its interval is exactly [min, max] no matter how the data are distributed. It
was measured to detect a one-standard-deviation shift with probability 0.43 at
n=5, 0.72 at n=10, 0.96 at n=20 and 0.998 at n=40. That is a property of the
method at small n, not of the experiment, and labelling such an output "95% CI"
would misrepresent it.

The primary interval is therefore distribution-free and exact: the
order-statistic interval for the median of the paired differences,

    [ x_(k), x_(n-k+1) ],   k = min{ k : 2*P(Bin(n, 1/2) <= k-1) <= alpha }

which is precisely the set of population medians the exact binomial sign test
fails to reject at level alpha. No distributional assumption is made about the
differences, so heavy tails and outliers -- which is exactly what a saturating
load generator produces -- cannot distort it.

Every interval reports the coverage it ACTUALLY attains, not the nominal level.
At n=2 no interval can reach 95%: the widest available is [min, max], whose true
coverage is 0.50. Those cells are reported as wide and explicitly flagged, so a
small-n result can never be read as though it were a well-resolved one.

PRACTICAL SIGNIFICANCE. A latency difference is judged against an explicit
margin, not only against zero. Four outcomes are distinguished, and the middle
two are the ones that matter:

  resolved but negligible   CI excludes 0 but lies inside +/-margin
  practically equivalent    CI lies entirely inside +/-margin
  practically meaningful    CI lies entirely outside +/-margin
  inconclusive              CI straddles 0 or the margin

A "resolved but negligible" result is a real difference that is too small to
matter, and is reported as such rather than collapsed into "no difference".

AMENDMENT 11 -- PRIMARY METRIC AND RELATIVE MARGIN. Two changes, both forced
by preflight evidence gathered on the study box under Amendment 10:

1. The primary latency source moves from cell_p99 to http_p99. Both cover the
   same population (every request in the cell, no window bucketing), but
   cell_p99 is built from Date.now() deltas, which k6 reports as whole
   milliseconds, so it is quantised to 1 ms. Six repeats of one cell at
   200 req/s returned cell_p99 = 2 for all six -- zero resolving power. The
   same repeats gave http_p99 = 1.593 +/- 0.041 ms (stdev). Between-pattern
   effects in this workload run 0.1-0.5 ms, so a 1 ms grid cannot express
   them. k6's own http_req_duration timer is Go-native and sub-ms.

2. The practical margin becomes RELATIVE: a fraction of the pair's own
   baseline, not a fixed millisecond count. The ladder spans p99 from ~1.6 ms
   at 200 req/s to ~30 ms at 1200 req/s, a 19x range, so no single absolute
   margin can serve both ends: the old fixed +/-30 ms was 30x the entire
   observed spread in the flat band, which made "practically equivalent" the
   only reachable verdict there and guaranteed a null by construction.

The relative fraction is calibrated on within-condition REPEATABILITY, never
on between-condition differences, so it does not bias the effects it is used
to judge. Measured repeat stdev/mean was 2.6% at 200 req/s and 16% at
1200 req/s; 10% sits above the noise in the bands where the study has power
and below it in the saturated band, which is therefore reported as
under-powered rather than as evidence of equivalence.

Run:  python analyze.py
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from collections import defaultdict
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent

SEED = 20260928          # already registered in the protocol; do not change
BOOT = 10000             # bootstrap resamples, sensitivity analysis only
ALPHA = 0.05

PATTERNS = ["s1_direct", "s2_depends", "s3_middleware", "s4_container", "s4_dishka"]
MODELS = ["sync", "async"]
LADDER = list(range(200, 1201, 100))

# Amendment 14: PATTERNS now has five entries, and it is duplicated across four
# files on purpose (run_matrix, analyze, gen_apps, runner.ARM's allowlist) so
# each stays runnable standalone against a bare cells.csv. That is also the
# hazard: adding an arm to one and forgetting another produces a report that
# silently omits it, or an ARM() that rejects it mid-run. The agreement is
# asserted by test_arm_sets.py rather than by a comment.

# Primary metric first. p99 over the WHOLE cell rather than the windowed trend:
# a severe stall moves samples between completion-time windows, so windowing can
# hide a stall that a whole-cell trend retains.
#
# Amendment 11: primary is http_p99, not cell_p99. Both are whole-cell trends
# over the same request population, but cell_p99 is measured with k6's
# Date.now() and is therefore quantised to whole milliseconds -- six repeats at
# 200 req/s all returned exactly 2. http_p99 comes from k6's Go-native timer and
# resolves ~0.04 ms. cell_* stays in METRICS as a coarse diagnostic.
PRIMARY = "http_p99"

# Pre-registration 4g.5, "Load-fidelity floor": "A cell below the floor (primary
# 95%; sensitivity 90% and 98%) is saturation evidence, not a latency data
# point: the arm did not keep up with offered load, so its percentiles describe
# only the fast requests that got through."
#
# This is the reason the floor exists as a number and not just prose. A collapsed
# arm can post an excellent p99 by serving a small fast subset -- 5% of requests
# served perfectly looks like a 20x speedup next to an arm that served
# everything slowly. Comparing those two percentiles measures the subset, not
# the wiring. run_matrix's runtime guard uses the same constant
# (runner.LOAD_FIDELITY_FLOOR) to catch the opposite contradiction; this is where
# sub-floor cells are kept OUT of the primary comparison.
FIDELITY_FLOOR = 0.95
FIDELITY_SENSITIVITY = (0.90, 0.98)

# max/median ratio within one arm above which the arm's reps are treated as
# dispersed rather than as a sample with a central tendency. In this design
# healthy arms sit at or below ~1.8 across every rate, so 2.5 only trips on
# genuinely bimodal or collapsing reps and leaves the normal cells alone.
DISPERSION_LIMIT = 2.5

METRICS = [
    "http_p99", "http_p95", "http_p50", "http_max",
    "cell_p99", "cell_p95", "cell_p50", "cell_max",
    "window_error_rate", "load_fidelity", "dropped_iterations",
    "cpu_seconds_per_req", "rss_peak_mb",
]

# Practical margin per latency metric, as a FRACTION of the pair's baseline
# (the mean of arm a's cells), not a fixed ms count. Amendment 11: the ladder
# spans p99 from ~1.6 ms to ~30 ms, so a single absolute margin cannot serve
# both ends -- the old fixed +/-30 ms exceeded the entire observed spread in
# the flat band and forced "practically equivalent" everywhere.
#
# 0.10 is calibrated on within-condition repeatability (stdev/mean was 2.6% at
# 200 req/s, 16% at 1200 req/s), NOT on between-condition differences, so it
# does not bias the effects it judges. It sits above the noise where the study
# has power and below it in the saturated band, which is then correctly
# reported as under-powered rather than as evidence of equivalence.
MARGIN_FRAC = {"http_p99": 0.10, "http_p95": 0.10, "http_p50": 0.10,
               "http_max": 0.10}

# Metrics whose margin is relative. Anything else listed in MARGIN_FRAC is
# treated as an absolute margin in the metric's own unit.
RELATIVE_METRICS = frozenset(MARGIN_FRAC)


def exact_sign_ci(values: list[float], alpha: float = ALPHA) -> dict:
    """Distribution-free CI for the median of `values`, exact at level ~alpha.

    Returns the interval, the number of observations trimmed from each tail,
    and the coverage actually attained. The attained coverage is always <= the
    nominal level and must be reported: binomial tails are discrete, so at small
    n the best available interval is wide and covers less than requested.
    """
    vals = sorted(v for v in values if v is not None)
    n = len(vals)
    if n == 0:
        return {"n": 0, "median": None, "ci": None, "method": "none",
                "attained_coverage": None, "trim": None}
    if n == 1:
        return {"n": 1, "median": vals[0], "ci": [vals[0], vals[0]],
                "method": "exact binomial (degenerate at n=1)",
                "nominal_coverage": 1 - alpha, "attained_coverage": 0.5,
                "attainable_at_nominal": False, "trim": 0,
                "note": "a single observation pins the interval to itself"}

    # Largest k with P(Bin(n,1/2) <= k-1) <= alpha/2, giving the NARROWEST
    # interval that still attains the nominal coverage. k=1 means no trimming
    # (the interval is [min, max]) and is the floor: for small n even that fails
    # the alpha/2 test, which is exactly the case that must be reported as
    # coverage-limited rather than presented as a 95% interval.
    total = 2 ** n
    budget = alpha * total / 2.0
    k = 1
    cum = comb(n, 0)  # numerator of P(B <= k-1)
    while k < n // 2 + 1:
        nxt = cum + (comb(n, k) if k < n else 0)
        if nxt > budget:
            break
        cum = nxt
        k += 1
    k = min(k, n // 2 + 1)
    coverage = 1.0 - 2.0 * cum / total

    lo, hi = vals[k - 1], vals[n - k]
    flag = ""
    if coverage < 1 - alpha:
        flag = (f"attained coverage {coverage:.1%} is below the nominal "
                f"{1 - alpha:.0%}; the interval is already the narrowest this "
                f"n allows, so it cannot be sharpened without more repetitions")
    return {
        "n": n, "median": statistics.median(vals), "ci": [lo, hi],
        "method": f"exact binomial sign/order-statistic (trim={k - 1} per tail)",
        "nominal_coverage": 1 - alpha,
        "attained_coverage": round(coverage, 4),
        "attainable_at_nominal": coverage >= 1 - alpha,
        "trim": k - 1, "note": flag,
    }


def bootstrap_ci(values: list[float], boot: int = BOOT, seed: int = SEED) -> dict:
    """Percentile bootstrap of the median. SENSITIVITY ANALYSIS ONLY.

    Degenerate at small n: for n <= 5 every resample median lies inside
    [min, max], so the interval equals the observed range regardless of shape.
    Flagged rather than presented as a primary result.
    """
    vals = [v for v in values if v is not None]
    n = len(vals)
    if n == 0:
        return {"n": 0, "median": None, "ci": None}
    rng = random.Random(seed)
    meds = sorted(statistics.median(rng.choices(vals, k=n)) for _ in range(boot))
    lo, hi = meds[int(0.025 * boot)], meds[int(0.975 * boot) - 1]
    degenerate = (n <= 5) and abs(hi - lo - (max(vals) - min(vals))) < 1e-9
    return {"n": n, "median": statistics.median(vals), "ci": [lo, hi],
            "degenerate_at_n": n <= 5,
            "note": ("interval equals observed min-max; not a real confidence "
                     "interval at this n") if degenerate else ""}


def margin_for(metric: str, baseline: float | None) -> tuple[float | None, str]:
    """Practical margin for `metric` against a pair's own baseline.

    For metrics in RELATIVE_METRICS the margin is MARGIN_FRAC x the baseline
    (arm a's median), so it scales with the regime instead of being a fixed
    millisecond count. `baseline` is the value of arm a, the arm being judged;
    that choice is fixed in advance and applied identically to both directions
    of every comparison.

    Returns (margin, basis) where basis records which rule fired, so the
    reported number is never ambiguous about how it was derived. When the
    baseline is missing or non-positive there is nothing to scale by and the
    margin is None, which yields a verdict against zero only.
    """
    frac = MARGIN_FRAC.get(metric)
    if frac is None:
        return None, "no margin for this metric"
    if baseline is None or baseline <= 0:
        return None, "relative margin unavailable: no positive baseline"
    return frac * baseline, f"{frac:g} x baseline {baseline:.4g}"


def classify(ci: dict, margin: float | None) -> str:
    """Judge a paired-median interval against zero and against the margin.

    The margin test requires the CI to lie ENTIRELY on one side of it. An
    interval that straddles the margin is inconclusive against it, even when it
    clearly excludes zero: "[10, 90] with margin 30" neither demonstrates
    equivalence nor a meaningful difference, and calling it "resolved but
    negligible" would claim the margin was excluded when it was not. Ordering
    the containment test first is what makes that case report correctly.
    """
    if not ci.get("ci"):
        return "no data"
    lo, hi = ci["ci"]
    if margin is None:
        return ("resolves an increase" if lo > 0 else
                "resolves a decrease" if hi < 0 else "inconclusive vs zero")
    if lo > margin:
        return "meaningful: a is worse beyond margin"
    if hi < -margin:
        return "meaningful: a is better beyond margin"
    if lo >= -margin and hi <= margin:
        return "practically equivalent"
    if lo > 0 or hi < 0:
        # Excludes zero, but straddles the margin: neither equivalence nor a
        # meaningful difference is demonstrated.
        return "inconclusive vs margin"
    return "inconclusive vs margin"


def paired(rows_a: list[dict], rows_b: list[dict], metric: str) -> dict:
    """Pair on the repetition index and compare a - b.

    Pairing on the rep index matters: the two arms of a pair occupy adjacent
    slots in the same (rate, rep) block, so host state at that slot is common to
    both and cancels from the difference.
    """
    mb = {int(r["rep"]): r for r in rows_b}
    diffs, a_vals, b_vals = [], [], []
    for ra in sorted(rows_a, key=lambda r: int(r["rep"])):
        rb = mb.get(int(ra["rep"]))
        if rb is None:
            continue
        va, vb = ra.get(metric), rb.get(metric)
        if va is None or vb is None:
            continue
        a_vals.append(va)
        b_vals.append(vb)
        diffs.append(va - vb)

    out = {
        "n_pairs": len(diffs),
        "a_median": statistics.median(a_vals) if a_vals else None,
        "b_median": statistics.median(b_vals) if b_vals else None,
        "exact": exact_sign_ci(diffs),
        "bootstrap_sensitivity": bootstrap_ci(diffs),
    }
    # Dispersion diagnostic. A median is robust to outliers, so a bimodal or
    # collapsing arm still yields a tidy median while its exact sign CI explodes
    # from those same outliers. That combination is not "we looked and could not
    # tell" -- it is "there is no stable central tendency to compare". Flagging it
    # here keeps the distinction visible instead of burying it in a wide CI.
    for side, vals in (("a", a_vals), ("b", b_vals)):
        if vals:
            med = statistics.median(vals)
            out[f"{side}_min"] = min(vals)
            out[f"{side}_max"] = max(vals)
            out[f"{side}_dispersion"] = (max(vals) / med) if med else None
        else:
            out[f"{side}_dispersion"] = None
    disp = [out[f"{s}_dispersion"] for s in ("a", "b")]
    disp = [d for d in disp if d is not None]
    out["max_dispersion"] = max(disp) if disp else None
    out["unstable_dispersion"] = bool(
        out["max_dispersion"] is not None
        and out["max_dispersion"] > DISPERSION_LIMIT
    )
    if diffs:
        out["diff_median"] = statistics.median(diffs)
        margin, basis = margin_for(metric, out["a_median"])
        out["margin"] = margin
        out["margin_basis"] = basis
        out["verdict"] = classify(out["exact"], margin)
    return out


def read_cells(path: Path, fidelity_floor: float | None = FIDELITY_FLOOR
               ) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Return (study rows, host-drift rows, failed rows, sub-floor rows).

    Failed, db-invalid, drift and sub-fidelity cells are all separated out here
    rather than filtered later, so that no filter can silently widen and let them
    into a result. Each bucket is reported to the caller rather than discarded,
    because a cell dropped for being sub-floor is evidence about the arm (it did
    not keep up), not a missing measurement.

    fidelity_floor=None disables the floor, which is only for the sensitivity
    analyses the pre-registration calls for at 90% and 98%.
    """
    with open(path) as fh:
        raw = list(csv.DictReader(fh))

    study, drift, failed, subfloor = [], [], [], []
    for r in raw:
        def num(k):
            v = r.get(k, "")
            if v in ("", None):
                return None
            try:
                return float(v)
            except ValueError:
                return None

        rec = {
            "condition": r["condition"], "pattern": r["pattern"],
            "model": r["model"], "rate": float(r["rate"]),
            "band": r.get("band", ""), "rep": int(r["rep"]),
            "db_unchanged": r.get("db_unchanged") == "True",
        }
        for m in METRICS:
            rec[m] = num(m)

        if r.get("is_drift", "0") not in ("0", "", None):
            drift.append(rec)
            continue
        if r.get("failed", "0") != "0":
            failed.append(rec)
            continue
        if not rec["db_unchanged"]:
            failed.append(rec)
            continue
        # Sub-floor fidelity is saturation evidence, not a latency sample. An
        # unknown fidelity is NOT treated as sub-floor: missing accounting is a
        # gap to report, not proof the arm fell behind, and inventing a
        # disqualification from absent data would quietly shrink the design.
        if (fidelity_floor is not None
                and rec["load_fidelity"] is not None
                and rec["load_fidelity"] < fidelity_floor):
            subfloor.append(rec)
            continue
        study.append(rec)

    # Keep only the latest successful row per (condition, rep). A retried cell
    # legitimately appears more than once; the final successful attempt is the
    # one that counts, and earlier attempts must not enter a statistic twice.
    dedup: dict = {}
    for r in sorted(study, key=lambda r: int(r.get("attempt", 1) or 1)):
        dedup[(r["condition"], r["rep"])] = r
    return list(dedup.values()), drift, failed, subfloor


def completeness(study: list[dict], rates: list[int] | None = None) -> dict:
    """Per (pattern, model, rate) rep counts, plus anything missing.

    Printed so that an underpowered rate is visible as a shortfall rather than
    quietly analysed with whatever repetitions happened to survive.

    `rates` must mirror run_matrix's --rates. completeness walks a PLANNED grid,
    so on a scope-reduced run it has to walk the reduced grid: left on the full
    ladder, every deliberately excluded rate is reported as a condition that
    "produced no cells at all", and the report would condemn a run for omitting
    what it was designed to omit.
    """
    grid = rates if rates is not None else LADDER
    have: dict = defaultdict(set)
    for r in study:
        have[(r["pattern"], r["model"], int(r["rate"]))].add(r["rep"])
    out = {"observed": {}, "shortfalls": [], "absent": [], "grid": list(grid)}
    # Walk the PLANNED grid, not just the observed keys. Iterating observed keys
    # alone reports nothing for a condition that never produced a single cell --
    # the case most worth flagging, since an entirely absent condition is
    # silently absent from the report rather than counted as a shortfall of 0.
    for p in PATTERNS:
        for model in MODELS:
            for rate in grid:
                k = (p, model, rate)
                reps = have.get(k, set())
                # Must track run_matrix.REPS_BY_BAND; see the Amendment 12 note
                # there. Duplicated rather than imported so analyze.py stays
                # runnable on a bare cells.csv, but the two must agree or the
                # report will call a fully-collected band a shortfall.
                want = 6 if rate <= 500 else (12 if rate <= 900 else 8)
                if not reps:
                    out["absent"].append({"cell": f"{p}/{model}@{rate}",
                                          "have": 0, "want": want})
                    continue
                out["observed"][f"{k[0]}/{k[1]}@{rate}"] = sorted(reps)
                if len(reps) < want:
                    out["shortfalls"].append({"cell": f"{k[0]}/{k[1]}@{rate}",
                                              "have": len(reps), "want": want})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", type=Path,
                    default=HERE / "results" / "main" / "cells.csv")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--metric", default=PRIMARY,
                    help="metric for the headline table (default http_p99)")
    ap.add_argument("--rates", default=None,
                    help="comma-separated planned rates, e.g. 600,700,800,900. "
                         "Must mirror run_matrix --rates for a scope-reduced run, "
                         "or completeness() will report every excluded rate as an "
                         "absent condition.")
    ap.add_argument("--fidelity-floor", type=float, default=FIDELITY_FLOOR,
                    help="exclude cells below this load fidelity from the primary "
                         "comparison as saturation evidence (prereg 4g.5; primary "
                         "0.95, sensitivity 0.90 and 0.98)")
    args = ap.parse_args()

    rates = None
    if args.rates:
        try:
            rates = sorted({int(p.strip()) for p in args.rates.split(",") if p.strip()})
        except ValueError:
            raise SystemExit("--rates: expected comma-separated integers")
        if not rates:
            raise SystemExit("--rates was given but selected no rates")
        off = [r for r in rates if r not in LADDER]
        if off:
            raise SystemExit(f"--rates: {off} not on the ladder {LADDER[0]}-{LADDER[-1]}")

    if not args.cells.exists():
        raise SystemExit(f"no cells file: {args.cells}")

    study, drift, failed, subfloor = read_cells(args.cells, args.fidelity_floor)
    print(f"cells file      {args.cells}")
    print(f"successful      {len(study)} unique (condition, rep)")
    if drift:
        print(f"excluded        {len(drift)} host-drift reference cells "
              "(diagnostic only)")
    if failed:
        print(f"excluded        {len(failed)} failed or db-invalid cells "
              "(see 'failed_cells')")
    if subfloor:
        print(f"excluded        {len(subfloor)} sub-floor-fidelity cells "
              f"(< {args.fidelity_floor:.0%} load fidelity): SATURATION EVIDENCE, "
              "not latency data points (prereg 4g.5)")
        by_arm: dict = {}
        for r in subfloor:
            by_arm.setdefault(r["condition"], []).append(r)
        for cond, rs in sorted(by_arm.items()):
            fids = [x["load_fidelity"] for x in rs if x["load_fidelity"] is not None]
            errs = [x["window_error_rate"] for x in rs
                    if x["window_error_rate"] is not None]
            fid_s = f"{min(fids):.3f}-{max(fids):.3f}" if fids else "n/a"
            err_s = f"{min(errs):.2f}-{max(errs):.2f}" if errs else "n/a"
            print(f"                  {cond}: {len(rs)} cell(s), "
                  f"fidelity {fid_s}, window_error_rate {err_s}")
    if not study:
        raise SystemExit("no successful cells to analyse")

    grid = rates if rates is not None else LADDER
    comp = completeness(study, rates)
    if comp["absent"]:
        # Distinguish "never ran" from "ran but every cell was excluded". These
        # are different failures and the wording has to say which: an arm whose
        # cells were all rejected as sub-floor DID produce data, and reporting it
        # as absent contradicts the exclusion list printed directly above and
        # invites the reader to go looking for missing cells that exist.
        starved = sorted({r["condition"] for r in subfloor})
        never_ran = [c for c in comp["absent"] if c["cell"] not in starved]
        if starved:
            print(f"absent          {len(starved)} planned condition(s) have no "
                  f"USABLE cell because every cell they recorded fell below the "
                  f"fidelity floor (listed above): "
                  f"{', '.join(starved[:6])}"
                  f"{' ...' if len(starved) > 6 else ''}")
        if never_ran:
            print(f"absent          {len(never_ran)} planned conditions produced "
                  f"no cells at all: "
                  f"{', '.join(c['cell'] for c in never_ran[:6])}"
                  f"{' ...' if len(never_ran) > 6 else ''}")
    if comp["shortfalls"]:
        print(f"shortfalls      {len(comp['shortfalls'])} cells below planned "
              "rep count")

    index: dict = defaultdict(list)
    for r in study:
        index[(r["pattern"], r["model"], int(r["rate"]))].append(r)

    metric = args.metric

    # --- A. execution model: async minus sync, per pattern per rate ---------
    model_cmp: dict = {}
    for p in PATTERNS:
        for rate in grid:
            s = index.get((p, "sync", rate), [])
            a = index.get((p, "async", rate), [])
            if not s or not a:
                continue
            model_cmp[f"{p}@{rate}"] = paired(a, s, metric)
            model_cmp[f"{p}@{rate}"]["_direction"] = "async - sync"

    # --- B. pattern: each pattern minus s1_direct, per model per rate ------
    pattern_cmp: dict = {}
    for mo in MODELS:
        for rate in grid:
            base = index.get(("s1_direct", mo, rate), [])
            if not base:
                continue
            for p in PATTERNS[1:]:
                cur = index.get((p, mo, rate), [])
                if not cur:
                    continue
                pattern_cmp[f"{p} vs s1_direct/{mo}@{rate}"] = paired(cur, base, metric)

    # --- secondary metrics at the same grouping ---------------------------
    secondary: dict = {}
    for m in METRICS:
        if m == metric:
            continue
        for p in PATTERNS:
            for rate in grid:
                s = index.get((p, "sync", rate), [])
                a = index.get((p, "async", rate), [])
                if s and a:
                    # a FIRST, then sync, so a positive diff_median means
                    # "async minus sync" here exactly as it does in section A.
                    # Passing (s, a) inverted the sign of every secondary
                    # metric relative to the headline it accompanies.
                    secondary[f"{p}@{rate}|{m}"] = paired(a, s, m)

    # --- headline table ----------------------------------------------------
    print(f"\n{'cell':<26} {'n':>3} {'async':>9} {'sync':>9} {'diff':>9} "
          f"{'exact 95% CI':>21} {'cov':>6}  verdict")
    print("-" * 108)
    for key, blk in model_cmp.items():
        e = blk["exact"]
        if not e.get("ci"):
            continue
        lo, hi = e["ci"]
        flag = "" if e["attainable_at_nominal"] else " *"
        ci_s = f"[{lo:.2f}, {hi:.2f}]{flag}"
        print(f"{key:<26} {blk['n_pairs']:>3} "
              f"{blk['a_median']:>9.2f} {blk['b_median']:>9.2f} "
              f"{blk['diff_median']:>9.2f} {ci_s:>21} "
              f"{e['attained_coverage']:>6.2f}  {blk['verdict']}")

    n_wide = sum(1 for b in model_cmp.values()
                 if b["exact"].get("ci") and not b["exact"]["attainable_at_nominal"])
    print(f"\n* = attained coverage below the nominal 95%; interval is the "
          f"widest this n allows")
    if metric in RELATIVE_METRICS:
        print(f"practical-delta margin on {metric}: "
              f"{MARGIN_FRAC[metric]:g} x each pair's own baseline "
              f"(relative, so it scales with the regime)")
    if n_wide:
        print(f"  {n_wide} cell(s) are width-limited by their rep count; their "
              f"intervals are honest but uninformative")

    unstable = [(k, b) for k, b in model_cmp.items()
                if b.get("unstable_dispersion")]
    if unstable:
        print(f"\n!! DISPERSION WARNING -- {len(unstable)} cell(s) have at least "
              f"one arm whose reps are dispersed by more than "
              f"{DISPERSION_LIMIT:g}x its own median:")
        for k, b in unstable:
            print(f"     {k}: async {b['a_min']:.2f}/{b['a_median']:.2f}/"
                  f"{b['a_max']:.2f} (min/med/max, {b['a_dispersion']:.1f}x)   "
                  f"sync {b['b_min']:.2f}/{b['b_median']:.2f}/{b['b_max']:.2f} "
                  f"({b['b_dispersion']:.1f}x)")
        print(f"     The median stays usable and the verdict above is reported as "
              f"computed, but for these cells the wide interval reflects a"
              f"\n     bimodal / collapsing arm rather than ordinary sampling "
              f"noise. Do not read the verdict as 'no difference detected': the"
              f"\n     arms are not stably distributed at this rate, and no "
              f"central-tendency")
        print(f"     claim about them is supported. Report the per-rep values "
              f"alongside.")

    # --- optional: bootstrap sensitivity, shown but never as primary ------
    print(f"\nbootstrap sensitivity ({BOOT} resamples) -- NOT primary; "
          f"degenerate at n<=5")
    for key, blk in list(model_cmp.items())[:6]:
        bs = blk["bootstrap_sensitivity"]
        if not bs.get("ci"):
            continue
        lo, hi = bs["ci"]
        degen = " (== min-max)" if bs.get("degenerate_at_n") else ""
        print(f"  {key:<26} n={bs['n']:>2} [{lo:>8.2f}, {hi:>8.2f}]{degen}")

    payload = {
        "cells_file": str(args.cells),
        "primary_metric": metric,
        "practical_margin_rule": (
            {"kind": "relative", "fraction": MARGIN_FRAC[metric],
             "calibrated_on": "within-condition repeatability, "
                              "not between-condition differences"}
            if metric in RELATIVE_METRICS else {"kind": "none"}),
        "completeness": {"shortfalls": comp["shortfalls"],
                         "absent": comp["absent"]},
        "alpha": ALPHA,
        "seed": SEED,
        "interval_method_primary":
            "exact binomial sign / order-statistic interval for the median of "
            "paired differences; attained coverage reported per cell",
        "interval_method_sensitivity": f"percentile bootstrap, {BOOT} resamples",
        "n_successful": len(study),
        "n_drift_excluded": len(drift),
        "n_failed_excluded": len(failed),
        "failed_cells": [{"condition": r["condition"], "rep": r["rep"]}
                         for r in failed],
        "completeness": comp,
        "execution_model_async_minus_sync": model_cmp,
        "pattern_vs_baseline": pattern_cmp,
        "secondary_metrics": secondary,
    }
    out = args.out or (args.cells.parent / "analysis.json")
    out.write_text(json.dumps(payload, indent=2))
    print(f"\nwritten {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())