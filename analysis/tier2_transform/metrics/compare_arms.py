"""compare_arms.py — turn bench raw.tsv + arm_meta.json into the study tables.

Reads results/bench/raw.tsv (per-rep rows, bench.py) and, per arm,
results/bench/<repo>__<arm>/arm_meta.json (knee_rps, cold-start import s,
cold_idle_rss_kb). Emits, per app under results/bench/<repo>/:

  summary.tsv        per-(arm, anchor): median p50/p95/p99 with min-max
                     spread, fidelity, err, rss/hwm peak, io read/write, and
                     (at the 1.0x anchor) S2-relative ratios for p99, rss,
                     disk read and knee.
  load_latency.csv   (arm, knee_rps, rate, anchor, p50, p95, p99, achieved, fidelity)
  cdf_<arm>.json     discrete CDF points at the arm's knee-rate cell
  resources.csv      per-arm knee, cold-start import s, cold-idle RSS, peaks

Reporting rule honored: median with min-max only (no CI wording).
"""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "results" / "bench"

ARM_ORDER = ["S2", "S1", "S3", "S4"]
ANCHORS = [0.25, 0.5, 0.75, 1.0, 1.25]
ANCHOR_LABEL = {0.25: "0.25x", 0.5: "0.5x", 0.75: "0.75x", 1.0: "1.0x", 1.25: "1.25x"}

def fnum(x) -> float | None:
    if x is None or x == "":
        return None
    try:
        return float(x)
    except ValueError:
        return None


def med(items) -> float | None:
    vals = []
    for x in items:
        v = fnum(x)
        if v is not None:
            vals.append(v)
    return statistics.median(vals) if vals else None


def read_raw() -> dict[tuple, list[dict]]:
    p = OUT / "raw.tsv"
    if not p.exists():
        raise SystemExit(f"{p} missing — run bench.py first")
    with open(p) as f:
        lines = f.read().splitlines()
    header = lines[0].split("\t")
    out: dict[tuple, list[dict]] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        row = dict(zip(header, line.split("\t")))
        if row.get("p95_ms") in ("", "ERRk6", None):
            continue
        try:
            float(row["p95_ms"])
        except (TypeError, ValueError):  # ERR / failure rows
            continue
        out.setdefault((row["repo"], row["arm"]), []).append(row)
    return out


def meta(repo: str, arm: str) -> dict:
    f = OUT / f"{repo}__{arm}" / "arm_meta.json"
    return json.loads(f.read_text()) if f.exists() else {}


def reps_at(rows_by_arm, repo, arm, rate):
    return [r for r in rows_by_arm.get((repo, arm), []) if float(r["rate"] or 0) == rate]


def main() -> None:
    rows_by_arm = read_raw()
    kneemap = {k: float(meta(*k).get("knee_rps", 0) or 0) for k in rows_by_arm}
    for repo in sorted({r for (r, _a) in rows_by_arm}):
        _write_repo(repo, rows_by_arm, kneemap)
    print(f"wrote summaries for {len({r for (r, _a) in rows_by_arm})} repos -> {OUT}")


