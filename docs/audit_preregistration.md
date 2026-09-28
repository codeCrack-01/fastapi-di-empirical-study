# Pre-registration — DI census validation and S3/S4 characterisation

**Status:** PRE-REGISTERED. No rating data existed when this document was committed.
**Date committed:** 2026-09-28
**Scope:** the peer review that validates the deterministic census and establishes the
manual/external DI (S3/S4) picture.
**Supersedes:** `peer_review_kit/` (327-row kit) — retired, see §1.

---

## 0. What this document does

It fixes, in advance of any human rating:

- the exact repository frames each arm draws from, by SHA-256 hash
- the random draw for each sampling arm, by seed
- the decisions raters may record
- the threshold at which the project's scope decision changes
- the inferential method for every number we intend to report

Any change to the items above after ratings begin is a deviation and must be reported
as one.

---

## 1. Why the previous design was retired

A 14B LLM (`qwen3:14b`) was used to attribute S1–S4 to all 2,179 corpus repositories,
and the 327-repository peer review kit was built to validate those attributions.

Two findings ended that design:

1. **The LLM agreed with the deterministic extractor on only 56.4% of repositories
   (1,230 / 2,179).** Where the two disagreed, the LLM was wrong at least as often as
   it was right.
2. **The disagreement was partly an input defect, not a model defect.** Repository
   evidence packs were built from a keyword vocabulary in which the token `settings`
   consumed 6,997 of ~11,000 excerpt slots by matching benign configuration code
   (`gensui_settings`, `get_settings`). Only 8% of evidence packs contained a single
   real `Depends` call. Repositories with 776 `Depends` calls were presented to the
   model with 20 lines of configuration plumbing and no `Depends`, and the model
   correctly reported "no evidence of framework-native DI" — because there was none in
   its input.

The LLM is therefore **retired from the evidentiary chain**: it supplies no census
label, determines no audit frame, sets no threshold, and appears in no inferential
step. Its 56.4% agreement rate is retained solely as a reported negative result about
tool reliability (§8).

The 327-row kit, the `stratum` column, the inverse-probability `weight` column
(6.370787 / 12.74359), and any prevalence number derived from the 327 are withdrawn.
Prevalence is computed from the full 2,179-repository deterministic census.

---

## 2. The deterministic classifier under test

`extractor/`, `EXTRACTOR_VERSION = 0.2.1`, `SCHEMA_VERSION = 0.2`.

Per non-test, FastAPI-importing file the extractor counts four constructs:

| Construct | Report field |
|---|---|
| `Depends(...)` | `depends_calls` |
| `Security(...)` | `security_calls` |
| `Annotated[..., Depends(...)]` | `annotated_depends` |
| generator/`yield` dependency | `yield_functions` |

Repo-level verdict:

- **S1 (detected zero-DI)** — all four totals are 0, and no external DI library import
- **S2 (detected framework-native)** — any total > 0, and no external DI library import
- **S4? (detected external)** — external DI library import present

**The extractor cannot emit S3.** No field corresponds to hand-rolled dependency
wiring; `analysis/novelty/labels.py` states that router/app-level `dependencies=[...]`
wiring, dependency overrides and callable-class dependencies are compositions of C1/C2
and are not counted as constructs. A consequence central to this design: **the S3
population is not observable to the detector**, and Arm 2 exists to establish it.

Deterministic coverage of the corpus: 804 detected-zero-DI, 1,375 detected-has-DI,
7 with a detected external library import (0 reports have `files_total == 0` and 0
have no production `file_details`, so no repository entered S1 through a silent parse
failure).

---

## 3. Arm 1 — false-negative audit (gates the project)

**Question.** Of the repositories the extractor classified as having no dependency
injection, how many in fact contain a DI mechanism the extractor did not detect?

**Frame.** All 804 detected-zero-DI repositories.
Frame SHA-256 (first 16 hex, sorted names joined by newline): `fb466c1883a28fb7`

**Draw.** 80, simple random, `random.Random(20260928)`.
Draw SHA-256: `3763e311dad256e2`
Sampling fraction 9.95%.

