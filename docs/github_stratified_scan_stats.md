# GitHub Stratified-Scan Statistics

> **SUPERSEDED IN PART (2026-09-28).** This document predates the retirement of
> the LLM strategy-attribution census. That census assigned S1-S4 to all 2,179
> repositories using `qwen3:14b`; it matched the deterministic extractor on only
> **56.4%** of repositories, and inspection showed the evidence packs it read
> contained a real `Depends` call in just **8%** of cases -- the token `settings`
> in the pack builder's keyword vocabulary matched benign configuration
> identifiers and consumed 63% of all excerpt slots. Its strategy counts
> (S1 1,188 / S2 712 / S3 268 / S4 11) are **withdrawn** and appear below only
> as a record of prior belief. The 327-repository peer review that was built to
> validate them is also retired and has been deleted.
>
> Still valid: any figure described as **construct presence** (does the extractor
> find `Depends`/`Security`/`Annotated` call sites), which is a statement about
> the extractor's output rather than about a repository's dominant strategy.
> **Not valid:** any statement that a strategy population has a known share.
> Manual (S3) and external (S4) strategy prevalence is currently *unquantified*.
>
> Authoritative replacement: `docs/audit_preregistration.md`
> (branch `prereg/census-validation`, commit `670af3b`).

Numbers and reasoning for peer review of the GitHub-scan sampling and the
in-sample static scan. Every number below re-read directly from the artifacts
(file paths given so the claim is verifiable).

_Status: scan is complete; the per-repo two-pass model pass (pass-1
observations, pass-2 reconciliations) is running on an offsite GPU box and its
results are appended when it returns (see "Pending" at the end)._

## 1. Corpus funnel (census)

| stage | count | artifact |
|---|---|---|
| Candidate crawl | **5,000** | `corpus/candidates.json` (target 5,000, `corpus/settings.py`) |
| Excluded | **2,821** | `corpus/exclusion_log.json` (first-failing rule per repo) |
| **Accepted pool** | **2,179** | `corpus/manifest.json["accepted"]` |

Inclusion rules E1–E4 (`corpus/filter.py`), binary existence checks:

- **E1** imports `fastapi` in >= 1 production file (AST extractor)
- **E2** not a fork and not archived (GitHub metadata)
- **E3** `pushed_at` within the last 60 months (temporal window)
- **E4** >= 2 distinct files import FastAPI (rejects single-file/demo projects)

## 2. Stratified sample — the 327

`analysis/sample_stratified.py` -> `analysis/out/sample.json`. Strategy:
stratification by GitHub stars; deterministic draw `random.Random(42)` over
sorted names; sample **frozen** (schema 0.2; the script refuses to re-draw).

| star stratum | stars | population | sample | weight (pop/sample) | coverage |
|---|---|---|---|---|---|
| st0 | 0 | 1,491 | **117** | 12.74359 | 7.8% |
| st1 | 1–9 | 567 | **89** | 6.370787 | 15.7% |
| st2 | 10–99 | 87 | **87** | 1.0 | **exhaustive** |
| st3 | 100+ | 34 | **34** | 1.0 | **exhaustive** |
| **total** | | **2,179** | **327** | | 15.0% |

Allocation reasoning (`STRATA`, `EXHAUSTIVE`, `OVERSAMPLE` in
`sample_stratified.py`):

- st2/st3 (10–99★, 100+★) are the high-complexity tail and taken
  **exhaustively** (87 + 34 = 121).
- The remaining 206 slots split st0:st1 proportional to population with **st1
  oversampled 2.0x** relative to proportional: proportions 1491 / (1491 + 2·567)
  => 117.0 and 2·567 / 2625 => 89.0; integer-perfect via largest-remainder.
- Each member carries a **reporting weight** population/sample so raw sample
  counts are never mistaken for population prevalence.

> Note: star strata are labelled `st0`–`st3` in this document to avoid
> collision with the experiment's **strategy** taxonomy (S1–S4, defined in
> `experiment_proposal.md` §3.1). Both are independent axes.

## 3. In-sample static scan

Extractor: deterministic AST analysis over clones pinned to `commit_sha`
(`analysis/novelty/out/novelty_repo_context.json`; all 327 repos carry a
commit). DI occurrences canonicalized to structural fingerprints
(`analysis/novelty/out/novelty_fingerprints.json`) from
`analysis/novelty/out/novelty_occurrences.json`.

| metric | value |
|---|---|
| repos with >= 1 DI occurrence / fingerprint | **302** (92.4%) |
| **zero-DI repos** | **25** (7.6%) |
| DI-adjacent AST nodes total | **28,089** (mean 85.9, median 26, max 1,654) |
| exported source excerpts (capped 48/repo) | **8,840** rows (12.8 MB context file) |

