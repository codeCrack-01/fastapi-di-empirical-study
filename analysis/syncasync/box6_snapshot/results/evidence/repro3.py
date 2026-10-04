import json, os, subprocess, sys, time, shutil
sys.path.insert(0, "/root/study")
import runner

port = 8900
module = "apps.s2_depends.sync.app:app"
RATE = 750
N = 10

def run_one(i):
    tag = f"p2repro{i:02d}"
    log = runner.HERE / "results" / "cells" / f"{tag}.server.log"
    summary = runner.HERE / "results" / "cells" / f"{tag}.summary.json"
    proc = runner.start_server(module, port, log)
    try:
        env = runner._env()
        env.update({
            "TARGET_URL": f"http://127.0.0.1:{port}", "SCENARIO": "steady",
            "RATE": str(RATE), "WINDOW_MS": "30000", "WARMUP_MS": "10000",
            "COOLDOWN_MS": "12000", "RAMP_MAX": str(RATE), "RAMP_MS": "8000",
            "SUMMARY_FILE": str(summary),
        })
        cmd = (["taskset", "-c", runner.K6_CORES] if shutil.which("taskset") else []) \
              + ["k6", "run", "--quiet", "k6/harness.js"]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(runner.HERE), env=env,
                           capture_output=True, text=True)
        dur = time.time() - t0
        data = json.loads(summary.read_text()) if summary.exists() else {}
        w = data.get("window") or {}
        reqs = data.get("window_requests") or 0
        fails = data.get("checkFailures") or 0
        bad = (reqs == 0) or (fails > 0)
        print(f"[{i:02d}] dur={dur:5.1f}s reqs={reqs:>6} iters={data.get('iterations')!s:>6} "
              f"fails={fails:>4} p95={w.get('p95')} rc={p.returncode} "
              f"srlog={log.stat().st_size}B {'<== ANOMALY' if bad else ''}", flush=True)
        if bad:
            print("      --- k6 stdout ---", flush=True)
            for line in (p.stdout or "").splitlines()[:40]:
                print("      " + line[:180], flush=True)
            print("      --- k6 stderr ---", flush=True)
            for line in (p.stderr or "").splitlines()[:15]:
                print("      " + line[:180], flush=True)
            print("      --- server log ---", flush=True)
            txt = log.read_text() if log.exists() else "<none>"
            print("      " + (txt[-1500:] if txt.strip() else "<EMPTY>"), flush=True)
            # probe the still-running server
            import urllib.request, urllib.error
            for path, hdr in [("/health", {}), ("/reviews/1", {}),
                              ("/users/me", {"Authorization": "Bearer user-token"}),
                              ("/admin/dashboard", {"Authorization": "Bearer admin-token"}),
                              ("/admin/dashboard", {"Authorization": "Bearer definitely-not-a-token"})]:
                req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers=hdr)
                try:
                    with urllib.request.urlopen(req, timeout=5) as r:
                        print(f"      PROBE {path:<20} {r.status}", flush=True)
                except urllib.error.HTTPError as e:
                    print(f"      PROBE {path:<20} HTTP {e.code}", flush=True)
                except Exception as e:
                    print(f"      PROBE {path:<20} ERR {type(e).__name__}: {e}", flush=True)
        summary.unlink(missing_ok=True)
        return reqs, fails
    finally:
        runner.stop_server(proc)

bad_count = 0
for i in range(1, N + 1):
    reqs, fails = run_one(i)
    if reqs == 0 or fails > 0:
        bad_count += 1
print(f"DONE: {bad_count}/{N} anomalous", flush=True)
