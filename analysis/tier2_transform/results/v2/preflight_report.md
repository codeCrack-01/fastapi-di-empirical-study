# Tier-2 Phase B — preflight report (items 3a–3f)

Date: 2026-10-09. Box: `voc-c-8c-16gb-150s-amd` (8 vCPU/16 GB, ord),
instance `e8cd6321-daa8-4f44-9ad6-da6adedc114a`, pinned online set `0,2,4,6`
(nproc 4). Commit `06ea0e6`. All runs pinned (`TIER2_PIN=1`).

## 3a. jhk token fix validated — PASS

One low-rate S2 cell (`parity.py lowrate johnsonhk88 S2 10`):

| app/arm | rate | p50 | p95 | p99 | window_errors | requests | fidelity |
|---|---|---|---|---|---|---|---|
| johnsonhk88/S2 | 10 | 3 | 4 | 4 | **0** | 300 | 1.00 |

Root cause was `api/app/config.py` `JWT_TTL_MINUTES=15` (token expired mid-arm,
binarizing window_errors to {0,4800}); fixed by `JWT_TTL_MINUTES=1440` in all
four jhk arms. Evidence: `results/v2/preflight/johnsonhk88/lowrate.tsv`.

## 3b. Status + body parity across arms — PASS (with branch checkout fixed)

Each arm is freshly booted on its own branch (distinct commits confirmed:
e.g. ciiceronee S2 `acc7fec` / S1 `ac33281` / S3 `b36fab1` / S4 `6ccd6fc`).
Bench route GET ×3 per arm:

| app | route | S2 | S1 | S3 | S4 | bodies equal |
|---|---|---|---|---|---|---|
| johnsonhk88 | /api/auth/me | 200/88B | 200/88B | 200/88B | 200/88B | OK (sha 2176aacc2d83) |
| vstorm-co | /sessions | 200/64B | 200/64B | 200/64B | 200/64B | OK (sha ce4e863dd1fd) |
| ciiceronee | /simulations/active | 200/41B | 200/41B | 200/41B | 200/41B | OK (sha bdfb3aa851f0) |
| azure-samples | /api/health | 200/291B | 200/291B | 200/291B | 200/291B | OK (sha 9cd3c9d865ee) |

Note (fixed bug): `phaseB.py`/`parity.py` call `boot()` directly, but `boot()`
originally did not check out the arm branch (only `bench.run_arm` did) — the
first parity pass measured one tree 4×. The checkout is now inside `boot()`;
the table above is the re-run with genuine branch switching.
Evidence: `results/v2/preflight/<app>/parity.tsv`.

## 3c. azure reported as S1/S2/S3 only on the bench route

Bench route is `/api/health`. `git diff main..arm_s4` (azure-samples) does NOT
touch `src/backend/routers/health.py` (only `pyproject.toml`, `app.py`,
`dependencies.py`, `routers/admin.py`, tests). The measured route therefore does
not cross the container on S4 → azure latency is reported for **S1/S2/S3**;
azure S4 is excluded from the latency comparison (health handler unchanged).

## 3d. vstorm measured app — repo's own code

`runner/apps/vstorm_remote.py` is a bench-side ASGI entry (not a
reimplementation): it imports the repo's factory
`pydantic_ai_backends.remote.server.create_app` and instantiates it with a
study config (token, runtime allowlist). The DI transformation lives in the
repo file `src/pydantic_ai_backends/remote/server.py`; the wrapper only supplies
the uvicorn import string. Measured app = repo's `create_app(...)`.

## 3e. Installed packages per arm within each app — identical

All four arms of an app share that app's single `.venv`; arm branches change
only app source, so the installed set is constant per app. Installed dists
(via importlib.metadata; three venvs have no `pip`) :

| app venv | pkgs | sha256[:16] |
|---|---|---|
| vstorm-co | 83 | 4857c3da1acf080d |
| ciiceronee | 166 | b736cd9d331289d2 |
| azure-samples | 151 | fbe9aa6fa41c44cd |
| johnsonhk88 | 183 | 0b1584e00360db17 |

Dependency-manifest deltas base..arm_s1 are empty (only app source changed).
Exception: azure `arm_s4` adds `dependency-injector>=4.41.0,<5.0` to
`pyproject.toml`; the shared venv already satisfies it (S4 parity = 200), so the
installed set still matches across arms.

## 3f. Run-time estimate from per-cell timestamps — exceeds the 4 h cap

`results/prelim_v1/bench/raw.tsv`: n=304 `cell_s`, min 50.1 / median 50.1 /
max 51.1 s. Revised design (my interpretation: 3 probes at **every** S2 ladder
rung, median; grid = 4 arms × 18):

| app | S2 knee | knee cells (3/rung + 3 ref) | grid cells | total | time |
|---|---|---|---|---|---|
| vstorm-co | 1280 | 27 | 72 | 99 | 82.7 min |
| ciiceronee | 2560 | 30 | 72 | 102 | 85.2 min |
| azure-samples | 2560 | 30 | 72 | 102 | 85.2 min |
| johnsonhk88 | 160 | 18 | 72 | 90 | 75.2 min |

Pure k6: 393 cells × 50.1 s = 19,689 s = **5.47 h**; plus ~5 boots/setups per
app (~15–25 min) → **~5.7–6.0 h for all four apps**. The matched **grids alone**
(288 cells) are 4.01 h. This is above the pre-registered 4 h run cap.

- **ciiceronee first run** (per brief): 102 × 50.1 s = 85.2 min + 5 boots
  ≈ **~1.5 h** (fits).
- If "3-probe knee" means single-probe ramp + 3 probes only at the knee, the
  knee stage shrinks (~15 cells/app), total ≈ **5.0–5.3 h** — still over 4 h
  because the grid dominates.
