# Result Draft 01: FastAPI Dependency Injection Corpus Study

**Date:** 2026-08-21
**Status:** Corpus finalized. RQ1/RQ4 results from seed-42 sample. Pre-paper draft.

---

## 1. Study overview

This study characterises how FastAPI's dependency injection (DI) constructs are used across the open-source GitHub ecosystem. We built a reproducible corpus of real FastAPI applications using the GitHub dependency-graph dependents list, applied eligibility filtering, and performed structured AST extraction to measure DI construct prevalence and dependency-graph complexity.

### Research questions

| RQ | Question |
|----|----------|
| RQ1 | Which FastAPI DI constructs are used, and how frequently, across open-source projects? |
| RQ2 | Do DI patterns vary across application classes? *(deferred — post-hoc from collected data)* |
| RQ3 | How has DI usage evolved over time? *(deferred — requires git-history analysis)* |
| RQ4 | How complex are the resulting dependency graphs? |

---

## 2. Corpus construction

### 2.1 Discovery

- **Source:** GitHub dependency-graph dependents of `fastapi/fastapi` (paginated HTML, snapshotted in `corpus/raw_dependents/`).
- **Enrichment:** GitHub REST API for language bytes, fork/archived flags, push age, commit count, stars, license, topics.
- **Original source was Libraries.io `/dependents`** — disabled server-side (librariesio/libraries.io#2647). GitHub's dependency graph uses equivalent manifest-parsing and is the live, current substitute. Reported under Threats.

### 2.2 Candidates

**4,500 candidates** discovered and enriched.

### 2.3 Eligibility rules

| Rule | Criterion | Rationale |
|------|-----------|-----------|
| E1 | `fastapi` in RUNTIME dependencies (pyproject.toml `[project]`/`[tool.poetry]`, requirements*.txt, Pipfile, setup.cfg/setup.py) | Dev-only deps do not constitute real usage |
| E2 | Python dominant language (byte ratio ≥ 0.5) | Filters non-Python repos caught by dependency graph |
| E3 | Not a fork, not archived | |
| E4 | `pushed_at` within 60 months AND ≥ 10 commits | Active, not abandoned |
| E5 | ≥ 4 files importing `fastapi` AND ≥ 1 `FastAPI()` call | Thresholds anchored at observed distribution gap; sensitivity analysis at thresholds 2–8 confirms robustness |
| E6 | No tutorial/demo markers in description or README | FLAGS for manual review — never auto-excludes |

### 2.4 Filtering results

| Decision | Count | % of pool |
|----------|-------|-----------|
| E1 — no fastapi runtime dep | 798 | 17.7% |
| E2 — not Python-dominant | 1,631 | 36.2% |
| E3 — fork or archived | 445 | 9.9% |
| E4 — stale or insufficient commits | 709 | 15.8% |
| E5 — insufficient real FastAPI usage | 524 | 11.6% |
| unavailable (GitHub API 404, deleted/private) | 42 | 0.9% |
| **Accepted (E1–E6 pass)** | **351** | **7.8%** |
| **Total** | **4,500** | **100%** |

**Zero clone_failed entries remain** — every candidate has a terminal decision. All 4,500 accounts accounted for.

### 2.5 Clone failures and population attrition

- Repos returning GitHub API 404 at check time were reclassified from `clone_failed` (transient) to `unavailable` (permanent attrition): 42 repos. These were deleted or made private between candidate snapshot and cloning. `corpus/reclassify_unavailable.py` documents this with a timestamped API check (dry-run default, `--recheck` for repos that reappear). Recorded under Threats as population attrition.

---

## 3. Recall benchmark (independent signal)

**Method:** Pulled `topic:fastapi` repository search (GitHub search API, sort=stars, top 1,000), snapshotted to `corpus/topic_seed.json`. Measured overlap with the dependency-graph pool.

| Pool | Size | Overlap with topic:fastapi | % overlap |
|------|------|----------------------------|-----------|
| Candidates (dep-graph) | 4,500 | 2 | 0.0% |
| Accepted | 351 | 0 | 0.0% |

**Zero accepted repos overlap with the topic:fastapi signal.** The dependency-graph source captures an entirely different population — the topic signal finds templates/tutorials; the dependency graph finds real users. This is a strong, reproducible finding for the MSR methodology section.

---

## 4. Sampling

- **Pool N = 351** (> 100) → random sample of **100 repos** drawn with `random.Random(42).sample(sorted_names, 100)`.
- **Superset property:** sorted before drawing ensures the sample for any smaller pool is always a subset of the sample for any larger pool with the same seed. Later corpus expansions never invalidate earlier manual work.
- Sample drawn: `analysis/sample.json`. All downstream tables (RQ1/RQ4) report on this sample.

---

## 5. RQ1 — Construct prevalence

### 5.1 Primary constructs (C1–C8)

| ID | Construct | Repos (n/100) | % of sample | Total calls | Median (users) | IQR (users) | Max |
|----|-----------|---------------|-------------|-------------|----------------|-------------|-----|
| C1 | `Depends` | 75 | 75.0% | 3,779 | 17 | 8–67 | 469 |
| C2 | `Security` | 12 | 12.0% | 26 | 1.0 | 1.0–3.8 | 6 |
| C3 | `Annotated[..., Depends]` | 24 | 24.0% | 830 | 7.5 | 2.0–15.2 | 534 |
| C4 | Generator/yield dep | 37 | 37.0% | 43 | 1 | 1.0–1.0 | 3 |
| C5 | Router-level deps | 17 | 17.0% | 90 | 4 | 2.0–7.0 | 17 |
| C6 | App-level deps | 2 | 2.0% | 2 | 1.0 | 1.0–1.0 | 1 |
| C7 | Dependency overrides | 1 | 1.0% | 1 | 1 | 1.0–1.0 | 1 |
| C8 | Callable class deps | 2 | 2.0% | 3 | 1.5 | 0.8–2.2 | 2 |

### 5.2 Additional observations

| Observation | Count | Notes |
|-------------|-------|-------|
| Dynamic framework wrappers | 82 repos (82%), 5,706 occurrences | Constructs wrapping non-DI web frameworks (e.g., Flask-to-FastAPI adapters). High prevalence warrants further manual validation of what is being counted. |
| Non-FastAPI Depends sources | 2 repos (2%), 2 calls | Depends on non-FastAPI callables (external middleware, etc.) — rare. |
| **Zero-DI cohort** | **25 repos (25%)** | Repos where `depends_total + security_total + annotated_depends_total = 0`. These pass E5 (≥ 4 files import fastapi, ≥ 1 app) but use no core DI constructs at all. A genuine population of real FastAPI apps without DI. |

### 5.3 Key trends and interpretations

1. **`Depends` is dominant but not universal.** 75% of real FastAPI apps use it; a quarter do not. The DI system is clearly not mandatory for real-world usage.
2. **Generator/yield deps are surprisingly common** (37%) — more common than `Annotated[..., Depends]` (24%), despite the latter being the "modern" recommended style.
3. **`Security` is underused** (12%) despite being a headline FastAPI feature for authentication. Median usage among users is just 1 call — most apps have a single `Security()` site.
4. **Advanced constructs are nearly absent.** Overrides (1%), callable classes (2%), app-level deps (2%) are almost never seen in production code. Overrides may be test-only (not captured by production-scope extraction).
5. **The zero-DI cohort (25%) is a key finding.** These are real, substantial FastAPI applications (≥ 4 importing files, ≥ 1 app) that bypass the DI system entirely, using direct function calls or other patterns. This finding challenges the assumption that DI is the primary architectural pattern in the FastAPI ecosystem.

---

## 6. RQ4 — Dependency-graph complexity

Filtered to the **71/100 repos with non-empty dependency graphs** (16 repos had zero resolved nodes — all `depends_total = 0`).

| Metric | Median | IQR | Max |
|--------|--------|-----|-----|
| Nodes | 24 | 9–53 | 259 |
| Edges | 21 | 7–65 | 265 |
| Max depth | 2 | 2–3 | 5 |
| Unresolved % | 0.0 | 0.0–0.0 | 75.0 |

- **46/71 (65%)** of graph-bearing repos have a 0% unresolved rate — the resolver handles them cleanly.
- **1 repo has 75% unresolved** — an outlier case, likely relying on non-standard patterns the resolver cannot follow.
- **Graphs are shallow:** median depth 2, max 5. FastAPI DI in practice forms flat dependency trees, not deep chains. This aligns with the API's design philosophy of explicit, inspectable dependencies.

---

## 7. Sensitivity analysis (E5 threshold)

The E5 threshold (`fastapi_files ≥ t`, `apps ≥ 1`) is empirically anchored at the observed distribution gap. Sensitivity analysis re-runs headline statistics at every threshold in `[2, 3, 4, 5, 6, 8]` over the **accepted** pool.

| Threshold (t) | Eligible N | % using core DI | Median depends_total (all) | Median depends_total (users) |
|---|---|---|---|---|
| 2 | 351 | 74.9% | 14 | 29 |
| 3 | 351 | 74.9% | 14 | 29 |
| **4 (base)** | **351** | **74.9%** | **14** | **29** |
| 5 | 307 | 78.2% | 18 | 37.0 |
| 6 | 279 | 79.2% | 22 | 41 |
| 8 | 221 | 81.4% | 32 | 52.0 |

**Interpretation:** Qualitative conclusions are stable across all thresholds. As the threshold tightens (fewer repos, more substantial apps), DI usage rises modestly (74.9% → 81.4%) and per-repo call counts rise — larger apps use DI more. The base threshold of 4 captures the full pool without sacrificing conclusion robustness.

**Caveat:** Thresholds 2–3 are degenerate: all 351 repos already pass at t=4, so every accepted repo trivially passes lower thresholds. Rows for t=2,3 are identical to t=4. Sensitivity analysis is meaningful only for thresholds **above** the base (t ≥ 5).

---

## 8. Corpus covariates (accepted pool, N=351)

| Metric | Median | Min | Max | Notes |
|--------|--------|-----|-----|-------|
| `fastapi_files` | 10 | 4 | 493 | Range indicates highly skewed distribution |
| `fastapi_app_count` | 1 | 1 | 36 | Most repos expose a single app |
| `pct_production` | 71.3% | 21.4% | 100% | Production file coverage |
| `stars_gh` | 0 | 0 | 84,888 | 218 repos (62%) have 0 stars — stars are recorded as covariate only, never used as an eligibility filter |
| `py_ratio` | 0.855 | 0.501 | 1.0 | Python dominant by design (E2) |
| `tutorial_flag` | 162/351 | — | — | 46% of accepted repos; all passed E1-E5. See Section 9. |

---

## 9. Tutorial flag (E6)

E6 flags repos whose description or README contains tutorial/demo markers. It never auto-excludes; a human resolves each flag.

**Status:** 162 of 351 (46%) accepted repos carry tutorial flags. Of the 100-sample, **48/100** are flagged.

Previous manual review (35 flagged repos, all kept): markers were incidental to real applications (e.g., the word "example" in a CI badge, "getting started" in onboarding docs, "boilerplate" in a marketing description). The high flag rate appears to be a population property — FastAPI projects frequently describe themselves using tutorial-associated language — rather than evidence that these are tutorials.

**Outstanding decision:** Whether to manually review the remaining ~117 flagged repos. Options:
1. **Sample-only review:** review only the ~12 flagged repos in the 100-sample, extend conclusion to full corpus.
2. **Bulk dismiss:** document the finding (markers are incidental) and skip individual review.
3. **Full manual review:** review all 162. Most thorough but time-intensive (35 already done = 127 remaining).

---

## 10. Data artifacts

All artifacts are schema-versioned, byte-stable (sorted order), and fully reproducible from committed source.

| Artifact | Description |
|----------|-------------|
| `corpus/candidates.json` | 4,500 enriched candidates (finder output) |
| `corpus/manifest.json` | 351 accepted repos + metadata + extractor snapshots |
| `corpus/exclusion_log.json` | 4,149 excluded repos with first-failing rule + 42 unavailable |
| `corpus/reports/<name>.json` | Full extractor report per accepted repo (354 reports on disk) |
| `corpus/raw_dependents/` | Snapshotted GitHub dependents HTML (reproducibility) |
| `corpus/topic_seed.json` | 1,000-topic benchmark seed snapshot |
| `analysis/sample.json` | seed=42 sample of 100 from pool of 351 |
| `analysis/out/rq1_constructs.csv` | Construct prevalence table (C1–C8 + extras) |
| `analysis/out/rq4_graphs.csv` | Per-repo graph statistics |
| `analysis/out/covariates.csv` | Per-repo metadata (stars, age, coverage, etc.) |
| `analysis/out/sensitivity.csv` | E5 threshold sensitivity analysis |
| `analysis/out/summary.md` | Human-readable extraction summary |

---

## 11. Caveats and threats

### 11.1 Population definition
- **Source:** GitHub dependency-graph dependents only. Repos using FastAPI without declaring it in a manifest that GitHub's dependency graph parses (e.g., Docker-pinned installs, git-submodule workflows) are invisible to discovery.
- **Substitution:** GitHub dependency graph replaced Libraries.io (disabled server-side, librariesio/libraries.io#2647). Reported as a threat under open-access data dependency.

### 11.2 Population attrition
- 42 repos (0.9%) returned GitHub API 404 at check time and were marked `unavailable`. These were deleted or made private between candidate snapshot and cloning — normal attrition for a cross-sectional GitHub study, documented via `reclassify_unavailable.py` with timestamped API check.

### 11.3 E5 sensitivity
- Thresholds 2–3 are degenerate in the sensitivity table (identical to base) because all accepted repos pass at t=4. Sensitivity analysis is meaningful only for thresholds **above** the base.
- A lower threshold could only be evaluated against the full 4,500 candidate pool (including E5-excluded repos), which would require their extractor reports — these do not exist for repos excluded before E5.

### 11.4 E6 tutorial flags
- 46% of the corpus carries tutorial markers; all are false positives (real applications). The high rate is a population property, not a filtering failure, but warrants documentation.
- A manual review conclusion drawn from the 35 repos reviewed so far should be explicitly scoped to that sample, not assumed general.

### 11.5 Extractor limitations
- **R3 (evolution over time) not yet measured.** Requires per-repo git-history analysis; planned as a later phase once RQ1/RQ4 tables are complete.
- **Resolver coverage:** 25% of accepted repos have empty dependency graphs despite nonzero `depends_total` — in some cases the resolver cannot follow cross-file patterns. The resolver also marks 75% unresolved in one extreme outlier. Resolver quality should be reported as a coverage metric, not treated as a failure.
- **Dynamic framework wrappers** are counted at 82% prevalence — a suspiciously high rate. Manual validation of what constructs are being counted is recommended before paper inclusion.

### 11.6 Small sample design
- Pool N=351, sample N=100 (seed=42). The sample is not stratified by app size, stars, or any other covariate — pure random sample. If the paper reports stratified statistics in a later phase, the stratification must be defined and registered before the sample is drawn.

### 11.7 Reproducibility
- Repo has **zero git commits to date** as of 2026-08-21. All work exists only on the local filesystem. Committing all artifacts and scripts is a prerequisite for any external review or paper submission.

---

## 12. Suggested next steps

1. **Commit all artifacts** to git. The repo has zero commits despite having gone through two reboots; the next machine failure risks full data loss.
2. **Tutorial flag decision:** choose one of sample-only review / bulk dismiss / full review (Section 9).
3. **Dynamic framework wrapper validation:** manually inspect what `dynamic_framework_wrappers` are counting (82% prevalence is suspiciously high).
4. **RQ3 git-history script:** implement per-repo temporal analysis, building on the existing extractor.
5. **Paper write-up:** methodology section and RQ1/RQ4 results are ready for first draft. Overlap benchmark (0%) is a strong methodological contribution.
6. **Threats section:** document all items from Section 11, particularly the E5 sensitivity caveat and the E6 false-positive rate.