**Rater response.** `yes` / `no` / `unclear`. `unclear` is a permitted and expected
answer; forcing a binary would reproduce the defect that retired the previous design.

**The question put to raters is "does this repository contain any dependency-injection
mechanism of any kind"** — not "does it contain FastAPI DI". A repository the
extractor called S1 because it has zero FastAPI constructs may still contain an
external container, a house-rolled `Depends`, or manual wiring.

**Triage.** Every row is pre-populated with the repository's import table and its
`non_fastapi_depends_sources` and `callable_class_deps` flags, so raters confirm
rather than search. This is an efficiency measure and is not itself a judgement.

**Gate.** Let *k* be the number of `yes` responses out of 80 after rater reconciliation.
The 95% Wilson upper bound on the false-negative rate is:

| *k* | Point | 95% upper bound | Decision |
|---|---|---|---|
| 0 | 0.0% | 4.6% | proceed; bound is reportable as-is |
| 1 | 1.2% | 6.7% | proceed; bound is reportable as-is |
| 2 | 2.5% | 8.7% | proceed; S1 share must be reported as a **range** in the table header |
| 3 | 3.8% | 10.5% | proceed; S1 share must be reported as a **range** in the table header |
| **≥4** | **≥5.0%** | **≥12.2%** | **STOP. Do not write any headline number. Build the resolution-edge detector first.** |

The threshold is **4**. It was fixed before any rating occurred and is not revisited
after the data are seen.

**Why 4, and not a softer number.** The exposure is the S1/S2 boundary, which is the
majority of the corpus, not the rare S3/S4 buckets. At a 12.2% false-negative rate,
1,230 AST-agreed zero-DI repositories contribute up to 150 misclassifications, moving
the detected-zero-DI share from 36.9% to 30.1%. That is not a limitation paragraph; it
is a different result.

---

## 4. Arm 2a — candidate characterisation (rubric development)

**Question.** Among repositories carrying a manual-DI or external-DI signal, what
patterns actually occur, and what rubric describes them?

**Frame.** All repositories carrying any of: `di_lib_hits` under the 27-name DI
library list, `non_fastapi_depends_sources` non-empty, or `callable_class_deps`
non-empty. **Exhaustive, not sampled.**
Frame SHA-256: `e1f34ea893fb2cde` — 23 repositories.

**Rating.** One rater, open taxonomy capture, ~12 minutes per repository. This arm
develops the rubric that Arm 2b then applies. **No κ is computed here** — it is rubric
development, and treating it as a reliability exercise would misdescribe it.

**Output.** A written rubric for detected manual DI, worked code examples, and a
**lower bound** on S3/S4 prevalence: the number of repositories found by targeted
search.

**This arm cannot estimate prevalence, and its lower bound is explicitly
uninterpretable in magnitude.** A purposive count of *m* candidates is consistent with
a true rate anywhere from *m/N* (if the signal list catches every case) to well above
that. It carries no confidence interval. Arm 2b exists to bracket it.

---

## 5. Arm 2b — S3/S4 prevalence (the estimable quantity)

**Question.** Among repositories the extractor classified as detected framework-native
DI, what fraction additionally use manual or external DI?

**Frame.** All 1,375 detected-has-DI repositories.
Frame SHA-256: `fc7c5c6295899972`

**Draw.** 200, simple random, `random.Random(20260928)`. **Flat — not stratified by
signal.** Oversampling signal-bearing repositories inside the draw would improve
efficiency per row but would require inverse-probability weights, and weights are a
known source of opacity in this project's prior design.
Draw SHA-256: `d497401503766ea6`
Sampling fraction 14.5%.

**Rater response.** `S2` / `S3` / `S4` / `unclear`.

**Inferential method.** Proportion with Wilson 95% confidence interval, reported
against the 1,375 frame. Precision was fixed in advance at n=200 rather than at a
target interval width, because for a low-rate category an absolute width target is
not a reasonable publishability criterion. At a true 5% rate, n=200 yields
[2.7%, 9.0%]; n=150 would yield [2.7%, 10.2%]; n=80 would yield [2.0%, 12.2%] and is
not used.

