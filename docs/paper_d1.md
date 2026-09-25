# Empirical Study of DI Usage Patterns in FastAPI Applications

> Draft 3 — for review. Census results are final for the 2,179-repository corpus
> (revised E1–E4 gate, schema 0.2). The earlier 402-repository results (pure
> Python-gate era) are superseded; see `docs/result_draft_01.md` for the full
> replica documentation.

## Abstract

Dependency injection (DI) is the mechanism that lets a framework supply an
application's components — database sessions, current users, configuration,
security — rather than having the application build them itself. For the
Python web framework that has made DI a first-class, everyday feature, no
quantitative picture of how it is actually used has been published. This paper
presents the first empirical study of DI usage in real FastAPI applications.
Section 2.1 defines the terms used below.

We started from the 5,000 open-source repositories that GitHub's dependency
graph identifies as depending on FastAPI, applied four eligibility rules, and
obtained a study corpus of 2,179 applications (the corpus is the set of
repositories that pass all four rules). We analysed **every** repository in that
corpus — a census, not a sample — measuring three things: how often each of
the DI constructs FastAPI offers is used (RQ1), the shapes those uses take
(bare functions, classes, annotated types, module references) and the
dependency relationships they form (RQ2), and how complex the resulting
dependency graphs are (RQ3).

Main findings.

1. **DI is common but not universal.** The core `Depends` construct appears in
   62.9% of applications, and 36.9% (805 repositories) use nothing from the
   framework's DI construct set. These categories are not exhaustive; 3
   repositories use `Annotated` but no other construct.
2. **Practice does not follow the documentation's stated preference.** The
   `Annotated` form, which the official documentation recommends, is used in
   18% of applications, while the generator-based form is used in 35%. The
   `Security` construct appears in one in twenty applications and is never used
   with its `scopes` argument.
3. **Real dependency graphs are broad and shallow, with a small deep tail.** A
   small set of shared dependencies (database sessions, current-user providers)
   is consumed by hundreds of handlers each — the largest hub serves 24,014
   dependents — while chains of dependencies are short in the median (median
   depth 2). A 4.3% tail of repositories (58 of 1,338 graph-bearing) reaches
   5–7 hops, always on top of the same shared-hub pattern.

These are the first quantitative answers to questions the FastAPI ecosystem has
asked but not measured. All artefacts — the 5,000-candidate pool, the
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
  `fastapi` topic tag) almost entirely misses: one of our 2,179 accepted
  applications (0.0%) overlaps with a top-1,000 topic search.
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
| Candidate repository | A repository that GitHub's dependency graph lists as declaring a dependency on FastAPI. The discovery pool contains 5,000 candidates. |
| Study corpus | The set of repositories that pass every eligibility rule and are analysed in full. Throughout this paper, "corpus" refers to this set of 2,179 repositories. |
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

- **RQ1 — Construct usage.** Which of the four measured DI constructs (C1
  `Depends`, C2 `Security`, C3 `Annotated`-typed dependency, C4
  generator/yield dependency) does a FastAPI project use, and how often (repo
  share and call volume)?
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
text search, provides the pool. The four eligibility rules (E1–E4) are
described in Section 4; the full funnel, with every rejection reason logged, is
shown there.

**The alternative source is nearly disjoint.** A `fastapi` topic search
(top 1,000 by stars) shares only **2 of our 5,000** candidates with our pool
and only **one** of our 2,179 accepted applications (0.0%, named in the
artifact table). The topic signal finds templates and tutorials; the dependency
graph finds applications that declare FastAPI as a dependency. Our corpus is
drawn from the latter.

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
  applications. We analyse a census of 2,179 applications drawn from a
  reproducible 5,000-candidate discovery over GitHub's dependency graph.
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
commit count, stars, license, topics), until we reached **5,000 candidates**.
The crawl is reproducible from a snapshot of the fetched pages.

### 4.2 Filtering to genuine applications

Five eligibility rules are applied in sequence; whatever a repository fails on,
the first failing rule is logged. A sixth rule (E6) *flags* tutorial-looking
repositories but never excludes them automatically.

| Rule | Requirement | Why it exists |
|------|-------------|---------------|
| **E1** | `fastapi` is imported in ≥ 1 *production* file (extractor) | A dev-only dependency does not mean FastAPI runs in production |
| **E2** | Not a fork, not archived (GitHub metadata) | Forks duplicate signal; archived projects are abandoned |
| **E3** | Active: pushed within the last 60 months (GitHub metadata) | Remove dead repositories |
| **E4** | Scale: ≥ 2 distinct files import `fastapi` (`E4_MIN_FASTAPI_FILES`) | Remove single-file / demo repositories where FastAPI is incidental |

