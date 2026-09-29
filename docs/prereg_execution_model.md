# Execution model and DI pattern: pre-registration

**Study.** How do four FastAPI dependency-injection patterns compare under a sync
versus an async execution model, at each app's own capacity and at 1.5x that
capacity?

**Status.** Pre-registered before any measured cell. The functional-equivalence
smoke and the harness plumbing have been run and are reported in §9; no
performance measurement from the study grid has been produced.

**Amendment 1** (§4a) changes the core pinning after inspecting the provisioned
box's topology. **Amendment 2** (§4b) records the final host, corrects the
environment, and fixes two harness defects found during bring-up. **Amendment 3**
(§4c) bounds the async connection pool after a file-descriptor leak invalidated
all four async arms at 19 of 80 cells into a smoke run. **Amendment 4** (§4d) adds
host-drift reference cells, because a single-session design on one host needs its
host measured, not assumed. **Amendment 5** (§4e) makes rate derivation integral
and refuses an unrunnable rate instead of silently recording a null cell.
**Amendment 6** (§4f) records the thread-limiter emission defect, the
`p2_depends/sync` threadpool-starvation deadlock it exposed, and the
admission-control fix — including what that fix changes about what the sync
arm measures. All six are dated before any valid measured cell.

**Config hash.** `5550afe4c438387e45b0a91f8f827227a7479be619e7b53981c1f9b63b0b6adc`
for amendments 1–5; `63a541fdc641813468fd514182792f3bd6b38cf816c987308023dbe81b37e716`
after amendment 6.
(amendment 5, §4a + §4b + §4c + §4d + §4e; supersedes
`4e288aefff814721343e90649ae9d04cbae92a72b21fcd0f84cb939fe2278e38`)

Covering: `core_read.py` (service), `routes_read.py` (routes), `gen_apps.py`
(generator), `runner.py` (pool + cell loop + pinning + topology checks),
`prepare_box.py` (pinning), `run_matrix.py` (orchestrator), `knee.py`,
`smoke_knees.py`, `k6/harness.js`, `build_db.py`, `_seed_source.py`, `smoke.py`,
`analyze.py`, `drift_report.py`. Any edit to any of these invalidates this
pre-registration and requires an amendment with a new hash.

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

**Five harness defects, all found and fixed during bring-up.** All five would
have produced wrong metadata, a wrong knee, or a crashed run rather than a
visible error, and all are in files covered by the config hash:

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
5. `run_matrix.py` built per-cell log paths from the condition name
   `p4_container/sync@capacity`, whose `/` made the log path a directory that
   does not exist. The grid died with `FileNotFoundError` on the first cell.
   Condition names are now sanitised where the tag is built, and `start_server`
   sanitises and creates the parent directory as a second layer, so no caller can
   lose a whole run to a log path.

All five were found before any grid cell was measured. Defects 1, 2, 4 and 5
would each have silently invalidated a full run; they are recorded here rather
than quietly patched because the pre-registration's own rule is that any edit to
these files requires an amendment.

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

**Config hash** for amendment 2: `082b3f24800028b82e7d6ac14467882a6eae891a99fe26a08abf45ec9f007cac`,
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

### 4c. Amendment 3 — async connection-pool bound (2026-09-28, before any valid measured cell)

**Reason for the change.** Amendment 2's statement that no measured study cell
had been produced was true when it was written. Nineteen cells into a smoke grid
run, **before any valid cell was produced**, every async arm began failing with
`OSError: [Errno 24] Too many open files`. The run was stopped at 19 of 80 cells.
The defect is described here because it is a property of the code under
measurement, found by the harness before any study data existed, and fixed
before it could bias a result.

**Root cause.** `core_read.py` bounded the sync pool at `POOL = 8` using a
`queue.Queue` of pre-opened connections, but the async pool was an unbounded
free list:

```python
conn = _async_free.pop() if _async_free else await make_async_conn(path)
```

When the free list was empty the async path opened a **new** connection, with no
upper bound. Because `aiosqlite` runs one non-daemon OS thread per `Connection`
*and* holds a real file descriptor, the free list grew 1:1 with request
concurrency. Measured directly on the study host under `ulimit -n 1024`:

| concurrent requests | connections | open fds |
|---|---|---|
| 1 | 1 | 8 |
| 16 | 16 | 23 |
| 64 | 64 | 71 |
| 200 | 200 | 207 |

At the measured knee the server reached roughly 880 concurrent requests, so
exhaustion was arithmetically certain rather than incidental. All four async
knees and the async smoke cells are **invalid** and are discarded. The sync
arms never took this path and their behavior is unaffected by the bug.

**Is this our bug or a library limitation?** It is our bug, with a library
property that makes it a known footgun rather than a surprising one. `aiosqlite`
0.22.1 contains **no pooling mechanism at all** (zero references to pool,
maxsize, or semaphore in `core.py`), and it presents itself as a drop-in
asynchronous replacement for `sqlite3.connect()`, for which the idiomatic pattern
is to open a connection per request. That pattern is cheap against a networked
database, where a connection costs a TCP handshake, and expensive against
SQLite, where it costs a file descriptor and a thread. The bound is ours to
enforce, and it is now enforced where the sync bound already was. We record the
mechanism because any researcher using `aiosqlite` in this way will hit it.

**Fix.** The async pool is now a fixed `asyncio.Queue` of exactly `POOL = 8`
slots, created lazily and acquired by **waiting** for a free slot, so the async
arm blocks under contention exactly as the sync arm does. The pre-registration's
"identical connection-pool size, held constant across both execution models" is
therefore satisfied by construction rather than by convention. Verified after
the fix under the same `ulimit -n 1024`: 1, 4, 16, 64, 200, and 500 concurrent
requests all settle at **8 connections and 15 open fds**, and
`close_async_pool()` returns the process to its 7-fd baseline.

**The sync path was not modified.** `make_sync_conn`, `_get_sync_pool`,
`sync_conn`, and `close_sync_pool` are byte-identical to their state at
amendment 2, verified by symbol-level diff against the committed revision. The
only changed symbols are `async_conn`, `close_async_pool`, and the newly added
`_get_async_pool`.

**Consequence for the study: all eight knees are re-measured.** A pool bound was
added to the async path, so the async arms are no longer the same code as the
arms whose sync knees were measured. Re-measuring only the async arms would
leave a set of knees split across two code revisions, which a reader could not
distinguish from a genuine sync/async difference. All eight arms are therefore
re-measured under the single post-fix revision, in one run, so the eight knees
that §2 refers to come from one codebase. The cost is roughly 35 minutes of
knee probing plus the smoke re-run; it is accepted deliberately.

**Validity of the discarded run.** The 19 partial cells and the eight first-pass
one-probe knees are retained as provenance but are **not analyzed** and are not
reported as results. They are not spliced with the re-measured set, and the
re-measured knees are not adjusted or compared against them. This run is the
first time the harness has surfaced a defect that would have produced an unfair
sync-versus-async result silently, and it is reported as such rather than
discarded quietly.

**Config hash for amendment 3:**
`9c2c0e243a560fdf8b5d90740a4377d52dd485db501bdb739f9ebc4c8626ddd0`, recorded after
the fix above is applied on the study host and **before any re-measured knee is
run**.

### 4d. Amendment 4 — host-drift reference cells (2026-09-28, before any measured cell)

**The limitation being addressed.** This is a single-session design on a single
host. Conditions are measured at different times within that session, so any
change in the host's own behaviour over the session is confounded with
condition. That is a real threat to validity, and the honest options are to
measure it or to acknowledge it. The pre-registration previously did neither: it
recorded per-cell steal and the plan type (§4b) but had no direct check on
whether the host drifted.

**What was added.** The grid repeats **one fixed reference cell** at fixed
positions: `p1_direct/sync` at **25% of its own capacity knee**. Same app, same
load, same pinning, every time; only its position in the run changes. It is
chosen to be the simplest arm and comfortably inside the linear region, so a
change in its latency is far more likely to be the host than the application.

