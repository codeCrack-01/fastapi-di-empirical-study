"""Sampler subprocess — external psutil tick on the uvicorn server PID.

Runs as a separate process (started by run_experiment.py), pinned to its own
core via taskset by the orchestrator. Writes one CSV row per tick (100 ms):

  ts_ms,cpu_percent,usr_pct,sys_pct,rss_mb,vms_mb

Plus a final line with peak RSS from resource.getrusage(RU_MAXRSS).
"""

from __future__ import annotations

import resource
import sys
import time

import psutil

PID = int(sys.argv[1])
OUT = sys.argv[2]
TICK = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1

proc = psutil.Process(PID)
out = open(OUT, "w")
out.write("ts_ms,cpu_percent,usr_pct,sys_pct,rss_mb,vms_mb\n")
out.flush()

t0 = time.monotonic()
rss_peak = 0
try:
    while True:
        try:
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_info()
            cpu_t = proc.cpu_times()
            total = cpu_t.user + cpu_t.system
            usr = (cpu_t.user / total * 100.0) if total else 0.0
            sys_ = (cpu_t.system / total * 100.0) if total else 0.0
            rss = mem.rss / 1024 / 1024
            rss_peak = max(rss_peak, rss)
            out.write(
                f"{int((time.monotonic() - t0) * 1000)},{cpu:.1f},{usr:.1f},{sys_:.1f},{rss:.1f},{mem.vms / 1024 / 1024:.1f}\n"
            )
            out.flush()
        except psutil.NoSuchProcess:
            break
        time.sleep(TICK)
finally:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # kB -> MB
    out.write(f"#peak_rss_mb={max(rss_peak, peak):.1f}\n")
    out.close()