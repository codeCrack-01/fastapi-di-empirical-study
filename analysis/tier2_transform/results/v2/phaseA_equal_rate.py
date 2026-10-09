"""Phase A1: equal-absolute-rate tables from prelim_v1 raw cells only.

Reads results/prelim_v1/bench/raw.tsv (never writes to it). Emits
phaseA_equal_rate.tsv and the equal-rate overlap matrix to stdout.

A cell is (repo, arm, rate); a rep is one row. For each rate present in all
four arms of an app we report, per arm:
  K, window_requests(min..max), fidelity(min..max),
  p50/p95/p99 median (min..max).
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
PRELIM = HERE.parents[1] / "prelim_v1" / "bench" / "raw.tsv"
REPOS = ["vstorm-co", "johnsonhk88", "ciiceronee", "azure-samples"]
ARMS = ["S1", "S2", "S3", "S4"]


def stats(vals: list[float]) -> tuple[float, float, float]:
    return statistics.median(vals), min(vals), max(vals)


def main() -> None:
    rows = list(csv.DictReader(PRELIM.open(), delimiter="\t"))
    by: dict[tuple[str, str, int], list[dict]] = defaultdict(list)
    for r in rows:
        by[(r["repo"], r["arm"], int(float(r["rate"])))].append(r)

    knees: dict[tuple[str, str], float] = {}
    # knee is not stored in raw.tsv; read it from each repo's load_latency.csv
    for repo in REPOS:
        with (PRELIM.parent / repo / "load_latency.csv").open() as f:
            for r in csv.DictReader(f):
                knees[(repo, r["arm"])] = float(r["knee_rps"])

    lines: list[str] = []
    lines.append("repo\tarm\tknee_rps\trate\tanchor\tK\twindow_requests\tfidelity\t"
                 "p50_med\tp50_min\tp50_max\tp95_med\tp95_min\tp95_max\t"
                 "p99_med\tp99_min\tp99_max")
    overlap_lines: list[str] = []
    for repo in REPOS:
        armset: dict[str, set[int]] = {}
        for arm in ARMS:
            armset[arm] = {rate for (rp, a, rate) in by if rp == repo and a == arm}
        shared = sorted(set.intersection(*armset.values()))
        union = sorted(set.union(*armset.values()))
        overlap_lines.append(f"{repo}\tshared={shared}\tunion={union}\t"
                             f"missing_from_shared={sorted(set(union)-set(shared))}")
        for rate in shared:
            for arm in ARMS:
                reps = by[(repo, arm, rate)]
                anchor = rate / knees[(repo, arm)]
                wr = [int(x["window_requests"]) for x in reps]
                fid = [round(float(x["fidelity"]), 6) for x in reps]
                p50 = stats([float(x["p50_ms"]) for x in reps])
                p95 = stats([float(x["p95_ms"]) for x in reps])
                p99 = stats([float(x["p99_ms"]) for x in reps])
                lines.append("\t".join(str(x) for x in [
                    repo, arm, f"{knees[(repo, arm)]:.0f}", rate,
                    f"{anchor:.2f}x", len(reps),
                    f"{min(wr)}..{max(wr)}",
                    f"{min(fid)}..{max(fid)}",
                    f"{p50[0]:.2f}", f"{p50[1]:.2f}", f"{p50[2]:.2f}",
                    f"{p95[0]:.2f}", f"{p95[1]:.2f}", f"{p95[2]:.2f}",
                    f"{p99[0]:.2f}", f"{p99[1]:.2f}", f"{p99[2]:.2f}",
                ]))

    out = HERE.parent / "phaseA_equal_rate.tsv"
    out.write_text("\n".join(lines) + "\n")
    print("=== equal-rate overlap matrix ===")
    for line in overlap_lines:
        print(line)
    print(f"\nwrote {out} ({len(lines)-1} rows)")


if __name__ == "__main__":
    main()