**Positions.** `DRIFT_REF_COUNT = 5` reference cells: after study cell 0, then at
evenly spaced intervals, and **one after the final study cell**, so the session
is bracketed at both ends. For the 80-cell smoke that is after cells 0, 16, 32,
48, 80; for the 640-cell main run, 0, 128, 256, 384, 640.

**These cells are diagnostics and cannot become results.** They are written with
`is_drift=1`, and `analyze.py` **drops every such row** before any aggregation,
in addition to the condition-name filter that would already exclude them. They
are never used to set a rate, never used to compute a knee, and never reported
as a measurement of the application. `drift_report.py` summarises them.

**Cost.** Five extra cells of ~52 s each, about **4 minutes** added to a ~1.2 h
smoke and a ~9 h main run. No measurement plan changes.

**What is reported, and how.** `drift_report.py` prints the reference cell's
p50, p95, mean, achieved rate and steal jiffies at each of the five positions,
and reduces them to a number: the p95 spread as a percentage of the median, and
the first-half to second-half p95 change. The tolerance is **10%**. The outcome
is decided in advance:

- **Spread ≤ 10%:** report that no material host drift was detected over this
  session. This is evidence that the single-session design was adequate *here*.
  It is not a claim that the host is stable in general, and it does not license
  comparison across sessions.
- **Spread > 10%:** report the drift as a **limitation, with these numbers
  attached**, name the affected cells by `after_cell`, and state that condition
  effects are confounded with time to that extent. Drift is **not** corrected
  for, and no cell is dropped for it.

**Effect on the design.** None on the randomised study order. Reference cells
are spliced in *after* the shuffle, so the study cells keep exactly the order
fixed by `SEED = 20260928`; verified by asserting the study-cell sequence is
unchanged by the interleave. The study's conclusions rest on the study cells;
the reference cells only calibrate the host they were measured on.

**Config hash for amendment 4:**
`4e288aefff814721343e90649ae9d04cbae92a72b21fcd0f84cb939fe2278e38`, recorded after
this change is applied on the study host and **before any measured cell is
run**. `drift_report.py` is added to the covered file list for the same reason
`run_matrix.py` was added in amendment 2: it participates in interpreting a
measurement, so a change to it has to invalidate the hash.

### 4e. Amendment 5 — integer rate derivation, and a loud failure instead of a silent one (2026-09-28, before any measured cell)

**What was found.** The first host-drift reference cell of §4d was scheduled at
25% of `p1_direct/sync`'s capacity knee. With a knee of 950 rps that is
**237.5 rps**, and k6 rejected it:

```
cannot unmarshal number 237.5 into Go struct field
Options.scenarios.stages.target of type int64
```

k6 exits during option parsing. The cell then records **zero requests, a null
window, and `achieved=0.0`** — and because that is a null result rather than a
non-zero exit status, the grid does not stop. The run was halted after the first
cell. No measured cell was produced.

**Why this matters beyond the reference cell.** `k6`'s arrival-rate stages take
an `int64` target, so **every** rate the study derives must be a whole number
of requests per second. The pre-registration defines the overload rate as
`1.5 x knee`, and a study knee is the **median of three probes**, so an odd knee
is entirely possible. An odd knee makes `1.5 x knee` fractional, and that cell
would have failed in exactly the same silent way during the main run. All eight
re-measured knees happened to be even, so no study rate was at risk *this* time,
but nothing in the design prevented it.

**The fix, in two parts.**

1. **Rates are integers by construction.** `build_plan()` rounds every rate to
   the nearest whole rps. The exact pre-rounding value is kept in a new
   `rate_exact` column and written to `cells.csv`, so the rounding is visible
   and auditable rather than silent. The largest rounding any rate in this study
   can incur is 0.5 rps, which is under 0.05% of the smallest rate used
   (1035 rps).
2. **A fractional rate is refused, not attempted.** `check_rate_is_usable()`
   raises before a cell is spent if a rate is not a positive integer, naming the
   condition, the rep, and the exact value. A cell that cannot produce a
   measurement now stops the run instead of quietly producing a null.

