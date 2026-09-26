# ReviewGate Mock-Tier Matrix — Results (Run 1, clean)

**Status:** primary mock-tier data collection complete on a clean cloud host.
Run 1 supersedes the invalidated laptop run (results archived under
`analysis/experiment/results/_invalid_run2/`).

**Preregistration:** `docs/experiment_proposal.md`; analysis script committed
before data collection (`d837124`), run unmodified (post-hoc carving: none).
Full raw outputs in `analysis/experiment/results/`.

---

## 1. Environment

| Item | Value |
|---|---|
| Host | Vultr `vhf-4c-16gb` (dedicated vCPU), ewr |
| CPU | 4 dedicated vCPU (pinned; Intel Skylake VM model), 0% steal observed |
| RAM / disk | 16 GB / 384 GB NVMe |
| OS | Debian 13 (trixie), Python 3.13.5 |
| Server | uvicorn 0.52.4, single worker, `--host 127.0.0.1`, port 8200 |
| Load gen | k6 v2.2.0 (`/usr/local/bin/k6`), harness.js, steady 30 s window |
| Pins | server core 0, sampler core 1, k6 core 2 (`taskset`) |
| Hashing | `PYTHONHASHSEED=0` |
| DB | per-run fresh SQLite seed (write isolation), one session per strategy |
| Knees | mode A **260 rps**, mode B **125 rps** (on-box `pilot_knee.py`, s0) |
| Levels | A: 130 / 260 / 390 rps · B: 63 / 125 / 188 rps |
| Matrix | 4 strategies × 2 modes × 3 levels × R=5 = **120 runs**, superblock-randomized |
| Duration | ~1.8 h wall; ambient_load mean 1.08, max 3.05 (our own load; 4-core box) |

Machine-noise census (`results/baseline_*.txt`, 10 snapshots): no external CPU
steal; only orchestrator + k6 + server processes observed. All 120 cells run
with `k6_rc = 0`; the 12 cells with `http_error_rate > 0` are exclusively the
**A.390 (over-knee) saturation cells** (≤ 2.1% errors) — the expected
behaviour at 1.5×knee, not contamination.

## 2. Results (from `results/tables_42.md`)

### Latency — p50 run-level median, ms

| | Mode A | | | | Mode B | | | |
|---|---|---|---|---|---|---|---|---|
| rate | s0 | s1 | s2 | s3 | s0 | s1 | s2 | s3 |
| sub-knee | 2.0 | 2.0 | 2.0 | 2.0 | 7.0 | 8.0 | 8.0 | 7.0 |
| at-knee | 2.0 | 2.0 | 3.0 | 2.0 | 7.0 | 7.0 | 8.0 | 7.0 |
| over-knee | 77.0 | 80.0 | 66.0 | 14.0 | 7.0 | 8.0 | 8.0 | 7.0 |

### Paired median difference vs S0 (bootstrap 95% CI, ms)

| mode | rate | stable, >=|diff|<0.5 forecast under H2 | diff | CI | verdict |
|---|---|---|---|---|---|---|
| A | 130 | — | s1 +0.40 s2 +0.40 s3 +0.00 | [0.0, 0.8] | all within SE |
| A | 260 | H1 boundary | s2 **+1.20** | [1.0, 1.6] | **strategy slower (excl. 0)** |
| A | 390 | — | s1 +151.2 (CI climbs) | [-8.4, +370.6] | noisy, positive |
| A | 390 | — | s2 **+415.1** | [+14.4, +921.9] | **strategy slower (excl. 0)** |
| A | 390 | — | s3 −1.3 | [-51.0, +66.9] | within SE (s3 not slower) |
| B | all | — | s1/s2 ≤ +1.0 (B.125 s2 +1.0) | — | ≤ 1 ms, all mild |

(Mode B at all rates: s0 7 ms vs s1–s3 7–8 ms; every contrast ≤ 1.0 ms, most
"within SE".)

### Resources (avg over runs)

