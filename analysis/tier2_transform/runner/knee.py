"""knee.py — tier-2 knee measurement (open-loop k6, tier-1 qualification).

Same pre-registered criterion as the tier-1 syncasync knee:

    reference : 30 s steady window at 10 req/s -> p95_ref
    knee      : highest offered rate r such that, at r,
                    p95 <= 3 * p95_ref
                    error rate <= 1%
                    achieved / offered >= 0.98

Tier-1 located the knee with a geometric ramp + binary search and took the
median of 3 probes. Tier-2 uses the SAME qualifier but discovers the knee by
ASCENDING steady windows at the geometric ladder {20,40,80,...}: the last rate
that qualifies. A single probe is used (knee is discovery; the measured grid
cells carry the K repetitions), with the divergence noted in the writeup.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

RUNNER = Path(__file__).resolve().parent
HARNESS = RUNNER / "k6" / "harness_t2.js"

# Load generator pinning (tier-1 layout: k6 on physical core 6). Disable with
# TIER2_K6_CORES="" or TIER2_PIN=0 (the S3@2560 pinned-vs-unpinned probe).
K6_CORES = os.environ.get("TIER2_K6_CORES", "6")
if os.environ.get("TIER2_PIN", "1") == "0":
    K6_CORES = ""


def read_allowed(pid: int) -> str:
    """Return the process's /proc/<pid>/status Cpus_allowed_list (evidence that
    pinning is actually in force), or '' if the pid is gone."""
    st = Path(f"/proc/{pid}/status")
    if not st.exists():
        return ""
    for line in st.read_text().splitlines():
        if line.startswith("Cpus_allowed_list:"):
            return line.split(":", 1)[1].strip()
    return ""

REF_RPS = 10.0
P95_MULT = 3.0
MAX_ERR = 0.01
MIN_ACHIEVED = 0.98
LADDER = [20, 40, 80, 160, 320, 640, 1280, 2560, 5120]

# grid anchors expressed as fractions of the arm's knee
GRID = [0.25, 0.5, 0.75, 1.0, 1.25]
# repeat count per anchor: the two upper anchors get K=5 (that is where arms
# separate), the three lower ones K=3.
REPS = {0.25: 3, 0.5: 3, 0.75: 3, 1.0: 5, 1.25: 5}

WINDOW_MS = 30000
WARMUP_MS = 10000
COOLDOWN_MS = 10000
TIMEOUT_S = 90

if os.environ.get("TIER2_FAST") == "1":
    # pipeline smoke only (local harness validation): tiny windows, 1 rep
    WINDOW_MS, WARMUP_MS, COOLDOWN_MS = 5000, 1000, 1000
    TIMEOUT_S = 30
    LADDER = [10, 40, 160]
    REPS = {a: 1 for a in GRID}


def run_cell(
    k6: str,
    base_url: str,
    path: str,
    rate: float,
    summary_file: Path,
    auth: str | None = None,
    auth_header: str = "Authorization",
) -> dict | None:
    """Run one open-loop steady cell; return harness summary dict or None.

    The summary is augmented with `cpus_allowed_k6` (the load generator's
    /proc/<pid>/status Cpus_allowed_list), recorded just after spawn so the
    pinning is evidenced per cell. k6 is confined to K6_CORES when set.

    The read waits briefly first: `taskset -c 6 k6 ...` spawns as the taskset
    pid, which calls sched_setaffinity then execs k6 in the SAME pid. Reading
    before that exec returns the wrapper's inherited affinity (e.g. 0,2,4,6),
    not the confined one (6).
    """
    cmd = [k6, "run", "--quiet", str(HARNESS)]
    if K6_CORES:
        cmd = ["taskset", "-c", K6_CORES] + cmd
    cmd += [
        "-e",
        f"TARGET_URL={base_url}",
        "-e",
        f"TARGET_PATH={path}",
        "-e",
        f"RATE={rate:.0f}",
        "-e",
        f"WINDOW_MS={WINDOW_MS}",
        "-e",
        f"WARMUP_MS={WARMUP_MS}",
        "-e",
        f"COOLDOWN_MS={COOLDOWN_MS}",
        "-e",
        f"SUMMARY_FILE={summary_file}",
    ]
    if auth:
        cmd += ["-e", f"AUTH_HEADER={auth_header}", "-e", f"AUTH_BEARER={auth}"]
    opp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.5)  # let taskset exec k6 so /proc shows the confined set
    allowed = read_allowed(opp.pid)
    try:
        _, _ = opp.communicate(timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        opp.kill()
        opp.communicate()
        return None
    if opp.returncode != 0:
        return None
    if not summary_file.exists():
        return None
    summary = json.loads(summary_file.read_text())
    summary["cpus_allowed_k6"] = allowed
    return summary


def find_knee(
    k6: str,
    base_url: str,
    path: str,
    auth: str | None = None,
    workdir: Path | None = None,
    auth_header: str = "Authorization",
) -> tuple[float, dict]:
    """Return (knee_rps, ref_summary). Reference cell at REF_RPS then ladder."""
    workdir = workdir or Path.cwd()
    ref = run_cell(k6, base_url, path, REF_RPS, workdir / "knee_ref.json", auth, auth_header)
    if not ref:
        return REF_RPS, {}
    ref_p95 = (ref.get("window") or {}).get("p95") or 0.0
    knee = REF_RPS
    for rate in LADDER:
        cell = run_cell(k6, base_url, path, rate, workdir / "knee_cell.json", auth, auth_header)
        if not cell:
            break
        win = cell.get("window") or {}
        p95 = win.get("p95") or 0.0
        err = (cell.get("window_errors") or 0) / max(1, cell.get("window_requests") or 1)
        fid = cell.get("load_fidelity") or 0.0
        if p95 > P95_MULT * max(ref_p95, 0.001) or err > MAX_ERR or fid < MIN_ACHIEVED:
            break
        knee = rate
        time.sleep(0.5)
    return knee, ref