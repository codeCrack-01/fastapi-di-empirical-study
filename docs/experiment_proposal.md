# Experiment Proposal — Dependency-Management Strategy × Runtime Resources

**Status:** design-only (phase 1). No benchmark code ships with this document;
implementation and execution are separate, gated phases (§11).

**Companions:** census results in `docs/result_draft_01.md`, journal-style
write-up in `docs/methodology_journal.md`. This proposal extends the census
(RQ1–RQ3) into a controlled experiment.

---

## 1. Abstract

The census of 2,179 accepted FastAPI repositories established that real projects
use mostly *framework-native* dependency injection (`Depends`) or direct
construction, and a handful of idioms
(class-based dependencies, `current_*` request-scope, module aliases,
`provide_*` locators, `.as_form`) exist but are rare. On the S1–S4 strategy
taxonomy used here (§3.1), the dominant strategies are S1 direct construction
(54.5%) and S2 framework-native DI (32.7%), with S3 manual context wiring
(12.3%) and S4 external containers (0.5%). This proposal turns the
question "does the choice of **dependency-management strategy** cost anything at
runtime?" into a controlled experiment. Using one corpus-grounded mock
application in two workload modes plus wiring-only transformations of two real
census repositories, we compare four strategies — direct construction,
framework-native DI, manual Python dependency passing, and (secondarily) one
external DI container — under fixed hardware and workload, measuring latency,
throughput, CPU, and memory. The design intentionally does **not** attempt to
declare a universal "best DI approach": it tests whether runtime differences
are *measurable* and *practically meaningful*, and reports them as bounds.

---

## 2. Research question and hypotheses

### 2.1 Research question (RQ-E)

For functionally equivalent FastAPI applications, at fixed hardware, workload,
database conditions, and software versions:

- Does the dependency-management strategy (S1 direct construction / S2
  framework-native DI / S3 manual Python DI / S4 external DI container)
  measurably change latency, throughput, CPU utilization, and memory usage?
- How does any measured effect scale with dependency-chain width/depth, request
  arrival rate (concurrency), and the share of request time spent in the
  resolver vs. in handler/business logic?

### 2.1a Research question (RQ5 — "most used vs most effective")

A second, complementary question, framed against the census:

- For the spellings the census found in volume — C1 `Depends(fn)` (62.9% of
  repos), C3 `Annotated[T, Depends(fn)]` (17.6%), C4 generator/yield (34.8%),
  and S1 zero-DI/ direct construction (36.9% by construct presence; 54.5% of
  repos are S1-dominant under §3.1 strategy attribution) — how do measured
  latency, throughput, CPU, and memory differ at fixed load?
- Is the most-used spelling (generator/yield, 34.8% of repos) also the
  empirically best, and what is the change-cost (LOC diff) of moving an
  application between spellings?

RQ5 reuses RQ-E's harness (Section 4) with the construct-spelling arm from
§3.2; it is answered *after* RQ-E's strategy results, on the same stay-locked
preregistration.

### 2.2 Hypotheses

All four preregistered (fixed before data collection):

- **H1 (resolvable differences):** under a DI-dominated workload (Mode A), mean
  per-request latency and CPU time differ across strategies, at the microsecond
  scale, with S1 fastest.
- **H2 (diminishing returns):** under a realistic workload (Mode B), the
  strategy difference is smaller than the run-level measurement error — i.e.
  the resolver overhead is *practically negligible* relative to handler work.
- **H3 (saturation invariance):** the throughput-saturation knee does not
  differ across strategies beyond run-to-run variability.
- **H4 (resource parity):** mean/peak RSS and CPU utilization differ by < 5%
  across strategies under Mode B; measurable differences are confined to
  Mode A.

**Prior evidence.** `analysis/out/bench_di_results.md` (synthetic 40-endpoint
apps, 1500 req/app, best-of-3) showed `Depends()` styles running ~1.5–1.8x a
direct-call baseline on a trivial body (~0.2 ms/request extra). That supports H1
and H2 directionally, but its endpoints were flat (no chain, no fan-in, no DB)
and it had no load-testing rigor. This experiment generalizes it.

