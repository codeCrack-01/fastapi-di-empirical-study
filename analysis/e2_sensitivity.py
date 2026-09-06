"""
analysis/e2_sensitivity.py — E2 (Python-dominant-language) threshold sensitivity.

E2 requires ``py_ratio >= E2_MIN_PYTHON_RATIO`` (default 0.5). This script shows
how the corpus changes under alternative thresholds using only committed local
artifacts:

  corpus/candidates.json     every discovered candidate has ``py_ratio``
  corpus/exclusion_log.json  terminal decision per candidate (reason = first
                             failing rule; E2 failures carry ``py_ratio=...``)
  corpus/manifest.json       the accepted repos (all ``py_ratio`` recorded)

Model (honest about first-failure ordering and un-cloned repos):

  * Raising the threshold removes accepted repos whose ``py_ratio < t`` — these
    are real, verifiable removals (they already passed every later rule).
  * Lowering the threshold would admit E2-excluded repos with ``py_ratio >= t``,
    but those were never cloned, so whether they pass E5/E6 is unknown. Their
    admission is reported as an UPPER BOUND only, not a projection.

Outputs:
  analysis/out/e2_sensitivity.csv     per-threshold accepted-kept and pool counts
  printed diagnostic of the accepted py_ratio margin
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

BASE_THRESHOLD = 0.5
THRESHOLDS = [0.0, 0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 1.0]


def _ratio_from_detail(detail: str) -> float | None:
    m = re.search(r"py_ratio=([0-9.]+)", detail)
    return float(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=str(ROOT.parent / "corpus" / "candidates.json"))
    ap.add_argument("--exclusion", default=str(ROOT.parent / "corpus" / "exclusion_log.json"))
    ap.add_argument("--manifest", default=str(ROOT.parent / "corpus" / "manifest.json"))
    ap.add_argument("--out", default=str(OUT_DIR / "e2_sensitivity.csv"))
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    candidates = json.loads(Path(args.candidates).read_text())["candidates"]
    exclusions = json.loads(Path(args.exclusion).read_text())["excluded"]
    manifest = json.loads(Path(args.manifest).read_text())["accepted"]

    pool_py = [c.get("py_ratio") or 0.0 for c in candidates]
    accepted_py = [a.get("py_ratio") or 0.0 for a in manifest]

    # E2-excluded repos and their recorded py_ratio (from detail)
    e2_excluded_py = []
    for x in exclusions:
        if x.get("reason") == "E2":
            r = _ratio_from_detail(x.get("detail", ""))
            if r is not None:
                e2_excluded_py.append(r)

    rows = []
    for t in THRESHOLDS:
        if t == BASE_THRESHOLD:
            # exactly the current corpus
            accepted_kept = len(accepted_py)
            e2_now_pass = sum(1 for r in e2_excluded_py if r >= t)
            upper_bound = accepted_kept + e2_now_pass
            note = "base (current setting)"
        else:
            # accepted kept for this threshold (their py_ratio is known & verified)
            accepted_kept = sum(1 for r in accepted_py if r >= t)
            # lower-threshold only: E2-excluded repos that would now pass the gate
            e2_now_pass = sum(1 for r in e2_excluded_py if r >= t)
            upper_bound = accepted_kept + e2_now_pass
            note = "E2-excluded admission is an upper bound (no reports; unverified past E2)"

        rows.append({
            "threshold": t,
            "pool_passing_gate": sum(1 for r in pool_py if r >= t),
            "accepted_kept": accepted_kept,
            "e2_excluded_now_passing_upper_bound": e2_now_pass if t < BASE_THRESHOLD else 0,
            "projected_accepted_upper_bound": upper_bound if t < BASE_THRESHOLD else accepted_kept,
            "note": "" if t == BASE_THRESHOLD else note,
        })

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"[e2_sensitivity] {len(candidates)} candidates; {len(accepted_py)} accepted; {len(e2_excluded_py)} E2-excluded")
    print("Accepted pool py_ratio: min %.3f  p25 %.3f  median %.3f  p75 %.3f  max %.3f"
          % (min(accepted_py), st.quantiles(accepted_py, n=4)[0],
             st.median(accepted_py), st.quantiles(accepted_py, n=4)[2], max(accepted_py)))
    near = [r for r in accepted_py if BASE_THRESHOLD <= r < 0.6]
    print(f"Accepted within [0.5, 0.6): {len(near)}  |  accepted < 0.6: "
          f"{sum(1 for r in accepted_py if r < 0.6)}  |  exact 0.5: "
          f"{sum(1 for r in accepted_py if abs(r - 0.5) < 1e-9)}")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()