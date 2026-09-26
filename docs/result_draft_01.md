# Result Draft 01: FastAPI Dependency Injection Corpus Study

**Date:** 2026-08-21 (rev. 2026-09-25, census refresh to the E1–E4 gate)
**Status:** Corpus finalized. RQ1/RQ2/RQ3 results are the FULL-CORPUS CENSUS over all 2,179 accepted repos. Pre-paper draft.

---

## 1. Study overview

This study characterises how FastAPI's dependency injection (DI) constructs are used across the open-source GitHub ecosystem. We built a reproducible corpus of real FastAPI applications using the GitHub dependency-graph dependents list, applied eligibility filtering, and performed structured AST extraction to measure DI construct prevalence and dependency-graph complexity.

### Research questions

> The study originally proposed four RQs. The standalone application-class question
> (originally RQ2) was **dropped** and folded into RQ1 as a covariate axis (see §5.4).
> **RQ2 is a new question** analysing *how* constructs are composed into dynamic
> dependency relationships and idiomatic usage (added after an exploratory pass over
> the full corpus revealed measurable, undocumented patterns). The graph-complexity
> question moved to RQ3 and evolution to RQ4.

| RQ | Question |
|----|----------|
| RQ1 | Which FastAPI DI constructs are used, and how frequently, across open-source projects? *(includes a covariate axis by stars and age — see §5.4)* |
| RQ2 | What dynamic dependency relationships do real FastAPI projects form, and what idiomatic roles do dependencies play? *(new — mixed-methods usage analysis, see §6)* |
| RQ3 | How complex are the resulting dependency graphs? *(renumbered from RQ4 → RQ3)* |
| RQ4 | How has DI usage evolved over time? *(deferred — requires git-history analysis)* |

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

**5,000 candidates** discovered and enriched (4,500 original snapshot plus 500
patched in 2026-09 via `finder.py --delta`; see §2.6).

### 2.3 Eligibility rules

| Rule | Criterion | Rationale |
|------|-----------|-----------|
| E1 | `fastapi` imported in ≥ 1 PRODUCTION file (extractor) | Dev-only deps do not constitute real usage |
| E2 | Not a fork, not archived | Original codebase, not abandoned |
| E3 | `pushed_at` within the last 60 months | Active, not abandoned |
| E4 | ≥ 2 distinct files importing `fastapi` (`E4_MIN_FASTAPI_FILES`) | Reject single-file / demo projects |

**Rule revision (2026-09).** The earlier E1–E6 gate added a Python-byte-ratio
threshold (old E2, ≥ 0.5) and a tutorial-marker *flag* (old E6). Both were
dropped in the current E1–E4 rules: the Python-share gate removed real
mixed-language FastAPI apps (PyTorch/notebook-backed services, microservice
repos) and the tutorial flag did not separate genuine from non-genuine apps
(§10). Rule values, counts, and the revision rationale are in
`docs/github_stratified_scan_stats.md`.

#### 2.3.1 Threshold robustness (legacy E2 note)

The old gate's 0.5 Python-byte-ratio cut was a stated convention, not a
distribution-derived value; a per-threshold sweep showed RQ1 ordering was
insensitive to it. This entire axis is **moot in the E1–E4 gate** — the
byte-ratio rule was removed, so no accepted repo is contingent on it. The
current robustness claim is the file-import threshold sweep (§8).

### 2.4 Filtering results

| Decision | Count | % of pool |
|----------|-------|-----------|
| E4 — below scale (single-file/demo) | 1,281 | 25.6% |
| E2 — fork or archived | 800 | 16.0% |
| E1 — no production `fastapi` import | 516 | 10.3% |
| Clone failed (metadata unavailable) | 224 | 4.5% |
| **Accepted (E1–E4 pass)** | **2,179** | **43.5%** |
| **Total** | **5,000** | **100%** |

Every candidate has a decision. The 224 clone failures are
repos that could not be cloned at snapshot time (deleted/private or transient
network) — recorded in `corpus/exclusion_log.json` as `clone_failed`.

### 2.5 Clone failures and population attrition

- Repos returning GitHub API 404 / failing to clone at check time are
  reclassified `clone_failed` (224; deleted/private between snapshot and
  cloning, or transient failures). These are permanent-until-recheck
  attrition; recorded under Threats as population attrition.

### 2.6 2026-09 candidate-pool expansion (4,500 → 5,000)

- The candidate pool was broadened from 4,500 to 5,000+ to sample the dependents
  list more deeply: 17 additional raw-dependent pages were scraped live
  (167 total, archived in `corpus/raw_dependents/`) and +500 candidates were
  enriched without re-deciding any already-finalised candidate.
- `corpus/finder.py --target 5000 --skip-scrape` replays the cached 150 pages
  then continues live from the last cursor; `corpus/filter.py --delta` processes
  only not-yet-decided candidates and merges into the existing manifest and
  exclusion log. A fresh machine can reproduce the full pipeline from scratch
  with `scripts/build_corpus.sh` (defaults to a 5,000-candidate target).
