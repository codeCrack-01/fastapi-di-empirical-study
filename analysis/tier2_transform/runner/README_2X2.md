# 2x2 Mechanism Experiment — Run Instructions

## Prerequisites
- Linux (WSL2 on Windows 11 is fine; native Linux preferred)
- Python 3.12+ with venv (ciiceronee repo has .venv)
- k6 on PATH
- uvicorn installed in the venv
- A dedicated machine (no other users, no background apps)

## Arms (git branches in the ciiceronee repo)
| Arm | Branch | Description |
|---|---|---|
| sync-inline | arm_s1 | sync getter, called inline (no Depends) |
| sync-depends | master | sync getter, via Depends() |
| async-inline | arm_2x2_async_inline | async getter, called inline |
| async-depends | arm_2x2_async_depends | async getter, via Depends() |
| wrapper | arm_2x2_wrapper | sync getter via anyio.to_thread.run_sync |
| limiter-200 | arm_2x2_limiter_200 | sync-depends, threadpool limiter = 200 |
| limiter-1000 | arm_2x2_limiter_1000 | sync-depends, threadpool limiter = 1000 |
| limiter-4000 | arm_2x2_limiter_4000 | sync-depends, threadpool limiter = 4000 |

## Pre-flight checklist
1. Set power plan to "High performance" (or "Ultimate Performance").
2. Disable Windows Defender real-time protection.
3. Pause Windows Update.
4. Close all apps (browser, Teams, etc.).
5. Check core layout: `lscpu` (Linux) or PowerShell `Get-CimInstance Win32_Processor | Select NumberOfCores,NumberOfLogicalProcessors`.
   - Confirm cores 0, 2, 4 are not hyperthread siblings of core 6.
6. Verify k6 and uvicorn are on PATH.

## Smoke test (single cell, ~1 min)
```bash
cd /path/to/ciiceronee
git checkout master
cd /path/to/runner
TIER2_FAST=1 CIICERONEE_REPO=/path/to/ciiceronee HARNESS=/path/to/runner/k6/harness_t2.js \
  python3 run_2x2.py --arm sync-depends --rate 1000 --reps 1 --port 8799 --out /tmp/smoke.tsv
```
Expected: p99_window ~10-15ms, fidelity ~1.0, dropped=0.

## Full grid (~6 hours)
```bash
cd /path/to/runner
CIICERONEE_REPO=/path/to/ciiceronee HARNESS=/path/to/runner/k6/harness_t2.js \
  python3 run_2x2.py --grid --port 8799 --out /path/to/results_2x2.tsv
```
This runs all 8 arms at rates 2500, 3000, 3200 (3 reps each in TIER2_FAST=1; 10 reps each in normal mode).

## After the run
1. Copy raw results + TSV off the machine immediately.
2. Compute SHA-256 checksums: `sha256sum results_2x2.tsv > manifest.txt`.
3. Verify checksums locally before terminating the session.
4. Do NOT destroy the machine until checksums are verified.

## Key measurement
The threadpool limiter check: compare sync-depends (default limiter) vs limiter-200/1000/4000.
- If the gap shrinks with higher limiter → pool exhaustion.
- If it doesn't → per-call handoff overhead.
- If neither → unresolved.
PY
echo "done"