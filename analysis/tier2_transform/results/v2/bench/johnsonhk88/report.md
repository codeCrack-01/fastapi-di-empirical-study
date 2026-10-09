# johnsonhk88 — Tier-2 Phase B, Protocol v1 (fresh boot per cell, randomised)

PRELIMINARY. Direction-only; not comparable in absolute terms to other hosts.
App: johnsonhk88 (FastAPI + Postgres + DI). Box `voc-c-8c-16gb-150s-amd` (8
vCPU/16 GB, ord), instance `e8cd6321-daa8-4f44-9ad6-da6adedc114a`. Pinned:
uvicorn `taskset -c 0,2,4` (`--workers 1`), k6 `taskset -c 6` (all cells
`0,2,4`/`6`). Online set `0,2,4,6`.

Protocol: fresh server per cell (each boot re-runs alembic migrate + token
preseed; boot age 3.5 s), randomised order (seed 20261009). S2 knee reused =
**160 rps** (`--knee`). Grid = 160 x {0.75,1.0,1.25,1.5} = 120/160/200/240 rps
(K3/K5/K5/K5). Raw: `raw.tsv` (72 rows, 0 `ERR*`).

## Per-cell results, p50/p95/p99 ms median [min–max]

| arm | 120 (K3) | 160 (K5) | 200 (K5) | 240 (K5) |
|---|---|---|---|---|
| S1 | 2[2-2]/3[3-3]/75[61-86] | 2[2-2]/3[3-4]/139[115-156] | 2[2-2]/4[4-8]/145[131-202] | 2[2-2]/11[11-13]/188[179-200] |
| S2 | 2[2-2]/2[2-2]/67[63-68] | 2[1-2]/3[3-3]/132[111-143] | 1[1-2]/4[3-4]/131[123-158] | 1[1-1]/11[9-13]/194[175-200] |
| S3 | 2[2-2]/3[3-3]/154[130-159] | 2[2-2]/4[4-8]/168[159-194] | 2[2-2]/11[10-13]/184[179-203] | 2[2-2]/81[64-92]/222[205-227] |
| S4 * | 2[1-2]/2[2-2]/69[58-69] | 1[1-2]/3[3-3]/118[114-144] | 1[1-1]/3[3-4]/135[131-140] | 1[1-2]/11[9-12]/175[173-201] |

\* **S4 = container instantiated per call, as transformed.**

Fidelity: `achieved == offered` at every cell for every arm (fid 0.99–1.00);
`window_errors` = 0. This is a **latency-growth regime, not saturation**: rates
are fully absorbed, but tail latency rises with rate. p99 already ~67–154 ms at
the lowest anchor (DB access dominates), climbing to ~175–222 ms at 240.

## Top-rate per-rep distribution (240; no 2560 cells — knee 160)

- S3@240 p95 reps = **[64, 65, 81, 81, 92]** ms — monotone rise, unimodal
  (no gap), uniformly shifted; p99 205–226 ms.
- S1@240 [11,11,11,11,13]; S2@240 [9,10,11,12,13]; S4@240 [9,10,11,11,12] —
  all clustered tight at ~9–13 ms.

## Reading (no cost claims)

Neutral only: all four arms absorb the full grid. Tail latency (p95/p99) grows
monotonically with rate for every arm; p95 is ~11–13 ms for S1/S2/S4 and
~81 ms for S3 at 240. No claim is made here that the S3 shift reflects
middleware or container cost.

## Per-cell diagnostics

`time_since_boot_s` (server process age at cell start) = 3.5 s (alembic +
preseed included in boot). `timewait_start` median 274, max 321 (no
accumulation). Affinity `0,2,4`/`6` on every cell.