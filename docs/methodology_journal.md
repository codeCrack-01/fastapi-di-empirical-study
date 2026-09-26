# FastAPI Dependency Injection in the Wild — Methodology Journal

*A census over 2,179 open-source FastAPI repositories: how the framework's
dependency-injection constructs are used, what relationships they form, and
which DI styles practitioners actually adopt.*

Data universe: `corpus/manifest.json` (2,179 accepted repos). Primary write-ups:
`docs/result_draft_01.md`, `docs/methodology_notes.md`. Analysis scripts under
`analysis/`, `corpus/`. All figures reproduce offline from committed artifacts
(`uv sync` + run scripts).

---

## 1. Study design

**Objective.** Measure, at corpus scale, (a) which FastAPI DI constructs appear
and how frequently (RQ1), (b) how those constructs are composed into dynamic
dependency relationships and idiomatic roles (RQ2), (c) the structural
complexity of the resulting dependency graphs (RQ3), and (d) whether the
observable DI styles differ on maintainability proxies and runtime cost
(exploratory comparison, §Appendix). Evolution over time (RQ4) is deferred.

**Design.** A **full-corpus census**: every repository that clears eligibility
is included. There is no sampling inference; reported figures are population
values, not estimates. A seed-42 subsample (N=100, `analysis/out/sample.json`,
draw-time pool 351) was used only for the extraction bug audit and is frozen.

**What is counted.** A *construct* is a discrete syntactic API token at a call
site (left-hand token): `Depends(`, `Security(`, `dependencies=[...]`,
`Annotated[Depends(...)]`. *Usage* additionally classifies the argument
(function / class / classmethod / module alias) and the graph relationship
(fan-in, chaining, class-vs-function nodes). Constructs answer *whether*;
usage answers *how*.

---

## 2. Methods

### 2.1 Population and target

Population: open-source GitHub repositories using FastAPI — import `fastapi`
and expose ≥ 1 `FastAPI()` app. Candidate discovery targets 5,000 repos
(`TARGET_CANDIDATES`, settings.py); the accepted census is whatever clears
E1–E4 (currently **2,179 / 5,000, 43.5%**).

### 2.2 Discovery and selection funnel

Primary source: the GitHub **dependency-graph dependents** list of
`fastapi/fastapi` (repos whose manifests GitHub resolves as depending on
fastapi). The HTML list is crawled per page and snapshotted for reprodibility
(`corpus/raw_dependents/`); each candidate is enriched via the REST API
(fork/archive flags, created/pushed dates, language byte ratios, commit count,
license, stars). Stars are recorded **as a covariate only**, never an
eligibility filter. A secondary `topic:fastapi` seed unions a subset of the
pool and also serves as the **recall benchmark** against the dependency-graph
signal.

Funnel (frozen `corpus/exclusion_log.json`):

| Stage | n | % of 5,000 |
|---|---|---|
| Candidates discovered and enriched | 5,000 | 100% |
| E4 — below scale (< distinct files importing fastapi) | 1,281 | 25.6% |
| E2 — fork or archived | 800 | 16.0% |
| E1 — no production fastapi import | 516 | 10.3% |
| Clone failed (metadata unavailable) | 224 | 4.5% |
| **Accepted (pass all)** | **2,179** | **43.5%** |

All accepted candidates have an extractor report; the 224 `clone_failed` were
non-clonable at snapshot time (permanent attrition, logged and timestamped —
these are the modern equivalent of the old `unavailable` class). Every
candidate has a decision.

**Eligibility rules (E1–E4):**

| Rule | Criterion | Rationale |
|---|---|---|
| E1 | `fastapi` imported in ≥ 1 *production* file (extractor) | dev-only deps are not real usage |
| E2 | not fork, not archived | original, active codebase |
| E3 | pushed within the last 60 months | active, not abandoned |
| E4 | ≥ 2 distinct files importing fastapi (`E4_MIN_FASTAPI_FILES`) | real app, not single-file/demo |

The earlier E1–E6 funnel (with the 0.5 Python-byte-ratio gate and the
tutorial-marker E6 *flag*) is superseded; the current E1–E4 rules measure
on-disk usage directly and drop the Python-share gate (`docs/github_stratified_scan_stats.md`). E6's blind review (24-flagged / 24-control,
66.7% vs 87.5% genuine) documented that tutorial markers did not separate the
pools on structural sophistication; the flag was retired rather than carried
forward.

### 2.3 Data acquisition

