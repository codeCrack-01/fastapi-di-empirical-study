import json, os, subprocess, sys, time
sys.path.insert(0, "/root/study")
import runner

port = 8900
module = os.environ.get("MOD", "apps.s2_depends.sync.app:app")
RATE = int(os.environ.get("RATE", "750"))
N = int(os.environ.get("N", "12"))
CELLS = runner.HERE / "results" / "cells"

wedges, cleans = 0, 0
for i in range(1, N + 1):
    log = CELLS / ("loop%02d.server.log" % i)
    summary = CELLS / ("loop%02d.summary.json" % i)
    for f in (log, summary):
        if f.exists():
            os.unlink(f)
    proc = runner.start_server(module, port, log)
    try:
        env = runner._env()
        env.update({
            "TARGET_URL": "http://127.0.0.1:%d" % port, "SCENARIO": "steady",
            "RATE": str(RATE), "WINDOW_MS": "30000", "WARMUP_MS": "10000",
            "COOLDOWN_MS": "12000", "RAMP_MAX": str(RATE), "RAMP_MS": "8000",
            "SUMMARY_FILE": str(summary),
        })
        cmd = ["taskset", "-c", runner.K6_CORES, "k6", "run", "--quiet", "k6/harness.js"]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(runner.HERE), env=env,
                           capture_output=True, text=True)
        dur = time.time() - t0
        d = json.loads(summary.read_text()) if summary.exists() else {}
        reqs = d.get("window_requests") or 0
        fails = d.get("checkFailures") or 0
        bad = (reqs == 0) or (fails > 0)
        if bad:
            wedges += 1
        else:
            cleans += 1
        print("cell %02d: reqs=%-6s fails=%-4s dur=%.0fs %s" % (
            i, reqs, fails, dur, "<== WEDGE" if bad else "ok"), flush=True)
        if summary.exists():
            os.unlink(summary)
    finally:
        try:
            proc.kill()
        except Exception:
            pass

print("")
print("module=%s rate=%d  clean=%d  wedge=%d  of %d" % (
    module, RATE, cleans, wedges, N), flush=True)
print("DONE", flush=True)