---
## 3. Treatments and design boundaries

### 3.1 What is a treatment

Treatments vary **how a handler acquires its dependencies per request**:

| ID | Strategy | Census link | Semantics |
|---|---|---|---|
| S1 | Direct construction (zero-DI) | **1,188 repos (54.5%)** | handler calls dependencies directly: `async with get_db() as session: ...`, explicit `get_current_user(token)`, explicit guard checks |
| S2 | Framework-native DI | **712 repos (32.7%)** | `Depends(get_db)`, `Depends(get_current_user)`, `Depends(require_admin)` — the corpus hub chain |
| S3 | Manual Python DI (explicit context) | **268 repos (12.3%)** | middleware builds a `RequestContext` (session, user) in `request.state`; handlers receive `ctx` explicitly |
| S4 | External DI container *(secondary)* | **11 repos (0.5%)** | `dependency-injector` container (9), `DIContainer` (1), `injector` (1); provider wired via `Depends(get_provider)` |

S1–S4 counts come from the **LLM strategy-attribution census** (`analysis/llm_census.py`, qwen3:14b over all 2,179 repos, 100% coverage after repair; see `docs/methodology_journal.md` §3.2). These *replace* the earlier extractor-based "Census link" estimates of 805 (36.9%) / 1,374 (63.1%) / "~3–6" in the strategy rows — the extractor counted **construct presence** (any `Depends` call site ⇒ "native"), while the LLM census attributes the repo's **dominant wiring strategy**, so repos using both idioms sort into the strategy that governs how handlers acquire dependencies. The extractor numbers remain valid for *construct-prevalence* claims (see §3.2 note and `result_draft_01.md`); the three known external-DI anchor repos (`darkspock/CareerPython`, `darkspock/renfeserver`, `gostgmaer/langchain-knoledgebase-rag`) all landed S4/dependency-injector.

S4 is **mock-only** (§6) and framed explicitly as a synthetic-app question —
"what does a container cost in a small app?" — not a population claim. Even so,
the census found 11 real external-DI-container repos (see §3.1 table), up from
the earlier "~3–6 indicative" probe; the peer-review sample (§5) now contains
5 of them as S4 rows to be verified by reviewers.

### 3.2 What is *not* a treatment (explicit boundary)

These are **census observations within framework-native DI**, reported
descriptively (`docs/methodology_journal.md` §4), and are **not** benchmark
treatments *at the S-strategy level*: `Depends(fn)` vs `Annotated[Depends(...)]`
vs `Security(...)` vs generator/yield dependencies vs class-as-dependency vs
module aliases vs `provide_*` idioms. All are variations *inside* S2; making
each a treatment would explode the matrix and over-weight patterns that appear
in 1–104 of 2,179 repos. Reviewer-facing guarantee: **the census observes; the
experiment tests management strategies.**

