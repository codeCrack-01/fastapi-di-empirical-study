# Execution model and DI pattern: pre-registration

**Study.** How do four FastAPI dependency-injection patterns compare under a sync
versus an async execution model, at each app's own capacity and at 1.5x that
capacity?

**Status.** Pre-registered before any measured cell. The functional-equivalence
smoke and the harness plumbing have been run and are reported in §9; no
performance measurement from the study grid has been produced.

**Amendment 1** (§4a) changes the core pinning after inspecting the provisioned
box's topology. It is dated before any measured cell, and the config hash above
is the one that includes it.

**Config hash.** `986f8e69b1972a86b61fbc4d7859cbd10a1a63c6318700cce4e75d7f55e76605`
(amendment 1, §4a; supersedes `53d78bb7...`)

Covering: `core_read.py` (service), `routes_read.py` (routes), `gen_apps.py`
(generator), `runner.py` (pool + cell loop + pinning + topology checks),
`knee.py`, `k6/harness.js`, `build_db.py`, `smoke.py`, `analyze.py`. Any edit
to any of these invalidates this pre-registration and requires an amendment
with a new hash.

Environment: Python 3.12.13, FastAPI 0.141.1, Starlette 1.6.0, Pydantic 2.13.2,
Uvicorn 0.52.4, aiosqlite 0.22.1, dependency-injector 4.49.1, k6 v2.2.0, one
worker. Database sha256 `ec432e8211b9767a...`, verified read-only.

---

## 1. Design

2 execution models x 4 DI patterns x 2 loads = **16 conditions, 40 reps each,
640 measured cells**.

| | Execution models |
|---|---|
| **DI patterns** | sync, async |
| P1 `direct` — handler constructs its own dependencies | |
| P2 `depends` — framework-native `Depends` | |
| P3 `middleware` — context assembled in middleware, read from `request.state` | |
| P4 `container` — external container, `dependency-injector` | |

**8 apps**: 4 patterns x 2 execution models.

This is a **fresh design**. The archived R=40 study measured something else
(a 21-route app with writes, on a 4-vCPU box) and is background only. None of
its numbers are reused here.

## 2. The knee, and why each app has its own

The sync and async arms of a pattern have different capacities, so a single
shared rate would not be "capacity" for both. Each app therefore gets its own
knee, and **1.0x is each app's own knee, not a shared absolute rate.**

- **Reference:** 30 s steady window at 10 req/s, giving `p95_ref` for that app.
- **Knee:** the highest offered rate `r` at which the app still satisfies all
  three criteria, located by a doubling ladder (10 → 3200) then a binary search
  to 2% of the lower bound:
  - `p95 <= 3 x p95_ref`
  - error rate `<= 1%`
  - achieved / offered `>= 0.98`
- **Three probes per app; the reported knee is the median of the three.** Each
  app's knee is reported as a result in its own right, including when an arm
  turns out to have no qualifying rate.
- A knee is right-censored if every ladder rate qualifies; it is then reported
  as censored at 3200, not extrapolated.

24 knee probes total (8 apps x 3).

## 3. Loads

- `1.0x` of the app's own knee — **"at capacity"**
- `1.5x` of the app's own knee — **"overload"**

`1.0x` is not called "normal load" anywhere in this study.

## 4. Held constant

Identical route table, identical SQL, identical response models, identical auth
semantics, identical read-only database, identical connection-pool size, one
worker, and disjoint core pinning. Per cell: fresh server process, pinned cores,
randomized order across the whole grid, 10 s warmup, 30 s measured window, 12 s
cooldown. Database sha256 recorded before and after every cell; a change aborts
the run.

**Only the dependency-acquisition layer differs between patterns. Only the
execution model differs between sync and async.** Nothing else is varied.

### 4a. Amendment 1 — topology and pinning (dated before any measured cell)

