import json, os, subprocess, sys, time, shutil
sys.path.insert(0, "/root/study")
import runner

# Replicate run_k6 EXACTLY, but keep stdout (run_k6 discards it) so we can see
# what k6 actually did. Server start/pin/env all come from runner itself.
port = 8900
module = "apps.p2_depends.sync.app:app"
RATE = int(os.environ.get("REPRO_RATE", "750"))

for attempt in range(1, 4):
    tag = f"repro{attempt}"
    log = runner.HERE / "results" / "cells" / f"{tag}.server.log"
    summary = runner.HERE / "results" / "cells" / f"{tag}.summary.json"
    proc = runner.start_server(module, port, log)
    try:
        env = runner._env()
        env.update({
            "TARGET_URL": f"http://127.0.0.1:{port}",
            "SCENARIO": "steady",
            "RATE": str(RATE),
            "WINDOW_MS": "30000",
            "WARMUP_MS": "10000",
            "COOLDOWN_MS": "12000",
            "RAMP_MAX": str(RATE),
            "RAMP_MS": "8000",
            "SUMMARY_FILE": str(summary),
        })
        cmd = []
        if shutil.which("taskset"):
            cmd += ["taskset", "-c", runner.K6_CORES]
        cmd += ["k6", "run", "--quiet", "k6/harness.js"]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(runner.HERE), env=env,
                           capture_output=True, text=True)
        dur = time.time() - t0
        data = json.loads(summary.read_text()) if summary.exists() else {}
        w = data.get('window') or {}
        print(f"--- attempt {attempt}: rc={p.returncode} dur={dur:.1f}s")
        print(f"    window_requests={data.get('window_requests')} "
              f"window_errors={data.get('window_errors')} "
              f"checks={data.get('checks')} "
              f"checkFailures={data.get('checkFailures')} "
              f"iterations={data.get('iterations')}")
        print(f"    httpErrors={data.get('httpErrors')} "
              f"p50={w.get('p50')} p95={w.get('p95')}")
        if p.returncode != 0:
            print("    STDERR:", (p.stderr or "")[:400])
        print(f"    warmup={data.get('warmup')} window={w} cooldown={data.get('cooldown')}")
        print("    SERVER LOG:", (log.read_text()[-400:] if log.exists() else "<none>").replace(chr(10),' | ')[:400])
        # non-JSON lines k6 printed to stdout (e.g. log lines, warnings)
        for line in (p.stdout or "").splitlines():
            if not line.strip().startswith("{"):
                print("    STDOUT:", line[:200])
        summary.unlink(missing_ok=True)
    finally:
        runner.stop_server(proc)