**RQ5 extension (construct-spelling arm).** RQ5 ("most used vs most
effective") adds one *focused* comparison inside S2, between the three
high-frequency spellings the census actually found in volume — C1
`Depends(fn)`, C3 `Annotated[T, Depends(fn)]`, and C4 generator/yield
`def dep(yield db)` — plus the zero-DI S1 spelling. This is a deliberate,
preregistered *exception* to the boundary above: 1,371 (62.9%), 384 (17.6%),
759 (34.8%) and 805 zero-DI (36.9%) repos use spellings worth a head-to-head.
Class-as-dependency (28 repos), module aliases (54) and `provide_*` (3)
remain excluded as too rare.
The 1,371/384/759/805 figures are **extractor construct-counts** (presence of
`Depends(fn)`/`Annotated`/generator spellings); the LLM strategy census
§3.1 re-sorts these repos by dominant wiring strategy (S2=712, S1=1,188),
so an RQ5 cell may draw from repos the attribution census calls S1 — the arm
compares *spellings*, not strategy membership, and the sample spread is
validated against both.

---

## 4. Experimental design

### 4.1 Design summary

- **Factors:** Strategy (S1–S4) × Workload mode (A/B) × Arrival-rate level
  (sub-knee / at-knee / over-knee).
- **Layout:** blocked, single machine; **randomized treatment order within
  superblocks** to cancel time drift; R = 5 fresh-process runs per cell.
- **Constant by construction:** application logic, endpoints, response
  serialization, database (identical SQLite seed, same session factory),
  Python 3.12.13, uvicorn, k6, hardware, payloads, auth semantics, seed.
- **Unit of analysis:** run-level median per cell; paired difference
  strategy-vs-S1.

### 4.2 Mock application ("ReviewGate")

One authoritative core (models, services, routers, a `get_deps()` seam); the four
straight-variant renders are generated from that core so that only the
dependency-acquisition adapter differs.

| Aspect | Design | Corpus motivation |
|---|---|---|
| Endpoints | 20 across 3 routers (reviews, users, admin); distinct shapes: list/detail/write/guarded/export | heterogeneous real handlers |
| `get_db` (yield session) | consumed by **all 20** endpoints | top hub — `get_db` 24,014 dependents corpus-wide |
| `get_current_user` (Bearer token) | consumed by 14 | `get_current_user` 11,432 dependents corpus-wide |
| `require_admin` / `require_editor` | 6 / 4 endpoints | `require_admin` 3,030, `require_role` 1,349 corpus-wide |
| Nested chain | `require_admin -> get_current_user -> get_db` (depth 3–4) | median depth 2, max 7 in census |
| Dependency kinds | function-only (no class nodes) | 96.6% bare-function `Depends`; class nodes only 4.1% |
| Auth | Bearer -> `get_current_user` + guard hubs; **no `Security()`** | census shows `Security()` is a flag with zero `scopes` usage; guards are `require_*` hubs |
| Data | seeded in-memory SQLite (10 rows/table), fixed seed | deterministic, no network |

**Workload modes (handler-body switch, one app):**

- **Mode A — DI-sensitive:** handler returns a small JSON after resolving deps;
  resolver share ~ 100% of request time. Upper bound of DI cost.
- **Mode B — realistic:** real SQLite CRUD through the injected session plus a
  fixed `await asyncio.sleep(5 ms)` modeling external I/O; resolver share ~ 2%.
  Lower bound.

Two separate apps would differ only along this same axis; one app with a body
switch gives the same information at half the build + verification cost.
(Optional later knob: chain-depth 2 vs 4.)

**Functional-equivalence guarantee:** one shared pytest suite asserts identical
status codes (200 / 401 / 403 / 404), bodies, and auth rejections on all four
variants, run before any timing, and again after any change.

---
## 5. Real-repository tier (external validity)

Wiring-only transformation of two small, hub-rich census repos; handler logic
stays byte-identical; strategies S1/S2/S3 only (external-DI transforms of real
repos are disproportionate effort for a secondary treatment).

| Repo | Size | Hub structure (from frozen reports) | Strategy set |
|---|---|---|---|
| `mbvgua/fastapi-primer` | 24 files / 3,015 LOC / 31 `Depends` | `get_db` hub ×20 | S1 / S2 / S3 |
| `krazywarez/hutch-notify` | 14 files / 418 LOC / 6 `Depends` | `get_db` ×3 + `require_api_key` ×3 | S1 / S2 / S3 |

Selection criteria (pre-screened from `analysis/out/pattern_features.csv` +
graph hubs): small, wiring-centralized, graph-bearing, fan-out >= 3, hub names
matching the corpus top hubs. Equivalence gated by each repo's own tests (if
present) plus our probe suite. These exercise *real handler bodies* (Mode A is
not meaningful on real repos), so they measure the realistic-workload cell on
authentic code.

---

## 6. Metrics

