# Evidence from the abandoned smoke run (2026-09-29)

Extracted from the Vultr box `voc-c-8c-16gb-150s-amd` (Ord) immediately before
the instance was destroyed. Captured under commit `9522d0d`
("Amendment 5: integer rate derivation; refuse an unrunnable rate").

## Arm-name rename (2026-09-29, Amendment 7)

The pattern arms were renamed from `pN_` to `sN_` prefixes to match the
published S1–S4 taxonomy. This archive was renamed with them, filenames and
structured content alike:

| was | now | taxonomy |
|---|---|---|
| `p1_direct` | `s1_direct` | S1 direct / zero-DI |
| `p2_depends` | `s2_depends` | S2 framework-native |
| `p3_middleware` | `s3_middleware` | S3 manual Python DI |
| `p4_container` | `s4_container` | S4 external container |

**Two classes of file in this archive are deliberately NOT identical, and the
difference is intentional:**

- **Renamed in content:** filenames, structured data (`cells.csv`, `rates.json`,
  `*.summary.json`, `knee_*.json`), executable scripts, and prose in this file
  and `semaphore_fix/README.md`.
- **Left verbatim in content:** raw terminal captures `repro5.log`,
  `semaphore_fix/stress20.log`, and `semaphore_fix/soak2x.log`. These are
  byte-for-byte records of what the shell printed on the box at the time. They
  still contain `pN_` strings because that is what the run emitted, and editing
  a captured log to match a later rename would falsify the record. **Any `pN_`
  string remaining in this archive is a captured log line, not a live reference.**

No measurement, rate, count, or verdict in this archive was altered by the
rename. Git retains the pre-rename paths in history regardless.

## Provenance

| check | value |
|---|---|
| `config_hash.json` → `config_sha256` | `5550afe4c438387e…` — matches commit `9522d0d` |
| `config_hash.json` → `database_sha256` | `ec432e8211b9767a…` — matches the pre-registration |
| runtime versions | Python 3.12.14, k6 v2.2.0, fastapi 0.141.1, uvicorn 0.52.4, aiosqlite 0.22.1 |

`config_hash.json` was read back from the box and cross-checked against the
committed hash rather than assumed, so these numbers are the ones the run
actually recorded.

## What is here

- **`smoke/cells.csv`** — the 85-cell smoke grid: 80 study cells + 5 host-drift
  reference cells. **76 valid, 9 null** (all `s2_depends/sync`). This is the
  central artifact.
- **`smoke/rates.json`** — the rate actually used per cell, including the
  `rate_exact` values that Amendment 5 added.
- **`smoke_knees/*.json`** — the eight valid post-fix single-probe knee
  measurements. These are harness rates, **not** the final three-probe medians
  the pre-registration requires.
- **`smoke_equivalence.json`** — functional-equivalence result: 8 arms × 13
  probes, byte-identical responses.
- **`config_hash.json`**, **`topology.json`** — provenance and host pinning.
- **`cells/`** — per-cell server logs (96 files, 1 non-empty).
- **`wedge.log`, `wedge2.log`, `wedge3.log`, `loop_fixed.log`, `poll.log`,
  `repro*.log`** — diagnostic output from the deadlock investigation.
- **`diag_app.py`, `repro5.py`, `loop.py`** — the diagnostic harness used to
  take the thread dumps and count connection checkouts.

## The run is NOT valid as a performance measurement

Do not compute latencies or throughput from `smoke/cells.csv` and present them
as results. Two independent reasons:

1. **9 null cells.** `s2_depends/sync` deadlocked and served zero requests in 9
   of its 10 cells. Those cells have no measurement, and the arm is incomplete.
2. **Host drift controls never ran.** All 5 drift cells failed on the fractional
   rate bug before the integer-rate fix, and the run was not repeated after
   `9522d0d`. `is_drift` is `False` for all 85 rows, so there is no evidence
   about host stability over the session.

