# A.480 failure diagnosis

Why the 160-cell A.480 leg produced check failures in S2 and S3 and in neither
S1 nor S4. Derived from the per-request `run.csv` / `run.json` dumps retained
under `raw_A480_failing/`.

## What failed

| cell | reps | checkFailures total | median/rep | max/rep | HTTP 500 | status 0 |
|---|---|---|---|---|---|---|
| `s1.A.480` (S2 native `Depends`) | 40 | 29,502 | 770 | 1,057 | 14,190 | 1,122 |
| `s2.A.480` (S3 manual context) | 40 | 3,448 | 84 | 212 | 1,609 | 230 |
| `s0.A.480` (S1 direct) | 40 | 0 | 0 | 0 | 0 | 0 |
| `s3.A.480` (S4 container) | 40 | 0 | 0 | 0 | 0 | 0 |

Failing checks are the harness's two checks, `auth works as intended`
(15,312 / 1,839) and `status is <500` (14,190 / 1,609). Per-rep counts
reconcile exactly against `run.json`'s `checkFailures` for all 80 retained reps.

## Mechanism

The retained `status 0` rows carry the diagnostic text:

```
read: connection reset by peer   (error_code 1220)
EOF                              (error_code 1000)
```

The server is **shedding connections**, not returning logic errors. This is
saturation behaviour, and it is not uniform across strategies.

The two failing cells are the two that add a threadpool hop to authentication:

- **S2** resolves a *synchronous* dependency through FastAPI `Depends`, which
  Starlette dispatches to the anyio worker threadpool.
- **S3** resolves the user in a `@app.middleware` handler wrapped in
  `run_in_threadpool`.

The two surviving cells add no such hop:

- **S1** calls `current_user(conn, request)` inline in the handler body.
- **S4** resolves through the container inline (`c.user_service()`).

So the surprising part is that S1, which *blocks* the event loop, is more
robust at 480 rps than S2, which does not block but pays a threadpool dispatch
per request. On a 4-vCPU / 2-physical-core box the threadpool is the scarcer
resource, and dispatch queueing degrades faster than inline execution. Thread
contention plus queueing, not raw CPU per resolution, is what breaks.

This is a mechanism inferred from status codes, connection-reset text, and the
known difference in how each strategy dispatches authentication. It is
consistent with the data and was not independently instrumented — the
anyio threadpool depth and queue length were not logged.

## Load evidence for the 401s

The `GET 401` counts are large (43,909 for s1, 47,695 for s2) but are **not**
failures: the harness deliberately probes unauthenticated routes, and 401 is the
expected answer there, so `status is <500` passes. Only 15,312 / 1,839 of those
requests additionally tripped `auth works as intended`. Do not report the raw
401 count as an error rate.

## How the paper should state this

At and below the A-mode knee (320 rps) all four strategies are
indistinguishable. Above it, S2 and S3 leave the regime of "slower" and enter
an erroring one, while S4 tracks S1. The honest claim is that S2 and S3
**degrade into connection resets at 480 rps**, not that they are slower there.

## Data gaps, recorded not papered over

- `window_count` and `p99` are absent from all 160 A.480 runs, in both the
  failing and the clean cells. Tail latency at 480 rps does not exist in this
  dataset. `analyze.py` never used `p99` — the preregistered unit is the
  run-level p50 median — so no reported result is affected, but no p99 may be
  quoted at 480.
- The `run_dir` column in `runs_A480.csv` points at
  `results/steady/00-sN.A.480.K`, but the per-request output for that leg was
  actually written to `results/steady_A480/`. `results/steady/` contains no
  `.480` directories at all. The path column is wrong and following it finds
  nothing.
- `knee_A.json` / `knee_B.json` come from separate ramp probes, not from these
  steady runs. They are independent measurements of the same quantity and are
  not expected to match the steady-run transition exactly.
- The box is a 4-vCPU Azure VM under a Microsoft hypervisor, not dedicated
  silicon, and `ambient_load` ran 1.96–2.07 at 480 rps. Paired within-session
  contrasts carry the result; the absolute milliseconds do not generalise.