| Metric | How | Unit |
|---|---|---|
| Latency p50 / p95 / p99 / mean | k6 summary per cell | ms |
| Throughput (saturation) | k6 summary at over-knee level | req/s |
| CPU utilization, %user/%system | external `psutil` sampler on the server process, 100 ms tick | % |
| Average / peak RSS | sampler + `resource.getrusage(RU_MAXRSS)` | MB |
| Allocation count / bytes | `tracemalloc` — **isolated runs only**, overhead flagged | — |
| Startup time | wall-clock to first `/health` 200, 5 repeats | ms |
| Scaling knee | ramping-arrival-rate run; knee = rate where p95 latency departs slope | rps |

`tracemalloc` runs are excluded from every timing figure; they answer "does the
strategy change allocation count?", not "is it faster?"

---

## 7. Load-testing methodology and controls (k6)

**Scenarios** (single shared JS harness; target URL via env):

1. **Steady-state sweep:** constant-arrival-rate at three levels per cell —
   sub-knee (~50% of knee), at-knee, over-knee (~150%). Knee is calibrated in a
   pilot (this machine) before data collection; the same three levels are used
   for all strategies in that mode.
2. **Ramping run:** 1 -> saturation over 5 min per strategy per mode to
   visualize the knee (single repetition, visualization only).

**Protocol per run (strict, scripted):** fresh server process -> warm-up
(abandon first N requests / first 10 s) -> measurement window (30 s) -> ramp
down -> cooldown (>= 10 s) -> process terminated. Sampler runs as a separate
process, pinned off-core, writing its own file; k6 writes raw CSV per run.

**Controls:**

- Python pinned 3.12.13; uvicorn and k6 versions pinned and recorded.
- **Single uvicorn worker** (isolates resolver cost from process scheduling;
  multi-worker scaling is a different, documented, out-of-scope question).
- `taskset`: server on dedicated core(s), sampler on another, k6 capped in
  concurrency so the load generator is never the bottleneck.
- Fixed `PYTHONHASHSEED`; identical asyncio loop policy across strategies;
  keep-alive HTTP; fixed payloads and auth tokens (one valid admin, one valid
  user, one invalid).
- Randomized treatment order inside each superblock; all runs for a mode are
  interleaved rather than blocked by strategy, so any thermal/scheduler drift
  hits all strategies equally.
- R = 5 fresh-process repetitions per cell; manual superblock rotation to spread
  across the day.

**Environment reporting (mandatory for validity):** `lscpu`, kernel, cpufreq
governor, turbo status (disabling turbo requires root — if not possible this is
reported as a variance source, mitigated by randomization and repeats, not
eliminated), memory, disk; the **same machine runs the entire matrix**.

---

## 8. Statistical analysis plan

- Unit = run-level median (not per-request, which inflates n).
- Primary contrast: strategy vs S1, **paired within session** (randomized order
  makes sessions comparable), bootstrap 95% CI on the median difference.
- Preregistered effect threshold: if the S2-S1 latency delta at Mode B is below
  the run-level standard error, H2 is accepted as "negligible" and reported as
  a bound (`delta < x ms`), not a zero.
- H4 is evaluated on RSS/CPU deltas with a 5% boundary; multiple-comparison
  caveat on the three arrival-rate levels is stated and adjusted (Holm) where
  crossing of tests occurs.
- Analysis script is written and committed **before** data collection
  (preregistration); results tables are generated by it without post-hoc
  carving.

---
## 9. Limitations and threats to validity