**The earlier `p2_depends/sync` empty-window cells are not explained by this.**
Those cells carried an integer rate (1155 rps), so the cause is different and is
**still unresolved**. It is recorded as an open harness question. The reference
cell is valuable partly because it made a *different* silent failure cheap to
reproduce and isolate: the same symptom, a different cause.

**Effect on the design.** None. Rates are integers, as they must have been all
along. §3's load definitions are unchanged; only the representation is now
explicit and checked.

**Config hash for amendment 5:**
`5550afe4c438387e45b0a91f8f827227a7479be619e7b53981c1f9b63b0b6adc`, recorded after
this change is applied on the study host and **before any measured cell is
run**.

### 4f. Amendment 6 — thread limiter emission, and the p2_depends/sync deadlock (2026-09-29, before any valid measured cell)

**Two defects, one consequence.** Recorded together because the second is only
visible once the first is fixed.

**Defect 1 — the limiter was never in force.** `gen_apps.py` emitted

```python
anyio.to_thread.current_default_thread_limiter().total_tokens = POOL
```

*after* the lifespan `yield`, which placed the assignment on the shutdown path.
During serving, the limiter therefore sat at anyio's default of 40 and the
intended bound of 8 was never applied. This was confirmed at runtime rather
than by reading source: a frozen server had 40 threads simultaneously inside
`get_db`, which cannot happen if a limit of 8 is being enforced. The line now
sits before the `yield`, and the `/__diag` endpoint reads `total_tokens: 8`
during load.

**Defect 2 — threadpool starvation in `p2_depends/sync`.** With the bound
genuinely enforced, this arm deadlocked 7 out of 7 consecutive runs
(`reqs=0 fails=600`, 62 s timeout each). The mechanism:

1. `p2_depends/sync` is the only arm whose routes take a generator
   dependency, `conn=Depends(get_db)`, 13 times. `get_db` holds a pooled
   connection across the `yield` for the whole request.
2. FastAPI suspends the generator at the yield and releases the worker thread.
   Returning the connection requires *resuming* that generator, which requires
   a thread.
3. Meanwhile, other requests call `sync_conn`, which blocks in an unbounded
   `queue.Queue.get()` — **while holding** a threadpool token.
4. Once all 8 tokens are held by such waiters, no cleanup can ever be
   scheduled. No connection is returned. Every later request blocks forever.

At the frozen moment: `pool_free=0`, `in_body_now=8`, `unreturned=8`, and 40
threads parked in `core_read.py:148`. No connection was orphaned, which is why
this is starvation and not a leak; a sequential control ran 960 checkouts and
960 returns with zero unreturned.

**Why only this arm.** `p1_direct`, `p3_middleware` and `p4_container` open
the connection with a plain `with conn_ctx()` *inside* the handler, so no
generator is suspended across the yield and no cleanup needs a reacquired
thread. Each ran 3/3 clean at the enforced limit. The async arms use an
`asyncio.Queue`, so waiting holds no thread token at all. The defect is a
property of generator dependencies in a threadpool-bound sync app, not of the
sync execution model in general.

**The fix — admission bounded to `POOL` before the sync dependency runs.**
Scoped to `p2_depends/sync` only:

```python
async def _slot():
    async with _slots:          # _slots = asyncio.Semaphore(POOL)
        yield

def get_db(_slot_dep=Depends(_slot)):
    with conn_ctx() as conn:
        yield conn
```

`_slot` is an async generator dependency, so the event loop resolves and tears
it down and it never consumes a threadpool token. Because `get_db` depends on
it, admission is bounded before the sync generator is entered, and the
semaphore is held across the entire lifetime of the `get_db` generator —
released only when `get_db` resumes and closes. The hold therefore spans the
whole window in which the connection is checked out.

The cap at `POOL` is load-bearing: a slot-holder must always be able to obtain
a connection, so the wait-for-connection edge can never be closed by someone
already holding a slot. This breaks the cycle rather than reordering it. A
larger cap would reintroduce the deadlock at a higher arrival rate; a smaller
one would idle the pool.

