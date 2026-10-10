# ciiceronee — Tier-2 Phase B, Protocol v1 (fresh boot per cell, randomised)

PRELIMINARY. Direction-only; not comparable in absolute terms to other hosts.
App: ciiceronee (FastAPI). Box `voc-c-8c-16gb-150s-amd` (8 vCPU/16 GB, ord),
instance `d60aee01-a3e0-4b74-b489-509780617d32`. Pinned: uvicorn `taskset -c
0,2,4` (`--workers 1`), k6 `taskset -c 6`; all cells recorded server `0,2,4`,
k6 `6`. NOTE: this box ran all 8 cores online (the first box had offlined
1,3,5,7 — online `0,2,4,6`); bench pinning identical. Same venv classes
verified by venv-config hash match against the first box's record.

Protocol: server process restarted for every grid cell, cells presented in
randomised order (seed 20261009). S2 knee reused = **2560 rps** (`--knee`,
measured 3-probe in the archived ascending run; ref_p95 = 2 ms). Grid =
S2knee x {0.75:K3, 1.0:K5, 1.25:K5, 1.5:K5} = 1920/2560/3200/3840 rps.
Raw: `raw.tsv` (72 rows, 0 `ERR*`).

S4 was re-measured with the **fair construct** (container built once at module
scope, resolved per request) — see variants/ciiceronee/patch.py + arm_s4 branch.
Parity: all four arms 200, body byte-identical to S2 (sha1 `bdfb3aa851f0`).
The earlier per-call-construction S4 run is superseded (kept in git history and
on branch `arm_s4.percall`); its table is NOT the one reported below.

## Per-cell results (72 cells), p50/p95/p99 ms median [min–max]

| arm | 1920 (K3) | 2560 (K5) | 3200 (K5) | 3840 (K5) |
|---|---|---|---|---|
| S1 | 0[0-0]/1[1-1]/3[3-3] | 0[0-0]/1[1-1]/4[3-4] | 0[0-0]/1[1-1]/4[3-4] | 0[0-0]/4[4-4]/9[9-10] |
| S2 | 1[1-1]/1[1-1]/7[6-7] | 1[0-1]/1[1-1]/3[3-3] | 1[1-1]/5[4-7]/27[18-34] | 182[177-185]/228[227-236]/239[234-252] |
| S3 | 1[1-1]/3[2-3]/23[23-25] | 1[1-1]/4[3-5]/29[27-34] | 3[3-184]/49[36-277]/69[54-304] | 220[211-227]/299[290-314]/324[303-340] |
| S4 * | 1[1-1]/1[1-1]/6[6-6] | 0[0-1]/1[1-1]/2[2-3] | 1[1-1]/5[5-14]/31[24-46] | 183[182-185]/232[230-237]/240[236-256] |

\* **S4 = dependency-injector container built once (module scope), resolved per
request.**

Fidelity (achieved/offered): S1 = 1.000 at every cell. S2 = 1.000 through 3200;
at 3840 fid min 0.788 (achieved ≈3028 of 3840). S3 fid min 0.814 at 3200
(achieved ≈2604) and 0.619 at 3840 (≈2379). S4 fid min 1.000 through 3200 and
0.780 at 3840 (≈2993). `window_errors` = 0 everywhere. The 3840 cells for every
arm are **load-limited** (achieved rate saturates, p50 jumps to ~180–230 ms);
latency there reflects the achieved rate, not the offered.

## 2560 and 3200 per-rep distributions (S4)

- S4@2560 p95 reps = **[1, 1, 1, 1, 1]** ms — flat, fid 1.000. (Per-call S4 run:
  21...59 ms.) S4@3200 p95 reps = **[5, 5, 5, 5, 14]** ms, fid 1.000. (Per-call
  S4 run: 236...289 ms.)
- S4@3840 p95 reps = **[237, 236, 230, 232, 232]** ms, fid 0.78–0.80 — the same
  collapse band as S2@3840 **[236, 227, 228, 227, 231]**, fid 0.79–0.82.
  Whichever arm you name, both sit at ≈ equivalent load-limited p95 ~228–232 ms.

## Reading the transition (no cost claims)

S1, S2 and S4 all flatten at **≤ 5 ms, fid 1.000 through 3200 (1.25x knee)**.
S3 (middleware) is the first to deviate: 49 ms / fid 0.814 at 3200. Every arm
collapses into an identical band at 3840 (1.5x knee). With the fair construct,
**S4 is indistinguishable from S2 and S1 below capacity** — matching the
ReviewGate controlled study and johnsonhk88's built-once S4.

## Per-cell diagnostics

`timewait_start` median ≈ 500–900, no runaway accumulation under fresh boots.
`cpus_allowed_server`/`cpus_allowed_k6` = `0,2,4`/`6` for all cells.
`time_since_boot_s` holds true process age (fixed in `6c9defa`).