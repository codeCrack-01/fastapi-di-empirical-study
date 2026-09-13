# FastAPI Dependency Injection in the Wild — Methodology Journal

*A census over 402 open-source FastAPI repositories: how the framework's
dependency-injection constructs are used, what relationships they form, and
which DI styles practitioners actually adopt.*

Data universe: `corpus/manifest.json` (402 accepted repos). Primary write-ups:
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
E1–E6 (currently **402 / 5,009, 8.0%**).

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

| Stage | n | % of 5,009 |
|---|---|---|
| Candidates discovered and enriched | 5,009 | 100% |
| E1 — no fastapi runtime dep | 887 | 17.7% |
| E2 — not Python-dominant (byte ratio < 0.5) | 1,801 | 36.0% |
| E3 — fork or archived | 509 | 10.2% |
| E4 — stale (>60 mo) or <10 commits | 781 | 15.6% |
| E5 — <4 files importing fastapi or 0 apps | 587 | 11.7% |
| **Accepted (pass all)** | **402** | **8.0%** |

All 5,009 candidates have a terminal first-failing-rule decision; zero
`clone_failed`. 42 repos (0.8%) returned 404 at check time (deleted/private
between snapshot and clone) and are reclassified `unavailable` — permanent
attrition, logged and timestamped.

**Eligibility rules (E1–E6):**

| Rule | Criterion | Rationale |
|---|---|---|
| E1 | `fastapi` in *runtime* deps (pyproject, poetry, Pipfile, setup.cfg/py, requirements) | dev-only deps are not real usage |
| E2 | Python byte ratio ≥ 0.5 | language dominance |
| E3 | not fork, not archived | original, active codebase |
| E4 | pushed within 60 months and ≥ 10 commits | active, not abandoned |
| E5 | ≥ 4 files importing fastapi and ≥ 1 `FastAPI()` | real app, not one-off script; anchored at a natural distribution gap |
| E6 | README/description tutorial markers | **flags only**, never auto-excludes |

E6 is a manual-review gate, not a filter: flagged repos are retained in the
census with `tutorial_flag: true`. Blind review of a frozen 24-flagged /
24-control subsample (48 repos) found genuine apps the majority class in both
groups (66.7% vs 87.5%); the flag does not separate the pools on structural
sophistication, so RQ1–RQ3 aggregates are insensitive to it.

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
  re-runs every headline at E5 thresholds 2–8 and E2 cutoff variants — no
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
  (`github_signals.py`, 390/402) joined; standardized OLS with HC1 robust SEs
  controlling for stars, age, size, Python share, tutorial flag; plus a
  40-endpoint/1500-request ASGI micro-benchmark per style
  (`bench_di.py`, `uv run --with fastapi --with httpx`).

### 2.5 Reproducibility

Python pinned 3.12.13, dependencies hash-pinned in `uv.lock`; snapshots for all
network sources (dependents HTML, topic seed, GitHub API responses cached);
sorted, byte-stable artifacts. Offline suites (`corpus/tests/`) verify finder
recovery and filter/retention invariants.

### 2.6 Limitations (summary)

Observational, cross-sectional; single-reviewer E6 judgments (frozen sample);
resolver coverage 26.9% of accepted repos have empty graphs (reported as a
coverage metric); RQ4 (git-history evolution) deferred; low-n Tier B idioms are
evidence-with-n only; the exploratory comparison is descriptive (no sampling
inference). The benchmark runs on minimal synthetic apps — an upper bound on a
body doing nothing, not a production ratio.

---

## 3. Results — DI pattern taxonomy and distribution (N=402)

Styles are assigned per repo from production-scope call sites; categories at
repo level are **not disjoint** (a repo can use several).

| Pattern | Repos | % of 402 | Definition / notes |
|---|---|---|---|
| **No DI at all (direct/zero-DI)** | **98** | **24.4%** | zero `Depends`/`Security`/`Annotated` call sites; handlers construct and call directly; still pass E5 (real apps) |
| **FastAPI-native DI** | **304** | **75.6%** | ≥ 1 framework DI construct |
| — `Depends(fn)` bare-function dominant | 294 | 73.1% | 96.7% of DI-using repos; 97.1% of all 25,166 call sites |
| — `Annotated[Depends(...)]` | 104 | 25.9% | typed-injection users |
| — `Security()` (OAuth2) | 42 | 10.4% | 163 call sites; **0 use `scopes=[...]`** |
| — `Depends(Cls)` class-as-dependency | 7 | 1.7% | constructor-injected classes |
| — module-alias deps (`mod.dep`) | 11 | 2.7% | namespaced dependency getters |
| **Hand-rolled "ground-up" Python DI** | 15–16 | ~3.7–4.0% | DIY idioms outside the resolver: `current_*` request-scope (15), `provide_*` service-locator (1); overlaps rows above |
| **External DI library** | ~3–6 | ~0.7–1.5% | **indicative (post-hoc probe, not a census facet):** confirmed `dependency-injector` in darkspock/CareerPython (+`inject`), gostgmaer/langchain-knoledgebase-rag, darkspock/renfeserver; ~3 more unverified |