- Clone retention: after `--delta`, rejected clones are pruned and accepted
  clones are kept (`CLONE_RETENTION="accepted"` in `corpus/settings.py`), so the
  on-disk clone set mirrors the accepted census for audit + E6 structural signals.
- Additions at +509 candidates: **+51 accepted**, no prior decision was altered.
- The frozen seed-42 pilot sample (pool_size=351, `analysis/out/sample.json`) is
  **not** re-drawn; see §4.

---

## 3. Recall benchmark (independent signal)

**Method:** Pulled `topic:fastapi` repository search (GitHub search API, sort=stars, top 1,000), snapshotted to `corpus/topic_seed.json`. Measured overlap with the dependency-graph pool.

| Pool | Size | Overlap with topic:fastapi | % overlap |
|------|------|----------------------------|-----------|
| Candidates (dep-graph) | 5,000 | 2 | 0.0% |
| Accepted | 2,179 | 1 | 0.0% |

**Exactly one accepted repo (0.0%) overlaps with the topic:fastapi signal** (the 2,179-accepted `MoMoM101/RAG-ReActAgent`; the other topic hit, `allgpt-co/QuickVoice`, is a candidate that failed the E1–E4 gate). An alternative corpus strategy built on the topic signal would recover ~0% of this population — the dependency-graph source captures an entirely different population: the topic signal finds templates/tutorials; the dependency graph finds real users. This is a strong, reproducible finding for the MSR methodology section.

---

## 4. Sampling

- **FULL-CORPUS CENSUS: Pool N = 2,179; all 2,179 accepted repos are analysed** (`--scope all`). This is a census, not a sample — every accepted repo contributes to every downstream table.
- **Separate peer-review sample (327) and pilot sample (100)** are used only for *manual verification* (extractor review, RQ2 qualitative idioms), never for statistical inference. The 327 is the star-stratified review sample (`analysis/out/sample.json`, schema 0.2, seed 42, quadrant weights — see `docs/github_stratified_scan_stats.md`); the legacy pilot sample is frozen at draw-time pool and is *not* re-drawn on corpus expansions.
- Census aggregation: `uv run python analysis/aggregate.py --scope all` → `analysis/out/rq1_constructs.csv`, `rq1_by_stars.csv`, `rq1_by_age.csv`, `rq4_graphs.csv`, `covariates.csv`, `sensitivity.csv`, `summary.md`.

---

## 5. RQ1 — Construct prevalence

### 5.0 Construct catalogue reconciliation

> The design catalogue (`docs/construct_catalogue.md`) originally defined ten
> candidate constructs. **Four (C1–C4) are operationalized** as per-repo
> prevalence counters and reported below. The catalogue has been renumbered so its
> C1–C4 match this section exactly (and its C9/C10 are explicitly marked
> *not operationalized*). Router-level wiring, app-level wiring, dependency
> overrides and callable-class dependencies are **compositions of C1/C2** (see
> §5.1 note) and are no longer reported as separate construct rows. Two
> constructs are intentionally not measured:
>
> - **Nested dependency (C9)** — not a distinct syntactic construct but a
>   graph-topological property (a dependency that is itself the target of another
>   dependency, i.e. a node with both incoming and outgoing edges). It is captured
>   by the RQ3 dependency-graph analysis (median depth, fan-out) and the RQ2
>   relationship analysis (chained edges, dependency roles) rather than as a
>   C-series prevalence counter.
> - **Parameterized dependency (C10)** — marked "Maybe detectable" in the
>   catalogue; factory-generated dependencies are not statically decidable from a
>   call site, so counting them would risk false positives. Deferred.

### 5.1 Primary constructs (C1–C4)

The four primary constructs are **mutually swappable spellings of a single
injection mechanism**: `Depends` (C1), `Security` (C2), `Annotated[..., Depends]`
(C3) and the generator/yield form (C4) resolve the same way, so a dependency
re-expressed in another construct keeps its behavior — C1⇄C3 differ only in
annotation-vs-default-value spelling, and C4 is consumed via the C1/C3 call site.
The swappable-pattern catalog (`analysis/swappable/out/catalog.json`) measures
this in the wild: **1,142 providers are written in two or more constructs within
one repo** (an *observed swap instance*), 933 of them as pure `C1|C3` pairs.

| ID | Construct | Repos (n/2,179) | % of corpus | Total calls | Median (users) | IQR (users) | Max |
|----|-----------|---------------|-------------|-------------|----------------|-------------|-----|
| C1 | `Depends` | 1,371 | 62.9% | 98,243 | 22.0 | 7.0–66.0 | 1,940 |
| C2 | `Security` | 104 | 4.8% | 620 | 1 | 1.0–2.8 | 305 |
| C3 | `Annotated[..., Depends]` | 384 | 17.6% | 23,241 | 10.0 | 4.0–44.8 | 3,880 |
| C4 | Generator/yield dep | 759 | 34.8% | 1,003 | 1.0 | 1.0–1.0 | 14 |

> **Note (derived, non-construct placements).** Router-level wiring
> (`APIRouter(dependencies=...)`), app-level wiring (`FastAPI(dependencies=...)`),
> dependency overrides (`app.dependency_overrides[...]`) and callable-class
> dependencies are *compositions* of the core constructs: their `Depends(...)`
> call sites are already counted under C1/C2, and no repository uses them without
> also using a core construct. They are therefore structural placements, not
> standalone constructs, and are intentionally excluded from this table.