Each accepted repo is shallow-cloned (`study_repos/corpus/`, clone retention
policy = accepted-only; rejected clones pruned) and a deterministic AST
extractor (`extract.py`) produces a per-repo report recording: construct counts
per category, per-file call sites with parsed argument shape, `Security()`
scopes, `Annotated[...]` typed injection, `app.dep`/`router.dep` declarations,
overrides, yield (generator) dependencies, and the resolved **dependency
graph** (nodes with class/function kind, edges consumer→dependency).
Determinism is guaranteed by sorted, repo-relative path iteration
byte-identical across interpreters (verified 3.12 vs 3.14 on pilot repos).

### 2.4 Analysis methods

- **RQ1 (construct prevalence):** census tables over all reports; sensitivity
  re-runs every headline at file-import thresholds 2–8 on the accepted pool — no
  conclusion changes.
- **RQ2 (usage, mixed methods):** `analysis/usage_patterns.py` re-classifies
  the frozen reports (no re-extraction). Tier A = quantitative facets
  (argument shapes, fan-in hubs, `Security` scopes, `Annotated` roles). Tier B =
  qualitative, explicitly-low-n idiom catalog, reported with counts, never as
  statistics.
- **RQ3 (graph complexity):** node/edge statistics with resolver-junk nodes
  (module-scope `Depends` placeholders) filtered at aggregation.
- **Pattern comparison (exploratory):** per-repo style flags + AST quality
  proxies (`ast_quality.py`) + GitHub issue/contributor signals
  (`github_signals.py`, accepted-pool) joined; standardized OLS with HC1 robust SEs
  controlling for stars, age, size, Python share (+ tutorial flag in the E6 era); plus a
  40-endpoint/1500-request ASGI micro-benchmark per style
  (`bench_di.py`, `uv run --with fastapi --with httpx`).

### 2.5 Reproducibility

Python pinned 3.12.13, dependencies hash-pinned in `uv.lock`; snapshots for all
network sources (dependents HTML, topic seed, GitHub API responses cached);
sorted, byte-stable artifacts. Offline suites (`corpus/tests/`) verify finder
recovery and filter/retention invariants.

### 2.6 Limitations (summary)

Observational, cross-sectional; single-reviewer E6 judgments (frozen sample,
E6 era); resolver coverage 1,338/2,179 of accepted repos have non-empty graphs
(61.4%, reported as a coverage metric); RQ4 (git-history evolution) deferred;
low-n Tier B idioms are evidence-with-n only; the exploratory comparison is
descriptive (no sampling inference). The benchmark runs on minimal synthetic
apps — an upper bound on a body doing nothing, not a production ratio.

---

## 3. Results — DI pattern taxonomy and distribution (N=2,179)

Styles are assigned per repo from production-scope call sites; categories at
repo level are **not disjoint** (a repo can use several).

| Pattern | Repos | % of 2,179 | Definition / notes |
|---|---|---|---|
| **No DI at all (direct/zero-DI)** | **805** | **36.9%** | zero `Depends`/`Security`/`Annotated` call sites; handlers construct and call directly; still pass E4 (real apps, ≥ 2 files) |
| **FastAPI-native DI** | **1,374** | **63.1%** | ≥ 1 framework DI construct |
| — `Depends(fn)` bare-function dominant | 1,354 | 62.1% | 96.6% of all 98,243 call sites |
| — `Annotated[Depends(...)]` | 384 | 17.6% | typed-injection users |
| — `Security()` (OAuth2) | 104 | 4.8% | 620 call sites; **0 use `scopes=[...]`** |
| — `Depends(Cls)` class-as-dependency | 28 | 1.3% | constructor-injected classes (38 distinct classes) |
| — module-alias deps (`mod.dep`) | 54 | 2.5% | namespaced dependency getters |
| **Hand-rolled "ground-up" Python DI** | ~76–79 | ~3.5% | DIY idioms outside the resolver: `current_*` request-scope (76), `provide_*` service-locator (3); overlaps rows above |
| **External DI library** | 11 | 0.5% | **confirmed by LLM attribution census (§3.2), supersedes the ~3–6 probe:** `dependency-injector` 9 (incl. darkspock/CareerPython, gostgmaer/langchain-knoledgebase-rag, darkspock/renfeserver), `DIContainer` 1, `injector` 1 |