The funnel:

| Decision | Count | Share of 5,000 |
|----------|-------|----------------|
| E4 — below scale (single-file/demo) | 1,281 | 25.6% |
| E2 — fork or archived | 800 | 16.0% |
| E1 — no production `fastapi` import | 516 | 10.3% |
| Clone failed (metadata unavailable) | 224 | 4.5% |
| **Accepted** | **2,179** | **43.5%** |

Every candidate ends in exactly one decision; nothing is dropped silently.

**Why the thresholds are defensible.** The E4 threshold (≥ 2 distinct
files that import fastapi) removes single-file demos and one-off scripts while
keeping genuine multi-file applications; the exact cutoff is documented in
`docs/github_stratified_scan_stats.md`. Headline statistics are stable when the
file threshold is varied from 2 to 8 — DI-adoption rises modestly and the
targeted thresholds (base = 4) bound a structurally-meaningful pool
(Section 8.1).

**The recall question.** How do we know this source doesn't miss the population?
We cannot measure what the dependency graph does not track, but we can measure
what an alternative source would have recovered. A `topic:fastapi` search
(top 1,000 by stars) — the most plausible alternative — shares **2 of 5,000**
candidates with our pool and **1 of 2,179** accepted applications (0.0%). The
two sources are cleanly disjoint: the topic signal surfaces templates and
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

**Census, not sample.** All 2,179 accepted repositories enter every downstream
table. The study reports population values for its population definition, which
avoids sampling-inference questions entirely (what it also means is discussed
in the threats, Section 8). A stratified 327-repository review sample is used
only for manual verification of the extractor, not for statistical inference.

---

## 5. Results

### 5.1 RQ1 — Which constructs are used, and how often

Across the 2,179-repository census:

| Construct | Repos | % of corpus | Total calls | Median calls (users) |
|-----------|-------|-------------|-------------|----------------------|
| C1 `Depends` | 1,371 | 62.9% | 98,243 | 22 |
| C2 `Security` | 104 | 4.8% | 620 | 1 |
| C3 `Annotated[..., Depends]` | 384 | 17.6% | 23,241 | 10 |
| C4 Generator/yield dependency | 759 | 34.8% | 1,003 | 1 |

> **Figure 2 — Construct prevalence.** Horizontal bar chart of the table above
> (`paper/figures/fig_constructs.pdf`). Bars show repo count (and % of 2,179)
> per construct; a repository may use several constructs.

**Findings.**

- **`Depends` usage.** Three-fifths (1,371/2,179, 62.9%) use the core construct.
  805 repositories (36.9%) use none of the constructs in the table above,
  despite passing every eligibility rule (≥ 4 importing files, ≥ 1 app). The
  two sets are not complementary: 3 repositories (`doshirush1901/brain-os`,
  `abushanisro/emithran`, `ATphobia22/PTDT-v33`) use `Annotated` but no
  `Depends`. Within the 36.9% none uses a generator/yield dependency either, so
  the classification as "no DI at all" is conservative with respect to the full
  construct set.
- **The documentation-preferred style is not the most common one.** The
  `Annotated[..., Depends]` form that the documentation states a preference for
  appears in 18% of repositories; generator/yield dependencies appear in 35%
  (Section 2.2).
- **`Security` usage.** The DI-level `Security` construct appears in one in
  twenty applications (4.8%) and, where present, usually exactly once.
- **Derived placements are compositions, not constructs.** Router-level wiring,
  app-level wiring, dependency overrides and callable-class dependencies are
  just the `Depends` mechanism applied at a wider scope or re-wired at runtime;
  not a single repository uses them without one of the four core constructs, so
  they are not counted as separate constructs (Section 2.1).

**Usage and popularity or age.** Core-DI usage (any of
`Depends`/`Security`/`Annotated`) is 61.0% for 0-star, 67.9% for 1–9, 69.0% for
10–99, and 58.8% for 100+ repositories, and is flat with repository age: 63.1%
under 12 months, 63.6% at 12–36 months, 61.4% at 36+ months. The corpus skews
young (1,903 of 2,179 repos under a year old); the E4 eligibility rule admits
repositories up to 60 months old, so the skew reflects the discovered
population rather than an artifact of the gate.

