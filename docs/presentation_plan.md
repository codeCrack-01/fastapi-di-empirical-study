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

**Numbers:** 2,179 accepted / 327 stratified sample / 1-of-2,179 topic overlap (0.0%).

**Significance:** three headline magnitudes set up in one slide. 2,179 is a
substantial corpus for an MSR study; 327 is the stratified review sample; the
~0% (exactly 1 repo of 2,179) topic overlap is the methodological anchor that
justifies the whole corpus design.

**Likely grill:** "Why did you drop the application-class RQ?"
**Defence:** the originally-proposed application-class question (it was RQ2 in the
original numbering) asked whether DI varies across *application classes*, which
required an a priori taxonomy we did not have; inventing one post-hoc is
methodologically weak. Per supervisor direction it is folded into RQ1 as a
covariate disaggregation (stars, age), answering "who uses DI" without
arbitrary labels. It remains listed as folded, not silent.

---

## 2. Corpus construction

**Numbers:** 5,009 candidates → rules table → 2,179 accepted.

**Significance:** demonstrates a rigorous, auditable funnel. Every rejection is
recorded with the first-failing rule; nothing is dropped silently.

**Likely grill:** "Why GitHub dependency graph instead of Libraries.io?"
**Defence:** Libraries.io `/dependents` is disabled server-side
(librariesio/libraries.io#2647). GitHub's dependency graph uses equivalent
manifest-parsing, is live, and is the current authoritative dependency source.
We disclose this substitution in Threats.

**Likely grill:** "Why these E4 thresholds?"
**Defence:** E4 (≥2 distinct files import fastapi) removes single-file demos
and one-off scripts while keeping genuine multi-file applications; the
threshold selection is documented in `docs/github_stratified_scan_stats.md`.
Sensitivity section (§6) proves conclusions hold across thresholds 4–8.

---

## 3. From 5,009 to 2,179 — the funnel

**Numbers:** 5,009 → 2,821 excluded (56.3%) → 2,179 accepted (43.5%).

**Significance:** the biggest rejection drivers are *population properties*, not
our thresholds. The revised E1–E4 rules (see `docs/github_stratified_scan_stats.md`)
dropped the arbitrary 50% Python-share gate. The remaining rejections split E4
(1,281 — single-file/demo-scale, < `E4_MIN_FASTAPI_FILES`), E2 (800 — fork or
archived), E1 (516 — no production fastapi import), plus 224 clone failures; 9
candidates remain in retry. Attrition is a small fraction — full auditability.

**Likely grill:** "Is 43.5% acceptance too permissive?"
**Defence:** No — the dependency-graph *source* intentionally over-includes
(any repo GitHub resolves as depending on fastapi) and the revised application
gate keeps every repo with a genuine multi-file FastAPI app. The recall
benchmark (§4) shows this source still captures a population the topic signal
cannot, and the census is analysed in full (no sampling error).

---

## 4. Headline method result: ~0% topic overlap

**Numbers:** candidates 2/5,009 (0.0%) in topic; accepted 1/2,179 (0.0% —
`MoMoM101/RAG-ReActAgent`, the sole accepted repo also captured by the topic
signal; the sibling topic hit `allgpt-co/QuickVoice` failed the E1–E4 gate).

**Significance:** This is the single strongest contribution of the study. The
`topic:fastapi` search — the most natural alternative signal — recovers exactly
one accepted repo (~0%). The dependency graph finds real users; the topic signal
finds templates/tutorials. It bounds the primary source's recall and justifies
the corpus.

**Likely grill:** "Top 1,000 by stars is a narrow topic probe, and you still
found one overlap."
**Defence:** Acknowledged and disclosed. Even this permissive probe (top 1,000)
shares essentially nothing with the corpus (1/2,179, 0.0%); the single overlap is
named and fully disclosed. Widening the probe only strengthens the conclusion
that the two sources are disjoint.

---

## 5. RQ1 — construct prevalence

**Numbers (full-corpus census of 2,179):** Depends 62.9% (median 22), Annotated 17.6% (10),
Generator/yield 34.8% (1), Security 4.8% (1). Router/app-level wiring, dependency
overrides and callable-class dependencies are compositions of the core constructs
(never used without C1/C2) and are reported as structural placements, not as
separate constructs.

**Significance:** the empirical DI usage distribution in real production code —
something the ecosystem lacks hard numbers for.

**Likely grill:** "Why is Security so low when it's a headline feature?"
**Defence:** Security() is scoped to auth/roles and appears once per app where
used; most implementations put auth in middleware or a single top-level
dependency. Low total does not mean insecure — it means the DI-level Security()
construct is not heavily adopted.

**Likely grill:** "Are these counts inflated by copying between repos?"  
**Defence:** The dependency graph source captures *distinct users*, not
tutorial clones; the ~0% topic overlap supports this. No de-duplication was found
necessary (see the recall benchmark).

---

## 6. Zero-DI cohort (36.9%)

**Numbers:** 805 of 2,179 repos use no Depends/Security/Annotated.

**Significance:** the counter-intuitive headline. Over a third of real FastAPI
applications that pass the corpus rules use *no* DI constructs.
FastAPI is commonly marketed around DI, yet practice shows substantial adoption without it.

**Likely grill:** "What do these repos use instead?"
**Defence:** They pass dependencies and DB sessions through direct function
calls / globals / constructors, or use frameworks differently. A follow-on
qualitative pass over the 25 would quantify the substitute patterns (future
work / RQ3 clutches).

---

## 7. RQ1 axis (folded application-class question) — by stars & age

**Numbers:** DI prevalence 58.8–69.0% across all star buckets (61.0% zero-star,
67.9% 1–9-star, 69.0% 10–99-star, 58.8% 100+); corpus 1,903/2,179 repos <12 months
old; 100+-star bucket has 34 repos, 36mo+ has 70.

**Significance:** DI adoption is **flat** across popularity — it is a stable
property of the population, not skewed by stars. The youth of the corpus
(1,903/2,179 repos under a year) is a property of the discovered dependency-graph
population; the E4 gate admits repos up to 60 months old, so the skew is not an
artifact of that gate.

**Likely grill:** "Your high-star/high-age buckets are nearly empty."
**Defence:** Correct and disclosed (§Threats). We do not over-read bins with
low n; they are reported for completeness. The flat-prevalence story rests on
the well-populated 0/1–9 star buckets (1,491 and 567 repos).

---

## 8. RQ2 — usage & dynamic relationships (new)

**Numbers (census of 2,179):** 96.6% of 98,243 `Depends()` call sites pass a bare
function; 0 of 620 `Security()` calls pass `scopes` (0/104 repos); 708 fan-in hub
nodes (≥10 dependents; `get_db` 24,014); 4.1% of graph nodes are classes (2,682 /
62,200+2,682); Tier B idioms at low n (`.as_form` 6 repos, class-as-dep 28 repos,
`current_*` 76 repos).

**Significance:** the *shape* of DI, not just its presence. RQ1 says "Depends is in
62.9%"; RQ2 says "how it's wired" — plain-callable dominance, the unused OAuth2
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

**Numbers (clean, 1,338/2,179 non-empty):** median nodes 19.0, IQR 7–49, max 1,444;
median depth 2, max 7; median unresolved 0.0%.

**Deep tail (depth ≥ 5):** 58 repos / 4.3% of graph-bearing (43 @ 5, 11 @ 6,
4 @ 7). All 58 still contain a fan-out hub; tail repos are larger (median 116
vs 19 clean nodes) but skew young (54/58 < 12 mo) and low-star (36/58
zero-star). Chains read as stacked service layers terminating at a shared
hub: `handle_swipes → get_swipe_service → get_spotify_service →
get_spotify_cache → get_redis_client → get_redis → get_state`
(`GG-Angel/overplayed`). Artifact: `analysis/out/rq3_depth_tail.csv`.

**Significance:** the empirical shape of DI in the wild is **broad and
shallow** — a small set of shared dependencies reused across many handlers
(fan-out). Deep chains are *possible* (up to 7 hops) but a 4.3% tail, appear
in younger/smaller apps, and never replace the hub pattern — they are stacked
on top of it.

**Likely grill:** "Why did you filter 'junk' nodes?"
**Defence:** Section on data-quality handling makes this transparent — see next.

---

## 10. The fan-out hub (architectural signature)

**Numbers:** 79.7% of clean graph-bearing repos have some dependency called by
≥3 other Depends sites (fan-out). Computed by `analysis/build_pptx.py`
(`_fan_out3`) directly from the census reports' clean dependency graphs — a
`file:line` junk-node id in either endpoint excludes that edge, matching the
RQ3 clean-graph definition.

**Significance:** DI's value proposition — one shared resource injected into
many consumers — is empirically the dominant pattern. This is the concrete,
quantifiable payoff of DI that justifies the study.

---

## 11. Robustness — threshold sensitivity

**Numbers:** % using core DI 63.1% (t=2) → 76.2% (t=4) → 84.1% (t=8); stable.

**Significance:** conclusions are **not threshold-dependent** — the pyramid
holds over every tighter file-import threshold (t = 2–8), so the base gate is
not cherry-picked.

**Likely grill:** "Isn't 62.9% just an artifact of a loose t=2 gate?"
**Defence:** The DI-usage share rises monotonically from 63.1% (t=2) to 84.1%
(t=8) as we admit only larger apps — the *ranking* of constructs and the
zero-DI / no-OAuth2-scopes absence findings hold at every threshold, so the
qualitative story does not depend on the gate.

---

## 12. Data-quality handling — resolver junk nodes

**Numbers:** 2,656 junk nodes across 425/2,179 repos (4.1% of all).
Median node count 20 → 19.0 after filtering. All 1,338 graph-bearing repos keep
a clean non-empty graph.

**Significance:** showing our own data QA is a *credibility asset* with this
reviewer. A real bug (module-scope `Depends` → `file:line` placeholder node id)
was found, measured, and mitigated, and is reported verbatim.

**Likely grill:** "Did the bug affect RQ1 too?"
**Defence:** No — RQ1 counts come from call sites (`file_details`), not graph
nodes. The bug only polluted the graph node set.

---

## 13. Caveats & threats

Presented plainly: source substitution, dependency-graph population limits,
attrition (224 clone_failed, 4.5%; 9 pending retry), threshold sensitivity,
**E-rule revision (E1–E6 → E1–E4)**, resolver coverage, and the 327-repo
stratified manual-review sample (vs full census as the analysis universe).

**On the E-rule revision:** the earlier E1–E6 gate (Python-byte-ratio E2,
tutorial-marker E6 flag) was superseded by the current E1–E4 rules. The E6
tutorial-flag review (48-repo blinded subsample, frozen historical evidence —
16/24 flagged labelled genuine (66.7%), 6 uncertain, 2 demo; control 21/2/1)
showed flagged descriptors are largely incidental; E6 is retained only as
historical rationale. This honesty preempts the "did you filter tutorials
properly?" probe: the population is genuine applications (backed by 0% topic
overlap + E1–E4 pass).

---

## 14. So what? — significance close

- **Methodology:** a corpus source with provable recall (0.0% topic overlap, 1/2,179).
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