### 5.2 Additional observations

| Observation | Count | Notes |
|-------------|-------|-------|
| Non-FastAPI Depends sources | 10 repos (0.5%), 22 calls | Depends on non-FastAPI callables (external middleware, etc.) — rare. |
| **Zero-DI cohort** | **805 repos (36.9%)** | Repos where `depends_total + security_total + annotated_depends_total = 0`. These pass E4 (≥ 2 distinct files import fastapi) and the corpus rules but use no core DI constructs at all. A genuine population of real FastAPI apps without DI. *Construct-presence measure* — the LLM strategy-attribution census (`methodology_journal.md` §3.2) re-sorts repos by dominant wiring strategy (S1 direct construction = 1,188, 54.5%), so this 805 figure describes *absence of framework constructs*, not the S1 strategy bucket. |

### 5.3 Key trends and interpretations

1. **`Depends` is dominant but not universal.** 62.9% of real FastAPI apps use it; the zero-DI cohort (36.9%) does not. The DI system is clearly not mandatory for real-world usage.
2. **Generator/yield deps are surprisingly common** (34.8%) — more common than `Annotated[..., Depends]` (17.6%), despite the latter being the "modern" recommended style.
3. **`Security` is underused** (4.8%) despite being a headline FastAPI feature for authentication. Median usage among users is just 1 call — most apps have a single `Security()` site. Moreover, **0 of 620 call sites pass `scopes=[...]`**, so `Security()` is behaviorally interchangeable with `Depends()` in every observed use — further evidence that the constructs form a swappable set.
4. **The core DI surface is small.** Four constructs (C1–C4) cover essentially all framework DI in production FastAPI code; the derived placements (router/app wiring, overrides, callable classes) are compositions of C1/C2 and are not observed without a core construct.
5. **The zero-DI cohort (36.9%) is a key finding.** These are real, substantial FastAPI applications (≥ 4 importing files, ≥ 1 app) that bypass the DI system entirely, using direct function calls or other patterns. This finding challenges the assumption that DI is the primary architectural pattern in the FastAPI ecosystem.

### 5.4 RQ1 covariate axis (folded application-class question) — DI prevalence by covariates

Folded from the (dropped) application-class question: who uses DI? Disaggregated by repo **stars** and **age** (no arbitrary application-class taxonomy).

**By stars** (`analysis/out/rq1_by_stars.csv`):

| Stars | Repos | % using core DI | Median core calls |
|-------|-------|-----------------|-------------------|
| 0 | 1,491 | 61.0% | 6 |
| 1–9 | 567 | 67.9% | 10 |
| 10–99 | 87 | 69.0% | 16 |
| 100+ | 34 | 58.8% | 3 |

**By age** (`analysis/out/rq1_by_age.csv`):

| Age | Repos | % using core DI | Median core calls |
|-----|-------|-----------------|-------------------|
| <12mo | 1,903 | 63.1% | 8 |
| 12–36mo | 206 | 63.6% | 6 |
| 36mo+ | 70 | 61.4% | 8 |

**Interpretation:**
- **DI prevalence is essentially flat across stars and age** (≈59–69% for all buckets; no monotonic trend — even the 100+ star bucket (58.8%, n=34) and the 36mo+ bucket (61.4%, n=70) sit inside the same band). Popularity and age do not predict DI adoption.
- **The corpus skews very young:** 1,903/2,179 repos are under a year old. The E4 eligibility rule admits repositories up to 60 months old, so the young skew reflects the discovered population rather than an artifact of the gate.
- **Net:** the covariate view supports the central finding that **DI use (and its absence) is a stable property across the population**, not skewed by popularity.

---

## 6. RQ2 — Usage & dynamic relationships (mixed methods)

### 6.0 Constructs vs. Usage — the definitional line

RQ1 counts **constructs**: whether a discrete syntactic API token appears at a call site (`Depends(`, `Security(`, `dependencies=[...]`). A construct is countable from the *left-hand token* alone, with no interpretation of the argument.

RQ2 analyses **usage**: *how* those constructs are composed into dynamic dependency relationships and idiomatic roles. It requires classifying the *argument and surrounding context* of each call (what is passed to `Depends(...)`? a function, a class, a classmethod, a module alias? does `Security()` pass `scopes`?) and the *relationship structure* of the resulting dependency graph (who depends on whom, fan-in hubs, chained/nested dependencies, class vs. function nodes). This is relationship analysis over the same extraction, **not** token counting.

The distinction is already latent in the construct catalogue: **C9 (nested dependency)** is explicitly *not a syntactic construct* but a graph-topological property "captured by the dependency-graph analysis (RQ3)" — i.e. a usage-level concept. This section makes that usage-level lens first-class.

Operationally: `analysis/usage_patterns.py` reads the frozen reports (`corpus/reports/*.json`) and classifies each `Depends()`/`Security()`/`Annotated()` call site plus the dependency graph. **No re-extraction.** Mixed methods: Tier A is quantitative and corpus-scale; Tier B is a qualitative, explicitly-low-n idiom catalog.

