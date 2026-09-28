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

# Provisioned host for amendment 2: Vultr voc-c-8c-16gb-150s-amd in ord, AMD EPYC
# (Milan), 4 physical cores x 2 SMT threads. Recorded in per-cell metadata.
PLAN_TYPE = os.environ.get("REVIEWGATE_PLAN_TYPE", "voc-c-8c-16gb-150s-amd")

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


def cpu_online(cpu: int) -> bool:
    """True if the cpu is online. cpu0 has no `online` file and cannot be offlined."""
    f = Path(f"/sys/devices/system/cpu/cpu{cpu}/online")
    if not f.exists():
        return True
    try:
        return f.read_text().strip() == "1"
    except OSError:
        return False


TOPOLOGY_CACHE = HERE / "results" / "topology.json"


def all_cpu_ids() -> list[int]:
    """Every cpu the kernel knows about, from the sysfs directories.

    NOT os.cpu_count(): that returns the number of ONLINE cpus, which drops to 4
    once the siblings are offlined and would truncate the topology to 0-3. The
    cpuN directories persist while offline, so they are the reliable source.
    """
    root = Path("/sys/devices/system/cpu")
    cpus = []
    for d in root.glob("cpu[0-9]*"):
        try:
            cpus.append(int(d.name[3:]))
        except ValueError:
            pass
    return sorted(cpus)


def read_sysfs_siblings() -> dict[int, list[int]]:
    """Map each cpu to its SMT siblings straight from sysfs."""
    groups: dict[int, list[int]] = {}
    for cpu in all_cpu_ids():
        path = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list")
        try:
            groups[cpu] = sorted(expand_cores(path.read_text().strip()))
        except OSError:
            # an offline cpu has no topology directory
            groups[cpu] = [cpu]
    return groups


def capture_topology() -> dict[int, list[int]]:
    """Record the true SMT topology. Must be called while the machine is online.

    An offline cpu has no topology directory, so a map read afterwards reports
    every cpu as its own physical core. That is not a cosmetic problem: it would
    make assert_disjoint()'s "offline cpu is a sibling of a core in use" guard
    pass on a misconfigured layout, e.g. server on cpu0 with cpu1 marked offline
    silently disables the server's own sibling. So the real map is captured once
    from a fully online machine and cached; everything afterwards reads the
    cache and refuses to fall back to a live read.
    """
    groups = read_sysfs_siblings()
    offline = [c for c in groups if not cpu_online(c)]
    missing = [c for c in groups
               if len(groups[c]) == 1 and c in expand_cores(
                   ",".join(str(x) for x in sorted(groups)))]
    if offline:
        raise SystemExit(
            f"FATAL: cannot capture topology, cpus {offline} are offline. "
            "Re-enable them (see enable_all_cpus) and capture before offlining."
        )
    # every cpu in a real SMT box shares a core with at least one other
    if len(groups) > 1 and all(len(v) == 1 for v in groups.values()):
        raise SystemExit(
            "FATAL: captured topology reports no SMT siblings at all, which means "
            f"it was read while cpus were offline. Got {groups}."
        )
    TOPOLOGY_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOPOLOGY_CACHE.write_text(json.dumps(
        {str(k): v for k, v in sorted(groups.items())}, indent=2))
    return groups


def enable_all_cpus() -> list[int]:
    """Bring every cpu online. Used to restore a box after a study run."""
    brought = []
    for cpu in all_cpu_ids():
        f = Path(f"/sys/devices/system/cpu/cpu{cpu}/online")
        if f.exists():
            try:
                if f.read_text().strip() == "0":
                    f.write_text("1")
                    brought.append(cpu)
            except OSError:
                pass
    return brought


def sibling_groups() -> dict[int, list[int]]:
    """The cached pre-offline SMT sibling map.

    Raises if it was never captured, rather than reading sysfs live: a live read
    after offlining is wrong, and guessing would defeat the point of the check.
    """
    if not TOPOLOGY_CACHE.exists():
        raise SystemExit(
            f"FATAL: {TOPOLOGY_CACHE} missing. Run prepare_box.py, which captures "
            "the topology while the machine is online, before any cell runs."
        )
    return {int(k): v for k, v in json.loads(TOPOLOGY_CACHE.read_text()).items()}


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
        if not f.exists():
            result["failed"].append({"cpu": cpu, "error": "no online file (cpu0?)"})
            continue
        try:
            before = f.read_text().strip()
            if before == "1":
                f.write_text("0")
                result["changed"].append(cpu)
            else:
                result["already"].append(cpu)
        except OSError as exc:
            result["failed"].append({"cpu": cpu, "error": str(exc)})
    for cpu in all_cpu_ids():
        f = Path(f"/sys/devices/system/cpu/cpu{cpu}/online")
        try:
            result["online_after"][str(cpu)] = f.read_text().strip()
        except OSError:
            result["online_after"][str(cpu)] = "absent"
    return result


