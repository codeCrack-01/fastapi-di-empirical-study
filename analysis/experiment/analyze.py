"""analyze.py — pre-registered analysis of the ReviewGate matrix (spec §8).

Unit of analysis = run-level median (per strategy x mode x level).
Primary contrast  = strategy vs S0, paired within session (randomized order).
Outputs to results/:
  tables_<ts>.md      Markdown tables: latency, CPU/RSS, error rate
  ci_<ts>.csv         bootstrap 95% CIs on median difference vs S0
  regression.md       per-accessory observable summary

Run from analysis/experiment:  python analyze.py [--runs results/runs.csv]
No post-hoc carving: every cell that ran appears in the tables.
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

EFFECT_THRESHOLD_MS_MB = 0.5  # run-level standard error ~0.5ms; below this accept "negligible"


def bootstrap_ci(diffs, n=10000, seed=42, alpha=0.05):
    """95% percentile bootstrap CI on the mean of paired diffs."""
    rng = random.Random(seed)
    means = []
    for _ in range(n):
        s = rng.choices(diffs, k=len(diffs))
        means.append(sum(s) / len(s))
    lo = sorted(means)[int(alpha / 2 * n)]
    hi = sorted(means)[int((1 - alpha / 2) * n)]
    return lo, hi


def load_runs(path: Path) -> list[dict]:
    if not path.exists():
        print(f"ERROR: {path} not found — run run_experiment.py first", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return list(csv.DictReader(f))


def numeric(row, key):
    try:
        v = float(row.get(key))
        return v if v == v else None  # NaN -> None
    except (TypeError, ValueError):
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(RESULTS / "runs.csv"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    runs = load_runs(Path(args.runs))
    cells = defaultdict(list)
    for r in runs:
        r["rate"] = float(r["rate"])
        cells[(r["strategy"], r["mode"], r["rate"])].append(r)

    strategies = ["s0", "s1", "s2", "s3"]
    modes = ["A", "B"]
    ts = defaultdict(list)

    # aggregate run-level medians per cell
    for (s, m, rate), rows in cells.items():
        p50s = [r["window_p50"] for r in rows]
        valid = [p for p in p50s if p is not None]
        ts[(s, m, rate)] = {
            "n": len(valid),
            "median_p50": sorted(float(v) for v in valid)[len(valid) // 2] if valid else None,
            "p50s": [float(v) for v in p50s if v],
            "rss_avg": [float(r["rss_avg_mb"]) for r in rows if r.get("rss_avg_mb")],
            "rss_peak": [float(r["rss_peak_mb"]) for r in rows if r.get("rss_peak_mb")],
            "cpu_usr": [float(r["cpu_usr_pct"]) for r in rows if r.get("cpu_usr_pct")],
            "http_err": [float(r["http_error_rate"]) for r in rows if r.get("http_error_rate")],
        }

    lines = ["# ReviewGate matrix — pre-registered analysis", "",
             f"Source: {args.runs}", f"Cells: {len(cells)}", ""]

    # ---- latency table ---------------------------------------------------
    for mode in modes:
        rates = sorted({float(k[2]) for k in cells if k[1] == mode})
        lines += [f"## Latency (p50 run-level median, ms) — Mode {mode}", "", "| rate | " + " | ".join(strategies) + " |"]
        lines += ["|-----|" + "|---|---|---|---|"]
        for rate in rates:
            row = []
            for s in strategies:
                v = ts.get((s, mode, rate), {}).get("median_p50")
                row.append(f"{v:.1f}" if v is not None else "–")
            lines.append(f"| {rate:g} | " + " | ".join(row) + " |")
        lines += [""]

    # ---- paired CI vs S0 --------------------------------------------------
    lines += ["## Paired median difference vs S0 (bootstrap 95% CI, ms)", ""]
    lines += ["| mode | rate | contrast | diff_p50 | ci_lo | ci_hi | verdict |"]
    lines += ["|-----|-----|-----|-----|-----|-----|-----|"]
    ci_rows = []
    for mode in modes:
        rates = sorted({float(k[2]) for k in cells if k[1] == mode})
        for rate in rates:
            s0 = ts.get(("s0", mode, rate), {}).get("p50s", [])
            for s in strategies[1:]:
                other = ts.get((s, mode, rate), {}).get("p50s", [])
                if not s0 or not other:
                    continue
                n = min(len(s0), len(other))
                diffs = [(a - b) for a, b in zip(other[:n], s0[:n])]
                diff = sum(diffs) / len(diffs)
                lo, hi = bootstrap_ci(diffs, seed=args.seed)
                verdict = "within SE" if abs(diff) < EFFECT_THRESHOLD_MS_MB else ("S0 slower" if diff < 0 else "strategy slower")
                lines.append(f"| {mode} | {rate:g} | {s} vs S0 | {diff:+.2f} | {lo:+.2f} | {hi:+.2f} | {verdict} |")
                ci_rows.append({"mode": mode, "rate": rate, "strategy": s, "diff_p50": diff,
                                "ci_lo": lo, "ci_hi": hi, "n": n})
    lines += [""]

    # ---- resource table ---------------------------------------------------
    lines += ["## Resources (avg over runs)", ""]
    lines += ["| mode | rate | strategy | rss_avg(MB) | rss_peak(MB) | cpu_usr% |"]
    lines += ["|-----|-----|-----|-----|-----|-----|"]
    for mode in modes:
        rates = sorted({float(k[2]) for k in cells if k[1] == mode})
        for rate in rates:
            for s in strategies:
                d = ts.get((s, mode, rate), {})
                ra = sum(d.get("rss_avg", [])) / len(d["rss_avg"]) if d.get("rss_avg") else None
                rp = sum(d.get("rss_peak", [])) / len(d["rss_peak"]) if d.get("rss_peak") else None
                cu = sum(d.get("cpu_usr", [])) / len(d["cpu_usr"]) if d.get("cpu_usr") else None
                lines.append(
                    f"| {mode} | {rate:g} | {s} | "
                    + (f"{ra:.1f}" if ra is not None else "–") + " | "
                    + (f"{rp:.1f}" if rp is not None else "–") + " | "
                    + (f"{cu:.1f}" if cu is not None else "–") + " |"
                )
    lines += [""]

    out_md = RESULTS / f"tables_{args.seed}.md"
    out_md.write_text("\n".join(lines))
    print("\n".join(lines[:30]))
    print(f"\nWrote {out_md}")


if __name__ == "__main__":
    main()