### 6.1 Tier A — quantitative facets

**`Depends()` argument shapes** (production scope, 98,243 call sites across 1,371 repos):

| Shape | Calls | % calls | Repos |
|---|---|---|---|
| bare function (`Depends(get_db)`) | 94,889 | 96.6% | 1,354 |
| module alias (`Depends(deps.get_session)`) | 2,433 | 2.5% | 54 |
| placeholder (`Depends(...)`, `<empty>`) | 720 | 0.7% | 120 |
| title-case class (`Depends(HTTPBearer)`) | 178 | 0.2% | 28 |
| classmethod (`Depends(X.as_form)`) | 23 | 0.0% | 4 |

The overwhelming idiom is *passing a plain callable* — 96.6% of `Depends()` sites pass a bare function reference. No `Depends(foo())` naive calls and no lambdas were found in the accepted census.

**`Security()` OAuth2 scopes are never used.** Of **620** `Security()` call sites across **104** repos, **0 pass `scopes=[...]`** (0.0% of calls and 0.0% of Security-using repos). The OAuth2 *scopes* mechanism FastAPI advertises for fine-grained authorization is effectively unadopted in the wild — `Security(scheme)` is used purely as a flag, never with scope arrays.

**Dependency-graph relationship topology** (1,338 graph-bearing repos):

- **1,338/2,179** repos have a non-empty graph: **62,200 function nodes + 2,682 class nodes** (4.1% class; **432 repos** contain class nodes), **90,863 directed edges**.
- **708 fan-in hub nodes** with ≥10 dependents — the *relationship-level* signature of FastAPI DI: a small set of shared dependencies (auth guards, DB sessions, current-user providers) each consumed by a large number of handlers. Top hubs: `get_db` (24,014 dependents), `get_current_user` (11,432), `get_session` (5,014), `require_admin` (3,030), `require_permission` (1,764), `get_db_session` (1,390), `require_role` (1,349), `require_user` (960).
- **Nested/chained dependencies exist at the graph level (C9):** edges where the target is itself a dependency (`require_api_admin → require_api_token`, `get_current_user → get_session`). Median depth 2, max 7 — chains are short but real. This confirms C9 is a usage-level (relationship) property, not a syntactic counter.
- **521 repos** have at least one unresolved dependency — a resolver-coverage footprint, not a usage claim (see §12.5).

**`Annotated[...]` type roles** — the top annotated types encode dependency *semantics*, dominated by request-context/session roles and domain objects: `AsyncSession` (2,435), `User` (2,133), `ActorContext` (1,630), `KernelContainer` (1,312), `Session` (1,107), then principal/session objects (`Principal`, `AuthPrincipal`, `AuthIdentity`) and configuration/registry types (`Settings`, `Any`). These are *what* practitioners name as injected dependencies.

### 6.2 Tier B — qualitative idiom catalog (low n, explicitly non-statistical)

These are *discovered patterns* practitioners invented beyond the documented API. Counts are tiny and reported as evidence-with-n, not headline rates:

| Idiom | Repos | Evidence |
|---|---|---|
| classmethod-as-dependency (`.as_form`/`.as_dependency`) | 6 repos | `.as_form`, `.from_query_parameters`, `.has_permission`, `.is_authed`, `.is_authed_optional`, `.require_role` — Pydantic models doubling as form-parsing dependencies |
| class-as-dependency (`Depends(MyClass)`) | 38 distinct classes / 28 repos | `APIKeyAuth`, `APIKeyHeader`, `AdminOnly`, `ArrestService`, `AttachmentRepo`, `AttachmentService`, `AttachmentStore` — constructor-injected classes |
| `provide_*` service-locator dialect | 3 repos | a `provide_*` namespace acting as a DIY service locator over DI |
| `current_*` request-scope injection | 76 repos | `current_*_repository`, `current_audit_sink`, `current_tenant_authorization` — request-scoped context objects injected via DI |
| module-alias dependencies | 54 repos | `deps.get_session`, `dependencies.get_prefect_client_version` — namespaced dependency getters |
| `*Repository`-typed injection | 1 repo | repository pattern observed as an injected type |

> **Note on `.as_dependency`:** a second classmethod-DI variant (`Class.as_dependency`) exists in `mealie-recipes/mealie`, but that repo is not in the current 2,179-repo accepted census, so it is reported here as an observed out-of-corpus idiom, not a census count.

### 6.3 Constructs vs. Usage — implications

- RQ1 tells us *whether* constructs appear; RQ2 tells us *how* they behave as a system. Together they separate "FastAPI DI adoption" from "FastAPI DI shape".
- The `Security(scopes=...)` zero-usage result is the strongest non-obvious, corpus-scale finding of RQ2.
- Tier B shows the community extends the API in ways the docs don't teach; but these are low-frequency, so RQ2's *quantitative* claims rest on Tier A.

---

## 7. RQ3 — Dependency-graph complexity

Filtered to the **1,338/2,179 repos with non-empty **clean** dependency graphs** (after dropping resolver-emitted junk nodes; see below). The remaining 841 repos have zero clean graph nodes — these do not form a DI graph the resolver can follow.

