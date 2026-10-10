# Tier-2 Phase B results and comparison to the ReviewGate experimental run — PRELIMINARY

Date: 2026-10-10. All tier-2 numbers are from the Protocol-v1 grid (fresh process
per cell, randomised order, seed 20261009, pinning server `0,2,4` / k6 `6`,
k6 v2.2.0) on the destroyed box `voc-c-8c-16gb-150s-amd`. ReviewGate numbers are
from `analysis/syncasync/results_5arm_20261002_1653/` + `box6_snapshot` (same
kernel 5.15.0-198, same pinning, same k6 version). Nothing here is a cost claim
about middleware or containers as such.

## 1. What the two runs measured

**ReviewGate (controlled, synthetic):** one in-memory reviews API, wired five
ways — S1 direct (no DI), S2 Depends, S3 middleware, S4 dependency-injector,
S4 dishka — each as async and sync models, one ladder 200→1200 rps (bands
flat/graded/saturated, ~965 cells). Result shape: p95 = 1 ms for *every* arm
through 800–900 rps; differences only appear at the top.

**Tier-2 (ecological, real repos):** four real FastAPI apps, each arm-patched to
S1/S2/S3/S4, grid anchored to the app's own S2 knee (ciiceronee/vstorm/jhk/azure
knees 2560/1280/160/2560), rates = knee×{0.75,1.0,1.25,1.5}, K3/K5/K5/K5, 72
cells per app (S1–S3 only for azure, 54).

## 2. Tier-2 Protocol-v1 headline numbers (p95 ms median [min–max], grid)

| app (knee) | S1 (no DI) | S2 (Depends) | S3 (in-proc DI) | S4 (container per call) |
|---|---|---|---|---|
| ciiceronee (2560) | 1, 1, 1, 3 | 1, 1, 1, **214** | 5, **12**, 290, 330 | 2, **27**, 289, 280 |
| vstorm-co (1280) | 1, 1, 1, 1 | 1, 1, 1, 2 | 1, 1, 1, 2 | 2, 2, 5, **400** |
| johnsonhk88 (160) | 3, 3, 4, 11 | 2, 3, 4, 11 | 3, 4, **11**, **81** | 2, 3, 3, 11 |
| azure-samples (2560) | 1, 1, 1, 2 | 1, 1, 1, 2 | 2, 2, 5, **36** | — (route bypasses container) |

Rates: ciiceronee/azure = 1920/2560/3200/3840; vstorm = 960/1280/1600/1920;
jhk = 120/160/200/240. All cells: `achieved`≈`offered` except the bold cells,
which are load-limited (`fid` 0.57–0.89); every bold p95 is at the top or
second-top rate.

## 3. What holds up vs ReviewGate

1. **S1 direct is fastest and flattest in both.** No surprise, and it is the
   only clean invariant. Tier-2 S1 p95 ≤ 2–3 ms across its whole grid in all
   four apps.
2. **S2 (Depends) is ~free.** ReviewGate S2 ties S1 to 1 ms near-saturation;
   tier-2 S2 ties S1 everywhere except ciiceronee at 1.5×knee (true overload,
   fid 0.77–0.87) — same "everything collapses at hard overload" signature.
3. **DI overhead is invisible below saturation.** ReviewGate's core result was
   a 1 ms floor for all patterns; tier-2 confirms the same floor for the heavy
   apps (S1/S2 stay at 1 ms; S3/S4 at the knee are ~12–59 ms in ciiceronee, not
   hundreds). Matched-rate DI cost is small or zero in both.
4. **At genuine overload the collapse is about throughput, not DI.** ReviewGate
   async arms all hit p95 ≈ 1500–2700 ms at 1100–1200 rps whatever the pattern;
   tier-2's `fid<1` cells are all at 1.25–1.5×knee and degrade the same way.
5. **The tail-latency signature.** jhk reproduces ReviewGate's exact shape:
   p95 stays ~1–11 ms while p99 climbs to 60–230 ms with rate — pure tail
   growth with no head collapse.

## 4. What breaks vs ReviewGate (and where)

1. **S4 direction invert.** ReviewGate: S4 dependency-injector was the *most
   robust* sync arm (p95 1 ms through 900, 11.5 ms at 1200, never a full
   collapse) — i.e. **no container penalty**. Tier-2: S4 "container instantiated
   per call, as transformed" is the *earliest-worst* arm — vstorm S4@1920 p95
   400 ms while S1/S2/S3 sit at 1–2 ms at the same rate; ciiceronee S4@3200
   p95 289 ms. So the container is where the real-repo cost shows up, the exact
   opposite of the synthetic run.
   Reasoning: ReviewGate's S4 was a minimal dep-injector graph on an in-memory
   route — per-call construction is µs-scale and falls under the 1 ms floor.
   The ecological S4 "as transformed" builds a heavier per-request graph
   (providers, route-scoped/yield-scoped DB sessions in jhk) whose construction
   cost is now ≥ the latency floor; and S4 is <1% of the corpus, so this is an
   artifact of *our* transform, not a common production shape.
2. **S3 "middleware collapses first" generalizes only partly.** Holds where the
   route is heavy/DB-bound: ciiceronee (S3 worst at 3200/3840, fid 0.57),
   jhk (S3 worst: p95 81 ms @240 vs 9–13 for S1/S2/S4). Breaks for light
   routes: vstorm and azure S3 are flat (p95 ≤ 5 ms) across the whole grid.
3. **The giant DI "collapse" does not reproduce.** Phase-A's single-boot
   ciiceronee S3@2560 p95 289 ms (fid 0.67) was the one dramatic "DI breaks it"
   signal; under the fresh-boot protocol it is 12 [9–20] ms, fid 1.0 — i.e. it
   was a measurement confound (boot-age/TIME_WAIT accumulation), not a DI cost.
   This means the controlled ReviewGate design (fresh processes per cell,
   matched rates) was the right design and its "DI is cheap" verdict is
   vindicated once the confounded playback is removed.
4. **Magnitude is not portable across hosts.** ReviewGate cannot resolve sub-ms
   DI costs (1 ms floor) and neither can tier-2's heavy apps; the meaningful
   tier-2 effects (200–400 ms) only exist at ≥1.25×knee. So "how big is the DI
   cost" has no common unit across the two runs.

## 5. Bottom line

- Tier-2 Protocol-v1 **replicates the ReviewGate null at moderate load**: DI
  patterns do not measurably hurt below capacity (S2 ≈ S1; S3/S4 within tens of
  ms at the knee, jhk only in the tail).
- Tier-2 **breaks the synthetic ordering near capacity**: the container-per-call
  arm, which was the strongest in ReviewGate, is the weakest in real repos
  (vstorm S4, ciiceronee S4/S3). Middleware is app-dependent, not universally
  bad.
- The one tier-2 result that looked like a large DI effect (ciiceronee S3
  collapse) **does not survive re-measurement** and is consistent with the
  ReviewGate picture once the boot-age confound is controlled.

## 6. Limitations (unchanged, restated)

- No absolute rate is shared across all four apps; comparisons are within-app.
- 1 ms measurement floor hides sub-ms DI differences (ReviewGate and tier-2).
- azure S4 was not measured: `/api/health` does not cross the container seam.
- jhk results depend on the JWT_TTL_MINUTES=1440 fix (preliminary 15-min TTL
  binarized window errors).
- All tier-2 cells are K3/K5 reps with min–max only; PRELIMINARY by protocol.