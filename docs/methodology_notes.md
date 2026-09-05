# Corpus Methodology (FINALIZED 2026-08-06)

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
- Minimum 50 repos, target 50-100, hard ceiling ~150 if candidates are good.
- Expandable in phases before the Oct'26 submission.

## Discovery (finder.py)
- Primary: **GitHub dependency-graph dependents** of `fastapi/fastapi`
  (`https://github.com/fastapi/fastapi/network/dependents`) — repos whose
  manifests GitHub's dependency graph resolves as depending on fastapi.
  Paginated HTML, snapshotted per page (`corpus/raw_dependents/`).
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
| E1   | `fastapi` in RUNTIME dependencies (pyproject.toml `[project]`/`[tool.poetry.dependencies]`, runtime requirements*.txt, Pipfile `[packages]`, setup.cfg/setup.py). Dev/optional deps do not count. |
| E2   | Python dominant language: Python byte ratio >= 0.5 (GitHub languages API). |
| E3   | Not a fork and not archived. |
| E4   | `pushed_at` within the last 60 months AND >= 10 commits. |
| E5   | Real FastAPI usage: >= 4 files importing `fastapi` AND >= 1 `FastAPI()` call (extractor, production files only). |
| E6   | No tutorial/demo markers in description or README (regex `tutorial|example|demo|sample|boilerplate|template|playground|starter|course|learn|getting started|walkthrough`). FLAGS for manual review — never auto-excludes. |

- Every candidate decision records per-rule PASS/FAIL + detail (exclusion_log.json).
- Repos failing E1-E5 are excluded with the first failing rule logged.
- E6-flagged repos stay in the manifest with `tutorial_flag: true`; a human resolves each.
- Thresholds are schema-versioned constants in corpus/settings.py.
- Repos returning GitHub API 404 after discovery (deleted/private between
  snapshot and cloning) are reclassified `clone_failed` -> `unavailable`
  (`corpus/reclassify_unavailable.py`, timestamped detail) — permanent
  attrition, distinct from transient network failures which stay `clone_failed`.

## Objectivity of E5 Thresholds
The >=4 files / >=1 app threshold is anchored in the observed data distribution
(histogram of files-importing-fastapi; a natural gap separates trivial one-off scripts
from real applications). Sensitivity analysis runs all downstream results at thresholds
2, 3, 4, 5, 6, 8 to confirm conclusions are not threshold-dependent (SENSITIVITY_THRESHOLDS).

## Sampling
- Exhaustive if the eligible pool N <= 100.
- If N > 100, random sample of 100 with seed=42; expansion superset property
  (the sample is a subset of any larger sample drawn with the same seed).

## Pipeline Artifacts
- corpus/candidates.json     — finder output (raw enriched candidates)
- corpus/manifest.json       — accepted repos + metadata + extractor aggregate snapshot
- corpus/exclusion_log.json  — every candidate, decision, first-failing rule
- corpus/reports/<name>.json — full extractor report per accepted repo
- corpus/raw_dependents/     — snapshotted GitHub dependents HTML pages (reproducibility)
- corpus/topic_seed.json     — benchmark signal snapshot (recall measurement)
- study_repos/corpus/        — shallow clones

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