| Metric | Median | IQR | Max |
|--------|--------|-----|-----|
| Nodes (clean) | 19.0 | 7–49 | 1,444 |
| Max depth | 2 | 2–3 | 7 |
| Unresolved % | 0.0 | 0.0–3.3 | 100.0 |

- **817/1,338 (61.1%)** of graph-bearing repos have a 0% unresolved rate — the resolver handles them cleanly.
- **21 repos have 100% unresolved** — a small outlier set with fully-unresolved graphs, likely relying on patterns the resolver cannot follow.
- **Graphs are shallow in the median but not flat everywhere:** median depth 2, max 7. FastAPI DI in practice forms flat dependency trees in the typical case; a small deep tail exists (see §7.2). This aligns with the API's design philosophy of explicit, inspectable dependencies.

### 7.2 Deep-tail: repos with long cross-callable chains

The median depth hides a real but small tail of repos where dependencies
chain through 5+ callables. We isolated every repo with `max_depth ≥ 5`
(`analysis/rq3_depth_tail.py` → `analysis/out/rq3_depth_tail.csv`):

| Depth | ≥5 (tail) | 5 | 6 | 7 |
|-------|-----------|-----|-----|-----|
| Repos (of 1,338 graph-bearing) | 58 (4.3%) | 43 | 11 | 4 |

- **Every tail repo still has a fan-out hub (58/58, 100%)** — depth is an
  overlay on top of the shared-hub pattern, not a replacement for it.
- Tail repos are **larger apps**: median **116 clean nodes** and **207 clean
  edges**, vs census medians of **19 nodes / 20 edges**.
- Chains resolve cleanly: median unresolved 0.6%; 17/58 fully-resolved **and**
  pull the full reported depth as genuine callable chains (the resolver counts
  a junk `file:line` node in a few cases, making the raw depth 1 higher than
  the clean chain in 6/58 repos).
- The deepest chains are *layered service constructions* — every depth-7 chain
  reads `endpoint → service → service → service → repository → db`, e.g.
  `handle_swipes → get_swipe_service → get_spotify_service → get_spotify_cache
  → get_redis_client → get_redis → get_state` (`GG-Angel/overplayed`).
- Tail repos skew young (54/58 < 12 mo) and low-star (36/58 zero-star) — deep
  chains are a **novice/early-architecture pattern**, not a sign of
  sophistication at scale.
- **Interpretation:** keep the "broad-and-shallow" headline (it holds for the
  corpus and, notably, even 4.3% of repos), but report the tail explicitly:
  FastAPI DI *permits* chains that reach 5–7 hops; in practice they arise in
  smaller, younger apps that stack service layers end-to-end instead of
  converging on shared hubs.

### 7.1 Data-quality fix: resolver-emitted junk nodes

The dependency graph construction had a genuine contamination bug. In `resolver.build_dependency_graph`, when a `Depends` call occurs **outside any function context** — module-scope declarations such as `FastAPI(dependencies=[...])` or router defaults — `context_function` is `None` and the resolver falls back to a `"{file_path}:{line}"` placeholder as the source node id (resolver.py line 112). These filesystem-path ids are not callable names.

- **Measures:** On the full corpus, **425/2,179** repos contain such junk nodes — **2,656 junk nodes of 64,882 total (4.1%)**.
- **Effect:** Inflates node counts (median 20 raw → **19.0** clean for graph-bearing repos) and can add spurious edge/density values. All 1,338 graph-bearing repos retain a non-empty clean graph; the junk was additive, never the sole content.
- **Fix:** `analysis/aggregate.py` now filters any node id containing a path separator or `file:line` anchor before computing RQ3 (both raw and clean columns are retained in `rq4_graphs.csv` for transparency).
- **Reporting sentence:** *"We filtered resolver-emitted non-callable artifact nodes (file:line placeholders from module-scope dependency declarations) from the dependency graphs before computing complexity metrics."*
- **RQ1 note:** RQ1 construct counts (C1–C4) come from `file_details`/aggregate call counts, not graph nodes, so RQ1 is unaffected by this bug.

---

## 8. Sensitivity analysis (E4 file-count threshold)

The E4 threshold (`fastapi_files ≥ t`) is empirically anchored at the observed distribution gap. Sensitivity analysis re-runs headline statistics at every threshold in `[2, 3, 4, 5, 6, 8]` over the **accepted** pool.

| Threshold (t) | Eligible N | % using core DI | Median depends_total (all) | Median depends_total (users) |
|---|---|---|---|---|
| 2 | 2,150 | 63.1% | 8 | 26 |
| 3 | 1,720 | 70.2% | 13 | 30 |
| **4 (base)** | **1,451** | **76.2%** | **19** | **35** |
| 5 | 1,284 | 79.4% | 24 | 40.5 |
| 6 | 1,167 | 80.8% | 27 | 45 |
| 8 | 937 | 84.1% | 41 | 55.5 |