**What this changes about what is measured — disclosed, not footnoted.**
The arm is now back-pressured rather than unbounded. Time spent waiting for a
semaphore slot lands in `p2_depends/sync`'s measured latency, so the sync arm
carries an admission-control queueing cost that the other three sync arms do
not. This is a real change to the thing being measured, in the one arm whose
absolute latency is the least favourable of the eight, and it cannot be
hidden behind a constant. Concretely: at 2x the offered rate, p95 moves from
6 ms to 796 ms with throughput held near the knee — that difference is
semaphore queueing, not service time.

**Effect on the design.** The independent variable — the dependency-acquisition
layer — is unchanged for the other seven arms, which are byte-identical before
and after (verified by hash, not by inspection). `p2_depends/sync` is
therefore no longer a pure "framework-native DI, unbounded" cell. Any
comparison of its latency against another sync arm is a comparison of two
different admission-control regimes and is labelled as such in the results.

**Gate before any main-run data.** 20 consecutive runs of the real
`apps.p2_depends.sync.app:app` at rate 750 (the p2 capacity knee), limiter 8,
on a fresh `voc-c-8c-16gb-150s-amd` with the §4a pinning re-applied: **20/20
clean**, every cell `reqs≈22,530 fails=0 dur=52s`, against a pre-fix signature
of `reqs=0 fails=600 dur=62s`. A soak at 2x is recorded as a measurement with
no pass/fail verdict attached, since slower throughput under overload is the
expected behaviour of bounded admission and is not evidence of a deadlock.
Equivalence re-verified on that box: 8 arms x 13 probes, byte-identical.

**Open question, unchanged.** The `p4_container/sync` "1/3 partial failure"
(§4e) is **withdrawn**, not resolved. `cells.csv` shows 10/10 clean cells with
zero check failures, and the quoted figures appear in no archived log, so they
cannot be reproduced or refuted from the evidence and may be an artifact of the
pre-amendment-5 fractional-rate bug. There is no evidence linking
`p4_container` to the deadlock above, and none is claimed.

**Config hash for amendment 6:**
`63a541fdc641813468fd514182792f3bd6b38cf816c987308023dbe81b37e716`, recorded on the
study host after both changes are applied and **before any cell that will be
treated as main-run data**. The hash differs from amendment 5's because
`gen_apps.py` and `apps/p2_depends/sync/app.py` changed; the database is
untouched and still hashes to `ec432e8211b9767a…` as in §4b.

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
2. **Smoke knee probes on the box** (8 arms x 1, one-probe, discarded) to supply
   per-arm rates. Per §4c these are re-measured from scratch, not reused from the
   invalidated first pass.
3. **Smoke on the box** (5 reps x 16 conditions). Harness only; discarded.
4. Knee probes: 8 apps x 3.
5. Report knees and the smoke outcome. **Stop.**
6. On explicit approval: the 640-cell main run.

Steps 1-5 are cheap. Step 6 is the expensive commitment and is gated on
approval after the knees are known, because the knees determine the 16 rates
that everything else depends on.

**Current state: at step 2, re-running from a clean revision.** Steps 1 and the
functional smoke in §9 are complete. The first pass through steps 2 and 3
produced 8 one-probe knees and 19 of 80 smoke cells, all invalidated by the
async connection-pool defect in §4c; the smoke was stopped at 19 cells and
nothing from that pass is analyzed. Steps 2 and 3 are re-run under the
amendment-3 config hash before the study proceeds.

**Current state: at step 2, again.** The amendment-3 re-run produced 8
one-probe knees and then 76 of 85 smoke cells, the remaining 9 being
`p2_depends/sync` nulls from the §4f deadlock; the drift controls did not run,
so that pass carries no host-stability evidence. It is retained as provenance
in `analysis/syncasync/results/evidence/` and is **not analyzed**. Amendment 6
fixes the deadlock and passed its 20-run gate, so steps 2 and 3 are re-run a
third time under config hash `63a541fd…`. The one-probe knees and the
`p2_depends/sync` capacity rate of 750 used in the §4f gate are harness
inputs only, and the 8 knees from the discarded pass are not reused.
