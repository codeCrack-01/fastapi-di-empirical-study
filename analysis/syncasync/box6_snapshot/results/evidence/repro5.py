import json, os, subprocess, sys, time, shutil, signal, threading
import urllib.request, urllib.error
sys.path.insert(0, "/root/study")
os.environ["PYTHONFAULTHANDLER"] = "1"
import runner

port = 8900
module = "diag_app:app"          # wrapper that adds /__diag
RATE = int(os.environ.get("R", "750"))


def probe(path="/health", timeout=4):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return f"HTTP{e.code}"
    except Exception as e:
        return f"ERR {type(e).__name__}"


def diag(timeout=4):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/__diag", timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return f"HTTP{e.code}"
    except Exception as e:
        return f"ERR {type(e).__name__}"


for i in range(1, 21):
    tag = f"hx{i:02d}"
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
        p = subprocess.run(cmd, cwd=str(runner.HERE), env=env,
                           capture_output=True, text=True)
        data = json.loads(summary.read_text()) if summary.exists() else {}
        reqs = data.get("window_requests") or 0
        fails = data.get("checkFailures") or 0
        hung = (reqs == 0 or fails > 0)
        print(f"[{i:02d}] reqs={reqs:>6} fails={fails:>4} health={probe()} "
              f"diag={diag()}{'  <== HUNG' if hung else ''}", flush=True)
        summary.unlink(missing_ok=True)
        if hung:
            print("=== hung; probing again, then SIGABRT for thread dump ===", flush=True)
            print(f"    health={probe(timeout=8)}", flush=True)
            print(f"    diag  ={diag(timeout=8)}", flush=True)
            time.sleep(1)
            os.kill(proc.pid, signal.SIGABRT)
            time.sleep(4)
            txt = log.read_text() if log.exists() else ""
            # count where threads are parked
            import re, collections
            frames = re.findall(r'File "([^"]+)", line \d+ in (\S+)', txt)
            top = collections.Counter(f"{f[0].split('/')[-1]}:{f[1]}" for f in frames)
            print(f"--- server log {len(txt)} bytes; top frames ---", flush=True)
            for k, v in top.most_common(12):
                print(f"    {v:>3}x {k}", flush=True)
            print("--- queue.get / limiter lines ---", flush=True)
            for line in txt.splitlines():
                if "queue" in line or "threadlimiter" in line or "sync_conn" in line \
                   or "get_db" in line:
                    print("   ", line.strip()[:150], flush=True)
            break
    finally:
        try:
            proc.kill()
        except Exception:
            pass
print("DONE", flush=True)
