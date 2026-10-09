"""Sample the MAX sustained RSS + VmHWM + cumulative disk I/O of a server pid.

Samples /proc/<pid>/status (VmRSS, VmHWM) every 0.25s for <seconds> and reports
the maximum of both plus cumulative read_bytes/write_bytes from /proc/<pid>/io
(a monotonic counter). Output: "<rss_kb> <hwm_kb> <read_kb> <write_kb>".

Usage: python runner/resource_sample.py <pid> <seconds>
"""

import sys
import time
from pathlib import Path


def snapshot(pid: int) -> tuple[int, int, int, int]:
    rss = hwm = ri = wi = 0
    status = Path(f"/proc/{pid}/status")
    if status.exists():
        for line in status.read_text().splitlines():
            if line.startswith("VmRSS:"):
                rss = int(line.split()[1])
            elif line.startswith("VmHWM:"):
                hwm = int(line.split()[1])
    io = Path(f"/proc/{pid}/io")
    if io.exists():
        for line in io.read_text().splitlines():
            if line.startswith("read_bytes:"):
                ri = int(line.split()[1]) // 1024
            elif line.startswith("write_bytes:"):
                wi = int(line.split()[1]) // 1024
    return rss, hwm, ri, wi


def main() -> None:
    pid = int(sys.argv[1])
    seconds = float(sys.argv[2])
    end = time.time() + seconds
    best = (0, 0, 0, 0)
    while time.time() < end:
        best = tuple(max(a, b) for a, b in zip(best, snapshot(pid)))
        time.sleep(0.25)
        if not Path(f"/proc/{pid}/status").exists():
            break
    print(f"{best[0]} {best[1]} {best[2]} {best[3]}")


if __name__ == "__main__":
    main()