| Threat | Detail | Mitigation |
|---|---|---|
| Construct validity | "performance" proxied by latency/CPU/RSS; the real differentiator of DI may be developer time, untested here | claim is bounded to runtime resources; developer-time stays qualitative (§10) |
| Construct validity | endpoint mix and chain width are artificial | corpus-grounded hub structure; real-repo tier |
| Internal validity — runtime confounders | GC, GIL, laziness, asyncio loop, loop-policy differences | single worker; identical async-identical handlers; fixed `PYTHONHASHSEED`; fresh processes |
| Internal validity — measurement | sampler and k6 add load; tracemalloc distorts timing | sampler/k6 pinned off-core; constant across strategies; tracemalloc isolated |
| Internal validity — drift | thermal/CPU-frequency drift over 4 strategy x N runs | randomized superblocks; R=5; cooldown; interleaved modes |
| External validity | synthetic app; single machine; 1 worker; no network/connection-pool/caching layers | real-repo tier; documented hardware; explicit non-goals |
| Functional equivalence | wiring-only transforms can smuggle divergence (init order, error paths) | shared core + template render; integration suite on 4 variants; independent pass-by |
| Conclusion validity / power | effects may be tiny; over-interpretation of CIs | run-level units; preregistered threshold; bounds, not point claims |
| Mock realism | in-memory SQLite + fixed `sleep` stand in for real DB/network | DB conditions constant by construction; flagged, not hidden |
| Single-machine benchmarking | turbo/scheduler noise not fully removable without root | pinning + randomization + repeats + documented governor; stated as residual |
| Small external-DI evidence | S4 is a small population (11 repos, 0.5%) | S4 kept secondary, mock-only, framed as synthetic-app cost; the 11-repo census count is now exact (peer-reviewed sample includes 5 S4 rows) |
| GIL / single-worker choice | reviewer may ask about multi-worker behavior | declared out of scope; process-scaling is OS scheduling, not DI resolution |

**Weaknesses a reviewer will likely challenge (stated preemptively):** (a) the
single-worker design cannot speak to multi-worker deployment; (b) Mode A handler
"does nothing" is deliberately unrealistic — it is an upper bound, and labelled
as such; (c) wiring-only transformation fidelity on real repos rests on the
integration suite; (d) benchmarks on one machine, however controlled, are not
reproducible-by-others without the same hardware class — mitigated by pinned
software + raw outputs + full protocol disclosure.

## 10. Claim boundaries

- We will **not** claim a universal "best DI approach".
- We will report: measurable vs negligible (bounded) runtime differences,
  direction (S1 relative ordering), and scaling behavior with concurrency.
- Ordering claims are limited to this machine, these workloads, these versions.
- The practical takeaway is allowed to be: "under realistic handler work the
  management strategy does not matter at runtime; under DI-only work it is
  measurable but small" — a claim the mock bounds from both sides.

## 11. Feasibility, timeline, artifacts

**Run budget (this machine):** mock = 4 strategies x 2 modes x 3 levels x 5
repeats = 120 steady runs (~30 s each + cooldown) + startup + ramping + pilot
calibration ≈ 3-4 h wall clock. Real tier = 2 repos x 3 strategies x 3 levels x
5 repeats = 90 runs similarly bound. Fits a single attentive day per tier.

**Timeline (undergrad, ~4 weeks):**

| Week | Work |
|---|---|
| 1 | ReviewGate core + S1/S2; equivalence suite; seed DB |
| 2 | S3/S4 renders; real-repo transforms (fastapi-primer, hutch-notify); extend suite |
| 3 | k6 harness + scenarios; pilot to calibrate knee levels; sampler + randomization; analysis script pre-registered |
| 4 | Full matrix runs; generate tables; write results + limitations |

**Artifacts (created during implementation phase, not here):**

```
docs/experiment_proposal.md            <- this document (design)
analysis/experiment/mock_app/core/     <- authoritative core (models, services, routers)
analysis/experiment/mock_app/straights/  <- S1-S4 rendered variants + get_deps seam
analysis/experiment/mock_app/tests/    <- functional-equivalence suite
analysis/experiment/real/              <- wiring-only transforms of the 2 repos
analysis/experiment/k6/                <- harness.js + scenarios (steady, ramp)
analysis/experiment/run_experiment.py  <- orchestrator: order randomization,
                                           warm-up, window, cooldown, sampling, CSV
analysis/experiment/results/           <- raw runs + summary.md + env report
analysis/experiment/analyze.py         <- pre-registered analysis (tables, CIs)
```

Implementation, execution, and analysis are gated phases that begin only after
this design is approved.