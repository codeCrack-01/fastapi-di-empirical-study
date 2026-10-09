"""bench.py — tier-2 open-loop bench orchestrator (runs ON the box).

Per arm in plan.json:
  1. checkout the arm branch
  2. run setup (docker/alembic, idempotent) + preseed (auth token if any),
     boot the server (uvicorn)
  3. cold-idle RSS snapshot + 3x cold-start import probe
  4. knee discovery (knee.py: reference @10 rps, geometric ladder, tier-1
     qualifiers p95<=3*p95_ref, err<=1%, fidelity>=0.98)
  5. grid cells = knee x {0.25,0.5,0.75,1.0,1.25}; K=5 at the two top cells,
     K=3 at the three lower; each cell is one k6 open-loop run with a
     resource_sample.py sidecar over warmup+window
  6. rows written to results/bench/raw.tsv (+ per-arm arm_meta.json)

k6 must be on PATH. Uses runner/k6/harness_t2.js (open-loop
constant-arrival-rate, 10s warmup / 30s window / 10s cooldown, REQ_TIMEOUT 5s).
The knee is single-probe discovery; measured cells carry the K repetitions.

TIER2_FAST=1 shrinks windows to 5s/1s/1s and 1 rep per cell — pipeline smoke
only, never for reported numbers.

NOTE on interpreter paths: never Path.resolve() a venv python — .venv/bin/python
is a symlink to the base interpreter and resolving it silently drops venv
activation (module-not-found uvicorn). Use .absolute().
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
import knee as KNEE  # runner/knee.py (same dir)

PY = sys.executable
K6 = shutil.which("k6") or "k6"

# Server pinning (tier-1 layout: uvicorn on physical cores 0,2,4). Disable with
# TIER2_SERVER_CORES="" or TIER2_PIN=0 (the S3@2560 pinned-vs-unpinned probe).
SERVER_CORES = os.environ.get("TIER2_SERVER_CORES", "0,2,4")
if os.environ.get("TIER2_PIN", "1") == "0":
    SERVER_CORES = ""
# Phase-B results land under results/<TIER2_OUTDIR> (v2 default), never over
# the prelim archive.
OUTDIR_REL = os.environ.get("TIER2_OUTDIR", "v2/bench")

ROWS: list[list] = []  # per-rep raw rows


def load_plan() -> dict:
    return json.loads((HERE / "plan.json").read_text())


def venv_python(arm: dict, repo_dir: Path) -> Path:
    return (repo_dir / arm["cwd"] / arm["venv"] / "bin" / "python").absolute()


def git(repo_dir: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo_dir), *args], check=True, capture_output=True)


def arm_env(arm: dict) -> dict:
    """Arm env with <RUNNER> placeholders resolved (runner dir)."""
    return {k: str(v).replace("<RUNNER>", str(HERE)) for k, v in arm.get("env", {}).items()}


def resolve_auth(arm: dict, py: Path, env: dict, cwd: Path) -> tuple[str | None, str]:
    """Return (auth header VALUE, header name)."""
    header = arm.get("auth_header", "Authorization")
    if arm.get("auth") == "bearer-token":
        out = subprocess.run(
            [str(py), str(HERE / "preseed_jhk.py")],
            cwd=cwd, env={**os.environ, **env}, capture_output=True, text=True, check=True,
        )
        return "Bearer " + out.stdout.strip(), header
    if arm.get("auth_token"):
        return arm["auth_token"], header
    return None, header


def boot(arm: dict, repo_dir: Path, workdir: Path) -> tuple[subprocess.Popen, str | None, str]:
    """setup + preseed, then boot uvicorn. Kills the server if readiness fails."""
    py = venv_python(arm, repo_dir)
    env = {**os.environ, **arm_env(arm)}
    for cmd in arm.get("setup", []):
        subprocess.run(
            ["bash", "-c", cmd.replace("<PY>", str(py)).replace("<RUNNER>", str(HERE))],
            cwd=repo_dir / arm["cwd"], env=env, capture_output=True, text=True,
        )
    auth, auth_header = resolve_auth(arm, py, env, repo_dir / arm["cwd"])
    args = shlex.split(arm.get("serve_args", "").replace("<RUNNER>", str(HERE)))
    uvi = [str(py), "-m", "uvicorn", f"{arm['module']}:{arm.get('attr', 'app')}"] + args \
        + ["--workers", "1", "--port", str(arm["port"])]
    cmd = ["taskset", "-c", SERVER_CORES] + uvi if SERVER_CORES else uvi
    pro = subprocess.Popen(
        cmd,
        cwd=repo_dir / arm["cwd"],
        env=env,
        stdout=open(workdir / "server.log", "a"),
        stderr=subprocess.STDOUT,
    )
    try:
        wait_ready(arm["port"], pro, timeout=90)
    except Exception:
        pro.kill()
        pro.wait(timeout=20)
        raise
    return pro, auth, auth_header


def wait_ready(port: int, pro: subprocess.Popen, timeout: float = 90.0) -> None:
    """Wait until the port answers AND the spawned server is still alive.

    A stray process on the port (leftover from a prior run) would otherwise be
    mistaken for readiness while the real server died on bind (Errno 98) and the
    resource sidecar samples a dead pid.
    """
    url = f"http://127.0.0.1:{port}/"
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if pro.poll() is not None:
            raise RuntimeError(f"server on :{port} exited early (rc={pro.returncode}); port may be held by a stray")
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except urllib.error.HTTPError:
            return  # any HTTP response means the app is wired up (even 404/401)
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"server on :{port} did not become ready")


def proc_io(pid: int) -> tuple[int, int]:
    io = Path(f"/proc/{pid}/io")
    if not io.exists():
        return 0, 0
    r = w = 0
    for line in io.read_text().splitlines():
        if line.startswith("read_bytes:"):
            r = int(line.split()[1])
        elif line.startswith("write_bytes:"):
            w = int(line.split()[1])
    return r // 1024, w // 1024


def read_status(pid: int) -> int:
    st = Path(f"/proc/{pid}/status")
    if not st.exists():
        return 0
    for line in st.read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1])
    return 0


def cold_start(arm: dict, repo_dir: Path) -> dict:
    env = {**os.environ, **arm_env(arm)}
    py = venv_python(arm, repo_dir)
    cwd = repo_dir / arm["cwd"]
    samples = []
    for _ in range(3):
        code = f"import importlib,time;t=time.perf_counter();importlib.import_module('{arm['module']}');print(time.perf_counter()-t)"
        out = subprocess.run(
            ["bash", "-c", f"cd {shlex.quote(str(cwd))} && {shlex.quote(str(py))} -c {shlex.quote(code)}"],
            env=env, capture_output=True, text=True,
        )
        if out.returncode == 0 and out.stdout.strip():
            samples.append(float(out.stdout.strip().splitlines()[-1]))
    return {"import_s": statistics.median(samples) if samples else None}


def run_arm(arm: dict, outdir: Path) -> None:
    repo_dir = HERE.parent / "repos" / arm["repo"]
    git(repo_dir, "checkout", "-q", arm["branch"])
    workdir = outdir / f"{arm['repo']}__{arm['arm']}"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "server.log").unlink(missing_ok=True)

    pro, auth, auth_header = boot(arm, repo_dir, workdir)
    pid = pro.pid
    try:
        time.sleep(2)
        idle = read_status(pid)
        cold = cold_start(arm, repo_dir)
        base = f"http://127.0.0.1:{arm['port']}"
        route = arm["route"]

        knee, ref = KNEE.find_knee(K6, base, route, auth, workdir, auth_header)

        for frac in KNEE.GRID:
            rate = max(1, int(round(knee * frac)))
            for rep in range(KNEE.REPS[frac]):
                ROWS.extend(run_rep(arm, pid, base, route, auth, auth_header, rate, rep, idle, workdir))

        (workdir / "arm_meta.json").write_text(json.dumps(
            {"repo": arm["repo"], "arm": arm["arm"], "branch": arm["branch"],
             "knee_rps": knee, "ref_p95": (ref.get("window") or {}).get("p95") if ref else None,
             **cold, "cold_idle_rss_kb": idle}))
    finally:
        pro.terminate()
        try:
            pro.wait(timeout=20)
        except subprocess.TimeoutExpired:
            pro.kill()
            pro.wait(timeout=10)


def run_rep(arm, pid, base, route, auth, auth_header, rate, rep, idle, workdir) -> list[list]:
    pre = proc_io(pid)
    sample_f = workdir / "sample.txt"
    side_seconds = (KNEE.WARMUP_MS + KNEE.WINDOW_MS) / 1000
    with open(sample_f, "w") as sf:
        side = subprocess.Popen(
            [PY, str(HERE / "resource_sample.py"), str(pid), str(side_seconds)],
            stdout=sf,
        )
    summary_f = workdir / "cell.json"
    summary_f.unlink(missing_ok=True)
    t0 = time.monotonic()
    s = KNEE.run_cell(K6, base, route, rate, summary_f, auth, auth_header)
    side.wait(timeout=side_seconds + 30)
    tok = time.monotonic() - t0

    rss_kb, hwm_kb, rd_kb, wr_kb = (0, 0, 0, 0)
    if sample_f.exists():
        vals = sample_f.read_text().split()
        if len(vals) == 4:
            rss_kb, hwm_kb, rd_kb, wr_kb = (int(v) for v in vals)
    io_rd = max(rd_kb - pre[0], 0)
    io_wr = max(wr_kb - pre[1], 0)

    base_cols = [arm["repo"], arm["arm"], arm["branch"], rate, rep]
    server_allowed = KNEE.read_allowed(pid)
    if s is None:
        return [base_cols + ["ERRk6", "", "", tok] + [""] * 9 + [server_allowed]]
    cell = s.get("window") or {}
    return [base_cols + [
        cell.get("p50"), cell.get("p95"), cell.get("p99"), tok,
        s.get("achieved_rate"), s.get("load_fidelity"),
        s.get("window_errors") or 0, s.get("window_requests") or 0,
        rss_kb, hwm_kb, idle, io_rd, io_wr,
        server_allowed, s.get("cpus_allowed_k6", ""),
    ]]


def main() -> None:
    if shutil.which(K6) is None:
        raise SystemExit(f"k6 not found on PATH (looked for {K6})")
    plan = load_plan()
    outdir = HERE.parent / "results" / OUTDIR_REL
    outdir.mkdir(parents=True, exist_ok=True)
    selected = sys.argv[1:] or [a["repo"] + "/" + a["arm"] for a in plan["arms"]]
    for arm in plan["arms"]:
        key = arm["repo"] + "/" + arm["arm"]
        if selected and key not in selected and arm["repo"] not in selected:
            continue
        print(f"=== {key} ===", flush=True)
        t0 = time.monotonic()
        try:
            run_arm(arm, outdir)
        except Exception as exc:
            print(f"  FAIL {key}: {exc}", flush=True)
            ROWS.append([arm["repo"], arm["arm"], arm["branch"], "", "",
                         "ERR", "", "", time.monotonic() - t0])
        print(f"  done in {time.monotonic() - t0:.0f}s", flush=True)
    # Merge with existing raw.tsv: keep rows for arms NOT run this
    # invocation (single-arm runs must not wipe other arms' data);
    # replace rows for arms that were re-run.
    raw_f = outdir / "raw.tsv"
    attempted = {(a["repo"], a["arm"]) for a in plan["arms"]
                 if (selected and (a["repo"] + "/" + a["arm"] in selected or a["repo"] in selected))}
    kept = []
    if raw_f.exists():
        for line in raw_f.read_text().splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 2 and (parts[0], parts[1]) not in attempted:
                kept.append(parts)
    with open(raw_f, "w") as f:
        header = [
            "repo", "arm", "branch", "rate", "rep", "p50_ms", "p95_ms", "p99_ms",
            "cell_s", "achieved_rate", "fidelity", "window_errors", "window_requests",
            "rss_max_kb", "hwm_max_kb", "cold_idle_rss_kb", "io_read_kb", "io_write_kb",
            "cpus_allowed_server", "cpus_allowed_k6",
        ]
        f.write("\t".join(header) + "\n")
        for row in kept + ROWS:
            row = list(row) + [""] * (len(header) - len(row))
            f.write("\t".join("" if v is None else str(v) for v in row) + "\n")


if __name__ == "__main__":
    main()