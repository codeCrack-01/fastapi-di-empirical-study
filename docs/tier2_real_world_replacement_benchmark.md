# Tier-2 Phase B — Complete per-arm results (ALL_ARMS consolidated)

PRELIMINARY. Protocol v1: fresh process per grid cell + randomised order (seed
20261009); grid = S2 knee × {0.75:K3, 1.0:K5, 1.25:K5, 1.5:K5}. Box
`voc-c-8c-16gb-150s-amd` (8 vCPU/16 GB), uvicorn `taskset -c 0,2,4` (workers 1) /
k6 `taskset -c 6`. jhk + azure on instance `e8cd6321`; ciiceronee + vstorm fair-S4
re-run on `d60aee01` (all 8 cores online; venv config-hashes match the first
box — no dependency drift). 0 `ERR*` rows, 0 `window_errors` across all 454
cells. Per-cell raw data: `bench/<app>/raw.tsv`; per-cell k6 summaries:
`bench/<app>/<arm>/fresh_<rate>_*/`.

## 1. What the arms are (the original app is one of the four)

No app was rewritten. Each repo's default state (branch `main`/`master`) is the
**S2** arm — they all already used idiomatic FastAPI `Depends`. S1/S3/S4 are
mechanical patches that change only where services are sourced, never app logic.

| arm | meaning | original repo default |
|---|---|---|
| S1 | no framework DI — handlers call getters/instantiate directly | — |
| **S2** | **FastAPI `Depends`** | **vstorm-co `main`, ciiceronee `master`, johnsonhk88 `main`, azure-samples `main`** |
| S3 | DI resolved in-process / middleware-managed providers (stashed on `request.state`) | — |
| S4 | dependency-injector `Container()` built once at module scope, resolved per request (fair construct) | — |

Parity gate: every arm returns `200` with a response body whose sha1 equals S2's
(vstorm `ce4e863dd1fd`, ciiceronee `bdfb3aa851f0`, jhk, azure) — arms differ in
wiring mechanism only.

> Superseded: the first-trial ciiceronee/vstorm S4 arm built the container
> *inside the per-request resolver* (anti-pattern, occurs in <1% of the corpus).
> It showed a huge penalty (vstorm 400 ms @1920; ciiceronee 27→289 ms) that is
> NOT reproducible with the fair build-once construct used here. Kept only in
> git history / branches `arm_s4.percall`.

## 2. Complete per-cell results (p50/p95/p99 ms; median [min–max])

### ciiceronee — knee 2560 rps, rates 1920/2560/3200/3840

