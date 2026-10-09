# ciiceronee — Tier-2 Phase B, Protocol v1 (fresh boot per cell, randomised)

PRELIMINARY. Direction-only; not comparable in absolute terms to other hosts.
App: ciiceronee (FastAPI). Box `voc-c-8c-16gb-150s-amd` (8 vCPU/16 GB, ord),
instance `e8cd6321-daa8-4f44-9ad6-da6adedc114a`. Pinned: uvicorn `taskset -c
0,2,4` (`--workers 1`), k6 `taskset -c 6`; all cells recorded server `0,2,4`,
k6 `6`. Online set `0,2,4,6`.

Protocol: server process restarted for every grid cell, cells presented in
randomised order (seed 20261009). S2 knee reused = **2560 rps** (`--knee`,
measured 3-probe in the archived ascending run; ref_p95 = 2 ms). Grid =
S2knee x {0.75:K3, 1.0:K5, 1.25:K5, 1.5:K5} = 1920/2560/3200/3840 rps.
Raw: `raw.tsv` (72 rows, 0 `ERR*`). The earlier single-boot ascending grid is
preserved untouched at `results/v2/ascending_order_v0/ciiceronee/` and labelled
"single boot, ascending rate; confounded".

## Per-cell results (72 cells), p50/p95/p99 ms median [min–max]

| arm | 1920 (K3) | 2560 (K5) | 3200 (K5) | 3840 (K5) |
|---|---|---|---|---|
| S1 | 0[0-0]/1[1-1]/3[3-3] | 0[0-0]/1[1-1]/3[3-3] | 0[0-1]/1[1-1]/4[4-5] | 0[0-0]/3[1-3]/8[5-10] |
| S2 | 1[1-1]/1[1-1]/5[5-6] | 1[1-1]/1[1-1]/2[2-3] | 0[0-0]/1[1-2]/5[4-11] | 171[164-184]/214[210-259]/221[218-267] |
| S3 | 1[1-1]/5[2-6]/35[16-36] | 1[1-1]/12[9-20]/34[30-43] | 175[1-238]/290[9-338]/327[34-392] | 234[185-241]/330[255-340]/360[268-436] |
| S4 * | 1[1-1]/2[2-2]/18[17-23] | 1[1-2]/27[21-59]/39[33-85] | 236[232-238]/289[278-317]/300[291-331] | 240[232-244]/280[276-305]/292[286-332] |

\* **S4 = container instantiated per call, as transformed.**

Fidelity (achieved/offered): S1 = 1.000 at every cell. S2 = 1.000 through 3200;
at 3840 fid min 0.768 (achieved 2951 of 3840). S3 fid min 0.674 at 3200
(achieved 2158) and 0.568 at 3840 (2181). S4 fid min 0.754 at 3200 (achieved
2412) and 0.618 at 3840 (2374). `window_errors` = 0 everywhere. So the 3200/3840
cells for S2/S3/S4 are **load-limited** (achieved rate saturates, p50 itself
jumps to ~170–240 ms); their latency reflects the achieved rate, not the offered.

## 2560 per-rep distribution (S3, S4)

- S3@2560 p95 reps = **[9, 10, 12, 17, 20]** ms — largest gap 5 (12→17) ⇒
  **unimodal**; NOT a collapse. Report p95 = 12 [9–20] ms; no knee bracket.
- S4@2560 p95 reps = **[21, 26, 27, 30, 59]** ms — largest gap 29 (30→59), a
  single high outlier around an otherwise ~21–30 ms cluster ⇒ **unimodal**.

Contrast with the archived ascending run, where S3@2560 med = 288 ms (fid 0.84)
and S4@2560 med = 338 ms (fid 0.80): that was a single-boot, ascending-order
artifact. Under fresh boots the S3/S4 "collapse at 2560" disappears.

## Reading the transition (no cost claims)

Neutral statement only: S1 showed no latency rise through 3840. Degradation
onset was 3840 for S2 and 3200 for S3 and S4, all with achieved < offered. No
claim is made here that the S3/S4 onset reflects middleware or container cost.

## Per-cell diagnostics

`timewait_start`: median 786, max 1419 (no runaway accumulation under fresh
boots). `cpus_allowed_server`/`cpus_allowed_k6` = `0,2,4`/`6` for all cells.
Caveat: in this one run the `time_since_boot_s` column holds cell duration
(≈50.2 s), not process age (measurement bug fixed afterwards in commit
`6c9defa`); it is not used. The TIME_WAIT and affinity columns are correct.