Stratum DI-node volume (sample): st0 7,421 · st1 8,427 · st2 8,866 · st3 3,375.
Zero-DI by stratum: st0 12 · st1 5 · st2 6 · st3 2.

Fingerprint inventory: **27** distinct structural DI fingerprints across
**187,443 occurrences in 2,797 repos** corpus-wide. **24 of 27 occur
in-sample**; the 3 absent are rare (`C3|CLASS|DOTTED`, `C3|BARE|CLASS`,
`C3|BARE|DOTTED`; 2–92 corpus occurrences each). Most common in-sample
(matched-fingerprint coverage of the 327): `C4|DEF` 282 · `C1|BARE|SIG` 164 ·
`C1|BARE|PARAM` 120 · `C4|USED` 116 · `C3|CLASS|BARE` 55.

Fingerprint corpus totals (fingerprint, occurrences, repos):

| fingerprint | occurrences | repos |
|---|---|---|
| C1\|BARE\|SIG | 83,548 | 1,199 |
| C4\|DEF | 56,644 | 2,573 |
| C3\|CLASS\|BARE | 20,139 | 363 |
| C1\|BARE\|PARAM | 18,195 | 824 |
| C1\|DOTTED\|SIG | 2,178 | 46 |
| C3\|BARE\|BARE | 1,316 | 108 |
| C3\|ELLIPSIS\|BARE | 1,113 | 153 |
| C4\|USED | 1,079 | 832 |
| C2\|BARE\|ascopes | 504 | 111 |
| C3\|CLASS\|ELLIPSIS | 477 | 3 |
| C1\|DOTTED\|PARAM | 422 | 32 |
| C3\|DOTTED\|BARE | 262 | 21 |
| C1\|EMPTY\|SIG | 254 | 85 |
| C1\|ELLIPSIS\|PARAM | 252 | 9 |
| C3\|DOTTED\|DOTTED | 216 | 5 |
| C1\|ELLIPSIS\|SIG | 201 | 12 |
| C1\|CLASS\|SIG | 149 | 20 |
| C2\|ELLIPSIS\|ascopes | 116 | 5 |
| C3\|CLASS\|DOTTED | 92 | 5 |
| C3\|CLASS\|EMPTY | 89 | 37 |
| C1\|CLASS\|PARAM | 72 | 11 |
| C1\|EMPTY\|PARAM | 45 | 37 |
| C3\|CLASS\|CLASS | 42 | 6 |
| C2\|CLASS\|ascopes | 26 | 11 |
| C3\|ELLIPSIS\|DOTTED | 8 | 2 |
| C3\|BARE\|CLASS | 2 | 1 |
| C3\|BARE\|DOTTED | 2 | 1 |

## 4. Review-layer derivation

- Stratification weights come from the frozen sample (`analysis/out/sample.json`).
- Star quartiles for the review grids (Q1..Q4) are assigned by
  `scripts/compile_review.py` from `analysis/out/covariates.csv`, which covers
  all 327 repos (GitHub + libio snapshots — no live GitHub API needed).
- Rows are pre-seeded for every sample repo, so zero-DI repos appear in the
  tables with zeroed stats rather than being dropped.

## 5. Peer-review notes / caveats

- Pool = "accepted" under E1–E4, **not** all 5,000 candidates; prevalence
  statements refer to the accepted corpus (2,179), re-weighted per stratum when
  extrapolating.
- Stars are a snapshot at draw/compile time; E3 means as-of-scan repos pushed
  within 60 months.
- Extractors are deterministic AST code; the 27-fingerprint taxonomy bounds
  what the static scan can express — the LLM pass exists to catch what the
  catalog misses.

## 6. Where the judge run landed

Two-pass model evidence for all 327 in-sample repos is complete (compute pod,
qwen3:14b, 7 stages, 36/36 journaled chunks):

- `job_state.stage = complete`, `blocked: false`; `repo_check` spanning the
  36 chunks (8,840 excerpts with source context, 33 repo_check chunks).
- Full job archive pulled to `pod_results/judge_full.tar.gz`; sha256
  `51d1ecc21547e7defbd894caa0cf1fea8a12d7255efc1bff16814f6339c3d458` (verified
  against the pod checksum) and extracted locally under `pod_results/`.
- Consensus labels for the 27-fingerprint taxonomy: **9 known / 11 false_pos /
  7 variant** (single-rater annotate stage; see §5 caveat on verification
  overrides).
- 28,089 DI nodes across 302/327 repos (25 repos with zero DI); 293/327 repos
  gained ≥1 pass-2 reconciliation after inventory blindly missed them;
  188/327 have ≥1 `missed_by_inventory` item.
