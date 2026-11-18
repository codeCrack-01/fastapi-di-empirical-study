"""run_2x2.py — 2x2 mechanism experiment runner (runs ON the box).

Arms (branches in the ciiceronee repo):
  arm_s1              sync getter, inline (no Depends)
  master              sync getter, via Depends  (sync-depends baseline)
  arm_2x2_async_inline  async getter, inline
  arm_2x2_async_depends async getter, via Depends
  arm_2x2_wrapper     sync getter via anyio.to_thread.run_sync
  arm_2x2_limiter_200/1000/4000  sync-depends with threadpool limiter N

Usage (single cell, smoke test):
  cd <ciiceronee repo>
  python run_2x2.py --arm master --rate 1000 --reps 1 --port 8799

Usage (full grid):
  python run_2x2.py --grid --port 8799

Environment:
  CIICERONEE_REPO  path to the ciiceronee repo (default: ./)
  K6_PATH          path to k6 binary (default: k6 on PATH)
  PYTHON           python interpreter (default: .venv/bin/python)
  TIER2_FAST=1     shrink windows to 5s/1s/1s, 1 rep (smoke only)
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

REPO = Path(os.environ.get("CIICERONEE_REPO", ".")).resolve()
PY = os.environ.get("PYTHON", str((REPO / ".venv" / "bin" / "python").absolute()))
K6 = os.environ.get("K6_PATH", shutil.which("k6") or "k6")
HARNESS = Path(os.environ.get("HARNESS", str(Path(__file__).resolve().parent / "k6" / "harness_t2.js")))
PORT = 8799
ROUTE = "/simulations/active"
SERVER_CORES = os.environ.get("SERVER_CORES", "0,2,4")
K6_CORES = os.environ.get("K6_CORES", "6")
FAST = os.environ.get("TIER2_FAST", "0") == "1"

WARMUP = 5000 if FAST else 10000
WINDOW = 5000 if FAST else 30000
COOLDOWN = 2000 if FAST else 10000
REPS_DEFAULT = 1 if FAST else 10

ARMS = {
    "sync-inline":    "arm_s1",
    "sync-depends":   "master",
    "async-inline":   "arm_2x2_async_inline",
    "async-depends":  "arm_2x2_async_depends",
    "wrapper":        "arm_2x2_wrapper",
    "limiter-200":    "arm_2x2_limiter_200",
    "limiter-1000":   "arm_2x2_limiter_1000",
    "limiter-4000":   "arm_2x2_limiter_4000",
}

RATES = [2500, 3000, 3200] if not FAST else [1000]


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def boot(arm_branch, port):
    git(REPO, "checkout", "-q", arm_branch)
    cmd = []
    if shutil.which("taskset"):
        cmd += ["taskset", "-c", SERVER_CORES]
    cmd += [PY, "-m", "uvicorn", "ciicerone.api.main:app",
            "--host", "127.0.0.1", "--port", str(port),
            "--workers", "1", "--log-level", "warning", "--no-access-log"]
    log = open(f"server_{arm_branch}.log", "a")
    pro = subprocess.Popen(cmd, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
    deadline = time.time() + 30
    while time.time() < deadline:
        if pro.poll() is not None:
            raise RuntimeError(f"server exited early rc={pro.returncode}")
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/simulations/active", timeout=2)
            return pro
        except Exception:
            time.sleep(0.5)
    pro.kill()
    raise RuntimeError("server did not become ready")


def run_k6(rate, port):
    env = {
        **os.environ,
        "TARGET_URL": f"http://127.0.0.1:{port}",
        "TARGET_PATH": ROUTE,
        "RATE": str(rate),
        "WARMUP_MS": str(WARMUP),
        "WINDOW_MS": str(WINDOW),
        "COOLDOWN_MS": str(COOLDOWN),
    }
    k6cmd = []
    if shutil.which("taskset"):
        k6cmd += ["taskset", "-c", K6_CORES]
    k6cmd += [K6, "run", str(HARNESS)]
    out = subprocess.run(k6cmd, env=env, capture_output=True, text=True, timeout=WARMUP+WINDOW+COOLDOWN+60)
    return out.stdout + "\n" + out.stderr


def parse_k6(text):
    import json, re
    # k6 prints a JSON summary on one line
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{") and "load_fidelity" in line:
            try:
                d = json.loads(line)
                return {
                    "p99_cell": d.get("cell", {}).get("p99"),
                    "p99_window": d.get("window", {}).get("p99"),
                    "p95_window": d.get("window", {}).get("p95"),
                    "p50_window": d.get("window", {}).get("p50"),
                    "fidelity": d.get("load_fidelity"),
                    "dropped": d.get("dropped_iterations", 0),
                    "window_errors": d.get("window_errors", 0),
                    "window_requests": d.get("window_requests", 0),
                    "achieved_rate": d.get("achieved_rate"),
                }
            except json.JSONDecodeError:
                pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="sync-depends", choices=list(ARMS.keys()))
    ap.add_argument("--rate", type=int, default=None)
    ap.add_argument("--reps", type=int, default=REPS_DEFAULT)
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--grid", action="store_true")
    ap.add_argument("--out", default="results_2x2.tsv")
    args = ap.parse_args()

    rates = RATES if args.rate is None else [args.rate]
    arms = list(ARMS.keys()) if args.grid else [args.arm]
    results = []
    for arm in arms:
        branch = ARMS[arm]
        for rate in rates:
            for rep in range(args.reps):
                print(f"=== {arm} @ {rate} rep {rep+1}/{args.reps} ===", flush=True)
                pro = None
                try:
                    pro = boot(branch, args.port)
                    time.sleep(2)
                    text = run_k6(rate, args.port)
                    parsed = parse_k6(text)
                    p99 = parsed["p99_window"] if parsed else None
                    fid = parsed["fidelity"] if parsed else None
                    dropped = parsed["dropped"] if parsed else None
                    print(f"  p99_window={p99} fidelity={fid} dropped={dropped}")
                    results.append({"arm": arm, "branch": branch, "rate": rate,
                                    "rep": rep+1, "p99": p99, "fidelity": fid,
                                    "dropped": dropped, "parsed": parsed})
                except Exception as e:
                    print(f"  ERROR: {e}")
                    results.append({"arm": arm, "branch": branch, "rate": rate,
                                    "rep": rep+1, "p99": None, "error": str(e)})
                finally:
                    if pro:
                        pro.kill(); pro.wait(timeout=20)
                    git(REPO, "checkout", "-q", "master")
                    time.sleep(3)

    # write TSV
    with open(args.out, "a") as f:
        for r in results:
            f.write(f"{r['arm']}\t{r['branch']}\t{r['rate']}\t{r['rep']}\t{r.get('p99')}\t{r.get('fidelity')}\t{r.get('dropped')}\t{r.get('error','')}\n")
    print(f"\nResults appended to {args.out}")


if __name__ == "__main__":
    main()