### 5.2 RQ2 — Call-site shape and dependence relationships

**Argument shapes.** Of 98,243 `Depends()` call sites in 1,371 repositories:

| Argument shape | Calls | % of calls | Repos |
|----------------|-------|-----------|-------|
| Bare function reference (`Depends(get_db)`) | 94,889 | 96.6% | 1,354 |
| Module alias (`Depends(deps.get_session)`) | 2,433 | 2.5% | 54 |
| Placeholder (`Depends(...)`, empty) | 720 | 0.7% | 120 |
| Title-case class (`Depends(HTTPBearer)`) | 178 | 0.2% | 28 |
| Classmethod (`Depends(LoginRequest.as_form)`) | 23 | < 0.1% | 4 |

The most common argument shape is a bare function reference (96.6% of call
sites). No `Depends(foo())` calls and no lambdas were found anywhere in the
census.

**Security is never used with scopes.** All 620 `Security()` call sites in all
104 repositories pass a plain scheme; none pass `scopes=[...]`. The `scopes`
argument, offered for granular OAuth2 authorization, does not occur in the
census.

**Annotated types.** The most common types named in `Annotated[Type,
Depends(...)]` declarations are `AsyncSession` (2,435), `User` (2,133),
`ActorContext` (1,630), and `Session` (1,107). The remaining frequent types are
session and current-user token names (`Principal`, `AuthPrincipal`,
`AuthIdentity`) and configuration types (`Settings`, `Any`).

**Relationship structure.** Among the 1,338 repositories with a dependency
graph, 708 functions each serve 10 or more dependents. The largest hubs are
`get_db` (24,014 dependents), `get_current_user` (11,432), `get_session`
(5,014), and `require_admin` (3,030): a small set of shared resources —
database sessions, current-user providers, admin guards — is injected into a
large number of handlers. Smaller idiomatic patterns appear at low frequency
(classmethod dependencies in 4 repos, `current_*` request-scope injection in 76
repos, module-alias dependency getters in 54).

> **Figure 3 — Dependency hubs by fan-in.** Top five hub functions plus three
> additional common hubs (`paper/figures/fig_hubs.pdf`). Values as in the
> paragraph above.

### 5.3 RQ3 — Dependency-graph complexity

Clean dependency graphs (excluding resolver placeholders; see Section 6) for
1,338 of 2,179 repositories:

| Metric | Median | IQR | Max |
|--------|--------|-----|-----|
| Nodes (clean) | 19.0 | 7–49 | 1,444 |
| Maximum dependency depth | 2 | 2–3 | 7 |
| Unresolved references | 0% | 0–3.3% | 100% |

- The graphs contain 62,200 function nodes, 2,682 class nodes, and 90,863
  directed edges; class nodes occur in 432 repositories (4.1% of nodes).
- **61.1% of graph-bearing repositories have zero unresolved references** — the
  resolver handles them cleanly. A small set of 21 repositories are fully
  unresolved.
- **Graphs are broad and shallow in the median.** The typical chain of
  dependencies is two levels deep. A deep tail exists but is small: 58
  repositories (4.3%) have a chain of five or more hops (43 at depth 5, 11 at
  depth 6, 4 at depth 7), and every one of them still contains a fan-out hub
  (shared dependency with ≥3 consumers). These chains read as layered service
  constructions that terminate at the same `db`/`repository` hubs as the
  shallow graphs — depth is an overlay on the fan-out pattern, not a
  replacement for it. Tail repositories skew young (54/58 < 12 months) and
  low-star (36/58 zero-star), and are larger than the typical graph (median
  116 vs 19 clean nodes). See `analysis/out/rq3_depth_tail.csv`.

*Summary:* the graphs are flat, fan-out structures in which a few shared
dependencies are consumed by many handlers. The typical chain is two levels;
deep (5–7 hop) chains occur in a 4.3% tail of younger, larger apps.

---

## 6. Data Quality and Reproducibility

We report the data-quality issues we found in the course of the study,
including one bug, rather than hiding them.

**A found and fixed bug in graph construction.** The dependency-graph rebuild
produced placeholder nodes shaped like `file:line` when a `Depends` call
occurred outside any function context (module-scope declarations such as
`FastAPI(dependencies=[...])`). This affected **425 of 2,179** repositories — **2,656 placeholder nodes**, 4.1% of all graph nodes — and inflated
node counts (median 20 raw → 19.0 clean). We filter these non-callable ids
before computing complexity metrics, retain both raw and clean columns in the
output tables, and report the numbers verbatim. **Construct counts (RQ1) are
unaffected**: they come from call sites, not graph nodes.