**Interpretation:** Qualitative conclusions are stable across all thresholds. As the threshold tightens (fewer repos, more substantial apps), DI usage rises modestly (63.1% → 84.1%) and per-repo call counts rise — larger apps use DI more. The base threshold of 4 captures the full structurally-meaningful pool without sacrificing conclusion robustness.

**Caveat:** Threshold 2 is near-null (2,150/2,179 repos pass; the 29 below are the low-file tail), and the base threshold (t=4, 1,451 repos) is a deliberate balance between inclusiveness and structural meaning. Sensitivity analysis is most meaningful for thresholds **above** the base (t ≥ 5), where DI usage and call counts climb monotonically.

---

## 9. Corpus covariates (accepted pool, N=2,179)

| Metric | Median | Min | Max | Notes |
|--------|--------|-----|-----|-------|
| `fastapi_files` | 6 | 1 | 493 | Range indicates highly skewed distribution |
| `fastapi_app_count` | 1 | 0 | 78 | Most repos expose a single app |
| `pct_production` | 80% | 10% | 100% | Production file coverage |
| `stars_gh` | 0 | 0 | 84,888 | 1,491 repos (68.4%) have 0 stars — stars are recorded as covariate only, never used as an eligibility filter |
| `py_ratio` | 0.644 | 0 | 1.0 | Python dominance relaxed versus the old corpus (the 0.5 byte-ratio gate was removed — see `github_stratified_scan_stats.md`) |
| `tutorial_flag` | — | — | — | E6 was dropped from the revised E1–E4 funnel; no tutorial-flag field exists in the new manifest |

---

## 10. Tutorial flag (E6) — historical (superseded)

> **Note:** E6 and the tutorial-flag analysis below belong to the **old E1–E6 corpus era**. The revised funnel for the 2,179-repo census uses **E1–E4 only** (`corpus/filter.py`, see `docs/github_stratified_scan_stats.md`) — E6 was dropped, so this section is retained for transparency about the removal decision, not as a live census result.

E6 flags repos whose description or README contains tutorial/demo markers. It never auto-excludes; a human resolves each flag.

**Status:** 188 of 402 (47%) accepted repos carry tutorial flags.

A blinded human review (`analysis/e6_sample.py`, fixed-seed stratified subsample of 24 flagged + 24 unflagged control drawn from the 162-flag pool of the 351-repo corpus era, labels recorded before un-masking) finds:

| label | flagged (n=24) | control (n=24) |
|-------|----------------|----------------|
| genuine application | 16 (66.7%) | 21 (87.5%) |
| uncertain (research / portfolio / challenge) | 6 (25.0%) | 2 (8.3%) |
| demo / tutorial / scaffold / capstone | 2 (8.3%) | 1 (4.2%) |

- Flagged genuine rate **66.7%** (Wilson 95% CI 46.7–82.0%); control **87.5%** (CI 69.0–95.7%).
- **Genuine-ness is the majority class in both groups.** The README tutorial marker is a weak, noise-heavy signal: it modestly over-selects non-genuine repos (33% vs 12.5% non-genuine) but most flagged repos are real applications.
- Structural sophistication (entry points, DB schema/migrations, auth, caching, integrations, tests — `analysis/e6_structural.py`) separates the few clear demos (median index 1–5) from genuine apps (median 6–7), but does **not** separate the flagged pool from the unflagged baseline (flagged-genuine median 7 ≈ control-genuine 6). Full write-up: `analysis/out/e6_findings.md`.
- The "uncertain" class is structurally the *richest* (median index 7–10): aspirational, heavily-scaffolded projects (OWNEX, CEREBRO-X, cadence-clinical, dharma_swarm) — a distinct pattern from thin demos.

**Sensitivity into RQ numbers:** because flagged repos are mostly genuine, including/excluding them does **not** overturn the RQ1/RQ3 headline aggregates (the flagged subset largely mirrors the unflagged baseline). See Section 12.4.

**Implication for corpus definition:** E6's flag is unsuitable as a hard exclusion rule; it should remain a documentation-only flag. Recomputation under a tighter rule (e.g. only multi-marker or demo-labeled repos) is feasible but not required by the current findings.

---

## 11. Data artifacts

All artifacts are schema-versioned, byte-stable (sorted order), and fully reproducible from committed source.

