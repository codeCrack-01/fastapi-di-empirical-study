# Semaphore fix — p2_depends/sync deadlock

Evidence for the 20-run deadlock gate run on a fresh box after the fix in
commit `60e5804`. **These are stress-test results, not study data.** Nothing
here is a measurement of the execution models and none of it may be used as
such; there is still no valid smoke or main-run dataset.

## What was run

| file | what it is |
|---|---|
| `stress20.log` | **the gate.** 20 consecutive runs, `loop.py`, real `apps.p2_depends.sync.app:app`, rate 750 (= the p2 capacity knee from the discarded smoke), limiter 8 |
| `diag5.log` | 5 runs through `diag_app:app`, same rate, for the `/__diag` counters |
| `soak2x.log` | 5 runs at rate 1500 (2x), real app — a measurement, **no** pass/fail verdict attached |
| `diagcap.py` | the counter sampler used for the two captures below |
| `diag_app.py` | diagnostic wrapper; see the fix note at the bottom |
| `config_hash.json` | box config + database hash at test time |
| `smoke_equivalence.json` | 8 arms x 13 probes on the box after the change, byte-identical |

`loop.py`, `poll.py` and the original `diag_app.py` came from this archive
(see the parent directory); the two `.PORT-COLLISION-DISCARD.log` files from
an earlier attempt are described under "A discarded attempt" below.

## Box

Same spec and pinning as the discarded smoke, so the gate is comparable to
the runs that found the bug:

- `voc-c-8c-16gb-150s-amd`, `ord`, AMD EPYC-Milan, 8 vCPU / 4 physical cores
- server `0,2,4`; k6 `6`; SMT siblings `1,3,5,7` taken offline before any run
  (verified: `changed=[1,3,5,7] failed=[]`, online set `{0,2,4,6}`)
- python 3.12.14, fastapi 0.141.1, starlette 1.6.0, anyio 4.15.1,
  uvicorn 0.52.4, aiosqlite 0.22.1, dependency-injector 4.49.1, k6 v2.2.0
- database sha256 `ec432e8211b9767a114d9ff60f584e94038217bb3aa7a6590faecc38ed67fec8`
  — matches the pre-registration
- `config_sha256 63a541fdc641813468fd514182792f3bd6b38cf816c987308023dbe81b37e716`
  (differs from the smoke's `5550afe4…` because `gen_apps.py` and the p2 app
  changed; computed from file hashes, and identical to the same tree hashed
  locally, so local and box sources agree)
- DB rebuilt on the box by `build_db.py` and hash-verified read-only before
  anything ran

## Result of the gate

20/20 clean. Every cell: `reqs≈22,530  fails=0  dur=52s`. The pre-fix
signature was `reqs=0 fails=600 dur=62s` (see `../loop_fixed.log`), so the
cells are directly comparable and none of them reproduce it.

## Counters

Sampled every 2 s during one run at each rate (27 samples each, 0 errors):

| | rate 750 | rate 1500 |
|---|---|---|
| `total_tokens` | 8 | 8 |
| `borrowed_tokens` min/max | 0 / 5 | 0 / 8 |
| `pool_free` min/max | 0 / 8 | 0 / 8 |
| `os_threads` min/max | 2 / 9 | 2 / 9 |
| `window_requests` | 22,533 | 24,708 |
| `window_p95` (ms) | 6 | 795.65 |
| `checkFailures` | 0 | 0 |

Two things worth reading off this. `total_tokens` reads 8 at runtime, which
is the direct confirmation that the limiter fix (`ac4afda`) put the bound on
the serving path — the archived README's 40-vs-8 finding, re-verified. And
`borrowed_tokens` reaches 8 at rate 1500 with `pool_free` at 0, yet the run
completes: the semaphore admits fewer requests than the pool can serve, so
the wait-for-connection edge is never closed by a token-holder. Before the
fix, saturating both was exactly what wedged it.

At 2x, p95 goes from 6 ms to 796 ms while throughput stays near the knee
(24,708 requests in a 30 s window at an offered 1500/s). That is queueing at
the semaphore, which is what a bounded admission control does under overload.
It is reported as a measurement and is deliberately **not** scored.

## A discarded attempt

The first `diag5` and `soak2x` runs were started concurrently and both bind
port 8900, so they collided. `diag5` cell 05 returned `reqs=49` and `soak2x`
cell 01 returned `reqs=868 fails=955` followed by `server exited early
(rc=3)`. Both are artifacts of the collision, not properties of the fix, and
were discarded and re-run sequentially. The discarded logs were renamed
`*PORT-COLLISION-DISCARD.log` on the box and were not carried into this
archive, because nothing in them is a valid reading; the collision is
recorded here instead.

## Note on `diag_app.py`

The copy in the parent directory was broken: its handler was a plain `def`,
so it ran in a worker thread with no event loop, and
`anyio.to_thread.current_default_thread_limiter()` raised `NoEventLoopError`
— `/__diag` returned HTTP 500. The endpoint had therefore never produced a
reading. The copy here is `async def` and works. The parent-directory copy is
left unfixed in git history as it was at the time; this one is the corrected
version and is what produced the counters above.