**Triage.** 98.7% of the 2b frame carries no manual/external signal and is expected to
resolve in ~3 minutes; 18 repositories carry a signal and require a deep read. Mean
~3.1 minutes per row.

---

## 6. Rater protocol

- Two raters, working **independently**. Each receives a private copy; no rater sees
  the other's responses before both are complete.
- **Raters.** Zain Ahmed Khan and Yahya Ahmed.
- **Per-arm assignment.**

  | Arm | Zain Ahmed Khan | Yahya Ahmed | κ |
  |---|---|---|---|
  | 1 — `AUDIT_80.xlsx` (80) | all 80 | all 80 | yes |
  | 2b — `S3S4_200.xlsx` (200) | all 200 | all 200 | yes |
  | 2a — `S3S4_CANDIDATES.xlsx` (23) | all 23 | — | no (rubric development) |

  Arm 2a is single-rater by design (§4): it develops the rubric that Arm 2b applies,
  so its purpose is coverage, not reliability. κ rests on Arm 1 and Arm 2b, which are
  both double-rated — see the next bullet.
- **κ is computed on Arm 1 (yes/no) and Arm 2b (S2/S3/S4).** Both arms were selected
  for a prevalence claim, and a poorly-reliable verdict on a headline number is a
  liability. Neither arm is single-rater, so the κ claim does not rest on one person.
- Raters see the extractor's verdict but are instructed to record their own decision
  from the repository source first, and only then compare. The guide states this
  explicitly; anchoring on the machine's answer would inflate agreement without
  adding information.
- Raters may record `unclear`. Rows left unclear are reported as such, not silently
  reassigned to the machine's verdict.
- `arm1 ≥ 4 misses` and `2b κ < 0.40` are both escalation triggers, decided in advance.

---

## 7. What this pre-registration does not establish

- It does not establish S3/S4 prevalence in the **detected-zero-DI** stratum. That
  stratum is, by construction, free of detected DI; Arm 1 bounds how much undetected
  DI may be hiding there.
- It does not produce a complete detector. A repository using an unnamed, unpublished
  or in-house container with no import name, no non-FastAPI `Depends`, and no
  callable-class dependency is not reachable by any arm here.
- "No DI detected" is an assertion about the extractor's output. It is never restated
  as "no DI exists." Every reported count uses "detected" in its label, in the table
  header, not only in a limitations paragraph.
- Arm 1 measures false negatives. False positives are assessed by structural argument
  (AST call detection in FastAPI-importing non-test files, with non-FastAPI `Depends`
  quarantined by `non_fastapi_depends_sources`) and by a definitional decision about
  the S1/S2 threshold, not by a separate sampling audit.

---

## 8. A note on prior LLM-based work

An earlier iteration of this project tested whether an LLM could label repositories
directly. That pipeline was withdrawn, together with all of its outputs, on the grounds
that agreement with the deterministic classifier was no better than a majority-class
baseline and the inputs it consumed were itself defective. Its results are not carried
into this document, into the evidence chain, or into any claim this study makes, and
should be treated as never having been produced. No LLM output contributes to any
figure reported here.

---

## 9. Fixed parameters, for the record

| Parameter | Value |
|---|---|
| Seed | 20260928 |
| Arm 1 frame / draw | 804 / 80 · `fb466c1883a28fb7` / `3763e311dad256e2` |
| Arm 2a frame | 23, exhaustive · `e1f34ea893fb2cde` |
| Arm 2b frame / draw | 1,375 / 200 · `fc7c5c6295899972` / `d497401503766ea6` |
| Gate | ≥4 misses in Arm 1 → stop |
| κ | Wilson/Poisson-free; Cohen's κ on Arm 1 and Arm 2b |
| Extract under test | `EXTRACTOR_VERSION 0.2.1`, `SCHEMA_VERSION 0.2` |

Machine-readable copy: `analysis/out/prereg_frames.json`.
