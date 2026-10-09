# Tier-2 Phase A report — equal-rate, cross-app, screening, limitations

- **Status:** PRELIMINARY — this is a read-only analysis of existing cells (no box, no new runs). No claim here is final until you confirm it.
- **Scope:** Phase A only (A1–A4). Phase B (box re-measure, 4 h cap) is NOT started.
- **Raw source:** `results/prelim_v1/bench/raw.tsv` (304 cells), `results/prelim_v1/metrics.tsv`, `results/prelim_v1/variants.tsv`, `results/v2/phaseA_equal_rate.tsv` (this dir), `runner/plan.json`, `runner/knee.py`, `runner/k6/harness_t2.js`, `variants/*/patch*.py`, `AI Git`-recorded diffs, `corpus/candidates.json`.
- **Defined tier-2 methodology (restated, not re-derived):** reference 30 s steady window @ 10 rps → `p95_ref`; knee = last qualifying rate on the geometric ladder `{20,40,80,160,320,640,1280,2560,5120}` (single probe); qualify `p95<=3*p95_ref`, err ≤ 1%, `achieved/offered>=0.98` (`runner/knee.py:29-39,95-122`). Grid per arm `{0.25,0.5,0.75,1.0,1.25} x knee`, K=5 at 1.0× and 1.25×, K=3 at the three lower anchors (`runner/knee.py:36-39`). Window 30 s, warmup 10 s, cooldown 10 s, constant-arrival-rate (`runner/k6/harness_t2.js:39-52`).

## A1 — Equal-rate comparison tables

### A1.1 per-arm knee (recorded; single-probe discovery)

| app | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| vstorm-co | 2560 | 1280 | 2560 | 1280 |
| ciiceronee | 5120 | 2560 | 2560 | 1280 |
| azure-samples | 5120 | 2560 | 1280 | 2560 |
| johnsonhk88 | 160 | 160 | 160 | 160 |

Pairs of arms within a single app share an absolute rate only when the rate is in both arms' grids. Shared rates (absolute rps) per app:

| app | rates shared by all 4 arms | knees implicated |
|---|---|---|
| vstorm-co | 640, 1280 | 640 == 0.25×2560 (S1/S3) == 0.5×1280 (S2/S4); 1280 == 0.5×2560 (S1/S3) == 1.0×1280 (S2/S4) |
| ciiceronee | 1280 | 1280 == 0.25×5120 (S1) == 0.5×2560 (S2/S3) == 1.0×1280 (S4) |
| azure-samples | 1280 | 1280 == 0.25×5120 (S1) == 0.5×2560 (S2/S4) == 1.0×1280 (S3) |
| johnsonhk88 | 40, 80, 120, 160, 200 | all arms knee 160, so every rate in the grid is shared |

**No absolute rate is shared across all four apps** (jhk grid tops out at 200; the other three at 640+). The only rate present in ≥1 cell of the three heavy apps is 1280 (12 cells).

### A1.2 all equal-rate cells (36 rows; full detail in `results/v2/phaseA_equal_rate.tsv`)

