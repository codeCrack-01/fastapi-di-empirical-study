# Presentation Plan for Dr. Abdul Ali Bangash

**Paper title:** Empirical Study of Dependency Injection (DI) Usage Patterns in FastAPI Applications

**Purpose:** Preparation guide for the RQ1/RQ2/RQ3/RQ4 corpus presentation. The deck
(`analysis/out/fastapi_di_presentation.pptx`, 22 slides, editable) prioritises
numbers and their significance over decoration. This document is the
talking-points / defence prep — the "why it matters" behind every number.

> **RQ numbering note (2026-09-05):** the paper now defines **RQ2 = usage/dynamic
> relationships** (new) and **RQ3 = dependency-graph complexity** (renumbered from RQ2);
> evolution is RQ4 (deferred). The current deck still uses the older graph-as-RQ2 labels;
> a future deck rebuild will migrate to the new numbering. The research-question and
> result sections below follow the new numbering.

---

## How to read this document
Each section below maps to one deck slide and gives:
- the **number(s)** on the slide,
- the **significance** — what the number actually tells us,
- the **likely grill** — what a strict methodology reviewer will probe,
- the **defence** — the honest answer.

---

## 1. Research questions

**Numbers:** 402 accepted / 100 sample / 0-of-402 overlap.

**Significance:** three headline magnitudes set up in one slide. 402 is a
substantial corpus for an MSR study; 100 is the registered sample; the 0%
overlap is the methodological anchor that justifies the whole corpus design.

**Likely grill:** "Why did you drop the application-class RQ?"
**Defence:** the originally-proposed application-class question (it was RQ2 in the
original numbering) asked whether DI varies across *application classes*, which
required an a priori taxonomy we did not have; inventing one post-hoc is
methodologically weak. Per supervisor direction it is folded into RQ1 as a
covariate disaggregation (stars, age), answering "who uses DI" without
arbitrary labels. It remains listed as folded, not silent.

---

## 2. Corpus construction

**Numbers:** 5,009 candidates → rules table → 402 accepted.

**Significance:** demonstrates a rigorous, auditable funnel. Every rejection is
recorded with the first-failing rule; nothing is dropped silently.