def steal_from_proc_stat() -> int | None:
    """Steal time (jiffies) from /proc/stat line 8, or None if unavailable.

    Recorded per cell as a threat to validity rather than filtered out. It is
    recorded whether or not the plan is dedicated, so the data can falsify the
    dedicated claim in the pre-registration.
    """
    try:
        line = Path("/proc/stat").read_text().splitlines()[0].split()
        return int(line[7])
    except (OSError, IndexError, ValueError):
        return None


def host_facts() -> dict:
    """What this machine actually is, read from the machine, per cell.

    Deliberately not hardcoded: if the box is ever replaced, the per-cell
    metadata shows the new CPU, and the pre-registration's topology claim
    becomes checkable rather than assumed.

    Note on counts: os.cpu_count() reports ONLINE processors, so with siblings
    1,3,5,7 offlined it returns 4 and would misreport an 8-CPU host. The CPU
    counts here come from sysfs cpu* directories instead, and the online count is
    recorded separately.
    """
    cpu_ids = all_cpu_ids()
    groups = sibling_groups()
    online = [c for c in cpu_ids if cpu_online(c)]

    def procinfo(key: str) -> set[str]:
        vals = set()
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.startswith(key):
                    vals.add(line.split(":", 1)[1].strip())
        except OSError:
            pass
        return vals

    def meminfo(key: str) -> str | None:
        try:
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith(key):
                    return line.split(":", 1)[1].strip()
        except OSError:
            return None
        return None

    uname = os.uname()
    return {
        "cpu_model": (sorted(procinfo("model name")) or [None])[0],
        "logical_cpus_present": len(cpu_ids),
        "logical_cpus_online": len(online),
        "online_cpus": online,
        "physical_cores": len({min(v) for v in groups.values()}),
        "sockets": len(procinfo("physical id")) or None,
        "thread_siblings_per_core": max((len(v) for v in groups.values()), default=0),
        "mem_total": meminfo("MemTotal"),
        "kernel": uname.release,
        "arch": uname.machine,
        "sibling_groups": {str(k): v for k, v in groups.items()},
    }


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
    # The offline set is SUPPOSED to be the unused SMT siblings of the cores in
    # use, so "offline cpu shares a physical core with the server" is the
    # intended design, not a fault. What would be a fault is a cpu that is
    # BOTH pinned and offline: that disables a core in use instead of isolating
    # one, and would silently halve the server's capacity. Checked against the
    # cached PRE-offline topology, since sysfs no longer reports sibling lists
    # once a cpu is offline.
    offline = expand_cores(OFFLINE_CORES)
    for name, used in (("server", server), ("k6", k6), ("sampler", sampler)):
        both = used & offline
        if both:
            raise SystemExit(
                f"FATAL: cpus {sorted(both)} are pinned to the {name} AND marked "
                f"offline (server={sorted(server)} k6={sorted(k6)} "
                f"offline={sorted(offline)}). A cpu cannot be both in use and "
                "offlined; that disables a core instead of isolating one."
            )
    # And confirm the offline set really is offline, so a stale layout cannot pass.
    not_offline = [c for c in sorted(offline) if cpu_online(c)]
    if not_offline:
        raise SystemExit(
            f"FATAL: cpus {not_offline} are marked offline in the layout but are "
            "still online. take_siblings_offline() must run before any cell."
        )
    for name, used in (("server", server), ("k6", k6)):
        down = [c for c in sorted(used) if not cpu_online(c)]
        if down:
            raise SystemExit(
                f"FATAL: {name} cpus {down} are offline; they cannot be pinned to."
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

    siblings = sibling_groups()
    offline_state = take_siblings_offline()
    assert_disjoint()
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
        "sibling_groups": {str(k): v for k, v in siblings.items()},
        # host noise is reported, never filtered -- recorded whether or not the
        # plan is dedicated, so the data can falsify the dedicated claim
        "steal_jiffies": (steal_after - steal_before)
                         if (steal_before is not None and steal_after is not None)
                         else None,
        # The pre-registered plan for amendment 2. Previously this defaulted to
        # the old shared "vc2-8c-32gb" and REVIEWGATE_PLAN_TYPE was unset on the
        # box, so every cell would have been mislabelled with the wrong plan.
        "plan_type": os.environ.get("REVIEWGATE_PLAN_TYPE", PLAN_TYPE),
        "host": host_facts(),
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
