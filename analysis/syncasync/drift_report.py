"""Host-drift report for the amendment-4d reference cells.

The study is a single session on one host, so condition effects measured at
different points in time are confounded with time to the extent that the host
drifts. The grid repeats one fixed reference cell (s1_direct/sync at a fixed
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


def _num(row: dict, key: str) -> float | None:
    """Read a float that may be absent, empty, or non-numeric.

    The drift report is the one artifact that must not raise on a bad row. It
    runs after a multi-hour session, and a KeyError here would destroy the
    drift evidence for the whole run over a single malformed cell. Columns also
    move: the CSV calls it achieved_rate, not achieved, and reading the wrong
    name raises KeyError on a file that is otherwise perfectly valid.
    """
    raw = row.get(key)
    if raw is None or str(raw).strip() == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _metric(row: dict, pct: str) -> float | None:
    """Client-observed latency at the given percentile, with a fallback.

    `http_p*` carries the client-side measurement at sub-millisecond
    resolution and is the metric family the primary analysis uses, so it is what
    the drift reference should be judged on. The `cell_p*` / `window_p*` columns
    are recorded as whole milliseconds, which is coarser than the drift this
    report exists to detect: at a 200 rps reference every one of them rounds to
    1.00 and the spread computes to exactly 0.0%, which is a property of the
    field's storage precision and not a measurement of the host. They are used
    only when the client-observed column is absent.
    """
    for key in (f"http_{pct}", f"window_{pct}", f"cell_{pct}"):
        v = _num(row, key)
        if v is not None:
            return v
    return None


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
    print(f"reference cell: {rows[0].get('condition','?')} @ {rows[0].get('rate','?')} rps")
    print()
    print(f"{'#':>2} {'after_cell':>10} {'p50':>8} {'p95':>8} {'p99':>8} {'mean':>8} "
          f"{'ach_rate':>9} {'steal':>6} {'db_ok':>6}")

    def fmt(v: float | None) -> str:
        return f"{'-':>8}" if v is None else f"{v:>8.3f}"

    p95s, p99s, p50s, steals, unusable = [], [], [], [], []
    for r in rows:
        p50 = _metric(r, "p50")
        p95 = _metric(r, "p95")
        p99 = _metric(r, "p99")
        mean = _num(r, "window_mean")
        ach = _num(r, "achieved_rate")
        steal = r.get("steal_jiffies", "") or "0"
        if p50 is not None:
            p50s.append(p50)
        if p95 is None:
            # A reference cell that never produced a p95 bounds nothing. It is
            # counted and named, never dropped silently: a drift bound computed
            # from fewer references is weaker, and pretending otherwise would
            # overstate the result.
            unusable.append(r)
        else:
            p95s.append(p95)
        if p99 is not None:
            p99s.append(p99)
        try:
            steals.append(int(float(steal)))
        except ValueError:
            pass
        ach_s = f"{ach:>9.3f}" if ach is not None else f"{'-':>9}"
        print(f"{r.get('drift_index','-'):>2} {r.get('after_cell','-'):>10} "
              f"{fmt(p50)} {fmt(p95)} {fmt(p99)} {fmt(mean)} {ach_s} "
              f"{str(steal):>6} {r.get('db_unchanged','-'):>6}")

    if unusable:
        print()
        print(f"WARNING: {len(unusable)} of {len(rows)} reference cells produced no")
        print("p95 and are excluded from the drift statistics below:")
        for r in unusable:
            print(f"    drift_index={r.get('drift_index','?')} "
                  f"after_cell={r.get('after_cell','?')} "
                  f"failed={r.get('failed','?')} "
                  f"reason={r.get('failure_reason','') or '-'}")
        print("The drift bound below therefore rests on fewer references than the")
        print("design intended, and is correspondingly weaker.")

    if not p95s:
        print()
        print("VERDICT: no usable reference cells; host drift cannot be assessed.")
        return 1

    n = len(p95s)
    p95_med = statistics.median(p95s)
    p95_min, p95_max = min(p95s), max(p95s)
    spread_pct = (p95_max - p95_min) / p95_med * 100 if p95_med else 0.0
    first_half = statistics.median(p95s[: max(1, n // 2)])
    second_half = statistics.median(p95s[max(1, n // 2):]) if n > 1 else first_half
    drift_pct = (second_half - first_half) / first_half * 100 if first_half else 0.0

    print()
    print(f"reference cells usable : {n} of {len(rows)}")
    print(f"p95 median             : {p95_med:.3f} ms")
    print(f"p95 min / max          : {p95_min:.3f} / {p95_max:.3f} ms")
    print(f"p95 spread (max-min)   : {p95_max - p95_min:.3f} ms "
          f"({spread_pct:.1f}% of median)")
    print(f"first-half -> second-half p95: {first_half:.3f} -> {second_half:.3f} ms "
          f"({drift_pct:+.1f}%)")
    if p50s:
        print(f"p50 min / max          : {min(p50s):.3f} / {max(p50s):.3f} ms")
    if p99s:
        p99_med = statistics.median(p99s)
        p99_spread = (max(p99s) - min(p99s)) / p99_med * 100 if p99_med else 0.0
        fh99 = statistics.median(p99s[: max(1, len(p99s) // 2)])
        sh99 = statistics.median(p99s[max(1, len(p99s) // 2):]) if len(p99s) > 1 else fh99
        print(f"p99 median             : {p99_med:.3f} ms  "
              f"(primary metric family)")
        print(f"p99 spread (max-min)   : {max(p99s) - min(p99s):.3f} ms "
              f"({p99_spread:.1f}% of median)")
        print(f"first-half -> second-half p99: {fh99:.3f} -> {sh99:.3f} ms "
              f"({(sh99 - fh99) / fh99 * 100 if fh99 else 0.0:+.1f}%)")
        print(f"absolute p99 drift     : {max(p99s) - min(p99s):.3f} ms across the session")
    if steals:
        print(f"steal jiffies min / max: {min(steals)} / {max(steals)}")

    print()
    if spread_pct <= DRIFT_TOLERANCE_PCT:
        print(f"VERDICT: no material host drift at p95 (spread {spread_pct:.1f}% <= "
              f"{DRIFT_TOLERANCE_PCT:.0f}%).")
    else:
        print(f"VERDICT: host drift of {spread_pct:.1f}% at p95 in the reference cell,")
        print(f"above the {DRIFT_TOLERANCE_PCT:.0f}% tolerance. This is a limitation to")
        print("report with the numbers above, not something to correct for.")
    print("This bounds drift for THIS session only; it is not a claim that the host is")
    print("stable in general or across sessions. Because the run is rate-major, time is")
    print("confounded with offered rate rather than with arm, and the two arms of every")
    print("pair occupy adjacent slots roughly 30 s apart, so a drift of this size acts as")
    print("common-mode inflation of absolute latencies at later rates rather than as a")
    print("bias in any paired difference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
