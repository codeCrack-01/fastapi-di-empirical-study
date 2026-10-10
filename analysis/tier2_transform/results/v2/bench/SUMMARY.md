# Tier-2 Phase B — Protocol v1 cross-app summary (PRELIMINARY)

All four apps, Protocol v1: fresh process per grid cell + randomised order
(seed 20261009), S2 knee reused ({0.75,1.0,1.25,1.5} x S2knee),
uvicorn `taskset -c 0,2,4` (workers 1) / k6 `taskset -c 6` on
`voc-c-8c-16gb-150s-amd`. Box-wide 0 `ERR*` cells; the archived
`ascending_order_v0/` run was a single-boot artifact. venv classes match the
first box by config-hash (no dependency drift).

S4 rows for ciiceronee/vstorm-co were re-measured with the **fair, built-once
container** construct (container built at module scope, resolved per request).
The earlier per-call-construction S4 runs are superseded (git history +
`arm_s4.percall` branches); they are NOT in this summary.

| app | S2 knee | grid rates | flat arms (p95 ≤ ~5 ms, fid≈1) | onset of degradation | note |
|---|---|---|---|---|---|
| ciiceronee | 2560 | 1920/2560/3200/3840 | S1, S2, S4 (≤3200) | S2/S4 @3840 (228/232 ms), S3 @3200 (49 ms) | S4@2560 p95 1 ms, S4@3200 5 ms (fair construct); S3 worst below capacity |
| vstorm-co | 1280 | 960/1280/1600/1920 | S1, S3, S4 (≤1600); S2 (≤1600) | S2/S4 @1920 collapse intermittently (13/45 ms med, 2/5 reps) | S4@1920 no longer uniform-collapse; same pattern as S2 |
| johnsonhk88 | 160 | 120/160/200/240 | all (fid≈1 to 240) | n/a — latency growth only | S3@240 p95 81 ms vs S1/S2/S4 ~11–13 ms; p99 60–230 ms everywhere |
| azure-samples (S1–S3) | 2560 | 1920/2560/3200/3840 | S1, S2 | S3 @3840 (36 ms, achieved 3628) | S3@2560 [2..3] ms; S3 p99 60–224 ms |

Direction-only readings (no cost claims): every app shows S1 (no DI) flat
through its full grid. S2 (`Depends`) is free everywhere. **S4 with a built-once
container is indistinguishable from S1/S2 below capacity in every app where it
was measured** (ciiceronee, vstorm-co fair runs; johnsonhk88's already-idiomatic
S4). The S3 (in-process/middleware) arm is the highest-latency arm below
capacity in jhk and ciiceronee, and is flat in vstorm/azure. Degradation onset
everywhere is the load-limited band at 1.25–1.5x knee. The earlier "S4 is
worst" tier-2 result was the per-request container-construction anti-pattern,
not container DI (see REPORT_phaseB_vs_reviewgate.md).

Individual cells, per-rep distributions and fidelity in
`results/v2/bench/<app>/report.md` + `raw.tsv`.

Runs: ciiceronee + vstorm-co re-run (fair S4) ≈ 2.6 h + first-run jhk/azure on
the original box; total ≈ 4.6 h + re-run within the 8 h cap.