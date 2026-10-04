"""Distinguish LEAK from STUCK under real concurrent load.

Runs k6 at the measured rate against the instrumented server while polling
/__diag once a second. Watches what happens as the pool drains:
  - pool_free -> 0 and in_body -> 0  => connections ORPHANED (leak)
  - pool_free -> 0 and in_body -> 8  => connections still HELD (stuck)
  - diag stops answering            => event loop wedged too
"""
import json, os, subprocess, sys, threading, time
import urllib.request, urllib.error

sys.path.insert(0, "/root/study")
import runner

port = 8900
rate = int(os.environ.get("RATE", "750"))
stop = threading.Event()
samples = []


def poll():
    while not stop.is_set():
        t0 = time.time()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/__diag", timeout=2) as r:
                d = json.loads(r.read())
            samples.append((round(time.time() - t0, 3), d))
        except Exception as e:
            samples.append((round(time.time() - t0, 3), {"ERR": type(e).__name__}))
        stop.wait(1.0)


th = threading.Thread(target=poll, daemon=True)
th.start()
time.sleep(2)

env = runner._env()
env.update({
    "TARGET_URL": f"http://127.0.0.1:{port}", "SCENARIO": "steady",
    "RATE": str(rate), "WINDOW_MS": "30000", "WARMUP_MS": "10000",
    "COOLDOWN_MS": "12000", "RAMP_MAX": str(rate), "RAMP_MS": "8000",
    "SUMMARY_FILE": "/tmp/polled.summary.json",
})
cmd = ["taskset", "-c", runner.K6_CORES, "k6", "run", "--quiet", "k6/harness.js"]
p = subprocess.run(cmd, cwd=str(runner.HERE), env=env, capture_output=True, text=True)
stop.set()
th.join(timeout=3)

data = json.loads(open("/tmp/polled.summary.json").read()) if os.path.exists("/tmp/polled.summary.json") else {}
print(f"k6 rc={p.returncode} window_requests={data.get('window_requests')} "
      f"checkFailures={data.get('checkFailures')}")
print()
print(f"{'t(s)':>6} {'resp_s':>7} {'free':>5} {'in_body':>8} {'unret':>6} {'max':>5}")
print("-" * 46)
for t, d in samples:
    if "ERR" in d:
        print(f"{'':>6} {t:>7}  <-- {d['ERR']}")
    else:
        print(f"{'':>6} {t:>7} {d['pool_free']:>5} {d['in_body_now']:>8} "
              f"{d['unreturned']:>6} {d['max_in_body']:>5}")
errs = [s for s in samples if "ERR" in s[1]]
print()
print(f"samples={len(samples)}  diag_failures={len(errs)}")
if samples:
    last = samples[-1][1]
    print("final:", json.dumps(last))