What the smoke *does* support is the negative result: **async and sync
throughput were within noise of each other across all arms that produced data.**
That is a real finding about FastAPI execution models. The missing data is an
artefact of harness bugs, not a measurement of the thing under test.

## Why the run was abandoned

`s2_depends/sync` intermittently froze — the process stayed alive, the socket
stayed open, the log stayed empty, and `/health` stopped answering. Diagnosis
(see the `wedge*.log` files and `diag_app.py`):

- **Threadpool-starvation deadlock, not a connection leak.** At the moment of
  the freeze: `pool_free=0`, `in_body_now=8`, `unreturned=8`, and 40 threads
  parked in `core_read.py:148` (`queue.get`). No connection was orphaned.
- **Cause.** `s2_depends/sync` is the only arm whose routes take
  `conn=Depends(get_db)`, a *generator* dependency that holds a pooled
  connection across the `yield` for the whole request. FastAPI suspends the
  generator at the yield and releases the worker thread, but returning the
  connection requires resuming it, which needs a thread. Other handlers block in
  `queue.get()` **while holding** worker tokens. Exhaust the tokens with waiters
  and cleanup can never be scheduled, so the 8 connections are never returned
  and every later request blocks forever.
- **Why it is confined to one arm.** `s1_direct/sync` and `s3_middleware/sync`
  open the connection with a plain `with conn_ctx()` inside the handler, so no
  generator is suspended; both ran 3/3 clean. The async arms are unaffected:
  their pool is an `asyncio.Queue`, so waiting holds no thread token.
- **Correction re: `s4_container/sync`.** An earlier note here reported 1/3
  partial failures (`reqs=381`, `checkFailures=1364`) and called them
  unexplained. That claim does not survive checking and is withdrawn. The
  `smoke/cells.csv` in this directory shows `s4_container/sync` **10/10 clean**:
  `check_fails=0` and `window_errors=0` in every cell, with overload cells
  reaching achieved rates of 0.64-0.76, which is the expected shape for an
  overload condition. The 381/1364 figures appear nowhere in this archive -- not
  in `cells.csv`, not in the `wedge*.log`, `repro*.log` or `loop_fixed.log`
  files here. They came from an isolation run that was never archived, so they
  cannot be reproduced or refuted from the evidence, and they may be an
  artifact of the pre-`9522d0d` fractional-rate bug rather than a property of
  this arm. There is no evidence that `s4_container` shares the p2 deadlock
  mechanism, and it must not be described as having one.

### The limiter finding (important, and counter-intuitive)

`gen_apps.py` emitted

```python
anyio.to_thread.current_default_thread_limiter().total_tokens = POOL
```

**after** the lifespan `yield`, putting it on the shutdown path. The bound was
therefore never applied during a run; the limiter sat at anyio's default of 40.
Confirmed at runtime, not by reading source: a frozen server had 40 threads
simultaneously inside `get_db`, which is impossible if the limit of 8 were in
force.

The line was moved before the `yield` — a real bug, now fixed. **But it did not
fix the freeze; it made it deterministic:**

| limiter | result |
|---|---|
| 40 (assignment after `yield`) | intermittent — 9/10 cells null, 1/10 passed |
| 8 (assignment before `yield`) | **7/7 wedged** |

With 40 tokens there were 32 spare workers that could win the race and release a
connection. Correctly applying the limit of 8 removed that slack. This is why the
limiter is not the fix for the deadlock.

The fix that *would* work is to stop a worker thread from blocking on
`queue.get()` at all: acquire an async semaphore of size `POOL` **before** the
sync dependency runs, so excess requests wait at the async layer holding no
thread token. That was not implemented. **The uncommitted limiter change in
`gen_apps.py` is correct on its own terms but must not be shipped without the
semaphore fix** — as committed it makes the deadlock certain rather than rare.

## Reproducing the box from scratch

Nothing on the instance was unreproducible. `sync_to_box.sh` recreates the venv,
installs the pinned versions, and `build_db.py` rebuilds the database and
verifies it against the pre-registration hash. A fresh instance was ~2 minutes.