**Graph topology context:** 1,338/2,179 (61.4%) have a non-empty dependency graph;
1,066 (79.7% of graph-bearing) contain at least one hub with ≥ 3 consumers —
fan-out is the norm; median graph depth 2 (max 7). **Deep tail:** 58 repos
(4.3% of graph-bearing) reach depth ≥ 5 (43 @ 5, 11 @ 6, 4 @ 7); all 58 still
have a fan-out hub; tail repos skew young (54/58 < 12 mo) and larger (median
116 clean nodes vs 19 corpus-wide). See `analysis/rq3_depth_tail.py` →
`analysis/out/rq3_depth_tail.csv`.

**Caveat.** Hand-rolled and external-library DI are not first-class extractor
facets; the two numbers above come from read-only probes over the corpus and
should be treated as order-of-magnitude signals for *construct prevalence*. The
measured backbone is FastAPI-native (63.1%) vs. no-DI (36.9%) by **construct
presence**. The LLM strategy-attribution census (§3.2) supersedes the "~3–6"
external-DI estimate (11 confirmed) and re-sorts repos by dominant wiring
strategy, which is the taxonomy the benchmark uses.

---

### 3.2 LLM strategy-attribution census (S1–S4, supersedes S3/S4 estimates)

**Purpose.** The extractor rows above measure *construct presence*. To drive
the experiment's S1–S4 strategy taxonomy, we ran a full-corpus attribution
census assigning each of the 2,179 repos one strategy.

| Strategy | Repos | % of 2,179 | Definition |
|---|---|---|---|
| S1 Direct construction (zero/native-only) | **1,188** | **54.5%** | handlers construct/call dependencies directly; no container, no manual wiring |
| S2 Framework-native DI | **712** | **32.7%** | `Depends`/`Security`/`Annotated` machinery is the dominant wiring path |
| S3 Manual Python DI (explicit context) | **268** | **12.3%** | `app.state`/`request.state` context, explicit wiring of a `RequestContext`, hand-rolled providers |
| S4 External DI container | **11** | **0.5%** | `dependency-injector`-family container: 9 `dependency_injector`, 1 `DIContainer`, 1 `injector` |

**Method.** qwen3:14b (Q4_K_M, 14 GB) over per-repo evidence built by
`analysis/render_census_inputs.py` (manifest, import table, DI-vocab excerpt
from a local clone); one label per repo with evidence + `s3_mechanism` /
`s4_library`. Driver `analysis/llm_census.py` is resumable and records raw
responses. 8 records initially failed strict JSON parse; all were recovered
(re-run, then JSON re-emit fix) → **2,179/2,179 labeled, 0 parse-error rows**.
Executed on a dedicated RTX 4090 node (ollama 0.34.4; RTX 4090 24 GB, driver
595.91.07, CUDA 13.2, Ryzen 7 5700X, 62 Gi RAM); env snapshot + run/setup logs
archived under `analysis/out/executor/`.

**Reliability checks.**
- All three known external-DI anchors (`darkspock/CareerPython`,
  `darkspock/renfeserver`, `gostgmaer/langchain-knoledgebase-rag`) → S4 /
  `dependency-injector` ✓.
- `morpheuslord/PICOTTY` (S4, `injector`) is a **known false-positive seed** —
  its "injector" is a CircuitPython firmware import, not DI; it is flagged in
  the review workbook's S4 rows for the reviewers to adjudicate.
- 58 S3/S4 repos fall inside the frozen 327-sample (5 of them S4): these are the
  rows the human reviewers check against the LLM (§5 of `experiment_proposal.md`).

**Why S1/S2 differ from the extractor rows.** The extractor counts a repo
"native" if it has ≥ 1 `Depends` call site (63.1%). The attribution census asks
which strategy *governs handler dependency acquisition*, so repos mixing idioms
sort by the dominant one — hence 1,188 S1 (not 805) and 712 S2 (not 1,374). The
experiment's treatments use the S1–S4 taxonomy, so §3.1 references these counts.

---

## 4. Results — emerging patterns *within* FastAPI DI (RQ2)

Patterns observed in how practitioners use the framework's own resolver.

### 4.1 Tier A — corpus-scale patterns (98,243 `Depends()` sites / 1,371 repos)

1. **Bare-function dominance.** 94,889 sites (96.6%) pass a plain callable
   (`Depends(get_db)`), across 1,354/1,371 repos. Neither naive calls
   (`Depends(foo())`) nor lambdas appear anywhere in the census. The community
   idiom is *reference-only*, framework-injected.

   | Shape | Calls | % calls | Repos |
   |---|---|---|---|
   | bare function | 94,889 | 96.6% | 1,354 |
   | module alias (`deps.get_session`) | 2,433 | 2.5% | 54 |
   | placeholder (`...`, `<empty>`) | 720 | 0.7% | 120 |
   | title-case class | 178 | 0.2% | 28 |
   | classmethod (`.as_form`) | 23 | 0.0% | 4 |

