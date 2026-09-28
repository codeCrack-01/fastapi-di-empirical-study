# Execution model and DI pattern: pre-registration

**Study.** How do four FastAPI dependency-injection patterns compare under a sync
versus an async execution model, at each app's own capacity and at 1.5x that
capacity?

**Status.** Pre-registered before any measured cell. The functional-equivalence
smoke and the harness plumbing have been run and are reported in §9; no
performance measurement from the study grid has been produced.

**Amendment 1** (§4a) changes the core pinning after inspecting the provisioned
box's topology. **Amendment 2** (§4b) records the final host, corrects the
environment, and fixes two harness defects found during bring-up. Both are dated
before any measured cell, and the config hash below is the one that includes both.

**Config hash.** `a5b80c41dfb77d105389eed9c41b58052006f04b599e10553c404ddb168b40f6`
(amendment 2, §4a + §4b; supersedes `986f8e69...`)

Covering: `core_read.py` (service), `routes_read.py` (routes), `gen_apps.py`
(generator), `runner.py` (pool + cell loop + pinning + topology checks),
`prepare_box.py` (pinning), `run_matrix.py` (orchestrator), `knee.py`,
`smoke_knees.py`, `k6/harness.js`, `build_db.py`, `_seed_source.py`, `smoke.py`,
`analyze.py`. Any edit to any of these invalidates this pre-registration and
requires an amendment with a new hash.

Amendment 2 adds `run_matrix.py`, `prepare_box.py` and `smoke_knees.py` to this
list. Amendment 1's list omitted `run_matrix.py`, which selects each arm's rate
and defines the grid, so that pre-registration was not in fact pinning everything
that determines a measurement. That gap is closed here.

Environment (measured on the study host, not the development machine): Python
3.12.14, FastAPI 0.141.1, Starlette 1.6.0, Pydantic 2.13.2, Uvicorn 0.52.4,
AnyIO 4.15.1 (asyncio backend), aiosqlite 0.22.1, dependency-injector 4.49.1,
k6 v2.2.0, one worker. Database sha256 `ec432e8211b9767a...`, verified read-only.

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

**Topology.** 4 physical cores, 8 logical CPUs, 1 socket. Amendment 1 recorded
this against the box that was provisionally inspected at the time; the *final*
host is recorded in §4b, and its sibling groups are identical, so the pinning
layout below is unchanged.

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

### 4b. Amendment 2 — final host, environment, and two harness fixes (2026-09-28, before any measured cell)

No measured study cell has been produced at the time of this amendment. One
knee probe was run and stopped mid-probe; it is harness validation, not a
measurement, and is excluded.

**Host.** The provisioned host is Vultr **`voc-c-8c-16gb-150s-amd`** in `ord`,
instance `e992ab49-a130-44ef-95db-d01e38ebe372`, 8 vCPU / 16 GB / 150 GB NVMe,
AMD EPYC (Milan), 1 socket, 4 physical cores x 2 SMT threads, 8 logical CPUs,
32 MiB L3, Ubuntu 22.04.5, kernel `5.15.0-191-generic`, `MemTotal`
16365880 kB. Listed at $0.219/h, $160/month.

This is a **dedicated-CPU** plan. Vultr's own documentation for Optimized Cloud
Compute states: *"Vultr Optimized Cloud Compute instances are dedicated virtual
machines"*; *"Choose **Dedicated CPU** as the instance type"*; and, for the
`-c` (CPU Optimized) category, *"Support compute-bound applications that require
proportionally more CPU than RAM (memory) and storage."*
(<https://docs.vultr.com/products/compute/instances/optimized-cloud-compute/provisioning>,
updated 26 May 2026). The `voc-c-*` plan ID is an Optimized Cloud Compute plan
code, and the observed host has 4 physical cores backing 8 vCPU threads, which is
consistent with dedicated vCPUs rather than oversubscribed shared ones.

Amendment 1 was written against the box inspected at the time and recorded an
Intel part; the sibling groups are identical, so the pinning layout is unchanged,
but the vendor and RAM are corrected here. RAM is **16 GB, not the 32 GB** of the
earlier provisional host.

