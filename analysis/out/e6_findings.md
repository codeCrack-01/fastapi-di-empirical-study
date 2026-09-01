# E6 human-review findings — structural-sophistication pattern analysis

## Protocol

Blinded human review of a fixed-seed stratified random subsample of the
E6-tutorial-flagged pool **and** an equal-sized unflagged control:

- **Sampling**: `analysis/e6_sample.py`, seed `20260817`, 24 flagged + 24 control,
  stratified by stars bucket x marker-count (flag) / stars bucket (control).
- **Blinding**: presentation order shuffled (seed `424242`); labels assigned from
  README + project tree + dependency profile **before** un-masking flag group.
- **Labels**: `G` genuine application, `U` uncertain (functional but
  research / portfolio / challenge / aspirational), `D` demo / tutorial /
  scaffold / capstone exercise.
- Evidence bundle: `analysis/out/e6_review_evidence.txt`; mapping/labels in
  `analysis/out/e6_labels.csv` (+ `analysis/e6_labels_blinded.py`).

This is a **judgment sample (48/351)**, not ground truth for the whole corpus.

## Unmasked label distribution

| label | flagged (n=24) | control (n=24) |
|-------|----------------|----------------|
| genuine | 16 (66.7%) | 21 (87.5%) |
| uncertain | 6 (25.0%) | 2 (8.3%) |
| demo | 2 (8.3%) | 1 (4.2%) |

- Flagged genuine rate: 66.7% (Wilson 95% CI 46.7–82.0%)
- Control genuine rate: 87.5% (Wilson 95% CI 69.0–95.7%)

## Structural-sophistication index (median) by group x label

| group / label | n | median index |
|---------------|---|--------------|
| flagged / genuine | 16 | 7 |
| flagged / uncertain | 6 | 9 |
| flagged / demo | 2 | 5 |
| control / genuine | 21 | 6 |
| control / uncertain | 2 | 8 |
| control / demo | 1 | 1 |

## Findings

1. **The README tutorial marker is a weak, negatively-loading signal, not a
   classifier.** Most repos carrying `example/demo/learn/sample/template` markers
   in their README are in fact genuine, functional applications: 67% genuine even
   among the flagged pool (vs 87.5% in the unflagged control). The marked repos are
   more often "uncertain + demo" (33% vs 12.5% in control), but genuine-ness is
   still the majority class in both groups.

2. **Structural sophistication separates clear demos from genuine apps.**
   The `D`(demo) repos have the lowest sophistication index (median 1–5:
   KB-NEST challenge=1, MSIT capstone=2, Nile-Connect portfolio demo=5), well below
   the genuine-median of 6–7. So "a toy project does not have a real schema/db/
   auth/cache/integrations" holds at the margin — but with only 3 demos in 48,
   this is thin evidence.

3. **Sophistication does NOT separate the flagged pool from the unflagged pool.**
   Flagged-genuine median index (7) ≈ control-genuine (6). The E6 marker is too
   noisy to be a useful corpus-exclusion rule: most flagged repos are sophisticated
   real apps.

4. **The 'uncertain' bucket is structurally the *richest*, not the emptiest.**
   Uncertain repos have the highest median index (7–10: OWNEX, CEREBRO-X,
   cadence-clinical, dharma_swarm, prima-tech-challenge, Earth-obs lab). These are
   ambitious-but-aspirational: lots of scaffolding, docs, infra signals, but often
   thin or unvalidated runtime cores. This is a distinct pattern from the low-index
   demos.

## Caveats

- Labels are a single (AI) reviewer's blinded judgment; spot-check ~30% for
  inter-rater consistency, and treat rate estimates as indicative only.
- n=48 is small; the demo class (n=3) is too small for statistical claims.
- Clones are depth-1 snapshots; structure reflects the repo's present state, not
  history.