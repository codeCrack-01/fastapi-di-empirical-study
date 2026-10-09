# LABEL — Tier-2 preliminary results (16 arms x 5 grid anchors = 304 cells)

- **Box:** 8 vCPU / 16 GB, same class as Tier 1 (Vultr `voc-c-8c-16gb-150s-amd`,
  AMD EPYC-Milan, ord, instance `e8cd6321-daa8-4f44-9ad6-da6adedc114a`; API record).
- **Pinning:** UNPINNED — the tier-2 runner launched uvicorn and k6 without
  taskset, and no Tier-1 core layout was applied during these runs (all 8 CPUs
  online, SMT siblings online).
- **Verdict: DIRECTION ONLY, NOT COMPARABLE IN ABSOLUTE TERMS to any Tier-1 cell.**

Background: `runner/plan.json` previously claimed "4 vCPU / 8 GB, deployment pending";
that was stale and is corrected to `voc-c-8c-16gb-150s-amd` / 8 vCPU / 16 GB / ord, plus
a `phaseB_preflight` block (topology, OS, kernel, python, k6 versions).

Data in this directory is UNTOUCHED (moved from analysis/tier2_transform/results/ on
2026-10-09; 137-file manifest byte-identical pre/post move).