**The dedicated designation is not load-bearing for any claim.** Steal time is
still read from `/proc/stat` and recorded per cell (§4a), so if the host were in
fact oversubscribed, the recorded data would show it. The designation is
disclosed background, not a premise; the pre-registered analysis in §7 is
unchanged.

**Four harness defects, all found and fixed during bring-up.** All four would
have produced wrong metadata or a wrong knee rather than an error, and all are
in files covered by the config hash:

1. `knee.py` tested `window["count"]` for sample sufficiency. The k6 summary
   stores the window request count as a top-level `window_requests`; the `window`
   object holds only percentiles and has no `count` key. Every probe therefore
   aborted with "reference run produced no samples" on runs that had produced
   hundreds of good requests. Corrected to test the actual request count.
2. The k6 `ramp` scenario ran a single 8 s stage, shorter than the 10 s warmup, so
   all traffic fell inside warmup and the measured `window` came back `null` with
   `window_requests` 0. Corrected to ramp and then hold at `RAMP_MAX` across the
   full warmup + window + cooldown, so the qualifying steady window exists at the
   rate under test.
3. `runner.py` wrote `"plan_type": "vc2-8c-32gb(shared)"` as the default for
   per-cell metadata while `REVIEWGATE_PLAN_TYPE` was unset on the box, so every
   cell would have been recorded against the wrong plan and the wrong plan tier.
   The default is now the real plan, `voc-c-8c-16gb-150s-amd`.
4. The smoke/main knee guard in `run_matrix.py` was incomplete. It compared each
   knee file's `mode` tag against its directory, but never checked the run's own
   mode against the directory, so `--main --knee-dir results/smoke_knees` was
   **allowed** and would have run the 640-cell grid on single-probe rates. Caught
   by a dry-run test before any grid cell ran. `load_rates()` now takes the run
   mode and refuses a main run from `smoke_knees`; verified on the box.

A consequence of the first two: the very first knee probe reported
`knee median None`, which was a harness bug and **not** evidence about capacity.
No capacity conclusion was drawn from it.

**Per-cell host facts.** Every cell now also records, read from the machine at
run time rather than asserted: CPU model, logical CPUs present and online, online
CPU list, physical-core count, socket count, threads per core, `MemTotal`, kernel,
arch, and the full sibling map. The counts come from sysfs `cpu*` directories
rather than `os.cpu_count()`, which reports *online* processors and so returns 4
on this 8-CPU host once siblings `1,3,5,7` are offlined. This makes the §4a/§4b
topology claim checkable from the data after the fact, and would expose a
silently replaced host.

**Smoke knees are single-probe and are not study knees.** §3 defines a knee as
the median of three probes. The 5-rep smoke needs capacity rates before the grid
can run, so it uses **one** probe per arm, written to `results/smoke_knees/` and
labelled `mode: smoke`. `run_matrix.py` refuses to run `--main` from that
directory, and refuses `--smoke` from a directory containing `mode: study` files,
so a single-probe rate cannot be substituted for a 3-probe median. Every run
writes `rates.json` recording which knee directory and mode produced its rates.
Smoke data is discarded and never analysed (§9); the study knees remain the
3-probe medians.

**Config hash** for amendment 2: `a5b80c41dfb77d105389eed9c41b58052006f04b599e10553c404ddb168b40f6`,
computed on the study host and covering the 13 files listed at the head of this
document, including `run_matrix.py`, `prepare_box.py` and `smoke_knees.py`, which
amendment 1 omitted.

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

**Plan type and host noise.** The provisioned plan is `voc-c-8c-16gb-150s-amd`
(dedicated-CPU Optimized Cloud Compute; see §4b for the provider citation). The
earlier provisional host used the **shared** `vc2-8c-32gb` tier, and was replaced
before any measured cell. Steal time is read from `/proc/stat` and recorded **per
cell**; high-steal cells are reported as a threat to validity rather than
silently dropped. Because steal is recorded regardless, the analysis does not
depend on the dedicated designation being correct. Any further plan change and
its cost delta would be reported to the sponsor before the main run, and
switching plans requires explicit approval.

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