**Determinism.** Repository files are iterated in explicitly sorted order, and
the extractor is byte-stable across interpreters (verified on Python 3.12 and
3.14). Every artefact — the raw candidate pool, the snapshot of fetched
dependency-graph pages, the per-repository extraction reports, and the result
tables — is archived with a schema version.

**The tutorial-flag question (historical, E6 era).** The E6 flag was *not* an
exclusion rule in the original E1–E6 funnel; 188 of 402 accepted repositories
(47%) carried tutorial/demo markers in their description or README. A blinded,
stratified subsample (24 flagged + 24 unflagged) judged 66.7% of flagged
genuine applications (vs. 87.5% of controls; demos 8.3% vs. 4.2%). The flagged
population largely mirrored the unflagged baseline for RQ1/RQ3 headlines. The
revised E1–E4 funnel for the 2,179-repo census dropped E6 entirely
(`docs/github_stratified_scan_stats.md`), so this paragraph is retained only
to document the removal decision. The judgement labels are from a single
reviewer and reported as indicative, not as a claim.

---

## 7. Discussion

**Framework design and tooling.** The measured dependency-graph shape is
broad, shallow (median depth 2), and built around a few shared hubs; hubs such
as `get_db` are consumed by thousands of dependents. A small deep tail (4.3%,
depth 5–7) is layered on top of the same hubs rather than replacing them.
Two features the documentation emphasizes do not appear at scale: the `Security`
`scopes` argument does not occur in the census, and the generator/yield style
is used in more applications than the documentation-preferred `Annotated`
style.

**Teaching.** The claim "FastAPI apps use DI" does not describe over a third of
the corpus: 805 of 2,179 applications use none of the DI constructs.

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
- **Population attrition.** 224 repositories (4.5%) were un-retrievable at
  clone time — normal churn for a cross-sectional
  GitHub study, documented in `exclusion_log.json` (`clone_failed`).
- **Tutorial/boundary sample size.** The blinded label review used 48
  repositories (24 flagged / 24 control), drawn from an earlier corpus era and
  single-reviewer. Rates are indicative and retained only as historical
  rationale for dropping the tutorial-marker rule (E6) from the final E1–E4
  gate.

### 8.1 Threshold sensitivity

Re-running the headline file-import threshold (files-importing-fastapi) across
the accepted 2,179-pool:

| Threshold | Eligible repos | % using core DI | Median calls (all) | Median calls (users) |
|-----------|----------------|-----------------|--------------------|----------------------|
| 2 | 2,150 | 63.1% | 8 | 26 |
| 3 | 1,720 | 70.2% | 13 | 30.0 |
| 4 | 1,451 | 76.2% | 19 | 35.0 |
| 5 | 1,284 | 79.4% | 24 | 40.5 |
| 6 | 1,167 | 80.8% | 27 | 45 |
| 8 | 937 | 84.1% | 41 | 55.5 |

As the threshold rises, measured DI usage and per-repo call counts increase
modestly (63.1% at 2 → 84.1% at 8). The ranking of constructs and the absence
findings reported in Section 5 are unchanged. The base corpus gate
(≥ 2 files, the full 2,179 pool) is the lower bound; conclusions hold across
every tighter threshold.

---

## 9. Future Work

- **Corpus re-run at the revised gate.** The results above reflect the revised
  E1–E4 gate over the full 5,000-candidate pool (2,179 accepted). A
  dependency-graph crawl at a wider target would test whether the qualitative
  findings hold beyond this scale. Replicability is preserved via the frozen
  5,000-candidate pool and the snapshot/archive conventions.
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
  (`Depends`, generator/yield lifecycles, the 4.3% deep-chain tail) and
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

Findings describe FastAPI in 2025–26, on a census of 2,179 real, open-source
applications. We built a reproducible corpus of 2,179 FastAPI applications,
analysed every one of them, and measured how DI is actually used: DI is common
but not universal (37% of applications use none of the DI constructs; the
accounting is detailed in Section 5.1); the generator/yield style appears in
more applications than the documentation-preferred `Annotated` form; the
`Security` `scopes` argument does not occur in the census; and DI graphs are
broad, shallow fan-out structures built around a few shared resources, with a
small 4.3% deep-chain tail that still terminates at the same hubs. These
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