**Reason for the change.** An initial inspection of a provisioned 8-vCPU box
showed the layout above to be mis-specified for the actual hardware. The
pre-registration assumed 8 independent cores; the host exposes **4 physical cores
with 2 SMT threads each** (`/sys/devices/system/cpu/*/topology/thread_siblings_list`
-> `0-1`, `2-3`, `4-5`, `6-7`). Under the original layout the server on `0-5`
would have spanned three physical cores plus one SMT sibling, and k6 on `6`
would have shared a physical core with sampler `7`. SMT co-tenancy between the
load generator and the process under measurement is an interference mechanism, and
it is the same class of defect as the k6-on-server-cores bug caught during
harness bring-up. The change is made **before any measured cell exists**, so no
result is affected by it.

**Topology.** 4 physical cores, 8 logical CPUs, Intel Xeon (Skylake), 1 socket.

**Pinning layout, final:**

| role | CPUs | physical cores |
|---|---|---|
| server (uvicorn, 1 worker) | `0,2,4` | 0, 1, 2 |
| k6 (load generator) | `6` | 3 |
| sampler (100 ms ticker) | `6`, low priority, co-located with k6 | 3 |
| offline (SMT siblings, not used) | `1,3,5,7` | — |

Siblings `1,3,5,7` are taken **offline** (`echo 0 > .../cpuN/online`) rather than
merely left unused, so no process can be scheduled onto them. The online/offline
state and the sibling lists are captured per cell and recorded in the cell
metadata, so the topology is verifiable per cell rather than asserted once.
`runner.py` refuses to start if the server and k6 core sets overlap.

The sampler is co-located with k6 deliberately: it is a 100 ms ticker whose cost
is negligible, and keeping it off the server's cores preserves all three server
cores for the process under measurement.

**Effect on the design, stated honestly.** The server is **one uvicorn worker**,
so it is GIL-bound in both arms and was never going to scale across six physical
cores. Sync handlers are plain `def` and run on the default anyio threadpool;
async handlers are `async def` on a single event loop. Read-only SQLite queries
release the GIL only briefly. Going from 6 server CPUs to 3 therefore costs
little, and the change is made for interference control, not throughput. The
pre-registration makes no claim that knees are unchanged by it; the knees are
measured on the final layout and reported as-is.

**Held fixed and not tuned:** the sync arm's anyio threadpool size is left at the
framework default and is **recorded as fixed configuration**. It is not raised,
lowered, or tuned in response to any result.

**Plan type and host noise.** The provisioned plan is `vc2-8c-32gb`, which is
Vultr's **shared** Cloud Compute tier, not a dedicated-CPU plan. Steal time is
read from `/proc/stat` and recorded **per cell**; high-steal cells are reported
as a threat to validity rather than silently dropped. Any dedicated-CPU
alternative and its cost delta are reported to the sponsor before the main run,
and switching plans requires explicit approval.

**Not comparable to archived numbers.** Absolute knees and latencies from this
study are **not comparable** to the archived R=40 study, which used a different
box, a different plan tier, and a different pinning layout. That is acceptable
because the archived study is not used as a result in this work; it is
background only. The eight knees measured here are the only knees this study
refers to.

## 5. Read paths only

The app exposes the **12 read routes** of the original 21-route app. The 9 write
endpoints are absent; the database is opened `mode=ro` and file mode `0444`, and
`build_db.py` verifies that INSERT/UPDATE/DELETE are refused. The smoke test
additionally confirms 405 on write methods of read paths and 404 on the removed
write paths.

**This study makes no claim about write performance.** Write-heavy workloads
are where sync-vs-async usually diverges most, so the omission is a real limit
and not a convenience.

## 6. Metrics

p50, p95, error rate, achieved throughput, CPU-seconds per completed request,
peak RSS. Latency percentiles are over the measured window only; warmup and
cooldown are bucketed separately and excluded. CPU-seconds are divided by
completed requests, so an arm is not rewarded for serving fewer requests at the
same offered rate.

## 7. Analysis

Fixed here; `analyze.py` implements exactly this and is covered by the config hash.

1. **Per condition:** median of the 40 reps with a **bootstrap 95% CI**
   (10,000 resamples, percentile method, seed 20260928).
2. **Per pattern per load:** the **paired** sync-minus-async difference of
   medians, with a paired bootstrap 95% CI that resamples *rep indices* and
   carries each index across both arms, so drift in box state at a given index
   is shared rather than attributed to the execution model. This is the primary
   comparison.