- 325 `missed_by_inventory` patterns across 188 repos; **0/325 carry an
  inventory fingerprint ID**, and the 72 with non-native mechanism language
  (container/`thread-local`/`app.state`/`lifespan`/`factory`/`override`/
  `middleware`/`manual`/... ) are folded into the Tier-B catalog (§7) as
  pass-2 candidate mechanisms.
- Weighted to the accepted 2,179-repo universe: 88.6% of repos had ≥1
  inventory-missed reconciliation in pass 2; 59.0% have ≥1 missed-by-inventory
  item; 91.2% have ≥1 non-zero DI node.
- Final totals (verified against raw chunks): 28,089 DI nodes across 302/327
  repos (25 zero-DI); 841 pass-1 observations; 794 pass-2 reconciliations;
  **0 novel fingerprints** (nothing beyond the 27-shape taxonomy).
- Hardcopy compiled locally: `scripts/compile_review.py --results
  pod_results/remote/results` wrote `analysis/out/review/review.tsv`,
  `review.xlsx`, and 327 per-repo `Q*/<owner__repo>/review.md` evidence pages
  (label sums: 147 known / 69 variant / 644 false_pos / 0 external / 0 novel).

## 7. Swappable-pattern catalog (observed interchangeability of C1–C4)

Discovery + 3-type screen over the accepted corpus (no GPU). It measures the
paper's central claim that the four DI constructs (C1 `Depends`, C2 `Security`,
C3 `Annotated[..., Depends]`, C4 generator/yield) are **mutually swappable
spellings of one injection mechanism**: every provider written in two or more
constructs within a repo is an *observed swap instance*. Re-derives
provider-level occurrences from `corpus/reports/*.json` (provider field: C1/C2
`argument`, C3 `depends_argument`, C4 `name`) and scopes to the 2,179 accepted
repos. Outputs: `analysis/swappable/out/catalog.json`,
`patterns_swappable.tsv`, `patterns_context_bound.tsv`,
`patterns_over_capture.tsv`.

- **Scope**: 2,179 accepted repos; 170,141 provider occurrences; 37,992 distinct
  providers; **3,291 swap candidates** (a candidate = one provider used via ≥2
  constructs within the same repo), plus **72** pass-2 non-native mechanism
  candidates appended to Context-bound (3,291 + 72 = 3,363 reconciled).
- **Screen** (per candidate): Over-capture when **every** fingerprint is
  false_pos/unknown; Swappable when ≥1 construct has a known/variant label and
  the provider is reused in ≥2 repos with a plain argument shape; Context-bound
  otherwise (single-repo provider, non-plain shape, or the pass-2 mechanism
  candidates).
- **Results**: Swappable (generic / interchangeable) **1,142**; Context-bound
  **1,593**; Over-capture **628**. Swappable breakdown: 933 pure `C1|C3` pairs
  (Depends ↔ Annotated — the directly interchangeable form), 197 `C1|C3|C4`
  (also generator-provider), 7 `C1|C4`, 5 involving C2.
- **Top generic providers** (multi-repo, in sweep order): `get_current_user`
  (101 repos), `get_db` (98), `get_session` (63), `get_settings` (54),
  `require_admin` (32), `oauth2_scheme` (32), `security` (19),
  `get_db_session` (18), `get_auth_service` (17), `bearer_scheme`/`_bearer`
  (16), `get_redis` (11). 183 Swappable pairs fall inside the 327-sample and
  carry stratum/weight.
- Verified spot excerpts (in-sample): e.g.
  `Annotated[AsyncSession, Depends(get_db)]` (EndofTimeWorks/pluris-haven
  `server/pluris_server/dependencies.py:30`),
  `Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]` (same
  file/line), `Annotated[str, Depends(oauth2_scheme)]`
  (IBM/docling-pipelines `src/docpipe/api/auth/dependencies.py:79`) — genuine
  DI in both `Depends` and `Annotated` forms.
- **Caveats**: labels are single-rater (qwen3:14b, nondeterministic) and some
  canonical shapes read as false_pos over-capture (e.g. `C3|CLASS|BARE`,
  `C4|USED`), so the screen treats them as a signal, not ground truth;
  Swappable count is the benchmark-ready *interchangeable pairs* candidate.
  **This validation path is retired.** It depended on validating against the
  human-review verdicts of the 327-sample and on the LLM strategy-attribution
  census (S1 1,188 / S2 712 / S3 268 / S4 11), both of which are withdrawn
  (`methodology_journal.md` §3.2). No peer-review verdicts exist for the S1–S4
  arms, and no strategy populations are quantified. The pre-registered audit in
  `docs/audit_preregistration.md` replaces this.
- **Reviewer-facing artifacts (peer-review kit): DELETED.** The 327-row workbook,
  the per-repo evidence pages, `pattern_gallery.md`, and the verdict tables have
  all been removed from the repository. They validated an LLM's output, not a
  classifier. Nothing in this section is a current deliverable.