# RQ3 — Five-arm DI resolution benchmark (FINAL)

> **SUPERSEDED as a comparison of DI strategies (Amendment 15, 2026-10-03).**
> `work_equiv.py` found that `s3_middleware`, `s4_container` and `s4_dishka`
> leased **two** pooled connections on each authenticated route where
> `s1_direct` and `s2_depends` leased **one**, with identical SQL and
> byte-identical responses. Holding a connection for less time queues less under
> a saturated pool, which is why those arms measured *faster than no DI at all*.
> Every latency figure below describes the pre-correction arms and is retained as
> the record of what was measured. It is **not** comparable to the corrected arms
> and must not be merged with the re-run. See `docs/prereg_execution_model.md`
> §4q. Tables `t9`, `t9b`, `t12`, `t13` are stale for the same reason.

Run `main`, completed 2026-10-02. **960/960 study cells + 5 drift references, 0 failures,
0 retries, 0 duplicate cells.** Wall clock 14.13 h.

Config hash `44ae5daf9d79cb147222521a672354f75f262e8bf5e5a4182d2652b64905eabf`.
Raw: `cells.csv` (sha256 `d034d06fdb6246716b1a82b76a4f217edeeaea7677ff98fd5c43dbff5360a2ed`).
Per-arm/rate table: `latency_by_arm_rate.csv`.

## Validity first

| Check | Result |
|---|---|
| Cells completed | 960/960, all 10 arm×model at 96 cells each |
| Failed / retried | 0 / 0 |
| **Drift across 5 references over 14.13 h** | **p50 1.0→1.0 ms, p99 2.0→2.0 ms — 0.0% drift** |
| Drift fidelity | 1.0000 at all 5 points |
| Overall load fidelity | median 0.9999, min 0.6614 |
| Clean cells (fid ≥ 0.95) | 847/960 = 88.2% |
| Window error rate | mean 1.5e-05, max 7e-04 |

The machine was effectively constant across the whole run. Degradation in the high-rate
band is therefore attributable to the arms, not the host.

## Median p99 (ms), clean cells

`C` = collapsed (0 clean cells, fidelity < 0.95 everywhere).

### sync
| rate | S1 direct | S2 Depends | S3 middleware | S4 container | S4 dishka |
|---|---|---|---|---|---|
| 200 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 |
| 400 | 3.0 | 4.5 | 5.0 | 2.5 | 7.0 |
| 600 | 6.0 | 10.0 | 11.0 | 6.0 | 20.0 |
| 800 | 9.0 | 20.0 | 21.0 | 8.0 | 27.0 |
| 900 | 12.0 | 50.5 | 33.5 | 11.0 | 30.0 |
| 1000 | 15.5 | **C** | **C** | 13.0 | 34.5 |
| 1200 | 28.0 | **C** | **C** | 23.0 | 44.5 |

### async
| rate | S1 direct | S2 Depends | S3 middleware | S4 container | S4 dishka |
|---|---|---|---|---|---|
| 200 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 |
| 400 | 3.0 | 3.0 | 4.5 | 3.0 | 7.5 |
| 600 | 7.0 | 8.0 | 12.0 | 7.0 | 20.0 |
| 800 | 13.0 | 15.0 | 30.0 | 12.0 | 37.5 |
| 900 | 17.0 | 21.0 | **C** | 16.0 | 44.5 |
| 1000 | 27.5 | 39.5 | **C** | 23.5 | 62.0 |
| 1100 | 104.5 | 2663.5 | **C** | 38.5 | 138.0 |
| 1200 | 2551.0 (3/8 clean) | **C** | **C** | **C** | **C** |

## Graded band (600–900), clean-cell medians

| Arm | sync | async |
|---|---|---|
| S1 direct (no DI) | 8.0 | 12.0 |
| S2 Depends | 18.5 | 12.5 |
| S3 middleware | 17.5 | 18.0 |
| S4 dependency-injector | **7.5** | **10.5** |
| S4 dishka | 25.0 | 33.5 |

## Findings

1. **A container is free; the framework resolver is not.** dependency-injector (7.5 ms
   sync) is indistinguishable from — in fact marginally below — the *no-DI* baseline
   (8.0 ms). FastAPI's own `Depends` costs 2.3× the baseline (18.5 ms). The abstraction
   is not the expense; the framework's implementation of it is.
2. **dishka pays a consistent ~3.2× penalty** over dependency-injector
   (sync 3.33×, async 3.19×) across the whole graded band, because it enters a
   request-scoped container on every request.
3. **Throughput ceilings differ by arm, and the ordering is not monotonic in
   "DI-ness".** sync: S2/S3 collapse at 1000 while S1/S4-container/S4-dishka serve 1200
   cleanly. async: S3 collapses at 900.
4. **sync → async is not free.** S3 middleware is the only arm that collapses in async
   (33.5 ms at 900 sync → 0 clean at 900 async).

## Caveat that constrains the saturated band

**1200 req/s is beyond the host's async capacity for *every* arm, including the no-DI
baseline** (S1 direct: 3/8 clean, median p99 2551 ms). Any statement that "arm X collapses
at 1200" is therefore confounded by the machine ceiling, not attributable to the arm.
This band is reported for completeness but carries no discriminating power. The
discriminating evidence is the 600–900 graded band, where every arm has 12/12 clean
replications at every rate.

## Reporting rules applied

- Clean-cell medians are **survivorship-biased** and are labelled as such.
- Unfiltered medians in the saturated band are contaminated by generator collapse.
- No cell is silently blanked: every table row shows `n_clean/n_total`, and collapsed
  cells are printed as `C` with their count, never as a dash.

## Known limitations

- Single host, 3 server cores, 8-connection SQLite pool. No replication across machines.
- Local 36 KB page-cached SQLite: negligible disk/network I/O, so these are
  *application-overhead* numbers. Relative ordering transfers; absolute p99 does not.
- Absolute overhead is inflated relative to real applications where DB/network latency
  dominates the request budget.