def _write_repo(repo: str, rows_by_arm: dict, kneemap: dict) -> None:
    d = OUT / repo
    d.mkdir(parents=True, exist_ok=True)
    s2_knee = kneemap.get((repo, "S2")) or 0

    summarows = []
    llrows = [["arm", "knee_rps", "rate", "anchor", "p50", "p95", "p99", "achieved", "fidelity"]]
    for arm in ARM_ORDER:
        knee = kneemap.get((repo, arm)) or 0
        for anchor in sorted(ANCHOR_LABEL):
            rate = max(1, int(round(knee * anchor))) if knee else 0
            cell = reps_at(rows_by_arm, repo, arm, rate)
            if not cell:
                continue
            p50, p50s = _stat(cell, "p50_ms")
            p95, p95s = _stat(cell, "p95_ms")
            p99, p99s = _stat(cell, "p99_ms")
            fid = med(r["fidelity"] for r in cell)
            err = med(_ratio(r) for r in cell)
            rss = med(r["rss_max_kb"] for r in cell)
            hwm = med(r["hwm_max_kb"] for r in cell)
            io_r = med(r["io_read_kb"] for r in cell)
            io_w = med(r["io_write_kb"] for r in cell)
            row = [arm, knee or "", ANCHOR_LABEL[anchor], len(cell),
                   _f(p50), f"{_f(p50s[0])}-{_f(p50s[1])}",
                   _f(p95), f"{_f(p95s[0])}-{_f(p95s[1])}",
                   _f(p99), f"{_f(p99s[0])}-{_f(p99s[1])}",
                   _f(fid), _f(err), _f(rss), _f(hwm), _f(io_r), _f(io_w)]
            if anchor == 1.0 and s2_knee:
                s2 = reps_at(rows_by_arm, repo, "S2", int(round(s2_knee)))
                s2_p99 = med(r["p99_ms"] for r in s2) if s2 else None
                s2_rss = med(r["rss_max_kb"] for r in s2) if s2 else None
                s2_ior = med(r["io_read_kb"] for r in s2) if s2 else None
                row += [ratio(p99, s2_p99), ratio(rss, s2_rss), ratio(io_r, s2_ior), ratio(knee, s2_knee)]
            summarows.append(row)
            llrows.append([arm, knee or "", rate, ANCHOR_LABEL[anchor],
                           _f(p50), _f(p95), _f(p99),
                           med(r["achieved_rate"] for r in cell), fid])
        _write_cdf(repo, arm, rows_by_arm, kneemap)

    header = ["arm", "knee_rps", "anchor", "reps", "p50", "p50_spr", "p95", "p95_spr",
              "p99", "p99_spr", "fidelity", "err", "rss_kb", "hwm_kb", "io_r_kb", "io_w_kb",
              "vsS2_p99", "vsS2_rss", "vsS2_io_r", "vsS2_knee"]
    _tsv(d / "summary.tsv", header, summarows)
    _csv(d / "load_latency.csv", llrows)

    resheader = ["arm", "knee_rps", "import_s", "cold_idle_rss_kb", "rss_peak_kb", "hwm_peak_kb", "io_read_kb_sum", "io_write_kb_sum"]
    resrows = []
    for arm in ARM_ORDER:
        m = meta(repo, arm)
        rows = rows_by_arm.get((repo, arm), [])
        resrows.append([
            arm, kneemap.get((repo, arm)) or "", m.get("import_s"), m.get("cold_idle_rss_kb"),
            _maxf(rows, "rss_max_kb"), _maxf(rows, "hwm_max_kb"),
            _f(sum(float(r["io_read_kb"]) for r in rows if r.get("io_read_kb") not in ("", None))),
            _f(sum(float(r["io_write_kb"]) for r in rows if r.get("io_write_kb") not in ("", None))),
        ])
    _csv(d / "resources.csv", [resheader] + resrows)


def _write_cdf(repo: str, arm: str, rows_by_arm: dict, kneemap: dict) -> None:
    knee = kneemap.get((repo, arm))
    if not knee:
        return
    cell = reps_at(rows_by_arm, repo, arm, max(1, int(round(knee))))
    if not cell:
        return
    (OUT / repo / f"cdf_{arm}.json").write_text(json.dumps(_cdf(repo, arm, rows_by_arm, kneemap), indent=2))


def _cdf(repo: str, arm: str, rows_by_arm: dict, kneemap: dict) -> dict:
    knee = kneemap.get((repo, arm)) or 0
    cell = reps_at(rows_by_arm, repo, arm, max(1, int(round(knee))))
    counts = [int(r["window_requests"]) for r in cell if (r.get("window_requests") or "").isdigit()]
    return {
        "repo": repo, "arm": arm, "rate": max(1, int(round(knee))), "anchor": "1.0x", "reps": len(cell),
        "cdf_points": [
            {"p": 50, "v": med(r["p50_ms"] for r in cell)},
            {"p": 95, "v": med(r["p95_ms"] for r in cell)},
            {"p": 99, "v": med(r["p99_ms"] for r in cell)},
        ],
        "count_per_rep": med(counts),
    }


def _stat(cell, col):
    vals = [v for v in (fnum(r[col]) for r in cell) if v is not None]
    return (statistics.median(vals), (min(vals), max(vals))) if vals else (None, (None, None))


def _maxf(rows, col):
    vals = [float(r[col]) for r in rows if r.get(col) not in ("", "0", None)]
    return _f(max(vals)) if vals else ""


def _ratio(r):
    a = fnum(r.get("window_errors"))
    b = fnum(r.get("window_requests")) or 1
    return (a / b) if a is not None and b else None


def ratio(a, b):
    if a is None or b in (None, 0):
        return ""
    return f"{a / b:.2f}"


def _f(x):
    if x is None or x == "":
        return ""
    return f"{x:.2f}" if isinstance(x, float) else str(x)


def _tsv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(header)
        w.writerows(rows)


def _csv(path, rows):
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)


if __name__ == "__main__":
    main()