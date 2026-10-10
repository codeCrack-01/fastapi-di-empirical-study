# vstorm-co — Tier-2 Phase B, Protocol v1 (fresh boot per cell, randomised)

PRELIMINARY. Direction-only; not comparable in absolute terms to other hosts.
App: vstorm-co (measured via repo's own `pydantic_ai_backends.remote.server.
create_app`; route `GET /sessions`). Box `voc-c-8c-16gb-150s-amd` (8 vCPU/16 GB,
ord), instance `d60aee01-a3e0-4b74-b489-509780617d32`. Pinned: uvicorn
`taskset -c 0,2,4` (`--workers 1`), k6 `taskset -c 6` (all cells recorded
`0,2,4`/`6`). NOTE: this box ran all 8 cores online (the first box had offlined
1,3,5,7 — online `0,2,4,6`); bench pinning identical. Same venv classes
verified by venv-config hash match against the first box's record.

Protocol: fresh server per grid cell, randomised order (seed 20261009). S2 knee
reused = **1280 rps** (`--knee`, 3-probe ascending measurement). Grid =
1280 x {0.75:K3, 1.0:K5, 1.25:K5, 1.5:K5} = 960/1280/1600/1920 rps.
Raw: `raw.tsv` (72 rows, 0 `ERR*`).

S4 was re-measured with the **fair construct** (container built once at module
scope, resolved per request) — see variants/vstorm/s4_patch.py + arm_s4 branch.
Parity: all four arms 200, body byte-identical to S2 (sha1 `ce4e863dd1fd`).
The earlier per-call-construction S4 run is superseded (kept in git history and
on branch `arm_s4.percall`); its table is NOT the one reported below.

## Per-cell results, p50/p95/p99 ms median [min–max]

| arm | 960 (K3) | 1280 (K5) | 1600 (K5) | 1920 (K5) |
|---|---|---|---|---|
| S1 | 0[0-0]/1[1-1]/2[2-2] | 0[0-0]/1[1-1]/3[3-3] | 1[1-1]/1[1-1]/3[3-4] | 1[1-1]/1[1-1]/4[4-4] |
| S2 | 1[1-1]/1[1-1]/6[6-6] | 1[1-1]/1[1-2]/5[4-5] | 1[1-1]/2[2-2]/3[3-4] | 4[2-317]/13[7-372]/34[22-385] |
| S3 | 1[1-1]/1[1-1]/5[5-5] | 1[1-1]/1[1-1]/6[6-7] | 1[1-1]/1[1-2]/7[7-8] | 1[1-1]/2[2-2]/11[10-15] |
| S4 * | 1[1-1]/1[1-1]/6[6-6] | 1[1-1]/1[1-2]/5[3-6] | 1[1-1]/2[2-2]/4[4-4] | 5[3-327]/45[25-379]/93[34-385] |

\* **S4 = dependency-injector container built once (module scope), resolved per
request.**

Fidelity: S1/S3 = 1.000 at every cell. S2 = 1.000 through 1600; at 1920 fid
min 0.944. S4 = 1.000 through 1600; at 1920 fid min 0.891.
`window_errors` = 0 everywhere.

## Top-rate per-rep distribution (1920; no 2560 cells for this app — knee 1280)

- S4@1920 p95 reps = **[25, 366, 25, 45, 379]** ms, fid [1.000, 0.936, 1.000,
  0.998, 0.891] — 3/5 reps near-flat (25–45 ms), 2/5 collapsed. Sporadic
  intermittent overload, NOT a uniform collapse (the per-call S4 run was
  uniformly degraded: [359, 379, 400, 403, 403]).
- S2@1920 p95 reps = **[364, 13, 7, 12, 372]** ms — S2 shows the SAME pattern
  (3/5 flat, 2/5 collapsed) on this box. 1.5x knee (1920) is an unstable
  operating point here regardless of arm.

## Reading (no cost claims)

S1, S3 and S4 stay flat (p95 1–2 ms, fid 1.000) through 1600 (1.25x knee). At
1920 the whole box is past capacity: S2 and S4 both collapse intermittently
(which reps collapse differs run to run). With the fair construct, **S4 is
indistinguishable from the other arms below the top rate** — the earlier 400 ms
S4 collapse is gone and was an artifact of per-request container construction.

## Per-cell diagnostics

`time_since_boot_s` (server process age at cell start) = 0.50–0.52 s (fresh
boot). `timewait_start` median 402, max 559 (no accumulation). Affinity
`0,2,4`/`6` on every cell.