**Likely grill:** "Why GitHub dependency graph instead of Libraries.io?"
**Defence:** Libraries.io `/dependents` is disabled server-side
(librariesio/libraries.io#2647). GitHub's dependency graph uses equivalent
manifest-parsing, is live, and is the current authoritative dependency source.
We disclose this substitution in Threats.

**Likely grill:** "Why these E5 thresholds?"
**Defence:** E5 (≥4 files import fastapi, ≥1 app) is anchored at a natural gap in
the observed distribution of `files_importing_fastapi`, separating one-off
scripts from applications. Sensitivity section (§6) proves conclusions hold
across thresholds 4–8.

---

## 3. From 5,009 to 402 — the funnel

**Numbers:** 5,009 → 4,607 excluded (92.0%) → 402 accepted (8.0%).

**Significance:** the biggest rejection drivers are *population properties*, not
our thresholds. E2 (39%, not Python-dominant) and E1 (19%, no runtime fastapi
dep) are the dependency graph surfacing mixed-language/other repos. Only 42
repos (0.8%) were deleted/private (attrition). Zero `clone_failed` remain —
full auditability.

**Likely grill:** "Is 8.0% acceptance a red flag?"
**Defence:** No — it's the cost of a dependency-graph *source* that intentionally
over-includes (any repo GitHub resolves as depending on fastapi) and then a
strict application gate. The recall benchmark (§4) shows this source still
captures a population the topic signal cannot.

---

## 4. Headline method result: 0% topic overlap

**Numbers:** candidates 2/5,009 (0.0%) in topic; accepted 0/402 (0.0%).

**Significance:** This is the single strongest contribution of the study. The
`topic:fastapi` search — the most natural alternative signal — recovers **zero**
accepted repos. The dependency graph finds real users; the topic signal finds
templates/tutorials. It bounds the primary source's recall and justifies the
corpus.

**Likely grill:** "Top 1,000 by stars is a narrow topic probe."
**Defence:** Acknowledged and disclosed. Even this permissive probe (top 1,000)
shares nothing with the corpus; widening it only strengthens the conclusion
that the two sources are disjoint.

---

## 5. RQ1 — construct prevalence

**Numbers (full-corpus census of 402):** Depends 75.4% (median 22), Annotated 25.9% (11),
Generator/yield 40.3% (1), Security 10.4% (1), Router 14.4% (3), App 2.5%, Override 1.7%,
Callable-class 0.5%.

**Significance:** the empirical DI usage distribution in real production code —
something the ecosystem lacks hard numbers for.

**Likely grill:** "Why is Security so low when it's a headline feature?"
**Defence:** Security() is scoped to auth/roles and appears once per app where
used; most implementations put auth in middleware or a single top-level
dependency. Low total does not mean insecure — it means the DI-level Security()
construct is not heavily adopted.

**Likely grill:** "Are these counts inflated by copying between repos?"  
**Defence:** The dependency graph source captures *distinct users*, not
tutorial clones; 0% topic overlap supports this. No de-duplication was found
necessary (see 0-overlap evidence).

---

## 6. Zero-DI cohort (24.4%)

**Numbers:** 98 of 402 repos use no Depends/Security/Annotated.

**Significance:** the counter-intuitive headline. A quarter of real FastAPI
applications with ≥4 importing files and ≥1 app use *no* DI constructs. FastAPI
is commonly marketed around DI, yet practice shows substantial adoption without it.

**Likely grill:** "What do these repos use instead?"
**Defence:** They pass dependencies and DB sessions through direct function
calls / globals / constructors, or use frameworks differently. A follow-on
qualitative pass over the 25 would quantify the substitute patterns (future
work / RQ3 clutches).

---

## 7. RQ1 axis (folded application-class question) — by stars & age

**Numbers:** DI prevalence ≈73–76% across 0-star and 1–9-star buckets; corpus
361/402 repos <12 months old; 100+-star bucket has 7 repos, 36mo+ has 11.

**Significance:** DI adoption is **flat** across popularity — it is a stable
property of the population, not skewed by stars. The youth of the corpus is a
consequence of the E4 recency gate × fast-growing dependency-graph population.

**Likely grill:** "Your high-star/high-age buckets are nearly empty."
**Defence:** Correct and disclosed (§Threats). We do not over-read bins with
n=7–14; they are reported for completeness. The flat-prevalence story rests on
the well-populated 0/1–9 star buckets (246 and 135 repos).

---

## 8. RQ2 — usage & dynamic relationships (new)

**Numbers (census of 402):** 97.1% of 25,166 `Depends()` call sites pass a bare
function; 0 of 163 `Security()` calls pass `scopes` (0/42 repos); 227 fan-in hub
nodes (≥10 dependents; `get_db` 4,683); 4.2% of graph nodes are classes (728 /
16,494+728); Tier B idioms at low n (`.as_form` 1 repo, class-as-dep 14 classes/7
repos, `current_*` 15 repos).

**Significance:** the *shape* of DI, not just its presence. RQ1 says "Depends is in
75.4%"; RQ2 says "how it's wired" — plain-callable dominance, the unused OAuth2
scopes feature (`Security(scopes=...) = 0%`), and the fan-out relationship
signature (small set of shared dependencies consumed by many handlers, i.e. what
the community actually builds with the documented constructs).

**Likely grill:** "Isn't this just the graph-complexity RQ?" / "Your Tier B
idioms are n=1–5."
**Defence:** RQ3 measures graph *summary statistics* (median nodes/depth);
RQ2 classifies *call-site argument shape and roles* (what is passed to `Depends()`,
does `Security()` use scopes) plus relationship topology at the node level — a
different, semantic lens. Tier B is explicitly qualitative, reported as
evidence-with-n, not as a statistical claim; the quantitative backbone is Tier A
(arg shapes, scopes=0%, hubs).

---

## 9. RQ3 — graph complexity

**Numbers (clean, 294/402 non-empty):** median nodes 19.5, IQR 8–54, max 1,444;
median depth 2, max 7; median unresolved 0.0%.

**Significance:** real FastAPI DI dependency graphs are **broad and shallow** —
a small set of shared dependencies reused across many handlers (fan-out), not
deep inheritance-like chains. This is the empirical shape of DI in the wild.

**Likely grill:** "Why did you filter 'junk' nodes?"
**Defence:** Section on data-quality handling makes this transparent — see next.

---

## 10. The fan-out hub (architectural signature)

**Numbers:** 78.2% of clean graph-bearing repos have some dependency called by
≥3 other Depends sites (fan-out). Computed by `analysis/build_pptx.py`
(`_fan_out3`) directly from the census reports' clean dependency graphs — a
`file:line` junk-node id in either endpoint excludes that edge, matching the
RQ3 clean-graph definition.

**Significance:** DI's value proposition — one shared resource injected into
many consumers — is empirically the dominant pattern. This is the concrete,
quantifiable payoff of DI that justifies the study.

---

## 11. Robustness — E5 sensitivity

**Numbers:** % using core DI 75.6% (t=4) → 80.6% (t=8); stable.

**Significance:** conclusions are **not threshold-dependent** — the anchor for
the E5 heuristic.

**Likely grill:** "Your t=2,3 rows are identical to t=4."
**Defence:** They are degenerate by construction — every accepted repo already
passes at t=4, so lower thresholds add nothing. Sensitivity is meaningful at
t ≥ 5, exactly where the monotone rise is observed.

---

## 12. Data-quality handling — resolver junk nodes

**Numbers:** 713 junk nodes across 122/294 graph-bearing repos (4.1% of all).
Median node count 22 → 19.5 after filtering. All 294 graph-bearing repos keep a
clean non-empty graph.

**Significance:** showing our own data QA is a *credibility asset* with this
reviewer. A real bug (module-scope `Depends` → `file:line` placeholder node id)
was found, measured, and mitigated, and is reported verbatim.

**Likely grill:** "Did the bug affect RQ1 too?"
**Defence:** No — RQ1 counts come from call sites (`file_details`), not graph
nodes. The bug only polluted the graph node set.

---

## 13. Caveats & threats

Presented plainly: source substitution, dependency-graph population limits,
attrition (42, 0.8%), E5 degeneracy, **tutorial flags as an open count**,
resolver coverage, non-stratified sample, and the late-first-commit caveat.

**On tutorial flags (E6, 47%):** flags reviewed via the 48-repo blinded
subsample (frozen, 351-pool era) are mostly incidental — 16/24 flagged were
labelled genuine (66.7%), 6 uncertain, 2 demo; control 21/2/1. Flags are
therefore an open count we present as unresolved rather than claiming resolved.
This honesty preempts the "did you filter tutorials properly?" probe: flagged
descriptors are largely incidental, and the population is genuine applications
(backed by 0% topic overlap + E1–E5 pass).

---

## 14. So what? — significance close

- **Methodology:** a corpus source with provable recall (0% topic overlap).
- **Practice:** DI is not universal (24% zero-DI); teaching should reflect reality.
- **Design:** the DI profile is broad-and-shallow fan-out — actionable for
  framework design and code-quality tooling.
- **Paper:** hard, reproducible, threshold-stable numbers.

---

## Open items before publication (be transparent in the talk)
1. **Keep the repository committed** — artifacts were first committed 2026-08-31
   (previously zero commits); keep history clean and push before external review.
2. **Resolve the 188 tutorial flags** (or explicitly scope as open).
3. **RQ4 git-history** enrichment for temporal DI analysis.
4. **Overall picture: what DI does (not) deliver** — the 24% zero-DI + 78%
   fan-out combo is the crispest "so what" to lead or close with.
