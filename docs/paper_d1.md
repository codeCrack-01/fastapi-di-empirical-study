# Empirical Study of DI Usage Patterns in FastAPI Applications

> Draft 2 — for review. Census results are final for the 402-repository corpus
> (schema 0.1). Corpus expansion to the newer, broader eligibility gate is in
> progress and reported as future work (Section 9), not as results.

## Abstract

Dependency injection (DI) is the mechanism that lets a framework supply an
application's components — database sessions, current users, configuration,
security — rather than having the application build them itself. For the
Python web framework that has made DI a first-class, everyday feature, no
quantitative picture of how it is actually used has been published. This paper
presents the first empirical study of DI usage in real FastAPI applications.
Section 2.1 defines the terms used below.

We started from the 5,009 open-source repositories that GitHub's dependency
graph identifies as depending on FastAPI, applied six eligibility rules, and
obtained a study corpus of 402 applications (the corpus is the set of
repositories that pass all six rules). We analysed **every** repository in that
corpus — a census, not a sample — measuring three things: how often each of
the DI constructs FastAPI offers is used (RQ1), the shapes those uses take
(bare functions, classes, annotated types, module references) and the
dependency relationships they form (RQ2), and how complex the resulting
dependency graphs are (RQ3).

Main findings.

1. **DI is common but not universal.** The core `Depends` construct appears in
   75.4% of applications, and 24.4% (98 repositories) use nothing from the
   framework's DI construct set. These categories are not exhaustive; one
   remaining repository uses `Security` but no other construct.
2. **Practice does not follow the documentation's stated preference.** The
   `Annotated` form, which the official documentation recommends, is used in
   26% of applications, while the generator-based form is used in 40%. The
   `Security` construct appears in one in ten applications and is never used
   with its `scopes` argument.
3. **Real dependency graphs are broad and shallow.** A small set of shared
   dependencies (database sessions, current-user providers) is consumed by
   hundreds of handlers each — the largest hub serves 4,683 dependents — while
   chains of dependencies are short (median depth 2).

These are the first quantitative answers to questions the FastAPI ecosystem has
asked but not measured. All artefacts — the 5,009-candidate pool, the
per-repository analyses, and the result tables — are snapshotted and publicly
reproducible.

---

## 1. Introduction and Motivation

FastAPI, a Python web framework built on the Starlette and Pydantic libraries,
has become the leading Python web framework. The Stack Overflow Developer
Survey 2025 reports it ahead of Django and Flask, and JetBrains' 2025 State of
Python report lists it first among Python frameworks at 38% usage. FastAPI
combines asynchronous I/O, automatic request validation, and self-generated API
documentation.

One of the framework's defining features is **dependency injection** (DI).
DI lets a developer write, for example, an endpoint that receives a database
session as an argument spelling out how it should be provided:

```python
@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

Instead of each endpoint constructing its own session, the framework supplies
it. FastAPI offers several ways to do this. This study counts four core DI
constructs — the `Depends` call, `Security`, `Annotated` dependency types,
and generator/yield dependencies — each defined in Section 2.1 and selected
because FastAPI's official documentation describes it as a DI mechanism.
Router- and app-level wiring, dependency overrides, and callable-class
dependencies are compositions of these core constructs rather than standalone
constructs (Section 2.1). Official documentation and community guidance
recommend these patterns. Whether practice follows that guidance has not been
measured with data; in this paper we measure it.

In this paper we provide the first empirical answer. We built a reproducible
corpus of real, open-source FastAPI applications; we analysed every one of
them; and we report how the constructs are used, the shapes the usage takes,
and the structure of the dependency relationships that result.

**Contributions.**

- **A reproducible corpus source.** We show that GitHub's dependency graph —
  repositories whose manifests actually declare a dependency on FastAPI —
  recovers a population that the obvious alternative (searching the
  `fastapi` topic tag) entirely misses: zero of our 402 accepted applications
  overlap with a top-1,000 topic search.
- **A public census, not a sample.** Every accepted repository is analysed;
  the per-repository analyses and result tables are archived and reproducible.
- **The first quantitative DI-usage results for a Python web framework.** Our
  findings — including the 24% "no-DI" population and the unused `scopes`
  argument — are concrete and independent of any self-report.

**Why this matters.** Framework documentation, tutorials, linting tools, and
AI coding assistants shape how teams build software; without measurement these
are based on unverified assumptions. This study is a first step toward
grounding FastAPI ecosystem advice in what real applications actually do.

---

## 2. Background, Terminology, and Study Design

### 2.1 Terminology

| Term | Definition |
|------|------------|
| Repository | An open-source project hosted on GitHub. Each item in the study is one repository. |
| Candidate repository | A repository that GitHub's dependency graph lists as declaring a dependency on FastAPI. The discovery pool contains 5,009 candidates. |
| Study corpus | The set of repositories that pass every eligibility rule and are analysed in full. Throughout this paper, "corpus" refers to this set of 402 repositories. |
| Eligibility rule | A pass/fail check applied to separate genuine FastAPI applications from other repositories. Six rules are used (Section 4). |
| Construct | One of the mechanisms FastAPI provides for injecting a dependency into a handler. We measure four core constructs (Table 1 in Section 5.1). |
| Call site | A single occurrence of `Depends(...)` or `Security(...)` in source code. |
| Bare default-value style | A dependency declared in a parameter's default value, e.g. `db: Session = Depends(get_db)`. This is the earliest documented form. |
| Annotated style | A dependency declared inside a parameter's type annotation, e.g. `db: Annotated[Session, Depends(get_db)]`. FastAPI added this form in v0.95.0 and its documentation states a preference for it. |
| Generator/yield style | A dependency implemented as a generator function (it contains `yield`); FastAPI runs the code before the `yield` before the handler and the code after it afterwards. |
| Router-level dependency | A dependency applied to every endpoint of an `APIRouter` through its `dependencies=[...]` argument. A *compositional placement* of the `Depends` construct, not a construct in its own right. |
| App-level dependency | A dependency applied to the whole application through `FastAPI(dependencies=[...])`. A *compositional placement* of the `Depends` construct, not a construct in its own right. |
| Dependency override | A runtime replacement of a dependency, normally via `app.dependency_overrides[...]`, typically for tests. Re-wires core constructs rather than introducing a new one. |
| Callable-class dependency | A class passed *by instance* to `Depends(SomeClass())`. A spelling of the `Depends` call. |
| `Security` | A DI construct dedicated to authentication and authorization. It takes an `scopes=[...]` argument for OAuth2 scopes. |
| Dependency graph | A directed graph whose nodes are functions and classes and whose edges record "used as a dependency by." |
| Hub | A dependency consumed by many other functions; we call a node a hub when it has ≥ 10 dependents. |

### 2.2 FastAPI's DI constructs in brief

FastAPI resolves a dependency when a path operation declares one. The
introductory example in Section 1 uses the bare default-value form: a function
receives `db`, and the framework calls `get_db()` and passes the result before
invoking the handler.

The framework offers variants of this mechanism, of which we count four core
constructs:

- **`Depends`** — Passes any callable's return value, e.g. `Depends(get_db)`.
- **`Security`** — The same mechanism, restricted to authentication and
  authorization schemes; it optionally takes `scopes=[...]` for OAuth2-based
  access control.
- **`Annotated[Type, Depends(...)]`** — Declares the dependency inside the
  parameter's type annotation rather than its default value. FastAPI added this
  form in version 0.95.0, and its documentation states: "Prefer to use the
  `Annotated` version if possible."
- **Generator/yield style** — A dependency implemented as a generator: setup
  code runs before the handler and teardown code after it, which suits resource
  lifecycles such as database sessions.

The following are **compositions** of the core constructs, not constructs of
their own; we therefore document them but do not count them as separate
prevalence categories:

- **Router- and app-level dependencies** — Lists of `Depends`/`Security` entries
  applied to every endpoint of a router or of the whole application.
- **Dependency overrides** — A runtime re-wiring of an existing dependency,
  typically used to swap a service for a mock in tests.
- **Callable-class dependency** — A class instance passed to `Depends(...)`; this
  is simply the `Depends` construct with a class argument shape.

Section 4.3 describes exactly how each construct is detected in source code.

### 2.3 Research questions

We answer three research questions. RQ1 measures which constructs exist in a
repository; RQ2 measures the syntactic shape of each `Depends` / `Security`
call site and the dependency relationships those calls establish; RQ3 measures
the resulting graph.

- **RQ1 — Construct usage.** Which of the eight DI constructs does a FastAPI
  project use, and how often does each appear?
- **RQ2 — Call-site shape and relationships.** In what syntactic form are DI
  call sites written (bare function reference, annotated type, class, module
  alias), and which dependencies do projects share — which functions serve as
  dependencies for many other functions?
- **RQ3 — Graph complexity.** How complex are the dependency graphs that result
  (nodes, edges, depth, unresolved references)?

### 2.4 Study pipeline and corpus credibility

The study pipeline is **discover → filter → analyse → aggregate**: we collect
candidate repositories, filter them down to genuine FastAPI applications, parse
each application's source code into a syntax tree, count DI constructs and
rebuild who-depends-on-whom, and combine the per-repository measurements into
corpus-wide statistics.

Two facts about the corpus's provenance affect the interpretation of the term
"real application" used throughout the paper.

**The candidates come from GitHub's dependency graph.** A candidate must
declare FastAPI in a package manifest; GitHub's dependency-graph data, not a
text search, provides the pool. The six filters are described in Section 4;
the full funnel, with every rejection reason logged, is shown there.

**The alternative source is disjoint.** A `fastapi` topic search (top 1,000 by
stars) shares only **2 of our 5,009** candidates with our pool and **zero** of
our 402 accepted applications. The topic signal finds templates and tutorials;
the dependency graph finds applications that declare FastAPI as a dependency.
Our corpus is drawn from the latter.

---

## 3. Related Work

**The direct antecedent: DI in Java.** The closest published work to ours is by
Yang, Tempero, and Melton (ASWEC 2008), *An Empirical Study into Use of
Dependency Injection in Java*. The authors develop **operational definitions**
for DI and analysis techniques to detect its use, then apply them to 34
open-source Java applications. To our knowledge it is the first empirical study
of DI usage, and it remains the reference point for the problem.

Our study is related but distinct:

- **Different ecosystem and programming model.** Java DI in the 2008 era was
  container-driven: dependencies were wired through XML or annotations read by
  a container such as Spring. FastAPI DI is *code-as-configuration*: injection
  is expressed directly in function signatures, resolved at runtime, per
  request, with generator-based lifecycles. The constructs we catalogue do not
  exist in the Java world, so the measurements are not comparable.
- **Different scale and sampling.** Yang et al. analyse 34 curated Java
  applications. We analyse a census of 402 applications drawn from a
  reproducible 5,009-candidate discovery over GitHub's dependency graph.
- **Deeper measurement.** Yang et al. give operational definitions for "is DI
  used, and how much." We additionally measure the *shape* of each use
  (argument type, annotated types, scopes), the *relationships* between
  dependencies (which shared resources are consumed by how many handlers), and
  the *complexity* of the resulting graphs.

**The DI maintainability line.** A separate empirical line asks whether DI
*helps*. Janzen and Razina (2007) compared 20 pairs of comparable Java projects
with and without Spring, finding no clear coupling/cohesion difference but a
trend toward lower coupling in projects with more than ~10% DI usage. Roubtsov,
Serebrenik, and van den Brand (2010) detect "modularity smells" in
annotation-injected dependencies. A 2019 study proposes a catalog of Java DI
anti-patterns and measures their occurrence in four projects. More recent work
proposes DI-weighted coupling metrics and applies them to open-source Java
projects (2022) and re-examines DI's influence on maintainability (2023).
All of this work targets Java and evaluates quality *outcomes*; none measures
DI *usage* in a Python web framework.

**Us.** To the best of our knowledge this is the first empirical characterization
of DI usage for FastAPI (and the first for any Python web framework), conducted
as a full-census study with a reproducible corpus.

---

## 4. Methodology

### 4.1 Discovering candidates

We wanted repositories that *actually* use FastAPI rather than ones that merely
mention it. The original plan was the Libraries.io `/dependents` endpoint —
repositories listed as dependent packages of FastAPI — but that endpoint is
disabled server-side and proved unusable (empty responses, hard rate limits).
We substituted GitHub's dependency graph, which uses the equivalent
manifest-parsing mechanism and is the live, current source: it parses each
repository's dependency manifests (`pyproject.toml`, `requirements*.txt`,
`Pipfile`, `setup.cfg`/`setup.py`) and records what each repository declares it
depends on.

We crawled the dependency graph of `fastapi/fastapi`, enriching every candidate
with GitHub API metadata (language byte ratios, fork/archived flags, push age,
commit count, stars, license, topics), until we reached **5,009 candidates**.
The crawl is reproducible from a snapshot of the fetched pages.

### 4.2 Filtering to genuine applications

Five eligibility rules are applied in sequence; whatever a repository fails on,
the first failing rule is logged. A sixth rule (E6) *flags* tutorial-looking
repositories but never excludes them automatically.

| Rule | Requirement | Why it exists |
|------|-------------|---------------|
| **E1** | `fastapi` is declared as a *runtime* dependency (not dev/test-only) | A dev-only dependency does not mean FastAPI runs in production |
| **E2** | Python is the dominant language (byte ratio ≥ 0.5) | Remove mixed-language repositories where FastAPI is incidental |
| **E3** | Not a fork, not archived | Forks duplicate signal; archived projects are abandoned |
| **E4** | Active: pushed within the last 60 months **and** ≥ 10 commits | Remove dead or one-off repositories |
| **E5** | Real usage: ≥ 4 files that import `fastapi` **and** ≥ 1 `FastAPI()` call | Remove repositories that import FastAPI once and never build with it |
| **E6** | *Flag only:* tutorial/demo markers in description or README | Flags are reviewed by a human; they never auto-exclude |

The funnel:

| Decision | Count | Share of 5,009 |
|----------|-------|----------------|
| E1 — no runtime `fastapi` dependency | 887 | 17.7% |
| E2 — Python not dominant | 1,801 | 36.0% |
| E3 — fork or archived | 509 | 10.2% |
| E4 — stale or too few commits | 781 | 15.6% |
| E5 — insufficient real FastAPI usage | 587 | 11.7% |
| Unavailable (deleted/private between discovery and cloning) | 42 | 0.8% |
| **Accepted** | **402** | **8.0%** |

Every candidate ends in exactly one decision; nothing is dropped silently.

**Why the thresholds are defensible.** The E5 threshold (≥ 4 files, ≥ 1 app)
is anchored at a natural gap in the observed distribution of
files-importing-fastapi — the boundary between one-off scripts and real
applications. We re-ran all headline statistics at thresholds 4 through 8; the
qualitative conclusions are stable (Section 8.1).

**The recall question.** How do we know this source doesn't miss the population?
We cannot measure what the dependency graph does not track, but we can measure
what an alternative source would have recovered. A `topic:fastapi` search
(top 1,000 by stars) — the most plausible alternative — shares **2 of 5,009**
candidates with our pool and **0 of 402** accepted applications. The two
sources are cleanly disjoint: the topic signal surfaces templates and
tutorials; the dependency graph surfaces real users. This is the strongest
single argument for the corpus design.

### 4.3 Analysing the corpus

Each accepted repository is shallow-cloned, then parsed with Python's standard
AST tooling — the source is reduced to a syntax tree *without executing any
code*. The four constructs counted (Table 1) are the DI mechanisms FastAPI's
official documentation describes; the detection rules for each are listed in
Table 2 of the extractor specification archived with the corpus. One pass over
this tree counts how often each construct appears per repository and records
each call site with its argument and surrounding function. A second pass
reconstructs the dependency graph: which function depends on which other
function, via DI, so we can later measure depth and fan-out without re-parsing.

The per-repository counts and graphs are combined into corpus-wide tables.
Because the extraction is a pure function of the repository source, it is
byte-stable across machines and Python versions — meaning another researcher
can reproduce our numbers exactly.

**Census, not sample.** All 402 accepted repositories enter every downstream
table. The study reports population values for its population definition, which
avoids sampling-inference questions entirely (what it also means is discussed
in the threats, Section 8).

---

## 5. Results

### 5.1 RQ1 — Which constructs are used, and how often

Across the 402-repository census:

| Construct | Repos | % of corpus | Total calls | Median calls (users) |
|-----------|-------|-------------|-------------|----------------------|
| C1 `Depends` | 303 | 75.4% | 25,166 | 22 |
| C2 `Security` | 42 | 10.4% | 163 | 1 |
| C3 `Annotated[..., Depends]` | 104 | 25.9% | 5,913 | 11 |
| C4 Generator/yield dependency | 162 | 40.3% | 216 | 1 |

> **Figure 2 — Construct prevalence.** Horizontal bar chart of the table above
> (`paper/figures/fig_constructs.pdf`). Bars show repo count (and % of 402)
> per construct; a repository may use several constructs.

**Findings.**

- **`Depends` usage.** Three-quarters (303/402, 75.4%) use the core construct.
  98 repositories (24.4%) use none of the constructs in the table above,
  despite passing every eligibility rule (≥ 4 importing files, ≥ 1 app). The
  two sets are not complementary: the remaining repository
  (`doshirush1901/brain-os`) uses `Security` but no other construct. Within the
  24.4%, none uses a generator/yield dependency either, so the classification
  as "no DI at all" is conservative with respect to the full construct set.
- **The documentation-preferred style is not the most common one.** The
  `Annotated[..., Depends]` form that the documentation states a preference for
  appears in 26% of repositories; generator/yield dependencies appear in 40%
  (Section 2.2).
- **`Security` usage.** The DI-level `Security` construct appears in one in ten
  applications (10.4%) and, where present, usually exactly once.
- **Derived placements are compositions, not constructs.** Router-level wiring,
  app-level wiring, dependency overrides and callable-class dependencies are
  just the `Depends` mechanism applied at a wider scope or re-wired at runtime;
  not a single repository uses them without one of the four core constructs, so
  they are not counted as separate constructs (Section 2.1).

**Usage and popularity or age.** Core-DI usage (any of
`Depends`/`Security`/`Annotated`) is 76.0% for 0-star, 73.3% for 1–9, 85.7% for
10–99, and 85.7% for 100+ repositories, and rises with repository age: 74.8%
under 12 months to 90.9% at 36+ months. The corpus skews young (361 of 402
repos under a year old); the E4 eligibility rule admits repositories up to 60
months old, so the skew reflects the discovered population rather than an
artifact of the gate.

### 5.2 RQ2 — Call-site shape and dependence relationships

**Argument shapes.** Of 25,166 `Depends()` call sites in 303 repositories:

| Argument shape | Calls | % of calls | Repos |
|----------------|-------|-----------|-------|
| Bare function reference (`Depends(get_db)`) | 24,444 | 97.1% | 297 |
| Placeholder (`Depends(...)`, empty) | 429 | 1.7% | 27 |
| Module alias (`Depends(deps.get_session)`) | 266 | 1.1% | 11 |
| Title-case class (`Depends(HTTPBearer)`) | 21 | 0.1% | 7 |
| Classmethod (`Depends(LoginRequest.as_form)`) | 6 | < 0.1% | 1 |

The most common argument shape is a bare function reference (97.1% of call
sites). No `Depends(foo())` calls and no lambdas were found anywhere in the
census.

**Security is never used with scopes.** All 163 `Security()` call sites in all
42 repositories pass a plain scheme; none pass `scopes=[...]`. The `scopes`
argument, offered for granular OAuth2 authorization, does not occur in the
census.

**Annotated types.** The most common types named in `Annotated[Type,
Depends(...)]` declarations are `User` (749), `AsyncSession` (616), `str`
(458), and `Session` (355). The remaining frequent types are session and
current-user token names (`Principal`, `UserPrincipal`, `CurrentAdminUser`,
`AuthIdentity`) and configuration types (`Settings`, `Any`).

**Relationship structure.** Among the 294 repositories with a dependency
graph, 227 functions each serve 10 or more dependents. The largest hubs are
`get_db` (4,683 dependents), `get_session` (1,732), `get_current_user`
(1,471), and `require_admin` (1,175): a small set of shared resources —
database sessions, current-user providers, admin guards — is injected into a
large number of handlers. Smaller idiomatic patterns appear at low frequency
(classmethod dependencies in 1 repo, `current_*` request-scope injection in 15
repos, module-alias dependency getters in 11).

> **Figure 3 — Dependency hubs by fan-in.** Top five hub functions plus three
> additional common hubs (`paper/figures/fig_hubs.pdf`). Values as in the
> paragraph above.

### 5.3 RQ3 — Dependency-graph complexity

Clean dependency graphs (excluding resolver placeholders; see Section 6) for
294 of 402 repositories:

| Metric | Median | IQR | Max |
|--------|--------|-----|-----|
| Nodes (clean) | 19.5 | 8–54 | 1,444 |
| Maximum dependency depth | 2 | 2–3 | 7 |
| Unresolved references | 0% | 0–3.6% | 100% |

- The graphs contain 16,494 function nodes, 728 class nodes, and 23,223
  directed edges; class nodes occur in 126 repositories.
- **61.2% of graph-bearing repositories have zero unresolved references** — the
  resolver handles them cleanly. One outlier repository is fully unresolved.
- **Graphs are broad and shallow.** The typical chain of dependencies is two
  levels deep (maximum observed: 7).

*Summary:* the graphs are flat, fan-out structures in which a few shared
dependencies are consumed by many handlers, rather than deep chains.

---

## 6. Data Quality and Reproducibility

We report the data-quality issues we found in the course of the study,
including one bug, rather than hiding them.

**A found and fixed bug in graph construction.** The dependency-graph rebuild
produced placeholder nodes shaped like `file:line` when a `Depends` call
occurred outside any function context (module-scope declarations such as
`FastAPI(dependencies=[...])`). This affected **122 of 294** graph-bearing
repositories — **713 placeholder nodes**, 4.1% of all graph nodes — and inflated
node counts (median 22 raw → 19.5 clean). We filter these non-callable ids
before computing complexity metrics, retain both raw and clean columns in the
output tables, and report the numbers verbatim. **Construct counts (RQ1) are
unaffected**: they come from call sites, not graph nodes.

**Determinism.** Repository files are iterated in explicitly sorted order, and
the extractor is byte-stable across interpreters (verified on Python 3.12 and
3.14). Every artefact — the raw candidate pool, the snapshot of fetched
dependency-graph pages, the per-repository extraction reports, and the result
tables — is archived with a schema version.

**The tutorial-flag question.** The E6 flag is *not* an exclusion
rule. 188 of 402 accepted repositories (47%) carry tutorial/demo markers in
their description or README. We reviewed a blinded, stratified subsample of
flag-flagged and unflagged repositories, grouped in advance. In the 24
flagged, 66.7% were judged genuine applications (vs. 87.5% of the 24
unflagged controls; 8.3% vs. 4.2% judged demos/tutorials). The flagged
population largely mirrors the unflagged baseline for the RQ1/RQ3 headline
aggregates: excluding the flagged repositories does not change them. The
judgement labels are from a single reviewer and reported as indicative, not as
a claim.

---

## 7. Discussion

**Framework design and tooling.** The measured dependency-graph shape is
broad, shallow, and built around a few shared hubs; hubs such as `get_db` are
consumed by thousands of dependents. Two features the documentation emphasizes
do not appear at scale: the `Security` `scopes` argument does not occur in the
census, and the generator/yield style is used in more applications than the
documentation-preferred `Annotated` style.

**Teaching.** The claim "FastAPI apps use DI" does not describe a quarter of
the corpus: 98 of 402 applications use none of the DI constructs.

**Methodological transfer.** The corpus source has a property most benchmark
corpora lack: an independent signal (topic search) recovers none of the
accepted population, which makes the "real application" classification a
property of the data source rather than of post-hoc filtering. The replicable,
census-scale pipeline transfers to other frameworks (Litestar, NestJS, Spring
Boot).

**Boundary of the measurement.** The study measures *detectable source-level*
usage: constructs the parser can see. It does not measure runtime behaviour,
performance, or code quality. The results characterise what developers write,
not what a program does when run.

---

## 8. Threats to Validity

Each threat is stated as *what we can't claim*, followed by *what we do about
it*.

- **Construct validity — what counts as "real."** Our eligibility criteria are
  source-level and reproducible, but they cannot perfectly capture whether
  FastAPI is "important" inside every application. *We keep the criteria
  explicit and sensitivity-test the usage threshold (Section 8.1).*
- **Construct validity — syntax is not semantics.** The parser detects syntactic
  constructs; similar syntax can have different runtime meaning. *We frame all
  results as characterization of detectable source-level usage, and we expose
  the placeholder-node issue that the one semantic-looking step (the graph)
  had (Section 6).*
- **Internal validity.** This is an observational, cross-sectional study; we
  make no causal claims about DI and quality or performance.
- **External validity — population.** The corpus is open-source GitHub
  repositories only; it omits private, proprietary, and internally hosted
  applications. *Stated plainly: the population we describe is the open-source
  FastAPI population.*
- **External validity — ecosystem.** Findings describe FastAPI in 2025–26.
  They should not be generalized to other languages or frameworks without
  analogous measurement.
- **Conclusion validity — small cells.** Several constructs and idioms occur in
  2–15 repositories. We report them as evidence-with-n and do not over-read
  them; the paper's quantitative backbone rests on the well-populated cells.
- **Population attrition.** 42 repositories (0.8%) disappeared between
  discovery and cloning (deleted or made private) — normal churn for a
  cross-sectional GitHub study, documented with timestamped checks.
- **Tutorial/boundary sample size.** The blinded label review used 48
  repositories (24 flagged / 24 control), drawn from an earlier corpus era and
  single-reviewer. Rates are indicative.

### 8.1 Threshold sensitivity

Re-running the headline E5 threshold (files-importing-fastapi ≥ 4) at 5, 6, and
8:

| Threshold | Eligible repos | % using core DI | Median calls (all) | Median calls (users) |
|-----------|----------------|-----------------|--------------------|----------------------|
| 4 (base) | 402 | 75.6% | 15 | 28.5 |
| 5 | 355 | 78.3% | 19 | 36 |
| 6 | 324 | 79.0% | 22 | 41.5 |
| 8 | 253 | 80.6% | 35 | 52.5 |

As the threshold rises, measured DI usage and per-repo call counts increase
modestly (75.6% at 4 → 80.6% at 8). The ranking of constructs and the absence
findings reported in Section 5 are unchanged.

---

## 9. Future Work

- **Corpus validation at a broader gate.** We are finalizing a newer eligibility
  pass on the same 5,009-candidate pool that measures real on-disk FastAPI
  imports directly (rather than manifest declarations) and yields a
  substantially larger corpus. Re-running this census at that scale will test
  whether the findings hold beyond 402 applications.
- **LLM-assisted validation of pattern detection.** The census statistics rest
  on source-level, syntactic detection. To verify the measured patterns against
  human judgement, we are designing a validation study that replaces the earlier
  judge-consensus design with a single-model evaluation grounded in sampling
  theory, per reviewer guidance. The corpus is first stratified into four
  quadrants by GitHub star count; within each quadrant we compute the sample
  size required to support a Wilson 95% confidence interval at a 5% error
  margin. A single state-of-the-art OpenAI model — selected on the basis of
  methodological literature on LLM-based software analysis — labels the sampled
  repositories for DI usage. The model's classifications are then cross-checked
  through a split peer-review between the study's collaborators, quantifying how
  well the LLM identifies DI patterns compared with human judgement. The top-10
  classified patterns are reported alongside the patterns documented in the
  official FastAPI documentation, so documented guidance can be weighed against
  observed usage.
- **Performance regression analysis.** DI resolution occurs at request time and
  adds runtime overhead relative to direct construction. We plan to measure that
  overhead empirically: micro-benchmarks of each of the dominant DI styles
  (`Depends`, generator/yield lifecycles, deeply nested chains) and
  regression-style benchmarks on representative applications, to quantify
  whether and where the patterns in the top-10 classification carry a measurable
  performance cost.
- **Qualitative depth.** A manual reading of the no-DI population and of the
  low-frequency idioms, to characterize *what these applications do instead of*
  DI — the substitute patterns behind the 24% finding.
- **Cross-framework transfer.** Applying the same census apparatus to another
  DI-capable framework (e.g. Litestar, NestJS) to test whether the
  broad-and-shallow shape is a property of DI or of this framework.

---

## 10. Conclusion

Findings describe FastAPI in 2025–26, on a census of 402 real, open-source
applications. We built a reproducible corpus of 402 FastAPI applications,
analysed every one of them, and measured how DI is actually used: DI is common
but not universal (24% of applications use none of the DI constructs; the
accounting is detailed in Section 5.1); the generator/yield style appears in
more applications than the documentation-preferred `Annotated` form; the
`Security` `scopes` argument does not occur in the census; and DI graphs are
broad, shallow fan-out structures built around a few shared resources. These
are the first quantitative facts about FastAPI DI usage.

---

## References

1. Yang, H. Y., Tempero, E., Melton, H. *An Empirical Study into Use of
   Dependency Injection in Java.* 19th Australian Software Engineering
   Conference (ASWEC 2008), pp. 239–247. IEEE.
2. Janzen, D. S., Razina, E. *Effects of Dependency Injection on
   Maintainability.* (2007).
3. Roubtsov, S., Serebrenik, A., van den Brand, M. *Detecting Modularity
   "Smells" in Dependencies Injected with Java Annotations.* CSMR 2010.
4. *Towards a Catalog of Java Dependency Injection Anti-Patterns.* ACM 2019
   (doi:10.1145/3350768.3350771).
5. *Measuring Impact of Dependency Injection on Software Maintainability.*
   Computers 11(9):141, MDPI, 2022.
6. Sun, C.-W., Liao, C.-F. *Examining the Influence of Dependency Injection on
   Software Maintainability.* BCD 2023.
7. Stack Overflow. *Developer Survey 2025.*
8. JetBrains. *The State of Python 2025.*