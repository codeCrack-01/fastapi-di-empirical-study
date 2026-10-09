# ciiceronee — Tier-2 Phase B first-run report (STAGED, awaiting go-ahead)

Status: **ciiceronee complete; remaining apps not started (gated on user
go-ahead).** All numbers preliminary / direction-only, not comparable in
absolute terms to other hosts.

- App: ciiceronee (FastAPI; `from fastapi import FastAPI...`, `ciicerone/api/main.py`)
- Box: `voc-c-8c-16gb-150s-amd` (8 vCPU/16 GB, ord), instance
  `e8cd6321-daa8-4f44-9ad6-da6adedc114a`
- Pinning: uvicorn `taskset -c 0,2,4` (--workers 1), k6 `taskset -c 6`; every
  cell's `/proc/<pid>/status Cpus_allowed_list` recorded (all cells show
  server `0,2,4`, k6 `6`). Online core set `0,2,4,6` (nproc 4).
- Runner commit: `5fb1d8f`. Raw: `results/v2/bench/ciiceronee/raw.tsv` (102 rows,
  0 `ERRk6`), `knee.json`, `probe2560_*_raw.tsv`.

## S2 knee (3 probes per rung, median qualifier)

ref_p95 (median of 3 @ 10 rps) = **2.00 ms**. Rungs 20,40,80,160,320,640,1280,
2560 all qualified; rung 5120 failed → **S2 knee = 2560 rps**. 27 knee-stage
cells + 3 ref cells.

## Matched absolute-rate grid @ S2knee=2560 (K=3/5/5/5)

p95 ms, median [min–max] across reps (server 0,2,4 / k6 6):

| arm | 1920 (K3) | 2560 (K5) | 3200 (K5) | 3840 (K5) |
|---|---|---|---|---|
| S1 | 1 [1–1] | 1 [1–1] | 1 [1–1] | 5 [2–7] |
| S2 | 1 [1–1] | 1 [1–1] | 2 [1–3] | 208 [39–219] |
| S3 | 11 [9–12] | 288 [60–326] | 261 [239–395] | 253 [240–262] |
| S4 | 2 [2–3] | 338 [327–354] | 340 [317–350] | 311 [299–348] |

Total `window_errors` = 0 across all 102 rows. **Load-fidelity caveat** (achieved
k6 rate / offered): S1 = 1.00 at all cells. S2 = 1.00 up to 3200, but at 3840
fid min 0.860 (achieved 3303 of 3840). S3 = 0.999 @1920, 0.844 @2560 (achieved
2160), 0.581 @3200 (1859), 0.512 @3840 (1966). S4 = 1.00 @1920, 0.799 @2560
(2047), 0.669 @3200 (2139), 0.566 @3840 (2172). So S3/S4 high-rate cells are
**load-limited** (the app saturates ~2.0–2.2k rps); their p95 reflects the
achieved rate, not the offered one.

## S3 @2560, pinned vs unpinned (fresh boot each; n=1)

| condition | server cpus | k6 cpus | p50 | p95 | p99 | fidelity | achieved |
|---|---|---|---|---|---|---|---|
| pinned | 0,2,4 | 6 | 1 | **10** | 33 | 0.99991 | 2559.8 |
| unpinned | 0,2,4,6 | 0,2,4,6 | 1 | **4** | 30 | 0.99992 | 2559.8 |

Both offer/achieve 2560 rps with 0 errors; unpinned p95 is lower here (2.5×).
n=1 each — direction only.

## Open issue to flag before continuing

The grid's S3@2560 cells (p95 med 288, fid 0.844, achieved ~2160) disagree
sharply with the **standalone** S3@2560 probe on a fresh boot (p95 10, fid
0.9999, achieved 2560) — same rate, same pinning. Hypothesis: within one arm's
18-cell single-boot sequence, client/server socket churn (TIME_WAIT / ephemeral
port accumulation) depresses the achieved rate on later high-rate cells, so
"cell N" is confounded with boot age. This also affects S4. The isolated probes
are clean. Options: fresh boot per high-rate cell, or interleave arms. Decision
needed before running the other three apps.

## Run-time accounting

Wall time: ciiceronee main design (30 knee + 72 grid + boots) ≈ 88 min;
2 probe2560 cells ≈ 4 min. Full 4-app estimate remains ≈ 5.7–6.0 h (above the
4 h cap; grids alone = 4.0 h).