| Artifact | Description |
|----------|-------------|
| `corpus/candidates.json` | 5,000 enriched candidates (finder output) |
| `corpus/manifest.json` | 2,179 accepted repos + metadata + extractor snapshots |
| `corpus/exclusion_log.json` | 2,821 excluded repos with first-failing rule (incl. 224 clone_failed) |
| `corpus/reports/<name>.json` | Full extractor report per accepted repo (2,179 accepted; stale non-manifest reports remain on disk) |
| `corpus/raw_dependents/` | Snapshotted GitHub dependents HTML — 167 pages (reproducibility) |
| `corpus/topic_seed.json` | 1,000-topic benchmark seed snapshot |
| `analysis/out/sample.json` | star-stratified review sample of 327 from pool 2,179 (seed 42, schema 0.2; manual verification only — final tables are the census) |
| `analysis/out/rq1_constructs.csv` | Construct prevalence table (C1–C4 + extras) |
| `analysis/out/rq4_graphs.csv` | Per-repo graph statistics (legacy filename; feeds RQ3) |
| `analysis/out/usage_patterns.csv` | RQ2 usage/relationship facets (arg shapes, scopes, graph topology, annotated roles) |
| `analysis/out/usage_patterns_summary.md` | RQ2 mixed-methods write-up (Tier A quantitative + Tier B idiom catalog) |
| `analysis/out/covariates.csv` | Per-repo metadata (stars, age, coverage, etc.) |
| `analysis/out/sensitivity.csv` | file-threshold sensitivity analysis (t = 2–8) |
| `analysis/out/summary.md` | Human-readable extraction summary |
| `analysis/out/pattern_features.csv` | Per-repo DI-style predictor matrix (Phase 1) |
| `analysis/out/ast_quality.csv` | Per-repo AST quality/complexity metrics (Phase 2A) |
| `analysis/out/github_signals.csv` | Per-repo GitHub maintainer signals (Phase 2B) |
| `analysis/out/pattern_outcomes.csv` | Joined dataset for the pattern comparison |
| `analysis/out/pattern_compare_results.md` | Style × outcome table + standardized regressions (Phase 2C) |
| `analysis/out/bench_di_results.md` | DI-style runtime micro-benchmark (Phase 3) |

---

## 12. Caveats and threats

