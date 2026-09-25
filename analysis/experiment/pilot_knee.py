"""pilot_knee.py — calibrate the scaling knee (Mode A and Mode B) on this machine.

Runs a ramping-arrival-rate k6 profile once per mode against a fresh server
process and reports the knee: the arrival rate (req/s) where p95 latency departs
the low-load slope. Saves results/knee_<mode>.json for the full matrix.

Pre-registered knee rule (do not change after data collection):
- bucket request durations into 2 s windows over the 300 s ramp;
- baseline = median of p95 over the first 3 buckets;
- knee    = the rate at the first bucket whose p95 exceeds max(3*base, 1 ms)
  AND that stays crossed for >= half the remaining buckets (a durable
  departure, not a transient spike).

Usage (from analysis/experiment, in .venv):
    python pilot_knee.py [--mode A|B] [--max-a N] [--max-b N]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
K6 = "k6"


def start_server(mode: str, port: int, core: str) -> tuple[subprocess.Popen, float]:
    cfg = ["taskset", "-c", core, HERE / ".venv/bin/python", "-m", "uvicorn",
           "straights.s0.app:app", "--host", "127.0.0.1", "--port", str(port),
           "--workers", "1", "--log-level", "warning"]
    env = dict(os.environ, REVIEWGATE_MODE=mode, PYTHONHASHSEED="0",
               REVIEWGATE_DB=str(RESULTS / f"pilot_{mode}.db"))
    proc = subprocess.Popen(cfg, cwd=HERE, env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    t0 = time.monotonic()
    return proc, t0


def wait_ready(port: int, timeout: float = 30.0) -> None:
    import httpx
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            r = httpx.get(f"http://127.0.0.1:{port}/health", timeout=1.0)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.05)
    raise RuntimeError(f"server on :{port} did not become ready")


def run_k6_ramp(mode: str, port: int, max_rps: int, out_csv: Path) -> dict:
    cmd = [K6, "run", "--quiet", "--summary-export=-",
           f"--out=csv={out_csv}", "-e", f"TARGET_URL=http://127.0.0.1:{port}",
           "-e", "SCENARIO=ramp", "-e", f"RAMP_MAX_RPS={max_rps}",
           "-e", f"SUMMARY_FILE={out_csv.with_suffix('.summary.json')}",
           str(HERE / "k6" / "harness.js")]
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=1800)
    try:
        summary = json.loads(r.stdout)
    except Exception:
        summary = {"_raw": r.stdout[:500]}
    summary["_rc"] = r.returncode
    return summary


def detect_knee(csv_path: Path, max_rps: int, mode: str) -> dict:
    """Bucket arrival rate + p95 latency over the ramp; find slope departure.

    The k6 CSV `timestamp` column is unix epoch seconds; we normalize to elapsed
    time from the first row. The ramp reaches max_rps at 300s; buckets are 2s
    wide, so bucket b ends at elapsed ~(b+1)*2 and the arrival rate at that
    point is approx max_rps*(b+1)/150. Knee = first bucket where p95 latency
    exceeds 3x the low-load baseline and stays above that threshold.
    """
    import statistics
    buckets: dict[int, list[float]] = {}
    t0 = None
    with open(csv_path) as f:
        header = f.readline()
        for line in f:
            p = line.strip().split(",")
            if len(p) < 3:
                continue
            metric, ts, val = p[0], float(p[1]), float(p[2])
            if metric != "http_req_duration":
                continue
            if t0 is None:
                t0 = ts
            elapsed = ts - t0
            b = int(elapsed // 2)  # 2 s buckets
            buckets.setdefault(b, []).append(val)  # k6 CSV duration is already ms
    if not buckets:
        return {"knee_rps": None, "note": "no request buckets"}

    def p95(vals):
        s = sorted(vals)
        return s[int(len(s) * 0.95)]

    base = statistics.median(p95(buckets[b]) for b in sorted(buckets)[:3])
    # knee = rate where p95 latency durably departs low-load level.
    # Use an absolute floor (1 ms) -- 3x of a sub-ms base triggers on noise.
    departure = max(3 * base, 1.0)
    knee_rps = None
    crossed_at = []
    for b in sorted(buckets):
        r = p95(buckets[b])
        rate_now = max_rps * (b + 1) / 150.0
        if r > departure:
            crossed_at.append((b, rate_now))
    for i, (b, rate_now) in enumerate(crossed_at):
        # confirm it stays crossed (not a transient spike)
        later = [bb for (bb, _) in crossed_at if bb >= b]
        if len(later) >= max(2, int(0.5 * len(crossed_at))):
            knee_rps = rate_now
            break
    return {"knee_rps": knee_rps, "base_p95_ms": round(base, 3),
            "departure_ms": round(departure, 3)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["A", "B"], default=None)
    ap.add_argument("--max-a", type=int, default=3000)
    ap.add_argument("--max-b", type=int, default=400)
    ap.add_argument("--core", default="0")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "env_report.txt").write_text(
        subprocess.run(["lscpu"], capture_output=True, text=True).stdout +
        subprocess.run(["cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"],
                       capture_output=True, text=True).stdout)

    modes = ["A", "B"] if not args.mode else [args.mode]
    for mode in modes:
        max_rps = args.max_a if mode == "A" else args.max_b
        port = 8500
        proc, t0 = start_server(mode, port, args.core)
        try:
            wait_ready(port)
            print(f"[pilot] mode {mode}: server up in {time.monotonic() - t0:.2f}s, ramping to {max_rps} rps")
            csv = RESULTS / f"knee_{mode}.csv"
            out = run_k6_ramp(mode, port, max_rps, csv)
            knee = detect_knee(csv, max_rps, mode)
            knee["mode"] = mode
            knee["summary"] = out
            (RESULTS / f"knee_{mode}.json").write_text(json.dumps(knee, indent=2))
            print(f"[pilot] mode {mode}: knee_rps={knee.get('knee_rps')} base_p95_ms={knee.get('base_p95_ms'):.3f}")
        finally:
            proc.terminate()
            proc.wait(timeout=15)


if __name__ == "__main__":
    sys.exit(main())