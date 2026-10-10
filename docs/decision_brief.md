# Tier-2 Decision Brief — which DI style should the codebase use?

Status: PRELIMINARY (Protocol-v1 tier-2 grid, K3/K5 reps, round 2026-10-10;
jhk/azure on box `e8cd6321`, ciiceronee/vstorm-co fair-S4 re-runs on
`d60aee01`). Nothing here is a per-library cost claim; it is ordering evidence.

## Question

Should a real FastAPI/DI codebase do DI at all, and if so, in which style? The
four arms are: **S1** no DI (module-level or per-route instantiation),
**S2** FastAPI `Depends`, **S3** DI resolved in-process/middleware-level
(dependency-injector graph resolved without FastAPI), **S4** dependency-injector
container built once at startup, resolved per request.

## Evidence (p95 ms, median across K reps; grid = S2 knee × {0.75,1.0,1.25,1.5})

| app (knee) | S1 | S2 | S3 | S4 fair |
|---|---|---|---|---|
| ciiceronee (2560 rps) | 1 1 1 4 | 1 1 5 **228** | 3 4 **49** **299** | 1 1 5 **232** |
| vstorm-co (1280 rps) | 1 1 1 1 | 1 1 2 **13** | 1 1 1 2 | 1 1 2 **45** |
| johnsonhk88 (160 rps) | 3 3 4 11 | 2 3 4 11 | 3 4 **11** **81** | 2 3 3 11 |
| azure-samples (2560 rps) | 1 1 1 2 | 1 1 1 2 | 2 2 5 **36** | (route bypasses container) |

Bold = load-limited (achieved < offered, fid 0.57–0.89) at ≥1.25× knee. S1 ties
or beats every DI arm at every rate below capacity; no arm ever beats S1.

Fairness note: S4's earlier per-call-construction run (vstorm 400 ms @1920,
ciiceronee 27→289 ms @2560/3200) is superseded — that construct happens nowhere
in the corpus (S4 = 0.5% of repos, idiom is build-once). The fair numbers stand.

## Verdict

1. **Use FastAPI `Depends` (S2) — it is the right default.** It is idiomatic,
   testable, and costs nothing measurable: tier-2 S2 ties S1 at every rate below
   capacity in all four real apps (p95 1–5 ms, fid 1.0 through 1.25×knee), and
   ReviewGate's controlled run shows a 1 ms floor for it near saturation.
2. **Do NOT construct DI containers per request** (the tier-2 S4 anti-pattern):
   it is the only construction that costs real latency (hundreds of ms past
   capacity) and nothing in the wild does it.
3. **A dependency-injector container built once at startup (S4 fair) is fine
   where your stack already commits to one** — it is indistinguishable from
   S1/S2 below capacity in both re-measured apps. Pick it only for its
   architecture (centralised wiring, overridability), not for speed: there is
   no measurable latency benefit or penalty either way.
4. **Middleware/in-process DI (S3) is the only app-dependent arm** — worst arm
   at high rate in ciiceronee (49→299 ms, fid 0.57) and jhk (81 ms), flat in
   the light-route apps vstorm/azure. If you use it, load-test the specific
   path; do not take a universal "middleware is bad" or "middleware is free"
   reading from any single app.
5. **Capacity, not DI, dominates tail latency.** Every arm collapses into the
   same band past ~1.25× knee (identical collapse regardless of arm). Your
   performance lever is rate/capacity planning; DI choice only shifts which
   arm tips first at ≥1.25× knee (in-process S3 tips earliest in 2/3 apps).

## Concrete recommendation for this codebase

- Use `Depends`/`Annotated` (S2 style) as the default wiring for request-scoped
  services and DB sessions (matches jhk's and most real repos' modern usage).
- If you adopt dependency-injector (S4), build the `Container()` **once at
  module/startup scope** and resolve per request; never construct it inside a
  resolver, factory, or route body.
- Avoid putting DI resolution in middleware for hot paths unless load-tested:
  S3 is the only arm with a reproducible penalty at sustained load ≥1.25× knee.
- Re-measure whenever you cross ~1.25× your measured knee: that is where all
  arms (including S1) stop being free.

## Caveats (see REPORT_phaseB_vs_reviewgate.md §6)

1 ms floor; within-app comparisons only (no shared absolute rate); K3/K5 reps;
jhk needs the JWT_TTL_MINUTES=1440 fix; ciiceronee/vstorm re-run on a different
(8-online vs 4-online) core box, arm comparisons still valid.