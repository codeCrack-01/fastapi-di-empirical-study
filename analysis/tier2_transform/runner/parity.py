"""parity.py — Phase B preflight validators (run BEFORE any Phase B cell).

  python parity.py parity <app>
      For each arm of <app>: boot it, GET the bench route 3x, record
      (status, sha1(body)); flag any arm whose status/body differs from S2.

  python parity.py lowrate <app> <arm> <rate>
      Boot one arm and run ONE k6 cell at <rate> (full 10/30/10 s windows);
      report window_errors / requests. Used to validate the jhk token fix
      (expect 0 window errors at a low rate).

Output goes to results/v2/preflight/<app>/parity.tsv / lowrate.tsv.
Runs pinned unless TIER2_PIN=0 (same env knobs as bench.py / phaseB.py) — the
parity GETs are single-shot, so pinning is irrelevant for them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import knee as KNEE  # noqa: E402
from bench import K6, boot, load_plan, venv_python, arm_env  # noqa: E402


def http_get(base: str, route: str, auth, header):
    req = urllib.request.Request(base + route, headers={header: auth} if auth else {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def parity(app: str) -> int:
    plan = load_plan()
    arms = [x for x in plan["arms"] if x["repo"] == app]
    repo_dir = HERE.parent / "repos" / app
    out = HERE.parent / "results" / "v2" / "preflight" / app
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    baseline = None
    for arm in arms:
        workdir = out / arm["arm"]
        workdir.mkdir(parents=True, exist_ok=True)
        (workdir / "server.log").unlink(missing_ok=True)
        pro, auth, auth_header = boot(arm, repo_dir, workdir)
        base = f"http://127.0.0.1:{arm['port']}"
        st, body = None, b""
        try:
            for _ in range(3):
                st, body = http_get(base, arm["route"], auth, auth_header)
        finally:
            pro.terminate()
            try:
                pro.wait(timeout=20)
            except subprocess.TimeoutExpired:
                pro.kill()
                pro.wait(timeout=10)
        sha = hashlib.sha1(body).hexdigest()[:12] if st is not None else ""
        row = [app, arm["arm"], st, sha, len(body)]
        if arm["arm"] == "S2":
            baseline = row
        rows.append(row)
        print(f"  {app}/{arm['arm']}: status={st} body_sha1={sha} bytes={len(body)}", flush=True)
    if baseline:
        b_st, b_sha = baseline[2], baseline[3]
        for row in rows:
            row.append("OK" if (row[2] == b_st and row[3] == b_sha) else "DIFF")
    with open(out / "parity.tsv", "w") as f:
        f.write("app\tarm\tstatus\tbody_sha1\tbytes\tequal_to_S2\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print(f"  wrote {out / 'parity.tsv'}", flush=True)
    return 0


def lowrate(app: str, arm_name: str, rate: int) -> int:
    plan = load_plan()
    arm = next(x for x in plan["arms"] if x["repo"] == app and x["arm"] == arm_name)
    repo_dir = HERE.parent / "repos" / app
    out = HERE.parent / "results" / "v2" / "preflight" / app
    out.mkdir(parents=True, exist_ok=True)
    workdir = out / f"lowrate_{arm_name}"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "server.log").unlink(missing_ok=True)
    pro, auth, auth_header = boot(arm, repo_dir, workdir)
    base = f"http://127.0.0.1:{arm['port']}"
    sf = workdir / "cell.json"
    sf.unlink(missing_ok=True)
    try:
        s = KNEE.run_cell(K6, base, arm["route"], float(rate), sf, auth, auth_header)
        server_allowed = KNEE.read_allowed(pro.pid)
    finally:
        pro.terminate()
        try:
            pro.wait(timeout=20)
        except subprocess.TimeoutExpired:
            pro.kill()
            pro.wait(timeout=10)
    win = (s or {}).get("window") or {}
    p50, p95, p99 = win.get("p50"), win.get("p95"), win.get("p99")
    err = (s.get("window_errors") or 0) if s else None
    reqs = (s.get("window_requests") or 0) if s else None
    fid = (s.get("load_fidelity") or 0.0) if s else None
    print(f"  {app}/{arm_name} @{rate} rps: p50={p50} p95={p95} p99={p99} "
          f"errors={err} requests={reqs} err%={100*(err or 0)/max(1,reqs or 1):.2f} fidelity={fid}", flush=True)
    with open(out / "lowrate.tsv", "a") as f:
        if f.tell() == 0:
            f.write("app\tarm\trate\tp50\tp95\tp99\twindow_errors\twindow_requests\tfidelity\tcpus_allowed_server\tcpus_allowed_k6\n")
        f.write("\t".join(str(x) for x in [
            app, arm_name, rate, p50, p95, p99, err, reqs, fid,
            server_allowed, (s or {}).get("cpus_allowed_k6", ""),
        ]) + "\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["parity", "lowrate"])
    ap.add_argument("app")
    ap.add_argument("arm", nargs="?", default=None)
    ap.add_argument("rate", nargs="?", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "parity":
        raise SystemExit(parity(a.app))
    if a.rate is None:
        raise SystemExit("lowrate needs a rate")
    raise SystemExit(lowrate(a.app, a.arm, a.rate))