| repo | arm | rate | anchor | K | p50 med | p95 med | p99 med |
|---|---|---|---|---|---|---|---|
| vstorm-co | S1 | 640 | 0.25x | 3 | 0 | 1 | 1 |
| vstorm-co | S2 | 640 | 0.50x | 3 | 1 | 1 | 1 |
| vstorm-co | S3 | 640 | 0.25x | 3 | 0 | 1 | 1 |
| vstorm-co | S4 | 640 | 0.50x | 3 | 1 | 1 | 1 |
| vstorm-co | S1 | 1280 | 0.50x | 3 | 0 | 1 | 1 |
| vstorm-co | S2 | 1280 | 1.00x | 5 | 1 | 1 | 2 |
| vstorm-co | S3 | 1280 | 0.50x | 3 | 1 | 1 | 2 |
| vstorm-co | S4 | 1280 | 1.00x | 5 | 1 | 2 | 6 |
| ciiceronee | S1 | 1280 | 0.25x | 3 | 0 | 1 | 1 |
| ciiceronee | S2 | 1280 | 0.50x | 3 | 1 | 1 | 1 |
| ciiceronee | S3 | 1280 | 0.50x | 3 | 1 | 1 | 3 |
| ciiceronee | S4 | 1280 | 1.00x | 5 | 1 | 1 | 5 |
| azure-samples | S1 | 1280 | 0.25x | 3 | 0 | 1 | 1 |
| azure-samples | S2 | 1280 | 0.50x | 3 | 1 | 1 | 1 |
| azure-samples | S3 | 1280 | 1.00x | 5 | 1 | 1 | 2 |
| azure-samples | S4 | 1280 | 0.50x | 3 | 1 | 1 | 1 |
| johnsonhk88 | S1 | 40 | 0.25x | 3 | 3 | 4 | 5 |
| johnsonhk88 | S2 | 40 | 0.25x | 3 | 2 | 2 | 4 |
| johnsonhk88 | S3 | 40 | 0.25x | 3 | 2 | 3 | 4 |
| johnsonhk88 | S4 | 40 | 0.25x | 3 | 2 | 3 | 3 |
| johnsonhk88 | S1 | 80 | 0.50x | 3 | 3 | 4 | 6 |
| johnsonhk88 | S2 | 80 | 0.50x | 3 | 2 | 2 | 3 |
| johnsonhk88 | S3 | 80 | 0.50x | 3 | 2 | 3 | 79 |
| johnsonhk88 | S4 | 80 | 0.50x | 3 | 2 | 3 | 84 |
| johnsonhk88 | S1 | 120 | 0.75x | 3 | 2 | 3 | 118 |
| johnsonhk88 | S2 | 120 | 0.75x | 3 | 2 | 2 | 69 |
| johnsonhk88 | S3 | 120 | 0.75x | 3 | 2 | 3 | 140 |
| johnsonhk88 | S4 | 120 | 0.75x | 3 | 2 | 3 | 108 |
| johnsonhk88 | S1 | 160 | 1.00x | 5 | 2 | 3 | 103 |
| johnsonhk88 | S2 | 160 | 1.00x | 5 | 1 | 2 | 91 |
| johnsonhk88 | S3 | 160 | 1.00x | 5 | 2 | 3 | 158 |
| johnsonhk88 | S4 | 160 | 1.00x | 5 | 1 | 2 | 66 |
| johnsonhk88 | S1 | 200 | 1.25x | 5 | 1 | 1 | 104 |
| johnsonhk88 | S2 | 200 | 1.25x | 5 | 1 | 2 | 90 |
| johnsonhk88 | S3 | 200 | 1.25x | 5 | 1 | 2 | 134 |
| johnsonhk88 | S4 | 200 | 1.25x | 5 | 1 | 1 | 55 |

### A1.3 own-knee cells (rate == knee, K=5) — needed because the ciiceronee S3 collapse occurs at a rate not shared across all four ciiceronee arms

| repo | arm | knee | reps | p50 med | p95 med | p99 med | err% (max) | fidelity (min) | win reqs min..max |
|---|---|---|---|---|---|---|---|---|---|
| vstorm-co | S1 | 2560 | 5 | 0 | 1 | 1 | 0.0000 | 1.0000 | 76798..76803 |
| vstorm-co | S2 | 1280 | 5 | 1 | 1 | 2 | 0.0000 | 0.9999 | 38397..38400 |
| vstorm-co | S3 | 2560 | 5 | 3 | 5 | 18 | 0.0000 | 0.9995 | 76763..76803 |
| vstorm-co | S4 | 1280 | 5 | 1 | 2 | 6 | 0.0000 | 0.9998 | 38392..38400 |
| ciiceronee | S1 | 5120 | 5 | 0 | 1 | 4 | 0.0000 | 0.9999 | 153590..153628 |
| ciiceronee | S2 | 2560 | 5 | 0 | 1 | 4 | 0.0000 | 1.0000 | 76798..76805 |
| **ciiceronee** | **S3** | **2560** | **5** | **252** | **289** | **5000** | **0.0000** | **0.6707** | **51513..59623** |
| ciiceronee | S4 | 1280 | 5 | 1 | 1 | 5 | 0.0000 | 0.9999 | 38397..38401 |
| azure-samples | S1 | 5120 | 5 | 0 | 1 | 1 | 0.0000 | 0.9999 | 153591..153616 |
| azure-samples | S2 | 2560 | 5 | 0 | 1 | 1 | 0.0000 | 0.9999 | 76794..76804 |
| azure-samples | S3 | 1280 | 5 | 1 | 1 | 2 | 0.0000 | 0.9993 | 38374..38392 |
| azure-samples | S4 | 2560 | 5 | 0 | 1 | 1 | 0.0000 | 0.9999 | 76790..76803 |
| johnsonhk88 | S1 | 160 | 5 | 2 | 3 | 103 | 1.0000 | 0.9998 | 4799..4800 |
| johnsonhk88 | S2 | 160 | 5 | 1 | 2 | 91 | 1.0000 | 1.0000 | 4800..4800 |
| johnsonhk88 | S3 | 160 | 5 | 2 | 3 | 158 | 1.0000 | 0.9994 | 4797..4800 |
| johnsonhk88 | S4 | 160 | 5 | 1 | 2 | 66 | 1.0000 | 0.9998 | 4799..4800 |