2. **Hub-and-spoke (fan-in) topology — the relationship-level signature.** A
   small set of shared *role* dependencies each consumed by many handlers: 708
   hub nodes with ≥ 10 dependents across 90,863 directed edges
   (62,200 function + 2,682 class nodes). Top hubs:
   `get_db` 24,014 · `get_current_user` 11,432 · `get_session` 5,014 ·
   `require_admin` 3,030 · `require_permission` 1,764 · `get_db_session` 1,390 ·
   `require_role` 1,349 · `require_user` 960.

3. **Chained/nested dependencies (C9) are real but short in the median.**
   Dependencies that depend on other dependencies
   (`get_current_user → get_session`): median chain depth 2, max 7. A deep
   tail of 58 repos (4.3% of graph-bearing) reaches depth 5–7, always with a
   fan-out hub present; example depth-7 chain: `handle_swipes →
   get_swipe_service → get_spotify_service → get_spotify_cache →
   get_redis_client → get_redis → get_state` (`GG-Angel/overplayed`). C9 is a
   graph-topological property, not a syntactic counter.

4. **`Security()` scopes are unadopted.** 620 sites / 104 repos; **0.0%** pass
   `scopes=[...]`. `Security(scheme)` is used purely as an authentication flag;
   the advertised fine-grained OAuth2 scopes mechanism is effectively unused.
   The strongest non-obvious finding of RQ2.

5. **`Annotated[...]` encodes dependency semantics by role.** Top injected
   types are request-context/session/principal objects: `AsyncSession` (2,435),
   `User` (2,133), `ActorContext` (1,630), `Session` (1,107), `Principal` (739),
   `str` (734), `AuthPrincipal` (613), `Settings` (522). Practitioners name what
   a dependency *is*, not how it is wired.

6. **Class nodes are a minority.** 2,682 / 64,882 graph nodes (4.1%); 432 repos
   contain any. Class-based dependency is an edge case even among graph
   carriers.

### 4.2 Tier B — idioms practitioners invented beyond the documented API

Explicitly low-n; reported as evidence-with-n, not statistically:

| Emerged idiom | Repos | Evidence |
|---|---|---|
| classmethod-as-dependency (`.as_form`) | 6 | Pydantic models doubling as form parsers (`.as_form`, `.from_query_parameters`, `.has_permission`, …) |
| class-as-dependency (`Depends(MyClass)`) | 38 classes / 28 | constructor-injected `APIKeyAuth`, `HTTPBearer`, stores |
| `current_*` request-scope injection | 76 | `current_tenant_authorization`, `current_audit_sink` — DIY request-scoped context |
| module-alias dependencies | 54 | `deps.get_session` namespaced getters |
| `provide_*` service-locator dialect | 3 | DIY container namespace |
| `*Repository`-typed injection | 1 | repository pattern barely observed |

Several Tier B idioms (`current_*`, class-as-dep, `.as_form`) occupy the
*hand-rolled-within-FastAPI* lane of the §3 taxonomy — framework extension
points, not external libraries.

---

## 5. Headline results (one paragraph)

FastAPI DI in the wild is narrow and homogeneous: three-fifths of real
projects use the framework's resolver, almost always by passing plain
functions to `Depends` as shared, fan-in hubs (DB sessions, auth guards,
current-user providers); over a third of legit apps (36.9%) use **no** DI
construct at all; class-based, namespaced, and typed-injection styles exist but
at single-digit prevalence; `Security`'s scopes feature is unused; and external
DI libraries are near-absent (11 repos, 0.5%, per the attribution census §3.2).
By dominant wiring strategy the picture is S1 direct construction (54.5%),
S2 framework-native (32.7%), S3 manual context (12.3%), S4 external (0.5%).
The exploratory comparison finds no style
robustly "better" once maturity/size are controlled, and the runtime cost of
`Depends()` (~0.25 ms over a trivial body) is negligible against any real
handler work — so the defensible recommendation is the community default
(bare-function `Depends`), by prevalence and neutrality.

---

## 6. Deferred work

- RQ4 evolution via git history (un-shallowing required; deliberately not done).
- Controlled change-cost experiment (§14) to support a causal "best pattern" claim.
- Making external-DI-library detection a first-class extractor facet.
- Inter-rater validation of the E6 judgment sample.