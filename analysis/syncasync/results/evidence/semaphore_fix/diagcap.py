import json, os, subprocess, sys, threading, time, urllib.request, shutil
sys.path.insert(0, "/root/study")
import runner
port = 8900
RATE = int(sys.argv[1]); tag = sys.argv[2]
samples = []
stop = threading.Event()
def sampler():
    while not stop.is_set():
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/__diag", timeout=2) as r:
                samples.append((round(time.time()-t0,1), json.loads(r.read())))
        except Exception as e:
            samples.append((round(time.time()-t0,1), f"ERR {type(e).__name__}"))
        time.sleep(2)
log = runner.HERE/"results"/"cells"/f"{tag}.server.log"
summary = runner.HERE/"results"/"cells"/f"{tag}.summary.json"
proc = runner.start_server("diag_app:app", port, log)
try:
    env = runner._env()
    env.update({"TARGET_URL": f"http://127.0.0.1:{port}", "SCENARIO": "steady",
                "RATE": str(RATE), "WINDOW_MS": "30000", "WARMUP_MS": "10000",
                "COOLDOWN_MS": "12000", "RAMP_MAX": str(RATE), "RAMP_MS": "8000",
                "SUMMARY_FILE": str(summary)})
    cmd = ["taskset","-c",runner.K6_CORES,"k6","run","--quiet","k6/harness.js"]
    t0 = time.time()
    th = threading.Thread(target=sampler, daemon=True); th.start()
    subprocess.run(cmd, cwd=str(runner.HERE), env=env, capture_output=True, text=True)
    stop.set(); th.join(timeout=5)
    d = json.loads(summary.read_text()) if summary.exists() else {}
    print(json.dumps({"tag":tag,"rate":RATE,
        "window_requests":d.get("window_requests"),"window_errors":d.get("window_errors"),
        "checkFailures":d.get("checkFailures"),"window_p95":(d.get("window") or {}).get("p95"),
        "achieved":d.get("achieved") or (d.get("window") or {}).get("mean"),"cpu_seconds":d.get("cpu_seconds"),
        "diag_samples":len(samples)}, indent=2))
    good=[s for _,s in samples if isinstance(s,dict)]
    if good:
        print("  pool_free   min/max:", min(g['pool_free'] for g in good), "/", max(g['pool_free'] for g in good))
        print("  borrowed    min/max:", min(g['borrowed_tokens'] for g in good), "/", max(g['borrowed_tokens'] for g in good))
        print("  total_tokens        :", sorted({g['total_tokens'] for g in good}))
        print("  os_threads   min/max:", min(g['os_threads'] for g in good), "/", max(g['os_threads'] for g in good))
        print("  err samples         :", sum(1 for _,s in samples if not isinstance(s,dict)))
    print("  trace:", json.dumps([s for _,s in samples][::max(1,len(samples)//8)][:9]))
    summary.unlink(missing_ok=True)
finally:
    try: proc.kill()
    except Exception: pass
