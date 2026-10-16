# RQ3 — Five-arm DI resolution benchmark (CORRECTED, Amendment 15)

> **Corrected re-run per Amendment 15 (§4q of `docs/prereg_execution_model.md`)**.
> The pre-correction run (`results_5arm_20261002_1653/`) was superseded because three arms leased the pooled DB connection twice where the other two leased it once; all arms now hold exactly one connection per request and `s2_depends` role mapping is corrected. The pre-correction record is retained as `results_5arm_precorrection.md`. No result below should be merged with pre-correction numbers.

Run: corrected ladder 600–900 req/s, graded_reps=12, completed 2026-10-04. **480/480 study cells + 5 drift references, 0 failures, 0 retries.** Wall clock ~7.09h.

Raw: `box6_snapshot/results/main/cells.csv` (sha256 `cccaf5900433e313398702c05ce958de4db1897aa8b4e9b233d38ffc4fe6e94a`). Analysis: `results/final_r2.json` (≈ `box6_snapshot/results/main/analysis.json`). Re-run log: `results/run_main_r2.log`. Config hash (run): `04b60fe9e302a713eb6d627444599c3255dfb0feef7f0ebbcf94d151fe9af2c6` (`results/config_hash_box_r2.json`).

## Validity

| Check | Result |
|---|---|
| Cells completed | 480/480 (4 rates × 5 arms × 2 models × 12 reps), all clean by design |
| Failed / retried | 0 / 0 |
| Drift across 5 references (entire run) | http_p50 0.51→0.56 ms, http_p99 1.26→1.40 ms — stable |
| Overall load fidelity | median 0.9999, min 0.9847, max 1.0026 (480/480 ≥ 0.98) |
| Clean cells (fid ≥ 0.95) | 480/480 = 100% |
| Window error rate | mean 0.0, max 0.0 |
| achieved/offered | median 0.9999, min 0.9847 |

All cells clean within the graded band; saturation is out of scope.

## Corrected latency — median http_p99 (ms)

### sync
| rate | S1 direct | S2 Depends | S3 middleware | S4 container | S4 dishka |
|---|---|---|---|---|---|
| 600 | 4.61 | 7.84 | 9.21 | 4.40 | 20.61 |
| 700 | 5.60 | 10.63 | 13.05 | 5.29 | 23.59 |
| 800 | 7.78 | 16.85 | 16.06 | 7.51 | 28.00 |
| 900 | 9.34 | 24.40 | 29.13 | 8.66 | 30.62 |

### async
| rate | S1 direct | S2 Depends | S3 middleware | S4 container | S4 dishka |
|---|---|---|---|---|---|
| 600 | 5.28 | 5.89 | 8.53 | 4.80 | 20.27 |
| 700 | 6.83 | 8.02 | 13.23 | 5.86 | 27.89 |
| 800 | 8.83 | 10.34 | 17.01 | 8.57 | 35.12 |
| 900 | 11.88 | 12.66 | 29.10 | 10.89 | 40.80 |

### Graded band medians (600–900 pooled)
| model | S1 direct | S2 Depends | S3 middleware | S4 container | S4 dishka |
|---|---|---|---|---|---|
| sync | 6.10 | 12.63 | 13.70 | 6.57 | 26.00 |
| async | 8.08 | 9.11 | 14.71 | 7.08 | 30.27 |

## Paired verdicts (corrected)
From `results/final_r2.json`, paired exact binomial/order-statistic intervals, relative 10% margin. B denotes baseline S1 direct in the same model.

- **S4 container vs baseline:** statistically indistinguishable — `practically equivalent` at sync@700, otherwise `inconclusive` in both models. The pre-correction sub-1.0× artifact is **gone**.
- **S2 Depends vs baseline (sync):** **meaningfully worse** at all rates (+3.5 → +15.4 ms, ~1.7–2.6×).
- **S2 Depends vs baseline (async):** **inconclusive** at all rates (~1.1×).
- **S3 middleware vs baseline:** **meaningfully worse** at every rate, both models (~2.0–3.1× sync, ~1.6–2.5× async).
- **S4 dishka vs baseline:** **meaningfully worse** everywhere (~3.3–4.5×), largest penalty.
- **Execution model (async − sync):** S2 Depends is **meaningfully better** async at all rates; S4 dishka is **meaningfully worse** async at 700/900; S1, S3, S4 container mostly **inconclusive**. S3@900 is bimodal — the null is not a stable "no difference".

## Revised findings
1. **Container ≈ no DI.** S4 container (dependency-injector) is indistinguishable from the no-DI baseline; it does not replicate a "faster than no DI" result.
2. **Framework Depends is cheap in async, costly in sync.** Sync Depends is meaningfully worse; async Depends is not distinguishable from baseline.
3. **Middleware adds substantial overhead.** S3 middleware is meaningfully worse than baseline in both models.
4. **dishka is the highest-cost arm.** Request-scoped container enters drive a large, consistent penalty.
5. **Scope note.** Corrected run covers 600–900 only. Throughput ceilings/collapse observed in the pre-correction run (1000/1200) are out of scope and not re-established.

## Caveats
- 36 KB page-cached SQLite; contended resource is the connection pool, not disk/network.
- Single host; no between-host replication. Interval quantifies within-run noise.
- Normalising to one lease buys internal validity at cost of ecological validity (real code often separates auth/business scopes).
- S3@900 dispersion suggests instability there, but doesn't flip the overall ordering.
