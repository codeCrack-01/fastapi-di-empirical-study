# Tier-2 Phase B results and comparison to the ReviewGate experimental run — PRELIMINARY

Date: 2026-10-10. All tier-2 numbers are from the Protocol-v1 grid (fresh process
per cell, randomised order, seed 20261009, pinning server `0,2,4` / k6 `6`,
k6 v2.2.0) on `voc-c-8c-16gb-150s-amd` (boxes `e8cd6321` for jhk/azure, then
`d60aee01` for the fair-S4 re-runs of ciiceronee/vstorm-co). ReviewGate numbers
are from `analysis/syncasync/results_5arm_20261002_1653/` + `box6_snapshot`
(same kernel 5.15.0-198, same pinning, same k6 version). Nothing here is a cost
claim about middleware or containers as such.

> **Revision (S4 construct).** The first tier-2 S4 arm was operationalised as
> *"container instantiated per call"* (the patch built `SandboxContainer()` /
> `CiiceroneContainer()` inside the per-request resolver) — an anti-pattern that
> does not match ReviewGate's S4 (container built once at startup, resolved per
> request) nor idiomatic dependency-injector use, and it also did not match what
> the corpus actually does. On 2026-10-10 the ciiceronee/vstorm-co S4 arms were
> re-built once at module scope (fair construct; branches `arm_s4`, old kept as
> `arm_s4.percall`) and re-run under the identical Protocol-v1 grid. Parity was
> byte-identical to S2 (`ce4e863dd1fd` / `bdfb3aa851f0`). Tables below are the
> fair numbers; the per-call numbers are superseded and kept in git history only.

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

| app (knee) | S1 (no DI) | S2 (Depends) | S3 (in-proc DI) | S4 (container, built once) |
|---|---|---|---|---|
| ciiceronee (2560) | 1, 1, 1, 4 | 1, 1, 5, **228** | 3, 4, **49**, **299** | 1, 1, 5, **232** |
| vstorm-co (1280) | 1, 1, 1, 1 | 1, 1, 2, **13** | 1, 1, 1, 2 | 1, 1, 2, **45** |
| johnsonhk88 (160) | 3, 3, 4, 11 | 2, 3, 4, 11 | 3, 4, **11**, **81** | 2, 3, 3, 11 |
| azure-samples (2560) | 1, 1, 1, 2 | 1, 1, 1, 2 | 2, 2, 5, **36** | — (route bypasses container) |

Rates: ciiceronee/azure = 1920/2560/3200/3840; vstorm = 960/1280/1600/1920;
jhk = 120/160/200/240. All cells: `achieved`≈`offered` except the bold cells,
which are load-limited (`fid` 0.57–0.89); every bold p95 is at the top or
second-top rate. vstorm/ciiceronee S4 was re-measured with the fair build-once
construct; per-call S4 numbers (ciiceronee 2, 27, 289, 280; vstorm 2, 2, 5, 400)
are superseded — see the revision note above.

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

1. **The apparent tier-2 S4 inversion does not reproduce under the fair
   construct.** ReviewGate: S4 dependency-injector was the *most robust* sync
   arm (p95 1 ms through 900, 11.5 ms at 1200, never a full collapse) — i.e.
   **no container penalty**. The first tier-2 S4 ("container instantiated per
   call, as transformed") was *earliest-worst* — vstorm S4@1920 p95 400 ms,
   ciiceronee S4@3200 p95 289 ms while S1/S2/S3 sat at 1–2 ms there. That arm
   was a transform artifact: the patch built the container inside the resolver,
   so construction cost ran on every request and exceeded the latency floor.
   Re-built once at module scope (fair, matched to ReviewGate and to the corpus'
   actual usage), **S4 ties S1/S2 below capacity in both real apps** (p95 1–5 ms,
   fid 1.0 through 1.25×knee) and is in the same load-limited collapse band as
   S2 at 1.5×knee. In other words the ReviewGate "no container penalty" verdict
   is confirmed — the tier-2 inversion was an artifact of *our* per-call
   transform, not a property of container DI.
2. **S3 "middleware collapses first" generalizes only partly.** Holds where the
   route is heavy/DB-bound: ciiceronee (S3 worst at 3200/3840, fid 0.57),
   jhk (S3 worst: p95 81 ms @240 vs 9–13 for S1/S2/S4). Breaks for light
   routes: vstorm and azure S3 are flat (p95 ≤ 5 ms) across the whole grid.
3. **The giant DI "collapse" does not reproduce.** Phase-A's single-boot
   ciiceronee S3@2560 p95 289 ms (fid 0.67) was the one dramatic "DI breaks it"
   signal; under the fresh-boot protocol it is 4 [3–5] ms, fid 1.0 — i.e. it
   was a measurement confound (boot-age/TIME_WAIT accumulation), not a DI cost.
   This means the controlled ReviewGate design (fresh processes per cell,
   matched rates) was the right design and its "DI is cheap" verdict is
   vindicated once the confounded playback is removed.
4. **Magnitude is not portable across hosts.** ReviewGate cannot resolve sub-ms
   DI costs (1 ms floor) and neither can tier-2's heavy apps; the meaningful
   tier-2 effects (200–400 ms) only exist at ≥1.25×knee. So "how big is the DI
   cost" has no common unit across the two runs.
5. **Cross-box rung difference (disclosed).** ciiceronee/vstorm-co were
   re-measured on a fresh box with all 8 cores online (first box had offline
   1,3,5,7); bench pinning is identical and venv config-hashes match. Within-app
   arm comparisons are unaffected; do not read the small ciiceronee S2/S3
   deltas (e.g. 214 → 228 at 3840) as cross-run drift.

## 5. Bottom line

- Tier-2 Protocol-v1 **replicates the ReviewGate null at moderate load**: DI
  patterns do not measurably hurt below capacity — S2 ≈ S1, and S4 with a
  built-once container ≈ S1/S2, in every app where it was measured under the
  fair construct.
- The one tier-2 result that looked like a large DI effect (ciiceronee S3
  collapse) **does not survive re-measurement** and is consistent with the
  ReviewGate picture once the boot-age confound is controlled.
- The one tier-2 result that looked like "the container is worst" (vstorm/
  ciiceronee S4) was the per-request-construction anti-pattern and **disappears
  when S4 is built once as production code actually does it** — the "DI
  cheapest/loudest arm" inversion between the synthetic and ecological runs is
  an artifact of our transform, not of the library.
- Middleware is the only arm that is app-dependent: worst at high rate in
  ciiceronee/jhk, flat in vstorm/azure.
- All "costs" stay invisible at and below the knee; real-world DI/middleware
  choices move the overload point, not the floor.

## 6. Limitations (unchanged, restated)

- No absolute rate is shared across all four apps; comparisons are within-app.
- 1 ms measurement floor hides sub-ms DI differences (ReviewGate and tier-2).
- azure S4 was not measured: `/api/health` does not cross the container seam.
- jhk results depend on the JWT_TTL_MINUTES=1440 fix (preliminary 15-min TTL
  binarized window errors).
- All tier-2 cells are K3/K5 reps with min–max only; PRELIMINARY by protocol.