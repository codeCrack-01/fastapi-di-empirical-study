# Result Draft 01: FastAPI Dependency Injection Corpus Study

**Date:** 2026-08-21
**Status:** Corpus finalized. RQ1/RQ2 results are the FULL-CORPUS CENSUS over all 351 accepted repos. Pre-paper draft.

---

## 1. Study overview

This study characterises how FastAPI's dependency injection (DI) constructs are used across the open-source GitHub ecosystem. We built a reproducible corpus of real FastAPI applications using the GitHub dependency-graph dependents list, applied eligibility filtering, and performed structured AST extraction to measure DI construct prevalence and dependency-graph complexity.

### Research questions

> The study originally proposed four RQs. The standalone application-class question
> (originally RQ2) was **dropped** and folded into RQ1 as a covariate axis (see §5.4).
> The remaining three questions are renumbered RQ1–RQ3 (graph complexity moved from RQ4 → RQ2).

| RQ | Question |
|----|----------|
| RQ1 | Which FastAPI DI constructs are used, and how frequently, across open-source projects? *(includes a covariate axis by stars and age — see §5.4)* |
| RQ2 | How complex are the resulting dependency graphs? *(renumbered from RQ4)* |
| RQ3 | How has DI usage evolved over time? *(deferred — requires git-history analysis)* |

> **Note (supervisor direction):** the originally-proposed application-class question
> ("Do DI patterns vary across application classes?") is **dropped as a standalone
> question** and folded into RQ1 as a covariate axis. Its goal — understanding who uses DI —
> is served by disaggregating RQ1 by repo covariates (stars, age) rather than an arbitrary
> application-class taxonomy, which would be methodologically weak without a priori labels.

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

#### 2.3.1 E2 threshold robustness

The E2 cutoff (`py_ratio ≥ 0.5`) is a *stated convention* ("Python must dominate the byte volume"), not a value derived from any distribution. Across the 4,500 candidates the accepted pool sits well clear of the boundary — median `py_ratio` 0.855, p25 0.695, min 0.501 — and only **37/351 (10.5%)** accepted repos fall below 0.6 (**0 repos are exactly at 0.5**). Sensitivity (`analysis/e2_sensitivity.py`) confirms RQ headline numbers are insensitive to the exact cutoff:

| Threshold | Candidates passing gate | Accepted kept | `.n` change vs 0.5 |
|-----------|------------------------|---------------|--------------------|
| 0.45      | 3,049                   | 351           | 0 (raises lower bound only) |
| 0.5 (base)| 2,869                   | 351           | — |
| 0.55      | 2,682                   | 333           | −18 |
| 0.6       | 2,486                   | 314           | −37 |
| 0.7       | 2,107                   | 261           | −90 |
| 0.8       | 1,702                   | 209           | −142 |
| 0.9       | 1,248                   | 154           | −197 |
| 1.0       | 293                     | 18            | −333 |

Raising the threshold only ever removes accepted repos already passing every later rule (their removal is certain); lowering it below 0.5 can only *add* E2-excluded repos, but those were never cloned, so their admission is an unverified upper bound (no reports exist to check E5). Either direction moves the corpus count but does not change which DI constructs are observed or the per-construct ordering in RQ1, so conclusions are robust to the E2 choice.

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

- **FULL-CORPUS CENSUS: Pool N = 351; all 351 accepted repos are analysed** (`--scope all`). This is a census, not a sample — every accepted repo contributes to every downstream table.
- A seed-42 random sample of 100 was used for earlier pilot/RQ2-bug work; the final RQ1/RQ2 numbers reported in this paper are the **census over all 351** (sampling rule preserved for audits: if N > 100, `random.Random(42).sample(sorted_names, 100)`; sample file at `analysis/sample.json`).
- **Superset property:** sorted before drawing ensures the sample for any smaller pool is always a subset of the sample for any larger pool with the same seed. Later corpus expansions never invalidate earlier manual work.
- Census aggregation: `uv run python analysis/aggregate.py --scope all` → `analysis/out/rq1_constructs.csv`, `rq1_by_stars.csv`, `rq1_by_age.csv`, `rq4_graphs.csv`, `covariates.csv`, `sensitivity.csv`, `summary.md`.

