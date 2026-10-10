# Tier-2 Phase B — Protocol v1 cross-app summary (PRELIMINARY)

All four apps, Protocol v1: fresh process per grid cell + randomised order
(seed 20261009), S2 knee reused ({0.75,1.0,1.25,1.5} x S2knee),
uvicorn `taskset -c 0,2,4` (workers 1) / k6 `taskset -c 6` on
`voc-c-8c-16gb-150s-amd`, online set 0,2,4,6. Box-wide 0 `ERR*` cells;
the archived `ascending_order_v0/` run was a single-boot artifact.

| app | S2 knee | grid rates | flat arms (p95 ≤ ~2 ms, fid≈1) | onset of degradation | note |
|---|---|---|---|---|---|
| ciiceronee | 2560 | 1920/2560/3200/3840 | S1, S2 (≤3200) | S2 @3840 (214 ms), S3/S4 @3200 | S3@2560 [9..20] ms, S4@2560 [21..59] ms — both tautly unimodal, no collapse |
| vstorm-co | 1280 | 960/1280/1600/1920 | S1, S2, S3 | S4 @1920 (400 ms, achieved 1608) | S4@1920 reps [359..403] ms all degraded |
| johnsonhk88 | 160 | 120/160/200/240 | all (fid≈1 to 240) | n/a — latency growth only | S3@240 p95 81 ms vs S1/S2/S4 ~11–13 ms; p99 60–230 ms everywhere |
| azure-samples (S1–S3) | 2560 | 1920/2560/3200/3840 | S1, S2 | S3 @3840 (36 ms, achieved 3628) | S3@2560 [2..3] ms; S3 p99 60–224 ms |

Direction-only readings (no cost claims): every app shows S1 (no DI) flat
through its full grid. The S3 (DI in-process) arm is flat-to-mildly degraded in
all apps except jhk, where it is the highest-latency arm but stays load-
absorbing. S4 (container per call) degrades earliest when present (vstorm at
its top rate, ciiceronee at 3200). Individual cells, per-rep distributions and
fidelity in `results/v2/bench/<app>/report.md` + `raw.tsv`.

Total elapsed across the four runs ≈ 4.6 h (within the 8 h cap).