### A1.4 observed at equal rates (no load-cause separation in any shared cell)

- Medians: p50/p95 identical to within 1 ms at every shared rate for every app; p99 equal within a few ms, except the jhk lower-load cells (see jhk flag in A4).
- The single repeatable divergence is **ciiceronee S3 at its own knee 2560** (not visible in the shared table): p50 252 ms / p95 289 ms / p99 5000 ms, fidelity 0.67 (51.5k–59.6k of 76.8k requested). Its single-probe knee discovery (2560) qualified; the K=5 grid re-check collapsed. After this finding, ciiceronee S3 is the first cell Phase B re-measures with the tier-1 3-probe median.

## A2 — Cross-app comparison table

| field | vstorm-co | ciiceronee | azure-samples | johnsonhk88 |
|---|---|---|---|---|
| repo (selected) | vstorm-co/pydantic-ai-backend | Ciiceronee/Ciiceronee | Azure-Samples/chat-with-your-data-solution-accelerator | johnsonhk88/AI-Bank-Statement-Document-Automation-By-LLM-And-Personal-Finanical-Analysis-Prediction |
| stars (candidates.json: stars_gh) | 117 | 544 | 1172 | 616 |
| license | MIT | MIT | MIT | Apache-2.0 |
| bench route (plan.json path) | GET /sessions | GET /simulations/active | GET /api/health | GET /api/auth/me |
| route choice | entry app `runner/apps/vstorm_remote.py` → creates the FastAPI app the framework resolves on this repo | live-state handler resolving app services via Depends getters | diagnostic endpoint that requires dependency resolution but is always-200 by contract (`routers/health.py:1-37`) | auth-heavy endpoint exercising the get_db/get_current_user chain end-to-end |
| chain depth (S2) | 2 | 2 | 1 | 3 |
| DI call sites swapped (files in S1/S3/S4 diffs) | S1: server.py; S3: server.py; S4: server.py + pyproject.toml (S4: `runner`-visible entry) | S1/S3: `ciicerone/api/main.py`; S4: main.py + requirements.txt | S1/S3: app.py, dependencies.py, admin router + tests; S4: app.py (16), dependencies.py (147), routers/admin.py (17), tests (loc below) | S1/S3: `api/app/decorators.py`-adjacent seams (db_scope, resolve_current_user) in handlers; S4: container.py (+19), deps.py (12), requirements.txt |
| Depends use-sites (metrics.tsv `depends`, S2→S4) | 3 → 3 | 5 → 5 | 13 → 13 | 24 → 25 |
| repo-wide DI footprint (variants.tsv notes) | 19 Depends | 5 handler Depends + 2 getters | 127 use-sites, 42 test-override sites; central deps.py | 24 use-sites, PG-backed |
| API-layer LOC (prod files touched by S4, @arm_s4) | 2475 (server.py) | 405 (main.py) | 1429 (app.py 330 + dependencies.py 311 + routers/admin.py 788) | 38 (deps.py 20 + container.py 18) |
| test suite (variants.tsv `suite` / `status`) | 1716 / green on all 4 arms | 460 / green on all 4 arms | 2515 / 2515 / 2520 / 2518 (S2/S1/S3/S4), green | 12 / green on all 4 arms |
| equivalence gate result | pass (suite green ×4 arms) | pass (suite green ×4 arms) | pass (suite green ×4 arms) | pass (suite green ×4 arms) |
| seam crossing on bench route | S1: none (imperative); S3: request.state (middleware); S4: container only at the dependency used by /sessions | S1: none; S3: request.state; S4: container via lifespan override + retained Depends | S3: request.state (middleware attaches app.state + guard/validator); **S4: /api/health does NOT cross the container** — `routers/health.py` is not in the S4 diff, handler still `settings: SettingsDep`, diff for that file is empty | S3: middleware owns session lifetime; S4: container provider + `deps.py` reads providers (Depends retained) |

Equivalence gate definition used in this draft: **the arm's own pytest suite passing at the recorded size** (`variants.tsv` status=green for all 16 benchmarked arms). There is no separate response-parity re-check artifact in `analysis/tier2_transform/`; check markers by app gating is from the k6 `check(...)` only (harness_t2.js:85), which asserts `status < 400`. Flag: whether the study's "equivalence gate" means something stricter is unverified (see A4-L1).

## A3 — Candidate screening list (tier-2 selection)

