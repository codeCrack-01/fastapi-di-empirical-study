# Presentation Plan for Dr. Abdul Ali Bangash

**Paper title:** Empirical Study of Dependency Injection (DI) Usage Patterns in FastAPI Applications

**Purpose:** Preparation guide for the RQ1/RQ2/RQ3 corpus presentation. The deck
(`analysis/out/fastapi_di_presentation.pptx`, 22 slides, editable) prioritises
numbers and their significance over decoration. This document is the
talking-points / defence prep — the "why it matters" behind every number.

---

## How to read this document
Each section below maps to one deck slide and gives:
- the **number(s)** on the slide,
- the **significance** — what the number actually tells us,
- the **likely grill** — what a strict methodology reviewer will probe,
- the **defence** — the honest answer.

---

## 1. Research questions

**Numbers:** 351 accepted / 100 sample / 0-of-351 overlap.

**Significance:** three headline magnitudes set up in one slide. 351 is a
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

**Numbers:** 4,500 candidates → rules table → 351 accepted.

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

## 3. From 4,500 to 351 — the funnel

**Numbers:** 4,500 → 4,149 excluded (92.2%) → 351 accepted (7.8%).

**Significance:** the biggest rejection drivers are *population properties*, not
our thresholds. E2 (36%, not Python-dominant) and E1 (18%, no runtime fastapi
dep) are the dependency graph surfacing mixed-language/other repos. Only 42
repos (0.9%) were deleted/private (attrition). Zero `clone_failed` remain —
full auditability.

**Likely grill:** "Is 7.8% acceptance a red flag?"
**Defence:** No — it's the cost of a dependency-graph *source* that intentionally
over-includes (any repo GitHub resolves as depending on fastapi) and then a
strict application gate. The recall benchmark (§4) shows this source still
captures a population the topic signal cannot.

---

## 4. Headline method result: 0% topic overlap

**Numbers:** candidates 2/4,500 (0.0%) in topic; accepted 0/351 (0.0%).

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

**Numbers (100-sample):** Depends 75% (median 17), Annotated 24% (7.5),
Generator/yield 37% (1), Security 12% (1), Router 17% (4), App 2%, Override 1%,
Callable-class 2%.

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

## 6. Zero-DI cohort (25%)

**Numbers:** 25 of 100 sampled repos use no Depends/Security/Annotated.

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

**Numbers:** DI prevalence ≈73–75% across 0-star and 1–9-star buckets; corpus
92/100 repos <12 months old; high-star/age buckets have 1–5 repos.

**Significance:** DI adoption is **flat** across popularity — it is a stable
property of the population, not skewed by stars. The youth of the corpus is a
consequence of the E4 recency gate × fast-growing dependency-graph population.

**Likely grill:** "Your high-star/high-age buckets are nearly empty."
**Defence:** Correct and disclosed (§Threats). We do not over-read bins with
n=1–5; they are reported for completeness. The flat-prevalence story rests on
the well-populated 0/1–9 star buckets (64 and 28 repos).

---

## 8. RQ2 — graph complexity

**Numbers (clean, 71/100 non-empty):** median nodes 19, IQR 7–53, max 259;
median depth 2, max 5; median unresolved 0.0%.

**Significance:** real FastAPI DI dependency graphs are **broad and shallow** —
a small set of shared dependencies reused across many handlers (fan-out), not
deep inheritance-like chains. This is the empirical shape of DI in the wild.

**Likely grill:** "Why did you filter 'junk' nodes?"
**Defence:** Section on data-quality handling makes this transparent — see next.

---

## 9. The fan-out hub (architectural signature)

**Numbers:** 91.3% of clean graph-bearing repos show ≥3-dependency fan-out.

**Significance:** DI's value proposition — one shared resource injected into
many consumers — is empirically the dominant pattern. This is the concrete,
quantifiable payoff of DI that justifies the study.

---

## 10. Robustness — E5 sensitivity

**Numbers:** % using core DI 74.9% (t=4) → 81.4% (t=8); stable.

**Significance:** conclusions are **not threshold-dependent** — the anchor for
the E5 heuristic.

**Likely grill:** "Your t=2,3 rows are identical to t=4."
**Defence:** They are degenerate by construction — every accepted repo already
passes at t=4, so lower thresholds add nothing. Sensitivity is meaningful at
t ≥ 5, exactly where the monotone rise is observed.

---

## 11. Data-quality handling — resolver junk nodes

**Numbers:** 619 junk nodes across 105/255 graph-bearing repos (3.9% of all).
Median node count 24 → 19 after filtering. All 71 sample repos keep a clean
non-empty graph.

**Significance:** showing our own data QA is a *credibility asset* with this
reviewer. A real bug (module-scope `Depends` → `file:line` placeholder node id)
was found, measured, and mitigated, and is reported verbatim.

**Likely grill:** "Did the bug affect RQ1 too?"
**Defence:** No — RQ1 counts come from call sites (`file_details`), not graph
nodes. The bug only polluted the graph node set.

---

## 12. Caveats & threats

Presented plainly: source substitution, dependency-graph population limits,
attrition (42, 0.9%), E5 degeneracy, **tutorial flags as an open count**,
resolver coverage, non-stratified sample, and the late-first-commit caveat.

**On tutorial flags (E6, 46%):** all flags reviewed so far (35 repos) are false
positives — real apps whose descriptions happen to contain words like
"example"/"getting started". We present the count openly as unresolved rather
than claiming it is resolved. This honesty preempts the "did you filter
tutorials properly?" probe: the flags are incidental, and the population is
genuine applications (backed by 0% topic overlap + E1–E5 pass).

---

## 13. So what? — significance close

- **Methodology:** a corpus source with provable recall (0% topic overlap).
- **Practice:** DI is not universal (25% zero-DI); teaching should reflect reality.
- **Design:** the DI profile is broad-and-shallow fan-out — actionable for
  framework design and code-quality tooling.
- **Paper:** hard, reproducible, threshold-stable numbers.

---

## Open items before publication (be transparent in the talk)
1. **Keep the repository committed** — artifacts were first committed 2026-08-31
   (previously zero commits); keep history clean and push before external review.
2. **Resolve the 162 tutorial flags** (or explicitly scope as open).
3. **RQ3 git-history** enrichment for temporal DI analysis.
4. **Overall picture: what DI does (not) deliver** — the 25% zero-DI + 91%
   fan-out combo is the crispest "so what" to lead or close with.