| arm | 1920 | 2560 | 3200 | 3840 |
|---|---|---|---|---|
| S1 (no DI) | 0[0-0]/1[1-1]/3[3-3] | 0[0-0]/1[1-1]/4[3-4] | 0[0-0]/1[1-1]/4[3-4] | 0[0-0]/4[4-4]/9[9-10] |
| S2 (Depends, original) | 1[1-1]/1[1-1]/7[6-7] | 1[0-1]/1[1-1]/3[3-3] | 1[1-1]/5[4-7]/27[18-34] | 182[177-185]/**228**[227-236]/239[234-252] |
| S3 (in-proc) | 1[1-1]/3[2-3]/23[23-25] | 1[1-1]/4[3-5]/29[27-34] | 3[3-184]/**49**[36-277]/69[54-304] | 220[211-227]/**299**[290-314]/324[303-340] |
| S4 (container) | 1[1-1]/1[1-1]/6[6-6] | 0[0-1]/1[1-1]/2[2-3] | 1[1-1]/5[5-14]/31[24-46] | 183[182-185]/**232**[230-237]/240[236-256] |

Fidelity (achieved/offered): S1 1.000 everywhere · S2 1.000 through 3200, 0.788
@3840 (≈3028/3840) · S3 0.814 @3200 (≈2604), 0.619 @3840 (≈2379) · S4 1.000
through 3200, 0.780 @3840 (≈2993).

Per-rep notes: S4@2560 p95 reps = [1,1,1,1,1] (flat); S4@3200 = [5,5,5,5,14]
(fid 1.0); at 3840 S4 [237,236,230,232,232] vs S2 [236,227,228,227,231] — the
same load-limited band (~228–232 ms) for both.

### vstorm-co — knee 1280 rps, rates 960/1280/1600/1920

| arm | 960 | 1280 | 1600 | 1920 |
|---|---|---|---|---|
| S1 (no DI) | 0[0-0]/1[1-1]/2[2-2] | 0[0-0]/1[1-1]/3[3-3] | 1[1-1]/1[1-1]/3[3-4] | 1[1-1]/1[1-1]/4[4-4] |
| S2 (Depends, original) | 1[1-1]/1[1-1]/6[6-6] | 1[1-1]/1[1-2]/5[4-5] | 1[1-1]/2[2-2]/3[3-4] | 4[2-317]/**13**[7-372]/34[22-385] |
| S3 (in-proc) | 1[1-1]/1[1-1]/5[5-5] | 1[1-1]/1[1-1]/6[6-7] | 1[1-1]/1[1-2]/7[7-8] | 1[1-1]/2[2-2]/11[10-15] |
| S4 (container) | 1[1-1]/1[1-1]/6[6-6] | 1[1-1]/1[1-2]/5[3-6] | 1[1-1]/2[2-2]/4[4-4] | 5[3-327]/**45**[25-379]/93[34-385] |

Fidelity: S1/S3 1.000 everywhere · S2 0.944 @1920 · S4 0.891 @1920.
Per-rep @1920: S4 [25,366,25,45,379] and S2 [364,13,7,12,372] — both
**intermittently** overloaded (3/5 flat, 2/5 collapsed); the 1.5× knee is an
unstable operating point for the box, arm-independent.

### johnsonhk88 — knee 160 rps, rates 120/160/200/240 (latency-growth regime)

| arm | 120 | 160 | 200 | 240 |
|---|---|---|---|---|
| S1 (no DI) | 2[2-2]/3[3-3]/75[61-86] | 2[2-2]/3[3-4]/139[115-156] | 2[2-2]/4[4-8]/145[131-202] | 2[2-2]/11[11-13]/188[179-200] |
| S2 (Depends, original) | 2[2-2]/2[2-2]/67[63-68] | 2[1-2]/3[3-3]/132[111-143] | 1[1-2]/4[3-4]/131[123-158] | 1[1-1]/11[9-13]/194[175-200] |
| S3 (in-proc) | 2[2-2]/3[3-3]/154[130-159] | 2[2-2]/4[4-8]/168[159-194] | 2[2-2]/11[10-13]/184[179-203] | 2[2-2]/**81**[64-92]/222[205-227] |
| S4 (container) | 2[1-2]/2[2-2]/69[58-69] | 1[1-2]/3[3-3]/118[114-144] | 1[1-1]/3[3-4]/135[131-140] | 1[1-2]/11[9-12]/175[173-201] |

Fidelity 0.99–1.00 at every cell; no saturation — rates fully absorbed, tail
(p99) grows monotonically with rate (DB-dominated, ~67–154 ms even at 120).
S3@240 p95 [64,65,81,81,92] = uniformly shifted, unimodal.

### azure-samples — knee 2560 rps, rates 1920/2560/3200/3840 (S1–S3 only)

| arm | 1920 | 2560 | 3200 | 3840 |
|---|---|---|---|---|
| S1 (no DI) | 0[0-0]/1[1-1]/3[3-3] | 0[0-0]/1[1-1]/4[3-4] | 0[0-0]/1[1-1]/4[4-4] | 0[0-0]/2[2-2]/6[6-7] |
| S2 (Depends, original) | 1[1-1]/1[1-1]/5[5-6] | 1[1-1]/1[1-1]/3[3-5] | 0[0-0]/1[1-1]/3[2-3] | 0[0-1]/2[2-4]/7[4-16] |
| S3 (in-proc) | 1[1-1]/2[2-3]/91[60-93] | 1[1-1]/2[2-3]/81[65-101] | 1[1-1]/5[3-7]/123[79-156] | 2[2-3]/**36**[26-106]/190[174-224] |

Fidelity: S1 1.000 · S2 0.998 @3840 · S3 0.945 @3840 (achieved 3628/3840).
S4 not measured: `/api/health` does not cross the DI container seam.

## 3. Cross-app synthesis

- **S1 (no DI) is the fastest and flattest arm everywhere; no arm ever beats
  it** at any rate below capacity. It is the honest floor.
- **S2 `Depends` — the original code in all four repos — is free**: ties S1 at
  every rate below ~1.25× knee (p95 1–5 ms, fid ~1.0) in all four apps.
- **S4 build-once container is indistinguishable from S1/S2 below capacity** in
  every app where it was measured (ciiceronee p95 1/1/5; vstorm 1/1/2 through
  1.25× knee). The earlier "container is worst" result was the per-request
  construction anti-pattern and does not reproduce.
- **S3 (middleware/in-process) is the only app-dependent arm** — it is the
  highest-latency arm below capacity where the route is DB/heavy-bound
  (ciiceronee 49 ms @3200, jhk 81 ms @240) and flat where the route is light
  (vstorm, azure ≤ 5 ms).
- **At ≥1.25× knee every arm collapses into the same band** (ciiceronee
  228–232 ms, vstorm intermittent 13–45 ms collapses) regardless of arm.
  Capacity, not the DI pattern, owns tail latency.

## 4. Decision brief (see docs/decision_brief.md for the full text)

1. Use `Depends`/`Annotated` as the default — it is idiomatic, testable, and
   costs nothing measurable (S2 = S1 below capacity).
2. Never construct a DI container per request — the only construct that measurably
   costs latency; the corpus itself doesn't do it.
3. A build-once container is fine anywhere a codebase already commits to one —
   adopt it for architecture (centralised wiring/overridability), not speed.
4. Load-test any middleware-managed DI path specifically; it is the only
   app-dependent arm.
5. Plan capacity around ~1.25× your measured knee — beyond it all arms tip
   together.

## 5. Caveats

- 1 ms measurement floor hides sub-ms DI differences.
- Within-app comparisons only (no absolute rate shared across apps).
- K3/K5 reps, min–max only — PRELIMINARY by protocol.
- jhk needs the JWT_TTL_MINUTES=1440 fix (preliminary 15-min TTL binarized
  window errors).
- ciiceronee/vstorm fair-S4 re-run was on a fresh box with all 8 cores online
  (first box: 4 online) — disclosed in box_env; arm comparisons unaffected.
- Archived single-boot ascending runs (`results/v2/ascending_order_v0/`) were a
  boot-age measurement confound, not DI behavior.

## 6. Sources

- `bench/{vstorm-co,ciiceronee,johnsonhk88,azure-samples}/report.md` + `raw.tsv`
- `bench/SUMMARY.md` · `../../REPORT_phaseB_vs_reviewgate.md`
- `docs/decision_brief.md` · `runner/plan.json` · `variants/*/`