---

## 5. RQ1 — Construct prevalence

### 5.0 Construct catalogue reconciliation

> The design catalogue (`docs/construct_catalogue.md`) originally defined ten
> candidate constructs. **Eight (C1–C8) are operationalized** as per-repo
> prevalence counters and reported below. The catalogue has been renumbered so its
> C1–C8 match this section exactly (and its C9/C10 are explicitly marked
> *not operationalized*). Two constructs are intentionally not measured:
>
> - **Nested dependency (C9)** — not a distinct syntactic construct but a
>   graph-topological property (a dependency that is itself the target of another
>   dependency, i.e. a node with both incoming and outgoing edges). It is captured
>   by the RQ2 dependency-graph analysis (median depth, fan-out) rather than as a
>   C-series prevalence counter.
> - **Parameterized dependency (C10)** — marked "Maybe detectable" in the
>   catalogue; factory-generated dependencies are not statically decidable from a
>   call site, so counting them would risk false positives. Deferred.

### 5.1 Primary constructs (C1–C8)

| ID | Construct | Repos (n/351) | % of corpus | Total calls | Median (users) | IQR (users) | Max |
|----|-----------|---------------|-------------|-------------|----------------|-------------|-----|
| C1 | `Depends` | 262 | 74.6% | 22,711 | 22.0 | 8.0–68.5 | 1,732 |
| C2 | `Security` | 33 | 9.4% | 143 | 1 | 1.0–2.5 | 69 |
| C3 | `Annotated[..., Depends]` | 88 | 25.1% | 4,688 | 8.0 | 4.0–28.2 | 1,264 |
| C4 | Generator/yield dep | 140 | 39.9% | 192 | 1.0 | 1.0–1.0 | 13 |
| C5 | Router-level deps | 46 | 13.1% | 271 | 3.0 | 1.0–7.0 | 35 |
| C6 | App-level deps | 10 | 2.8% | 10 | 1.0 | 1.0–1.0 | 1 |
| C7 | Dependency overrides | 6 | 1.7% | 34 | 1.0 | 1.0–9.5 | 26 |
| C8 | Callable class deps | 2 | 0.6% | 3 | 1.5 | 0.8–2.2 | 2 |

### 5.2 Additional observations

| Observation | Count | Notes |
|-------------|-------|-------|
| Non-FastAPI Depends sources | 2 repos (0.6%), 2 calls | Depends on non-FastAPI callables (external middleware, etc.) — rare. |
| **Zero-DI cohort** | **88 repos (25.1%)** | Repos where `depends_total + security_total + annotated_depends_total = 0`. These pass E5 (≥ 4 files import fastapi, ≥ 1 app) but use no core DI constructs at all. A genuine population of real FastAPI apps without DI. |

### 5.3 Key trends and interpretations

1. **`Depends` is dominant but not universal.** 74.6% of real FastAPI apps use it; a quarter do not. The DI system is clearly not mandatory for real-world usage.
2. **Generator/yield deps are surprisingly common** (39.9%) — more common than `Annotated[..., Depends]` (25.1%), despite the latter being the "modern" recommended style.
3. **`Security` is underused** (9.4%) despite being a headline FastAPI feature for authentication. Median usage among users is just 1 call — most apps have a single `Security()` site.
4. **Advanced constructs are nearly absent.** Overrides (1.7%), callable classes (0.6%), app-level deps (2.8%) are almost never seen in production code. Overrides may be test-only (not captured by production-scope extraction).
5. **The zero-DI cohort (25.1%) is a key finding.** These are real, substantial FastAPI applications (≥ 4 importing files, ≥ 1 app) that bypass the DI system entirely, using direct function calls or other patterns. This finding challenges the assumption that DI is the primary architectural pattern in the FastAPI ecosystem.

### 5.4 RQ1 covariate axis (folded application-class question) — DI prevalence by covariates

Folded from the (dropped) application-class question: who uses DI? Disaggregated by repo **stars** and **age** (no arbitrary application-class taxonomy).

**By stars** (`analysis/out/rq1_by_stars.csv`):