### 12.1 Population definition
- **Source:** GitHub dependency-graph dependents only. Repos using FastAPI without declaring it in a manifest that GitHub's dependency graph parses (e.g., Docker-pinned installs, git-submodule workflows) are invisible to discovery.
- **Substitution:** GitHub dependency graph replaced Libraries.io (disabled server-side, librariesio/libraries.io#2647). Reported as a threat under open-access data dependency.

### 12.2 Population attrition
- 224 repos (4.5%) were un-retrievable at clone time (`clone_failed`). Documented via `exclusion_log.json`; normal attrition for a cross-sectional GitHub study.

### 12.3 E4 threshold sensitivity
- Sensitivity is most meaningful for thresholds **above** the base (t ≥ 5), where DI usage and call counts climb monotonically. Threshold 2 is near-null (2,150/2,179 pass; the 29 below are the low-file tail).
- A lower threshold could only be evaluated against the full 5,000 candidate pool (including E4-excluded repos), which would require their extractor reports — these do not exist for repos excluded before E4.

### 12.4 E6 tutorial flags (historical — superseded)
- **Status as of 2026-09:** E6 was dropped from the revised E1–E4 funnel; the tutorial flag is no longer part of corpus construction or headlining. The material below is retained for historical rationale. See "Rule revision (2026-09)" in §2.
- The high flag rate (47%) is a population property: FastAPI projects frequently describe themselves in tutorial-associated language, and the README marker regex is not a useful exclusion rule.
- A blinded review of a 24-flagged / 24-control subsample (`analysis/out/e6_findings.md`) confirms genuine-ness is the majority class in both groups (66.7% flagged vs 87.5% control). The flagged pool is only modestly over-selected for non-genuine repos (33% vs 12.5%), and structural sophistication does not separate the two pools — so **including or excluding flagged repos does not materially change the RQ1/RQ3 headline aggregates** (constructs and graphs). RQ numbers are insensitive to E6.
- The label set is a single-reviewer judgment sample (drawn from the 402-repo era and frozen); treat rate estimates as indicative and spot-check for inter-rater consistency before any stronger claim.

### 12.5 Extractor limitations
- **Resolver junk nodes (mitigated):** module-scope `Depends` declarations produced `file:line` placeholder nodes (2,656 across 425/2,179 repos). Filtered at aggregation time; see §7.1. The resolver *output*, not the extraction of construct counts, is affected — RQ1 is clean.
- **RQ4 (evolution over time) not yet measured.** Requires per-repo git-history analysis; planned as a later phase once RQ1/RQ2/RQ3 tables are complete.
- **Resolver coverage:** 841/2,179 (38.6%) of accepted repos have empty dependency graphs despite passing E1–E4 — in some cases the resolver cannot follow cross-file patterns. Resolver quality should be reported as a coverage metric, not treated as a failure.

### 12.6 Census (not a sample) design
- Analysis is a **full-corpus census over all 2,179 accepted repos**; there is no sampling inference to generalize from, so standard-errors-inference does not apply — the RQ1/RQ2 figures ARE the population values.
- The stratified review sample (N=327) is used only for manual verification of the extractor; it is superseded by the census for all reported figures (see §4).
- Sparse covariate buckets (e.g. 100+ stars = 34 repos, 36mo+ = 70 repos) hold too few repos for stable conclusions and are reported for completeness, not over-read (see §5.4).

---

## 13. Planned Up Ahead

2. ~~**Tutorial flag decision:**~~ (resolved — E6 retired in the revised E1–E4 gate; Section 10 retained as historical rationale).
3. **RQ4 git-history script:** implement per-repo temporal analysis, building on the existing extractor.
4. **Controlled change-cost experiment** (resolves the "which pattern is best" bound from §14): hand-write equivalent apps per style and measure edit-blast-radius over modification tasks — the only design that can support a causal "best"-style claim.
4. **Paper write-up:** methodology section and RQ1/RQ2 results are ready for first draft. Overlap benchmark (0%) is a strong methodological contribution.
5. **Threats section:** document all items from Section 12, particularly the threshold-sensitivity caveat.

---

## 14. Comparative assessment of DI patterns (exploratory)

> **Era note (2026-09-25):** This section has **not** been re-run over the
> 2,179-repo census. The `pattern_features` / `ast_quality` / `github_signals` /
> `pattern_outcomes` outputs remain from the earlier **402-repo run** and are
> retained here for continuity. Its numbers below are **NOT comparable** with
> the §5/§6 census figures and must be re-computed (or dropped) before this
> draft is used. RQ3 output (`rq4_graphs.csv`) *is* census-refreshed; this
> sections is the only remaining 402-era block.

*Scripts: `analysis/pattern_features.py`, `analysis/ast_quality.py`,
`analysis/github_signals.py`, `analysis/pattern_outcomes.py`, `analysis/bench_di.py`.
Outputs: `analysis/out/pattern_features.csv`, `ast_quality.csv`,
`github_signals.csv`, `pattern_outcomes.csv`, `pattern_compare_results.md`,
`bench_di_results.md`.*

A deliberately *bounded* question: does the DI style a repo chooses associate
with maintainability proxies, and does any style carry a measurable runtime
cost? This section answers **associations**, not "which pattern is best" — a
ranking is not statistically resolvable here because the Tier B idiom groups are
tiny (n=1–15) and the design is cross-sectional and observational.

### 14.1 Outcome means by style

Per-repo features joined for **402 accepted repos (402-era run)**; GitHub maintainer signals
for 390/402 (98.5%; 12 deleted/private), of which **384** (95.5%) have issue
tracking enabled and enter the issues-per-kLOC model.

| style | n | hygiene (0–5) | sophist. | func_len | branch/fn | doc% | type-ann% | issues/1kLOC | contribs |
|---|---|---|---|---|---|---|---|---|---|
| bare-function dominant | 279 | 3.27 | 6.5 | 20.6 | 2.56 | 43 | 92 | 0.36 | 5 |
| zero-DI | 98 | 2.72 | 4.9 | 21.8 | 3.07 | 47 | 88 | 0.18 | 26 |
| class-as-dependency | 7 | 3.71 | 7.3 | 17.9 | 1.98 | 64 | 84 | 1.24 | 6 |
| `current_*` request-scope | 15 | 3.33 | 7.7 | 21.4 | 2.68 | 51 | 95 | 0.15 | 4 |
| module-alias deps | 3 | 2.67 | 4.3 | 21.2 | 2.94 | 34 | 86 | 0.06 | 28 |

### 14.2 Regression highlights (standardized OLS, controls for stars/age/size/Python share/tutorial flag — 402-era run)

Descriptive census regressions (HC1 robust SEs); CIs are descriptive, not
sampling inference (see §12.6).

- **module-alias deps (continuous share; n=3 dominant / 11 users):** positive for
  hygiene, sophistication, func length, branch density, docs, annotations, and
  *negative* for open-issues-per-kLOC. Direction is consistent but the effective
  n is tiny — treat as incidental evidence, not a recommendation.
- **hub-rich graph (fan-out≥3):** positive for sophistication and mean function
  length — larger/healthier repos are the ones that build shared hub
  dependencies.
- **`current_*` request-scope:** negative for branch density (CIs exclude 0).
- **zero-DI:** positive for log#contributors — repos that skip DI constructs
  tend to have more contributors (collinear with maturity, not necessarily
  causal).
- **class-as-dependency and `Annotated[...]`:** all CIs include 0 — no
  detectable association with any proxy outcome.

Net: once maturity/size are controlled, **no style is robustly "better" on
maintainability proxies**, and the few significant coefficients cluster in
n≈3–15 groups.

### 14.3 Runtime micro-benchmark

Synthetic 40-endpoint apps per style, 1500 requests/app over ASGI, best-of-3
medians:

| style | median req | vs. fastest |
|---|---|---|
| zero-DI (direct call) | 385 µs | 1.00× |
| bare `Depends(fn)` | 581 µs | 1.51× |
| class `Depends(Cls)` | 632 µs | 1.64× |
| `current_*` request-scope | 683 µs | 1.78× |

`Depends()` adds ≈0.25 ms/request on a body doing nothing → **measurable, not
free**, but a single DB round-trip (1–10 ms) dwarfs it. Run-to-run variance is
high; treat the multiplier as an upper bound on a trivial handler, not a
production ratio.

### 14.4 Bottom line

No corpus evidence supports a "single best DI pattern". Bare-function
`Depends(...)` is the community default (97.1% of call sites) and shows no
downside in any proxy outcome, so it is the defensible recommendation by
*prevalence + neutrality*. Class-based, `current_*`, module-alias, and `Annotated`
styles are neutral-to-weakly-evidenced; zero-DI trades the (small, ~0.25 ms)
DI overhead for added plumbing-by-hand with no detectable maintainability
benefit in this data. Any stronger "which is best" claim requires a controlled
change-cost experiment (planned future work) or maintainer surveys.