3. **A CI spanning zero is reported as "unresolved at n=40."** It is never
   reported as "no difference" and never as "no effect."

**Not done, and not to be added post hoc:** p-values, interaction or 2x2 tests,
multiplicity correction, outlier removal, per-rep trimming, or any ranking of
the four patterns into a single league table. Per-rep distributions go to the
appendix. Nothing is discarded.

**Power, stated in advance:** at n=40 the overload arm resolves only differences
of roughly 30% or larger. At capacity, smaller. An "unresolved" result is the
expected outcome for a real difference below that threshold, and is not evidence
of equivalence.

## 8. What this study does and does not support

**Supports:** for a read-heavy FastAPI app on one machine with one worker and
SQLite, how the four DI patterns compare to each other under each execution
model, and how much the sync-to-async difference changes between capacity and
overload. Each app's knee is itself a result.

**Does not support, and must not be claimed:**

- anything about write performance (§5)
- that the comparison isolates "DI under async" — the async arm uses
  `aiosqlite` and `async def` handlers, so **sync-vs-async here is a difference
  between two implementations**, not a controlled manipulation of execution
  model alone
- generalisation to real repositories, other databases, other machines, or
  multi-worker deployments. This is one synthetic app, one box, one worker.
- cross-pattern ranking into a single ordering. The 8 knees differ, so "P2 is
  faster than P3" is not a claim this design supports at a shared rate.

## 9. Smoke, run before any measurement

`smoke.py` verifies functional equivalence in-process, with no server, no port
and no load:

- all 8 apps expose **exactly** the 12 read routes, same paths, methods, auth
  levels, and **no write method anywhere**;
- all 8 return **byte-identical** status and body on all 12 routes plus the 401
  probe;
- write methods on read paths return 405; the 9 removed write paths return 404.

**Result: passed.** 8 arms, 13 probes each, all identical
(`results/smoke_equivalence.json`).

The smoke also measured one thing that must be disclosed rather than assumed.
The sync arm drives the shared `async def` service layer through `resolve()` so
that all 8 apps run *literally the same* service code and no arm can drift. The
cost is **under 0.5 us per request** (0.18-0.46 us observed across runs; the
figure is noisy at this scale and is stated as an upper bound, not a point
estimate), uniform across all four sync patterns. It therefore does not affect
pattern-to-pattern comparison within the sync arm, and at the per-request costs
observed it is well under 1%. It is reported because a non-zero, measurable
overhead in one arm is exactly the kind of thing that should be stated in
advance rather than discovered later.

**Smoke cell data is written for provenance and never analysed.** `analyze.py`
refuses to read a smoke directory.

## 10. Cost

640 cells at 52 s of in-k6 time each, plus ~0.3 s median recorded startup, plus
per-cell teardown/drain that is **not measured** — which is the main source of
uncertainty in the wall-clock estimate. 24 knee probes, each a reference window
plus a ladder of ramps, dominate the non-cell time.

Indicative total: **~12-21 h** for the grid plus knees, on the 8-vCPU box
described in §4a. The dollar figure is **not stated here**; it is read from the
rental record at provisioning time. A budget ceiling of $50 is authorised; CPU
count is fixed at 8 vCPU and will not be increased, so a plan that costs more per
hour than that ceiling allows over ~20 h must be met by shortening the run or
splitting it across sessions, never by resizing the box — resizing would change
the unit under study and void the pinned configuration in §4.

---

## 11. Order of operations

1. Provision the box. Take SMT siblings `1,3,5,7` offline, verify core count,
   topology, and disjoint pinning per §4a, and record the plan type.
2. **Smoke on the box** (5 reps x 16 conditions). Harness only; discarded.
3. Knee probes: 8 apps x 3.
4. Report knees and the smoke outcome. **Stop.**
5. On explicit approval: the 640-cell main run.

Steps 1-4 are cheap. Step 5 is the expensive commitment and is gated on
approval after the knees are known, because the knees determine the 16 rates
that everything else depends on.
