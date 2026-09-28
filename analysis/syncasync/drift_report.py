"""Host-drift report for the amendment-4d reference cells.

The study is a single session on one host, so condition effects measured at
different points in time are confounded with time to the extent that the host
drifts. The grid repeats one fixed reference cell (p1_direct/sync at a fixed
fraction of its own capacity knee) at fixed positions; this script turns those
cells into a drift number.

Usage:
    python drift_report.py results/smoke/cells.csv
    python drift_report.py results/main/cells.csv

Exit status is 0 regardless of drift; the caller decides what to do. Drift is
reported, never silently corrected for.
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

DRIFT_TOLERANCE_PCT = 10.0  # p95 spread above this is worth reporting as drift


def load_drift_rows(path: Path) -> list[dict]:
    rows = []
    with open(path) as fh:
        for r in csv.DictReader(fh):
            if r.get("is_drift", "0") not in ("0", "", None):
                rows.append(r)
    rows.sort(key=lambda r: int(r["drift_index"]))
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"no such cells file: {path}")
        return 2
    rows = load_drift_rows(path)
    if not rows:
        print(f"no drift reference cells in {path}")
        return 1

    print(f"host-drift report: {path}")
    print(f"reference cell: {rows[0]['condition']} @ {rows[0]['rate']} rps")
    print()
    print(f"{'#':>2} {'after_cell':>10} {'p50':>8} {'p95':>8} {'mean':>8} "
          f"{'achieved':>9} {'steal':>6} {'db_ok':>6}")
    p95s, p50s, steals = [], [], []
    for r in rows:
        p50 = float(r["window_p50"]); p95 = float(r["window_p95"])
        mean = r["window_mean"]
        ach = float(r["achieved"])
        steal = r.get("steal_jiffies", "") or "0"
        p50s.append(p50); p95s.append(p95)
        try:
            steals.append(int(float(steal)))
        except ValueError:
            pass
        print(f"{r['drift_index']:>2} {r['after_cell']:>10} {p50:>8.2f} {p95:>8.2f} "
              f"{float(mean):>8.2f} {ach:>9.3f} {steal:>6} {r['db_unchanged']:>6}")

    n = len(p95s)
    p95_med = statistics.median(p95s)
    p95_min, p95_max = min(p95s), max(p95s)
    spread_pct = (p95_max - p95_min) / p95_med * 100 if p95_med else 0.0
    first_half = statistics.median(p95s[: max(1, n // 2)])
    second_half = statistics.median(p95s[max(1, n // 2):]) if n > 1 else first_half
    drift_pct = (second_half - first_half) / first_half * 100 if first_half else 0.0

    print()
    print(f"reference cells        : {n}")
    print(f"p95 median             : {p95_med:.2f} ms")
    print(f"p95 min / max          : {p95_min:.2f} / {p95_max:.2f} ms")
    print(f"p95 spread (max-min)   : {p95_max - p95_min:.2f} ms "
          f"({spread_pct:.1f}% of median)")
    print(f"first-half -> second-half p95: {first_half:.2f} -> {second_half:.2f} ms "
          f"({drift_pct:+.1f}%)")
    print(f"p50 min / max          : {min(p50s):.2f} / {max(p50s):.2f} ms")
    if steals:
        print(f"steal jiffies min / max: {min(steals)} / {max(steals)}")

    print()
    if spread_pct <= DRIFT_TOLERANCE_PCT:
        print(f"VERDICT: no material host drift (p95 spread {spread_pct:.1f}% <= "
              f"{DRIFT_TOLERANCE_PCT:.0f}%).")
        print("The single-session design is not undermined by host drift over this")
        print("session. This bounds drift for THIS session only; it is not a claim")
        print("that the host is stable in general or across sessions.")
    else:
        print(f"VERDICT: host drift of {spread_pct:.1f}% in the reference cell, above")
        print(f"the {DRIFT_TOLERANCE_PCT:.0f}% tolerance. This is a limitation to report")
        print("with the numbers above, not something to correct for. Condition effects")
        print("measured at different points in the run are confounded with time to that")
        print("extent, and the affected cells should be identified by after_cell.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
