# Peer review results — IRR, gold standard, parser validation (n=327)

> Supersedes the previous `peer_review_results.md`, `s1s4_interrater_matrix.md`
> and `agreement_recompute.md` (all moved to `deprecated_/`).

## 0. What was built

A **single 327-row table** on which both raters give an S1–S4 verdict —
no `unclear`, no blanks, so nothing is dropped by listwise deletion.

| block | rows | Zain's cell | Yahya's cell |
|---|---|---|---|
| Returned kits (Arm 1 zero-DI 80 + Arm 2b has-DI 200) | 280 | real, else scan | real, else scan |
| Added class-stratified repos (star sample, seed 42) | 47 | scan | independent v0.4 verdict |
| **total** | **327** | | |

Added-repo quota across strategy classes (corpus mix 518/1368/286/7, ≥1 S4 forced): `{'S1': 11, 'S2': 29, 'S3': 6, 'S4': 1}`.

Imputed cells: Zain **42**, Yahya **13** undefined cells replaced by the reviewer scan (`analysis/ai_review_scan.py`).

**The reviewer scan is never counted as a rater.** It only fills undefined
cells and adjudicates disagreements.

## A. Human inter-rater reliability (Zain vs Yahya)

**Headline = the 232 rows both humans actually labelled** (no synthetic
padding).

| scope | n | % agreement | Cohen's κ | Gwet AC1 |
|---|---|---|---|---|
| **4-cat ['S1', 'S2', 'S3', 'S4'] pooled (both human)** | 232 | 97.84% | 0.9475 [0.8967, 0.9892] | 0.9750 [0.9501, 0.9950] |
| binary `{none, DI}` pooled (both human) | 232 | 98.28% | 0.9576 [0.9098, 0.9900] | 0.9709 [0.9387, 0.9930] |

Reference — the whole 327 rows *including* imputed/extrapolated cells
(inflated; shown for continuity only):

| scope | n | % agreement | κ | AC1 |
|---|---|---|---|---|
| 4-cat all 327 | 327 | 93.58% | 0.8514 | 0.9250 |
| binary all 327 | 327 | 93.88% | 0.8427 | 0.9001 |

By arm (both-human rows only):

| arm | n | % agreement | κ | AC1 |
|---|---|---|---|---|
| Arm 1 | 68 | 94.12% | -0.0303 [-0.0584, 0.0000] | 0.9400 [0.8778, 0.9852] |
| Arm 2b | 164 | 99.39% | 0.0000 [0.0000, 0.0000] | 0.9939 [0.9754, 0.9939] |
| strat+ | 0 | — | — | — |

By provenance:

| block | n | % agreement | κ | AC1 |
|---|---|---|---|---|
| both human | 232 | 97.84% | 0.9475 | 0.9750 |
| one imputed in kit | 41 | 82.93% | 0.6106 | 0.8012 |
| both imputed in kit | 7 | 100.00% | 1.0000 | 1.0000 |
| added | 47 | 80.85% | 0.6524 | 0.7670 |

> `both imputed in kit` rows carry the same scan on both sides, so they are
> agreement by construction; this is why the headline excludes every imputed
> cell. The `added` rows are **not** independent humans either — Zain is the
> scan and Yahya the independent v0.4 verdict, so they agree on clear cases
> and differ only on the uncertain (S1/S3-boundary) ones.

## B. Gold standard

Rule: **agreement kept; disagreement → reviewer scan.**

| source | rows |
|---|---|
| disagreement scan adjudicates | 21 |
| rater agreement | 268 |
| added extrapolated | 38 |
| **total** | **327** |

Gold distribution: `{'S3': 19, 'S1': 77, 'S2': 230, 'S4': 1}`

## C. AST parser v0.5 validation

### Agreement with gold

| universe | n | % agreement | Cohen's κ | Gwet AC1 |
|---|---|---|---|---|
| 4-cat ['S1', 'S2', 'S3', 'S4'] | 327 | 91.13% | 0.8064 [0.7466, 0.8643] | 0.8954 [0.8568, 0.9311] |
| binary `{none, DI}` | 327 | 91.44% | 0.7413 [0.6484, 0.8253] | 0.8723 [0.8210, 0.9173] |

### Confusion (gold rows × parser columns)

| gold \ parser | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| **S1** | 54 | 0 | 23 | 0 |
| **S2** | 0 | 229 | 1 | 0 |
| **S3** | 5 | 0 | 14 | 0 |
| **S4** | 0 | 0 | 0 | 1 |

### Per-class precision / recall / F1 (parser = positive, gold = truth)

| class | precision | recall | F1 | tp | fp | fn |
|---|---|---|---|---|---|---|
| S1 | 0.9153 | 0.7013 | 0.7941 | 54 | 5 | 23 |
| S2 | 1.0000 | 0.9957 | 0.9978 | 229 | 0 | 1 |
| S3 | 0.3684 | 0.7368 | 0.4912 | 14 | 24 | 5 |
| S4 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 |
| **macro F1** | | | **0.8208** | | |
| **micro F1** | | | **0.9113** | | |

| binary class | precision | recall | F1 | tp | fp | fn |
|---|---|---|---|---|---|---|
| none | 0.9153 | 0.7013 | 0.7941 | 54 | 5 | 23 |
| DI | 0.9142 | 0.9800 | 0.9459 | 245 | 23 | 5 |
| **macro F1** | | | **0.8700** | | |
| **micro F1** | | | **0.9144** | | |

## D. Caveats

- Headline IRR uses only the 232 rows both humans labelled; the 327-wide
  figure is inflated because imputed cells are agreement by construction.
- The 47 added rows are **not** independent second human judgements: Zain's
  value is the reviewer scan and Yahya's is the v0.4 extractor verdict, so
  they differ only on uncertain (S1/S3-boundary) cases.
- The added draw is **class-stratified with one S4 forced in**, so it is a
  validation sample, not a prevalence sample; S4 still has only a handful of
  rows, so its per-class metrics stay uninformative.
- S3 precision stays low because gold rarely awards S3: humans almost never
  chose it, so surviving S3 labels come from scan adjudication.
- Per-arm κ is degenerate where one class dominates — read AC1.

## Artifacts

| artifact | path |
|---|---|
| Computation | `analysis/evaluate_s1s4_327.py` |
| Numbers | `analysis/out/peer_review_327.json` |
| Reviewer scan (fill/adjudication) | `analysis/ai_review_scan.py` |
| Parser v0.5 | `corpus/reports_v0.5/` |
| Independent v0.4 verdicts | `corpus/reports_v0.4/` |
| Registered 327 sample | `analysis/out/sample.json` |
| Returns | `review_results/merged/per_repo_labels.json` |
| Rubric | `docs/s1s4_reviewer_rubric.md` |