**Graph topology context:** 294/402 (73.1%) have a non-empty dependency graph;
248 (84.4% of graph-bearing) contain at least one hub with ≥ 3 consumers —
fan-out is the norm; median graph depth 2 (max 7).

**Caveat.** Hand-rolled and external-library DI are not first-class extractor
facets; the two numbers above come from read-only probes over the corpus and
should be treated as order-of-magnitude signals. The measured backbone is
FastAPI-native (75.6%) vs. no-DI (24.4%).

---

## 4. Results — emerging patterns *within* FastAPI DI (RQ2)

Patterns observed in how practitioners use the framework's own resolver.

### 4.1 Tier A — corpus-scale patterns (25,166 `Depends()` sites / 303 repos)

1. **Bare-function dominance.** 24,444 sites (97.1%) pass a plain callable
   (`Depends(get_db)`), across 297/303 repos. Neither naive calls
   (`Depends(foo())`) nor lambdas appear anywhere in the census. The community
   idiom is *reference-only*, framework-injected.

   | Shape | Calls | % calls | Repos |
   |---|---|---|---|
   | bare function | 24,444 | 97.1% | 297 |
   | placeholder (`...`, `<empty>`) | 429 | 1.7% | 27 |
   | module alias (`deps.get_session`) | 266 | 1.1% | 11 |
   | title-case class | 21 | 0.1% | 7 |
   | classmethod (`.as_form`) | 6 | 0.0% | 1 |

2. **Hub-and-spoke (fan-in) topology — the relationship-level signature.** A
   small set of shared *role* dependencies each consumed by many handlers: 227
   hub nodes with ≥ 10 dependents across 23,223 directed edges
   (16,494 function + 728 class nodes). Top hubs:
   `get_db` 4,683 · `get_session` 1,732 · `get_current_user` 1,471 ·
   `require_admin` 1,175 · `require_user` 635 · `get_db_session` 537 ·
   `get_current_active_user` 463 · `require_role` 454.

3. **Chained/nested dependencies (C9) are real but short.** Dependencies that
   depend on other dependencies (`get_current_user → get_session`): median
   chain depth 2, max 7. C9 is a graph-topological property, not a syntactic
   counter.

4. **`Security()` scopes are unadopted.** 163 sites / 42 repos; **0.0%** pass
   `scopes=[...]`. `Security(scheme)` is used purely as an authentication flag;
   the advertised fine-grained OAuth2 scopes mechanism is effectively unused.
   The strongest non-obvious finding of RQ2.

5. **`Annotated[...]` encodes dependency semantics by role.** Top injected
   types are request-context/session/principal objects: `User` (749), 
   `AsyncSession` (616), `str` (458), `Session` (355), `Principal` (235),
   `UserPrincipal` (180), `Settings` (142). Practitioners name what a
   dependency *is*, not how it is wired.

6. **Class nodes are a minority.** 728 / 17,222 graph nodes (4.2%); 126 repos
   contain any. Class-based dependency is an edge case even among graph
   carriers.

### 4.2 Tier B — idioms practitioners invented beyond the documented API

Explicitly low-n; reported as evidence-with-n, not statistically:

| Emerged idiom | Repos | Evidence |
|---|---|---|
| classmethod-as-dependency (`.as_form`) | 1 | Pydantic model doubling as a form parser |
| class-as-dependency (`Depends(MyClass)`) | 14 classes / 7 | constructor-injected `HTTPBearer`, `JWTHandler`, stores |
| `current_*` request-scope injection | 15 | `current_tenant_authorization`, `current_audit_sink` — DIY request-scoped context |
| module-alias dependencies | 11 | `deps.get_session` namespaced getters |
| `provide_*` service-locator dialect | 1 | DIY container namespace |
| `*Repository`-typed injection | 0 | repository pattern **not observed** |

Several Tier B idioms (`current_*`, class-as-dep, `.as_form`) occupy the
*hand-rolled-within-FastAPI* lane of the §3 taxonomy — framework extension
points, not external libraries.

---

## 5. Headline results (one paragraph)

FastAPI DI in the wild is narrow and homogeneous: three-quarters of real
projects use the framework's resolver, almost always by passing plain
functions to `Depends` as shared, fan-in hubs (DB sessions, auth guards,
current-user providers); one-quarter of legit apps (24.4%) use **no** DI
construct at all; class-based, namespaced, and typed-injection styles exist but
at single-digit prevalence; `Security`'s scopes feature is unused; and external
DI libraries are near-absent (~1%). The exploratory comparison finds no style
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