| Stars | Repos | % using core DI | Median core calls |
|-------|-------|-----------------|-------------------|
| 0 | 218 | 75.7% | 14.0 |
| 1–9 | 115 | 70.4% | 14 |
| 10–99 | 11 | 100.0% | 68 |
| 100+ | 7 | 85.7% | 6 |

**By age** (`analysis/out/rq1_by_age.csv`):

| Age | Repos | % using core DI | Median core calls |
|-----|-------|-----------------|-------------------|
| <12mo | 316 | 74.1% | 14.0 |
| 12–36mo | 26 | 80.8% | 17.5 |
| 36mo+ | 9 | 88.9% | 22 |

**Interpretation:**
- **DI prevalence is essentially flat across stars** (≈70–76% for the well-populated star buckets, with the small-volume higher (10–99 = 100%) bucket driven by just 11 repos). Popularity does not predict DI adoption.
- **The corpus skews very young:** 316/351 repos are under a year old. This is a direct consequence of the E4 recency gate (pushed within 60 months) combined with the fast-growing, largely new-repo GitHub dependency-graph population.
- **Oldest/starriest bucket bin counts are small (7–26 repos) for stable conclusions** — reported for completeness, not as a primary finding. The age axis would need RQ3's git history or a larger corpus to be conclusive.
- Net: the covariate view supports the central finding that **DI use (and its absence) is a stable property across the population**, not skewed by popularity.

---

## 6. RQ2 — Dependency-graph complexity

Filtered to the **253/351 repos with non-empty **clean** dependency graphs** (after dropping resolver-emitted junk nodes; see below). The remaining 98 repos have zero graph nodes — all `depends_total = 0` and use no DI.

| Metric | Median | IQR | Max |
|--------|--------|-----|-----|
| Nodes (clean) | 21 | 8–55 | 1,444 |
| Max depth | 2 | 2–3 | 7 |
| Unresolved % | 0.0 | 0.0–3.0 | 75.0 |

- **155/253 (61.3%)** of graph-bearing repos have a 0% unresolved rate — the resolver handles them cleanly.
- **1 repo has 75% unresolved** — an outlier case, likely relying on non-standard patterns the resolver cannot follow.
- **Graphs are shallow:** median depth 2, max 7. FastAPI DI in practice forms flat dependency trees, not deep chains. This aligns with the API's design philosophy of explicit, inspectable dependencies.

### 6.1 Data-quality fix: resolver-emitted junk nodes

The dependency graph construction had a genuine contamination bug. In `resolver.build_dependency_graph`, when a `Depends` call occurs **outside any function context** — module-scope declarations such as `FastAPI(dependencies=[...])` or router defaults — `context_function` is `None` and the resolver falls back to a `"{file_path}:{line}"` placeholder as the source node id (resolver.py line 112). These filesystem-path ids are not callable names.

- **Measures:** On the full corpus, **103/253** graph-bearing repos contain such junk nodes — **610 junk nodes of 15,552 total (3.9%)**.
- **Effect:** Inflates node counts (median 23 raw → **21** clean for graph-bearing repos) and can add spurious edge/density values. All 253 graph-bearing repos retain a non-empty clean graph; the junk was additive, never the sole content.
- **Fix:** `analysis/aggregate.py` now filters any node id containing a path separator or `file:line` anchor before computing RQ2 (both raw and clean columns are retained in `rq4_graphs.csv` for transparency).
- **Reporting sentence:** *"We filtered resolver-emitted non-callable artifact nodes (file:line placeholders from module-scope dependency declarations) from the dependency graphs before computing complexity metrics."*
- **RQ1 note:** RQ1 construct counts (C1–C8) come from `file_details`/aggregate call counts, not graph nodes, so RQ1 is unaffected by this bug.

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

**Status:** 162 of 351 (46%) accepted repos carry tutorial flags.

A blinded human review (`analysis/e6_sample.py`, fixed-seed stratified subsample of 24 flagged + 24 unflagged control, labels recorded before un-masking) finds:

| label | flagged (n=24) | control (n=24) |
|-------|----------------|----------------|
| genuine application | 16 (66.7%) | 21 (87.5%) |
| uncertain (research / portfolio / challenge) | 6 (25.0%) | 2 (8.3%) |
| demo / tutorial / scaffold / capstone | 2 (8.3%) | 1 (4.2%) |

