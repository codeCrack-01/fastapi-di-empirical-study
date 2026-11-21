# DEVIATIONS.md

## Known gap (recorded per Phase 0 rule 1)

- **Earlier controlled benchmark ran on uncommitted changes with a configuration-hash mismatch.** The ReviewGate-R grid (480 cells) reported in the paper was produced from a working tree whose configuration fingerprint did not match the archived box fingerprint; a local recomputation gives a different value. This is documented in main.tex (Section "Threats to Validity", internal validity). The Phase 3 re-run (E1) supersedes it; the old grid is retained only for a comparison appendix.
- Tag `eval-freeze-1` created on commit `9b065d3` (local only; Overleaf remote rejected the tag push, "wrong branch"). Local tag is authoritative for this freeze.
- Phase 2 blocking heuristic (2.4) and name-collision sensitivity (2.3) are not yet implemented; `extractor/verdict.py` has an import error (`is_local_module` from config) that must be fixed first.
- `lock_pip.txt` generated with `uv pip freeze` (no pip in venv); 36 packages recorded.
- k6 version available locally: v2.3.0 (work order references v2.2.0; minor version difference to be reconciled in replication package).
- `extractor/verdict.py` repaired: added `is_local_module` to config.py, `ManualDiSite` + missing fields to models.py. All 19 boundary tests pass. Per-repo labels generated (`corpus_labels_v0.5.csv`), audit draw produced (`audit_draw_187.csv`).
- Route-reachability traversal completed: 68.3% of graph-bearing repos (911/1,337) have a route-reachable sync target; 61.4% sync edge share (vs 61.2% all edges). Report: `analysis/out/phase2_route_reachability.csv`.
- 100-target sample prepared: `analysis/out/phase2_sync_sample_100.csv` + codebook `phase2_sync_codebook.md`. Human labeling pending.
- 2x2 app variants built and smoke-tested: async-inline, async-depends, wrapper, limiter-200/1000/4000 (all start and serve). Branches created in ciiceronee repo. Runner: `analysis/tier2_transform/runner/run_2x2.py`. README: `README_2X2.md`.
- Per-repo predicted labels now generated (`analysis/out/corpus_labels_v0.5.csv`: S1=518, S2=1368, S3=286, S4=7) and the stratified audit draw produced (`analysis/out/phase1_1/audit_draw_187.csv`: 60/60/60/all-7, seed 20261105, shuffled). Human labeling still required.
- The 95 imputed-repo blinded sheet was produced for the 48 kit-imputed rows only; the 47 added stratified rows need reproduction from `analysis/out/sample.json` (seed 42, quota S1=11/S2=29/S3=6/S4=1).
- Phase 2 blocking heuristic (2.4) is keyword-based; manual validation on 100 targets not yet done (sample generation timed out).