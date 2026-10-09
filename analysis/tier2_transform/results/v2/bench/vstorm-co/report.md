# vstorm-co — Tier-2 Phase B, Protocol v1 (fresh boot per cell, randomised)

PRELIMINARY. Direction-only; not comparable in absolute terms to other hosts.
App: vstorm-co (measured via repo's own `pydantic_ai_backends.remote.server.
create_app`; route `GET /sessions`). Box `voc-c-8c-16gb-150s-amd` (8 vCPU/16 GB,
ord), instance `e8cd6321-daa8-4f44-9ad6-da6adedc114a`. Pinned: uvicorn
`taskset -c 0,2,4` (`--workers 1`), k6 `taskset -c 6` (all cells recorded
`0,2,4`/`6`). Online set `0,2,4,6`.

Protocol: fresh server per grid cell, randomised order (seed 20261009). S2 knee
reused = **1280 rps** (`--knee`, 3-probe ascending measurement). Grid =
1280 x {0.75:K3, 1.0:K5, 1.25:K5, 1.5:K5} = 960/1280/1600/1920 rps.
Raw: `raw.tsv` (72 rows, 0 `ERR*`).

## Per-cell results, p50/p95/p99 ms median [min–max]

| arm | 960 (K3) | 1280 (K5) | 1600 (K5) | 1920 (K5) |
|---|---|---|---|---|
| S1 | 0[0-0]/1[1-1]/2[2-2] | 0[0-0]/1[1-1]/3[3-3] | 0[0-0]/1[1-1]/3[3-3] | 1[0-1]/1[1-1]/3[3-4] |
| S2 | 1[1-1]/1[1-1]/5[4-6] | 1[1-1]/1[1-1]/5[4-6] | 1[1-1]/1[1-2]/3[2-3] | 1[1-1]/2[2-3]/4[3-8] |
| S3 | 1[1-1]/1[1-1]/4[4-4] | 1[1-1]/1[1-1]/6[6-6] | 1[1-1]/1[1-1]/7[7-7] | 1[1-1]/2[2-2]/9[7-10] |
| S4 * | 1[1-1]/2[1-2]/7[6-7] | 1[1-1]/2[2-2]/6[4-8] | 1[1-1]/5[4-5]/18[12-19] | 358[289-361]/400[359-403]/407[396-415] |

\* **S4 = container instantiated per call, as transformed.**

Fidelity: S1/S2/S3 = 1.000 at every cell. S4 = 1.000 through 1600; at 1920 fid
min 0.837 (achieved 1608 of 1920) — load-limited. `window_errors` = 0 everywhere.

## Top-rate per-rep distribution (1920; no 2560 cells for this app — knee 1280)

- S4@1920 p95 reps = **[359, 379, 400, 403, 403]** ms, fid [0.971, 0.892,
  0.846, 0.842, 0.837] — uniformly degraded (all reps past capacity), not
  bimodal. Report p95 = 400 [359–403] ms at an achieved ≈1608 rps.
- S1/S2/S3@1920 p95 reps all ≤ 3 ms, fid 1.000.

## Reading (no cost claims)

Neutral only: S1/S2/S3 stayed flat (p95 ≤ 2 ms) through the top rate 1920.
Only S4 rose, at 1920 (p95 400 ms, achieved 1608). No claim is made here that
this reflects container cost.

## Per-cell diagnostics

`time_since_boot_s` (server process age at cell start) = 0.50–0.52 s (fresh
boot). `timewait_start` median 402, max 802 (no accumulation). Affinity
`0,2,4`/`6` on every cell.