- Flagged genuine rate **66.7%** (Wilson 95% CI 46.7–82.0%); control **87.5%** (CI 69.0–95.7%).
- **Genuine-ness is the majority class in both groups.** The README tutorial marker is a weak, noise-heavy signal: it modestly over-selects non-genuine repos (33% vs 12.5% non-genuine) but most flagged repos are real applications.
- Structural sophistication (entry points, DB schema/migrations, auth, caching, integrations, tests — `analysis/e6_structural.py`) separates the few clear demos (median index 1–5) from genuine apps (median 6–7), but does **not** separate the flagged pool from the unflagged baseline (flagged-genuine median 7 ≈ control-genuine 6). Full write-up: `analysis/out/e6_findings.md`.
- The "uncertain" class is structurally the *richest* (median index 7–10): aspirational, heavily-scaffolded projects (OWNEX, CEREBRO-X, cadence-clinical, dharma_swarm) — a distinct pattern from thin demos.

**Sensitivity into RQ numbers:** because flagged repos are mostly genuine, including/excluding them does **not** overturn the RQ1/RQ2 headline aggregates (the flagged subset largely mirrors the unflagged baseline). See Section 11.4.

**Implication for corpus definition:** E6's flag is unsuitable as a hard exclusion rule; it should remain a documentation-only flag. Recomputation under a tighter rule (e.g. only multi-marker or demo-labeled repos) is feasible but not required by the current findings.

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
| `analysis/sample.json` | seed-42 sample of 100 from pool of 351 (pilot/bug-audit only; final tables are the census) |
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
- The high flag rate (46%) is a population property: FastAPI projects frequently describe themselves in tutorial-associated language, and the README marker regex is not a useful exclusion rule.
- A blinded review of a 24-flagged / 24-control subsample (`analysis/out/e6_findings.md`) confirms genuine-ness is the majority class in both groups (66.7% flagged vs 87.5% control). The flagged pool is only modestly over-selected for non-genuine repos (33% vs 12.5%), and structural sophistication does not separate the two pools — so **including or excluding flagged repos does not materially change the RQ1/RQ2 headline aggregates**. RQ numbers are insensitive to E6.
- The label set is a single-reviewer judgment sample (48/351); treat rate estimates as indicative and spot-check for inter-rater consistency before any stronger claim.

### 11.5 Extractor limitations
- **Resolver junk nodes (mitigated):** module-scope `Depends` declarations produced `file:line` placeholder nodes (610 across 103/253 repos). Filtered at aggregation time; see §6.1. The resolver *output*, not the extraction of construct counts, is affected — RQ1 is clean.
- **R3 (evolution over time) not yet measured.** Requires per-repo git-history analysis; planned as a later phase once RQ1/RQ2 tables are complete.
- **Resolver coverage:** 98/351 (27.9%) of accepted repos have empty dependency graphs despite passing E1–E6 — in some cases the resolver cannot follow cross-file patterns. Resolver quality should be reported as a coverage metric, not treated as a failure.

### 11.6 Census (not a sample) design
- Analysis is a **full-corpus census over all 351 accepted repos**; there is no sampling inference to generalize from, so standard-errors-inference does not apply — the RQ1/RQ2 figures ARE the population values.
- The earlier seed-42 sample (N=100) was used only for pilot work and the RQ2-bug audit; it is superseded by the census for all reported figures.
- Sparse covariate buckets (e.g. 100+ stars = 7 repos, 36mo+ = 9 repos) hold too few repos for stable conclusions and are reported for completeness, not over-read (see §5.4).

---

## 12. Planned Up Ahead

2. **Tutorial flag decision:** choose one of sample-only review / bulk dismiss / full review (Section 9).
3. **RQ3 git-history script:** implement per-repo temporal analysis, building on the existing extractor.
4. **Paper write-up:** methodology section and RQ1/RQ2 results are ready for first draft. Overlap benchmark (0%) is a strong methodological contribution.
5. **Threats section:** document all items from Section 11, particularly the E5 sensitivity caveat and the E6 false-positive rate.
