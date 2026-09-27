# Corpus Methodology (FINALIZED 2026-08-06)

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

> **Correction (2026-08-29):** E4 applies a **60-month** recency gate, matching
> `corpus/settings.py` (`E4_MAX_AGE_MONTHS = 60`) and the reported results
> (709 E4 exclusions). An earlier draft here stated 36 months; 60 is what was
> actually run.

## Research Questions

**Origin:** The study originally proposed four RQs. The standalone application-class
question (originally RQ2) was **dropped** and folded into RQ1 as a covariate axis
(supervisor direction): no a priori application-class taxonomy is imposed, and the
covariate view (stars, age) answers "who uses DI" without arbitrary class labels.
**RQ2 (usage/relationships) is a new question** added after an exploratory pass over
the full corpus revealed measurable, undocumented usage patterns beyond construct
prevalence. The graph-complexity question moved to RQ3 and evolution to RQ4.

- RQ1: Which FastAPI DI constructs are used, and how frequently, across open-source projects?
  - DI prevalence is additionally disaggregated by repo covariates (stars, age) as a
    second axis of RQ1 (the folded application-class question).
- RQ2: What dynamic dependency relationships do real FastAPI projects form, and what
  idiomatic roles do dependencies play? *(new — mixed-methods usage analysis)*
- RQ3: How complex are the resulting dependency graphs? *(renumbered from RQ4)*
- RQ4: How has DI usage evolved over time (repo history)? *(deferred)*

**Constructs vs. Usage (definitional line):** a *construct* is a discrete, syntactically
detectable API token (counted from the left-hand token at a call site — `Depends(`, `Security(`,
`dependencies=[...]`). *Usage* refers to how those constructs are composed into dynamic
dependency relationships and idiomatic roles — it requires classifying the argument and
context at each call site (function vs. class vs. classmethod vs. module alias) and the
relationship structure of the dependency graph (fan-in hubs, chained/nested dependencies,
class vs. function nodes). The extractor stores both (construct totals in `aggregate`, call
details in `file_details`, graph in `dependency_graph`); RQ2 re-classifies that stored raw
data with `analysis/usage_patterns.py` — no re-extraction.

## Population
Open-source GitHub repositories that use FastAPI (import `fastapi`, expose >= 1 FastAPI app).

## Target
- **Candidate discovery pool targets 5,000 repos** (`TARGET_CANDIDATES` in
  settings.py) via a best-effort deep crawl of the GitHub dependents list.
- **Accepted (the census) is whatever clears E1–E4** — the 5,000-candidate
  pool yields 2,179 accepted (43.5%); the pool size and accepted count are
  deliberately distinct concepts.
- Expanded in phases (2026-09: pool increased 4,500 → 5,000 candidates;
  +51 accepted under the old gate, no decision altered). The current E1–E4
  gate (revised 2026-09, see `docs/github_stratified_scan_stats.md`) replaces
  the earlier E1–E6 gate (which included the Python-byte-ratio E2 and the
  tutorial-marker E6 flag).

## Discovery (finder.py)
- Primary: **GitHub dependency-graph dependents** of `fastapi/fastapi`
  (`https://github.com/fastapi/fastapi/network/dependents`) — repos whose
  manifests GitHub's dependency graph resolves as depending on fastapi.
  Paginated HTML, snapshotted per page (`corpus/raw_dependents/`).
- Crawl stops at `--target` unique repos (default `TARGET_CANDIDATES = 5000`);
  deep-pagination 429s and the last page are hard best-effort stops.
  `--max-pages` remains only as an absolute safety cap.
- `--include-topic corpus/topic_seed.json` unions the `topic:fastapi` seed as a
  secondary source; `--skip-scrape` replays the snapshotted pages offline.
  The crawl is resumable (checkpoint to `candidates.partial.json`).
