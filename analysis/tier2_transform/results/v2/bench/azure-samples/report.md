# azure-samples — Tier-2 Phase B, Protocol v1 (fresh boot per cell, randomised)

PRELIMINARY. Direction-only; not comparable in absolute terms to other hosts.
App: azure-samples (measured via repo's own `create_app`; route `GET /api/health`).
Per plan (pyproject-only DI transform for arm_s4, health route untouched by the
transform diff), **S1–S3 only** — S4 not run. Box `voc-c-8c-16gb-150s-amd` (8
vCPU/16 GB, ord), instance `e8cd6321-daa8-4f44-9ad6-da6adedc114a`. Pinned:
uvicorn `taskset -c 0,2,4` (`--workers 1`), k6 `taskset -c 6` (all cells
`0,2,4`/`6`). Online set `0,2,4,6`.

Protocol: fresh server per cell (boot age 1.5 s), randomised order (seed
20261009). S2 knee reused = **2560 rps** (`--knee`). Grid =
2560 x {0.75,1.0,1.25,1.5} = 1920/2560/3200/3840 rps (K3/K5/K5/K5).
Raw: `raw.tsv` (54 rows, 0 `ERR*`).

## Per-cell results, p50/p95/p99 ms median [min–max]

| arm | 1920 (K3) | 2560 (K5) | 3200 (K5) | 3840 (K5) |
|---|---|---|---|---|
| S1 | 0[0-0]/1[1-1]/3[3-3] | 0[0-0]/1[1-1]/4[3-4] | 0[0-0]/1[1-1]/4[4-4] | 0[0-0]/2[2-2]/6[6-7] |
| S2 | 1[1-1]/1[1-1]/5[5-6] | 1[1-1]/1[1-1]/3[3-5] | 0[0-0]/1[1-1]/3[2-3] | 0[0-1]/2[2-4]/7[4-16] |
| S3 | 1[1-1]/2[2-3]/91[60-93] | 1[1-1]/2[2-3]/81[65-101] | 1[1-1]/5[3-7]/123[79-156] | 2[2-3]/36[26-106]/190[174-224] |

Fidelity: S1 = 1.000 everywhere. S2 = 0.998 (achieved 3833 of 3840 at the top).
S3 fid 0.989/0.974/0.951/0.945 (achieved 3628 of 3840 at 3840). `window_errors`
= 0 everywhere. S3 stays load-absorbing but shows rising tail latency and a
small achieved shortfall at 3840; S1/S2 are flat.

## 2560 per-rep distribution

- S3@2560 p95 reps = **[2, 2, 2, 2, 3]** ms — effectively constant, unimodal.
  Report p95 = 2 [2–3] ms. No knee bracket needed.

## Reading (no cost claims)

Neutral only: S1 and S2 flat through the top rate (p95 ≤ 2 ms). S3 keeps p95 ≤ 5
ms through 3200 and rises to 36 [26–106] ms at 3840 with a 5.5% achieved
shortfall; its p99 is ~60–224 ms across the grid. No claim is made here that
this reflects middleware cost.

## Per-cell diagnostics

`time_since_boot_s` (server process age at cell start) = 1.50–1.51 s.
`timewait_start` median 215, max 603 (no accumulation). Affinity `0,2,4`/`6` on
every cell.