| candidate | stars | outcome | reason / evidence |
|---|---|---|---|
| johnsonhk88/AI-Bank-Statement-… | 616 | selected | ≥50 stars; pytest suite (12 tests) green; PG-bound DI chain (variants.tsv:16-19) |
| Ciiceronee/Ciiceronee | 544 | selected | ≥50 stars; 460-test suite green (variants.tsv:6-9) |
| vstorm-co/pydantic-ai-backend | 117 | selected | ≥50 stars; 1716-test suite green (variants.tsv:2-5) |
| Azure-Samples/chat-with-your-data-solution-accelerator | 1172 | selected | ≥50 stars; ~2515-test suite green (variants.tsv:10-13) |
| vstorm-co/agenticos | 4 | rejected | below star cutoff (candidates.json stars_gh=4) |
| Azure-Samples/document-reviewer | 1 | rejected | below star cutoff (candidates.json stars_gh=1) |
| blessedrebus (krawl) | — | rejected at preflight | no pytest suite — standalone CLI script (preflight.sh:76-78; variants.tsv:14) |
| infosecinnovations/docker_containers/shabti_api | — | rejected at preflight | unit gate hangs without local OpenSearch/LangSmith infra (preflight.sh:72-74; variants.tsv:15) |

## A4 — Limitations of these cells (each with evidence)

| # | limitation | evidence |
|---|---|---|
| L1 | Equivalent-rate comparisons exist only within an app (not across apps; no absolute rate is in all four apps' grids) | A1.1 table; jhk grid ≤200 vs 640–5120 grids |
| L2 | Knees known only to a factor of 2 and capped at 5120; any knee hitting the ladder top is a lower bound (azure S1, ciiceronee S1) | knee.py:33 LADDER ends at 5120; A1.1 knee values |
| L3 | Single-probe knee discovery vs tier-1's 3-probe median; all conclusions rest on one discovery pass | knee.py:12-15 |
| L4 | K=3 at the three lower anchors; only median + min/max, no CI | knee.py:36-39; phaseA_equal_rate.tsv K column |
| L5 | 1 ms latency floor: p50/p95 sit at 1 ms for all three heavy apps, so sub-ms DI differences are not resolvable | A1.2/A1.3 tables |
| L6 | azure S4 bench route bypasses the container seam: `routers/health.py` unchanged in arm_s4 (empty diff), handler still `async def health(settings: SettingsDep)`; depends stays 13 | git diff `main..arm_s4 -- src/backend/routers/health.py`; metrics.tsv azure S2/S4 row |
| L7 | jhk window-errors anomaly: at rate 160 the 5 reps are binarized (window_errors ∈ {0,4800}); ≥2 reps exceed the 1% error gate while p95 stays 1 ms. Pattern is consistent with the auth JWT expiring mid-bench (all-401 burst), not a load effect. Knee = 160 for all arms means the "collapse-free" jhk result is contingent on valid-token reps | raw.tsv johnsonhk88 rate=160 rows; harness_t2.js:84 (`r.status >= 400`); fix for Phase B: per-rep token refresh |
| L8 | S4 semantics differ between apps: jhk S4 adds a container provider (depends 24→25) but the route still resolves through Depends; azure S4 crosses on the admin router but not on /api/health; vstorm/ciiceronee S4 keep Depends + container providers | metrics.tsv (depends col); A2 seam-crossing rows |
| L9 | Only one of four apps is DB-bound on the bench route (jhk; fresh AsyncSessionLocal + SELECT per request); load ≠ representative for the other three | variants.tsv:16; prior per-arm code read |
| L10 | Fidelity gate counts arrival rate (window_requests/offered) and status<400; response bodies are not validated under load (discardResponseBodies=true) | harness_t2.js:51,83-85 |
| L11 | "Equivalence gate" unverified as a distinct artifact — this draft uses suite-green as the gate; a stricter parity gate would need a defined procedure | no equivalence artifact found in analysis/tier2_transform (only suite + smoke/check) |

## B0 watch item (blocker to confirm before Phase B, not part of Phase A results)

The brief requires Phase B box to match Tier-1 (plan `voc-c-8c-16gb-150s-amd`, 8 vCPU, 16 GB). `runner/plan.json` box section records 4 vCPU / 8192 MB with note "deployment pending user permission" (planned size for the tier-2 box used for these 16 arms); the deployed box handoff was `216.128.147.46` (runcard in `/tmp/opencode/study_box_t2_ip`). Confirm at B0 which plan is authorized before any Phase B run.

---

*All cells, screening facts, and LOC counts above are transcribed from the files listed in the header; recomputed where noted. Treated as preliminary until you confirm.*