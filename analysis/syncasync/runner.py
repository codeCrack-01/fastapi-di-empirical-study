"""runner.py — one measured cell, or one ramp, for a ReviewGate-R app.

Every cell is a fresh uvicorn process on a pinned core set, driven by one k6
invocation, with the read-only database hashed before and after. Nothing is
reused between cells: no warm process, no cached pool, no carried connections.

The only things held constant across the whole study live here: worker count,
core pinning, warmup/window/cooldown lengths, the k6 script, and the hash
check. If any of these drifts, the cells are not comparable, so they are
constants in code rather than arguments at the call site.

Run:  python runner.py --pattern p1_direct --model sync --rate 100
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
K6_SCRIPT = HERE / "k6" / "harness.js"

# ---- study constants (see docs/prereg_execution_model.md) ----
WORKERS = 1

# Core allocation, per preregistration 4a.
#
# The server, the load generator, and the resource sampler must not share physical
# cores: k6 competing with the process it measures inflates latency and steals CPU,
# and the earlier sanity run demonstrated it (p4_container at 1 ms p50 while every
# other arm sat at 2-3 ms, with 40% lower CPU/req -- an artefact of k6 running on
# the server's cores, not a finding).
#
# The 8-vCPU study box is 4 PHYSICAL cores x 2 SMT threads, with siblings
# 0-1 / 2-3 / 4-5 / 6-7. Pinning the server to "0-5" would have spanned three
# physical cores plus one SMT sibling, and k6 on cpu 6 would have shared a physical
# core with the sampler -- the same interference defect in subtler form. So the
# default takes ONE logical CPU per physical core and leaves the siblings offline
# (see take_siblings_offline), which makes the layout verifiable rather than
# merely requested.
#
#   server  0,2,4  -> physical cores 0,1,2
#   k6      6      -> physical core 3
#   sampler 6      -> physical core 3, low priority, co-located with k6
#   offline 1,3,5,7
#
# The server is ONE uvicorn worker and is GIL-bound in both arms, so 3 physical
# cores is not a downgrade in practice; see preregistration 4a.
#
# Override for a different topology:
#   REVIEWGATE_SERVER_CORES=0,2,4 REVIEWGATE_K6_CORES=6 REVIEWGATE_SAMPLER_CORE=6
SERVER_CORES = os.environ.get("REVIEWGATE_SERVER_CORES", "0,2,4")
K6_CORES = os.environ.get("REVIEWGATE_K6_CORES", "6")
SAMPLER_CORE = os.environ.get("REVIEWGATE_SAMPLER_CORE", "6")
OFFLINE_CORES = os.environ.get("REVIEWGATE_OFFLINE_CORES", "1,3,5,7")

WARMUP_S = 10
WINDOW_S = 30
COOLDOWN_S = 12


def expand_cores(spec: str) -> set[int]:
    """Expand a core spec like "0,2,4" or "0-3" into a set of ints."""
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            out |= set(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


def sibling_groups() -> dict[int, list[int]]:
    """Map each online cpu to its SMT siblings, from sysfs."""
    groups: dict[int, list[int]] = {}
    for cpu in sorted(expand_cores(f"0-{os.cpu_count() - 1}")):
        path = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list")
        try:
            sibs = sorted(expand_cores(path.read_text().strip()))
        except OSError:
            sibs = [cpu]
        groups[cpu] = sibs
    return groups


def take_siblings_offline() -> dict:
    """Take unused SMT siblings offline so nothing can be scheduled onto them.

    taskset only restricts a process; it does not stop anything else from landing
    on the sibling thread. With the server pinned to 0,2,4 and k6 to 6, the
    siblings 1,3,5,7 have no legitimate user, so they are taken offline and the
    result is recorded per cell.
    """
    offline = expand_cores(OFFLINE_CORES)
    result: dict = {"requested": sorted(offline), "changed": [], "already": [],
                    "failed": [], "online_after": {}}
    for cpu in sorted(offline):
        f = Path(f"/sys/devices/system/cpu/cpu{cpu}/online")
        try:
            before = f.read_text().strip()
            if before == "1":
                f.write_text("0")
                result["changed"].append(cpu)
            else:
                result["already"].append(cpu)
        except OSError as exc:
            result["failed"].append({"cpu": cpu, "error": str(exc)})
    for cpu in sorted(expand_cores(f"0-{os.cpu_count() - 1}")):
        f = Path(f"/sys/devices/system/cpu/cpu{cpu}/online")
        try:
            result["online_after"][str(cpu)] = f.read_text().strip()
        except OSError:
            result["online_after"][str(cpu)] = "absent"
    return result


def steal_from_proc_stat() -> int | None:
    """Steal time (jiffies) from /proc/stat line 8, or None if unavailable.

    The study box is Vultr shared Cloud Compute, so a noisy neighbour can take
    CPU time. Recorded per cell as a threat to validity rather than filtered out.
    """
    try:
        line = Path("/proc/stat").read_text().splitlines()[0].split()
        return int(line[7])
    except (OSError, IndexError, ValueError):
        return None


def assert_disjoint() -> None:
    """Refuse to run if the server shares a PHYSICAL core with k6 or the sampler.

    The sampler is deliberately co-located with k6 (a 100 ms ticker), so
    k6/sampler overlap is allowed. Server overlap with either is not: they must
    not share a physical core, which is checked via sysfs sibling lists, not just
    by comparing logical CPU numbers.
    """
    server, k6, sampler = (expand_cores(SERVER_CORES), expand_cores(K6_CORES),
                          expand_cores(SAMPLER_CORE))
    sibs = sibling_groups()

    def physical(cpus: set[int]) -> set[int]:
        phys = set()
        for c in cpus:
            phys.update(sibs.get(c, [c]))
        return phys

    for name, other in (("k6", k6), ("sampler", sampler)):
        shared = physical(server) & physical(other)
        if shared:
            raise SystemExit(
                f"FATAL: server shares a PHYSICAL core with {name}: {sorted(shared)}. "
                "SMT siblings count as the same core; see preregistration 4a."
            )
    offline = expand_cores(OFFLINE_CORES)
    if physical(server) & physical(offline) or physical(k6) & physical(offline):
        raise SystemExit(
            "FATAL: a core marked offline is a sibling of a core in use; "
            f"offline={sorted(offline)}"
        )
    # stderr, not stdout: stdout carries the machine-readable JSON result
    print(f"cores: server={sorted(server)} k6={sorted(k6)} sampler={sorted(sampler)} "
          f"offline={sorted(offline)}", file=sys.stderr)
    print(f"physical cores: server={sorted(physical(server))} "
          f"k6={sorted(physical(k6))}", file=sys.stderr)

# cells per condition, fixed in advance
REPS = 40

# The sync arm's handlers are plain `def`, so Starlette dispatches them to the
# anyio threadpool. That pool size is framework default and is recorded as fixed
# configuration, per preregistration 4a. It is NOT tuned in response to a result.
ANYIO_THREADPOOL_SIZE = 40

# CPU-seconds are reported per completed request, so a slower arm is not
# rewarded for serving fewer requests at the same offered rate.


def sha256_db(path=None) -> str:
    from core_read import DB_PATH

    p = Path(path or DB_PATH)
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class RampResult:
    rate: float
    window: dict | None = None
    achieved: float = 0.0
    http_error_rate: float | None = None
    window_error_rate: float | None = None
    checks: dict | None = None
    returncode: int = 0
    startup_ms: float | None = None
    cpu_seconds: float | None = None
    rss_peak_mb: float | None = None
    db_sha256_before: str = ""
    db_sha256_after: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def db_unchanged(self) -> bool:
        return self.db_sha256_before == self.db_sha256_after and bool(self.db_sha256_before)


def ARM(pattern: str, model: str) -> str:
    """Module path of a generated app."""
    if pattern not in ("p1_direct", "p2_depends", "p3_middleware", "p4_container"):
        raise ValueError(f"unknown pattern {pattern}")
    if model not in ("sync", "async"):
        raise ValueError(f"unknown model {model}")
    return f"apps.{pattern}.{model}.app:app"


def _env() -> dict:
    e = dict(os.environ)
    e["PYTHONPATH"] = str(HERE) + os.pathsep + e.get("PYTHONPATH", "")
    e["PYTHONUNBUFFERED"] = "1"
    return e


def start_server(module: str, port: int, log: Path) -> subprocess.Popen:
    """Start one uvicorn worker, pinned to CORES, and wait for readiness."""
    cmd = []
    if shutil.which("taskset"):
        cmd += ["taskset", "-c", SERVER_CORES]
    cmd += [
        sys.executable, "-m", "uvicorn", module,
        "--host", "127.0.0.1", "--port", str(port),
        "--workers", str(WORKERS),
        "--log-level", "warning",
        "--no-access-log",
    ]
    fh = open(log, "w")
    proc = subprocess.Popen(cmd, cwd=str(HERE), env=_env(), stdout=fh, stderr=subprocess.STDOUT)

    import urllib.error
    import urllib.request

    deadline = time.time() + 30
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early (rc={proc.returncode}); see {log}")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as r:
                if r.status == 200:
                    return proc
        except (urllib.error.URLError, OSError):
            time.sleep(0.05)
    proc.kill()
    raise RuntimeError(f"server not ready within 30s; see {log}")


def stop_server(proc: subprocess.Popen) -> float:
    """SIGTERM then SIGKILL, returning wall seconds. ru_maxrss gives peak RSS."""
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage_after.ru_maxrss / 1024.0  # kB -> MB


def run_k6(port: int, rate: float, window_s: int, warmup_s: int, cooldown_s: int,
            ramp: bool, ramp_max: float, ramp_ms: int, summary: Path,
            errlog: Path) -> tuple[dict, int]:
    env = _env()
    env.update({
        "TARGET_URL": f"http://127.0.0.1:{port}",
        "SCENARIO": "ramp" if ramp else "steady",
        "RATE": str(rate),
        "WINDOW_MS": str(window_s * 1000),
        "WARMUP_MS": str(warmup_s * 1000),
        "COOLDOWN_MS": str(cooldown_s * 1000),
        "RAMP_MAX": str(ramp_max),
        "RAMP_MS": str(ramp_ms),
        "SUMMARY_FILE": str(summary),
    })
    # NOTE 1: k6 treats its script argument as a module specifier, not a path, so
    # an ABSOLUTE path breaks when the repo directory contains an apostrophe
    # ("Fall'26"). cwd is set to HERE, so a relative specifier sidesteps that.
    #
    # NOTE 2: k6 is pinned to its own core set, disjoint from the server's.
    cmd = []
    if shutil.which("taskset"):
        cmd += ["taskset", "-c", K6_CORES]
    cmd += ["k6", "run", "--quiet", "k6/harness.js"]
    proc = subprocess.run(
        cmd, cwd=str(HERE), env=env, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        errlog.write_text(proc.stderr or "")
    data = {}
    if summary.exists():
        try:
            data = json.loads(summary.read_text())
        except json.JSONDecodeError:
            data = {}
    return data, proc.returncode


def run_ramp(module: str, port: int, rate: float, window_s: int = WINDOW_S,
             warmup_s: int = WARMUP_S, cooldown_s: int = COOLDOWN_S,
             ramp: bool = False, ramp_max: float | None = None,
             ramp_ms: int = 8000, tag: str = "cell") -> RampResult:
    """One measured cell or ramp. Returns the window-only result."""
    out = HERE / "results" / "cells"
    out.mkdir(parents=True, exist_ok=True)
    stamp = f"{tag}-{int(time.time() * 1000)}"
    log = out / f"{stamp}.server.log"
    summary = out / f"{stamp}.summary.json"

    before = sha256_db()
    usage0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.time()
    proc = start_server(module, port, log)
    startup_ms = (time.time() - t0) * 1000.0

    try:
        data, rc = run_k6(port, rate, window_s, warmup_s, cooldown_s,
                          ramp, ramp_max if ramp_max is not None else rate, ramp_ms,
                          summary, out / f"{stamp}.k6.err")
    finally:
        stop_server(proc)

    usage1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    after = sha256_db()

    cpu_seconds = (
        (usage1.ru_utime - usage0.ru_utime) + (usage1.ru_stime - usage0.ru_stime)
    )
    data = data or {}
    win_reqs = data.get("window_requests") or 0
    win_errs = data.get("window_errors") or 0
    res = RampResult(
        rate=rate,
        window=(data or {}).get("window"),
        http_error_rate=(data or {}).get("httpErrors"),
        checks={"passes": (data or {}).get("checks"), "fails": (data or {}).get("checkFailures")},
        returncode=rc,
        startup_ms=round(startup_ms, 1),
        cpu_seconds=round(cpu_seconds, 3),
        rss_peak_mb=round(usage1.ru_maxrss / 1024.0, 1),
        db_sha256_before=before,
        db_sha256_after=after,
    )
    res.extra = {
        "iterations": (data or {}).get("iterations"),
        "window_requests": win_reqs,
        "window_errors": win_errs,
        "window_error_rate": (win_errs / win_reqs) if win_reqs else None,
        "cpu_seconds_per_req": round(cpu_seconds / win_reqs, 6) if win_reqs else None,
        "http_req_duration": (data or {}).get("http_req_duration"),
    }
    # achieved throughput and error rate come from the window-scoped counters,
    # not from the Trend sample count, which is a latency-sample count
    if win_reqs and rate:
        res.achieved = (win_reqs / window_s) / rate
        res.window_error_rate = win_errs / win_reqs
    summary.unlink(missing_ok=True)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True)
    ap.add_argument("--model", required=True, choices=["sync", "async"])
    ap.add_argument("--rate", type=float, required=True)
    ap.add_argument("--port", type=int, default=8900)
    ap.add_argument("--window", type=int, default=WINDOW_S)
    ap.add_argument("--warmup", type=int, default=WARMUP_S)
    ap.add_argument("--cooldown", type=int, default=COOLDOWN_S)
    ap.add_argument("--tag", default="manual")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    assert_disjoint()
    offline_state = take_siblings_offline()
    print(f"offline siblings: {json.dumps(offline_state)}", file=sys.stderr)
    steal_before = steal_from_proc_stat()
    before = sha256_db()
    res = run_ramp(ARM(args.pattern, args.model), args.port, args.rate,
                   args.window, args.warmup, args.cooldown, tag=args.tag)
    steal_after = steal_from_proc_stat()
    payload = {
        "pattern": args.pattern, "model": args.model, "rate": args.rate,
        "workers": WORKERS,
        "server_cores": SERVER_CORES, "k6_cores": K6_CORES,
        "sampler_core": SAMPLER_CORE, "offline_cores": OFFLINE_CORES,
        # recorded per cell so the topology is verifiable, not just asserted
        "offline_state": offline_state,
        "sibling_groups": {str(k): v for k, v in sibling_groups().items()},
        # shared-plan host noise; reported, never filtered
        "steal_jiffies": (steal_after - steal_before)
                         if (steal_before is not None and steal_after is not None)
                         else None,
        "plan_type": os.environ.get("REVIEWGATE_PLAN_TYPE", "vc2-8c-32gb(shared)"),
        "anyio_threadpool_size": ANYIO_THREADPOOL_SIZE,
        "warmup_s": args.warmup, "window_s": args.window, "cooldown_s": args.cooldown,
        "db_unchanged": res.db_unchanged,
        "result": res.__dict__,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return 0 if res.db_unchanged else 2


if __name__ == "__main__":
    raise SystemExit(main())