- Original choice was Libraries.io `/dependents`; **disabled server-side**
  ("Disabled for performance reasons", librariesio/libraries.io#2647).
  GitHub's dependency graph uses the same manifest-parsing mechanism and is
  the live, fresh equivalent. This substitution is reported under Threats.
- Enrich each candidate via the GitHub REST API: fork/archived flags, pushed_at,
  created_at, language byte ratios, commit count, license, topics.
- Stars are RECORDED as a covariate only, never used as an eligibility filter.
- FastAPI role (primary / auxiliary / MCP-only) is NOT a filter — recorded as covariate
  (`fastapi_files / python_files` ratio + classification flag).

## Recall Benchmark (benchmark.py)
- Independent signal: `topic:fastapi` repository search (GitHub search API,
  sort=stars, top 1000, snapshotted to corpus/topic_seed.json).
- Overlap measured against the candidates pool and the accepted corpus;
  reported as "fraction of the dependency-graph pool an alternative signal
  would have recovered" — bounding the primary source's recall.
- The topic signal is used ONLY as a measurement, never as a pool member or
  eligibility criterion (topic tags are self-selected and not a population definition).

## Eligibility Rules (filter.py)
| Rule | Criterion |
|------|-----------|
| E1   | `fastapi` imported in >= 1 PRODUCTION file (extractor). |
| E2   | Not a fork and not archived. |
| E3   | `pushed_at` within the last 60 months. |
| E4   | Scale: >= 2 distinct files importing `fastapi` (`E4_MIN_FASTAPI_FILES`, rejects single-file/demo projects). |

- Every candidate decision records per-rule PASS/FAIL + detail (exclusion_log.json).
- Repos failing E1-E4 are excluded with the first failing rule logged.
- Thresholds are schema-versioned constants in corpus/settings.py.
- **Incremental `--delta` mode** processes only candidates not yet decided,
  merging new decisions into the existing manifest/exclusion_log — used to
  patch the pool upward (4,500 → 5,000) without re-cloning what was judged.
- **Clone retention** (default `accepted`): clones of rejected repos are
  deleted after extraction; accepted clones are kept for audit; `--keep-clones
  all|none` and `--prune-rejected` override.
- Repos returning GitHub API 404 after discovery (deleted/private between
  snapshot and cloning) are reclassified `clone_failed` (timestamped detail) —
  permanent attrition, distinct from transient network failures.

> **E-rule history.** The earlier E1–E6 gate (Python-byte-ratio >= 0.5 as E2,
> >= 10 commits as E4, >= 4 files / >= 1 app as E5, tutorial-marker E6 as a
> manual-review *flag*) is superseded. The current E1–E4 rules measure on-disk
> usage directly and drop the Python-share gate; see
> `docs/github_stratified_scan_stats.md` for the revision rationale.

## Objectivity of E4 Thresholds
The >= 2 files / production-import threshold is anchored by a manual
qualitative review of below-threshold repos (single-file scripts and demos are
the dominant class; see `github_stratified_scan_stats.md`). Sensitivity
analysis runs all downstream results at file thresholds 2, 3, 4, 5, 6, 8 to
confirm conclusions are not threshold-dependent (SENSITIVITY_THRESHOLDS).

## Sampling
- A stratified sample of 327 accepted repos (by GitHub-star quadrant, seed=42,
  schema 0.2) is used for **manual verification** of the extractor
  (peer-review release: 28,089 DI-adjacent observations, 8,840 excerpts, 27
  fingerprint classes). See `docs/github_stratified_scan_stats.md`.
- The **full accepted census (2,179) — not the sample — is the analysis
  universe** for every reported RQ1/RQ2/RQ3 number. Sampling is used only for
  human labelling, never for statistical inference.

## Pipeline Artifacts
- corpus/candidates.json     — finder output (raw enriched candidates)
- corpus/manifest.json       — accepted repos + metadata + extractor aggregate snapshot
- corpus/exclusion_log.json  — every candidate, decision, first-failing rule
- corpus/reports/<name>.json — full extractor report per accepted repo
- corpus/raw_dependents/     — snapshotted GitHub dependents HTML pages (reproducibility)
- corpus/topic_seed.json     — benchmark signal snapshot (recall measurement)
- study_repos/corpus/        — shallow clones (accepted retained by default; rejected pruned)

## Pilot Validation (2026-08-06)
| Repo | E1 | E2 | E3 | E4 | E5 | E6 | Decision |
|------|----|----|----|----|----|----|----------|
| mealie-recipes/mealie      | P | P | P | P | P (98 files, 1 app) | FLAG 'demo' (live-site link) | ACCEPTED, manual review include |
| Netflix/dispatch           | P | P | F (archived) | P | P | P | EXCLUDED (E3) |
| deepset-ai/hayhooks        | P | P | P | P | P (19 files, 1 app) | FLAG 'boilerplate' (marketing copy) | ACCEPTED, manual review include |
| PrefectHQ/prefect          | P | P | P | P | P (42 files, 8 apps) | P | ACCEPTED |

Note: hayhooks lives at deepset-ai/hayhooks (moved from pipelineai/hayhooks).

## Environment / Reproducibility
- Tooling: `uv` 0.11.32 manages the interpreter and virtualenv.
- Python: pinned to **3.12.13** (`.python-version`, patch-exact).
- Dependencies locked in `uv.lock` (hash-pinned full graph):
  `requests==2.33.1`, `python-dotenv==1.2.1`, `pydantic==2.13.2`
  (+ transitive `pydantic-core==2.46.2`, `urllib3==2.7.0`, etc.).
  `pyproject.toml` declares these as ranges; `[tool.uv].constraint-dependencies`
  pins the lock to the exact versions used during analysis.
- `requirements.txt` is a plain-pip export of the lock (reviewer-friendly
  alternative to uv).
- Restore: `uv sync` (or `pip install -r requirements.txt` + `python 3.12`).
- Run all scripts via `uv run python corpus/...` / `uv run python extract.py ...`
  so every invocation uses the locked environment.
- Extractor determinism: output is byte-identical across interpreters and
  filesystems because file iteration is explicitly sorted by repo-relative
  path (extractor v0.2.1). Verified 3.12.13 == 3.14.6 on all three pilot repos.