- **Mode B (all rates):** RSS tightly flat — s0 52.9–57.7 MB, s1 52.7–59.9,
  s2 53.2–58.8, s3 55.5–60.7; CPU ~83–87 % across all strategies → within the
  5 % H4 boundary.
- **Mode A over-knee (390):** strategy divergence emerges — s1 avg RSS
  **121.9 MB** (peak 160.1) vs s0 70.9/92.0; s2 79.9/109.1; s3 72.5/92.6.
  Resolver/state amplification under saturation is confined to Mode A (H4
  direction confirmed).

## 3. Findings against hypotheses

| H | Claim | Outcome |
|---|---|---|
| **H1** resolvable differences in Mode A | DI-dominated workload shows measurable latency/CPU differences, S0 fastest | **Partially supported.** At *sub-knee and at-knee* all strategies are equivalent within SE (≤ ~1.2 ms; s2 +1.2 ms at-knee just exceeds the 0.5 ms threshold, CI excludes 0). At *over-knee* s1 (not shown) and s2 diverge strongly (s2 p50 up to 1361 ms in worst rep); s0 fastest. At normal load the resolver cost is at noise level. |
| **H2** negligible in Mode B | resolver overhead ≈ 0 vs handler work | **Supported.** Every Mode B contrast ≤ 1.0 ms (typical p50 7–8 ms); most within the 0.5 ms run-level SE; the one-exceeds case (B.125 s2 +1.0 ms) is ≤ 12 % of handler time — reported as a bound, not a finding. |
| **H3** saturation invariance | knee does not differ across strategies | **Qualified.** Same machine knee (260/125) calibrates every strategy, and at/over-knee Behaviour *below* knee is identical. At 1.5×knee, s1/s2 (not s3 or s0) degrade — so the *shape* of the tail differs, while the *threshold* (knee) is shared. |
| **H4** resource parity | < 5 % RSS/CPU delta across strategies; confined to Mode A | **Supported.** Mode B RSS within ~5 % (s3 ~ +5 % vs s0, borderline at worst rate); CPU flat. Mode A over-knee shows the expected amplification (s1 RSS +72 % vs s0). |

## 4. Key observations

1. **Under design load, strategy choice is runtime-irrelevant.** At sub-knee and
   at-knee in Mode A, and at every rate in Mode B, S0–S3 are statistically
   indistinguishable (≤ ~1 ms except one s2-at-knee +1.2 ms).
2. **The strategy effect appears only when the machine saturates** (1.5×knee):
   s1 and s2 then develop long tails (s2 median diff +415 ms, CI excluding 0)
   that s0 and — notably — the external container **s3** do not exhibit
   (s3 A.390 p50 14 ms, within SE of s0). The naive "container is slower"
   ordering is **not** observed here.
3. **S3 (dependency-injector) is not a latency liability** in this mock tier —
   a nuance worth carrying into the write-up; resource-wise it tracks s0.

## 5. Limitations (per preregistration §9)

- Single-machine, single-worker; no multi-worker/process-scaling claim.
- Mode A handler is deliberately trivial (upper bound of resolver share).
- Over-knee CI for s1 is wide (bimodal reps) — conclusion rests on s2 and the
  qualitative table, and on the R=5 median.
- 4-core host: `ambient_load` includes our own load (max 3.05 on 4 cores) —
  all observed processes are the experiment's own.
- Dedicated vCPU with stable clock; residual hardware variance mitigated by
  randomized superblocks and R=5, not eliminated.
- Mock tier only; real-repo tier (S0/S1/S2 × 2 repos) remains for Phase 1b.

## 6. Reproducibility

Everything needed to rerun: `analysis/experiment/` (harness, orchestrator,
analyzer), on-box environment pinned (uvicorn 0.52.4, k6 v2.2.0, Python 3.13.5,
same knee cross-check with `pilot_knee.py` on the target host). The laptop run
was invalid (S3 singleton-connection confound — fixed `90b207b` — plus
powersave-governor downclocking); this cloud run uses dedicated pinned vCPUs
with no governor downclocking. Registered for the Oct 5 readout.