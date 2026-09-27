# Peer review kit

Three workbooks and one guide for the review fixed in
[`docs/audit_preregistration.md`](../docs/audit_preregistration.md).

| File | Rows | Raters | Purpose |
|---|---|---|---|
| `REVIEWER_GUIDE.docx` | — | — | Read this first. Plain-language instructions; no Markdown viewer needed. |
| `AUDIT_80.xlsx` | 80 | 2 | **Arm 1.** Random draw from the 804 detected-zero-DI repos. Finds DI the extractor missed. Gates the project. |
| `S3S4_200.xlsx` | 200 | 2 | **Arm 2b.** Random draw from the 1,375 detected-has-DI repos. Gives manual/external DI prevalence with a CI. |
| `S3S4_CANDIDATES.xlsx` | 23 | 1 | **Arm 2a.** Exhaustive, signal-bearing repos. Builds the rubric and a lower bound. |

## What was retired

An earlier 327-row kit in this directory validated the labels of a 14B LLM
(`qwen3:14b`) that assigned S1–S4 to all 2,179 corpus repositories. It was
removed on 2026-09-28. The model matched the deterministic extractor on
1,230/2,179 repositories (56.4%) against a 55% majority-class baseline, and the
evidence packs it read contained a real `Depends` call in only 8% of cases — the
token `settings` in the pack builder's keyword vocabulary matched benign
configuration identifiers and consumed 63% of all excerpt slots.

The kit validated an input, not a classifier. Its strata, inverse-probability
weights, evidence pages, and verdict tables are withdrawn. See
[`docs/methodology_journal.md`](../docs/methodology_journal.md) §3.2.

## Reproducing the workbooks

```bash
.venv/bin/python analysis/build_review_workbooks.py
.venv/bin/python analysis/build_reviewer_guide.py
```

The builder re-derives both frames and both draws from the census and asserts
their SHA-256 against the values in the pre-registration. **If a hash does not
match it exits non-zero rather than emitting a workbook**, so a workbook cannot
silently exist for a different sample than the one that was registered.

| Set | Size | `sha256[:16]` |
|---|---|---|
| Arm 1 frame | 804 | `fb466c1883a28fb7` |
| Arm 1 draw | 80 | `3763e311dad256e2` |
| Arm 2a frame | 23 | `e1f34ea893fb2cde` |
| Arm 2b frame | 1375 | `fc7c5c6295899972` |
| Arm 2b draw | 200 | `d497401503766ea6` |

Seed `20260928`. Arm 1 and Arm 2b are drawn from a single RNG stream, in that
order.

## The gate

Fixed before any rating occurred. From the `gate` sheet of `AUDIT_80.xlsx`:

| Misses / 80 | Wilson 95% upper bound | Decision |
|---|---|---|
| 0–1 | 4.6% – 6.7% | proceed, bound reportable as-is |
| 2–3 | 8.7% – 10.5% | proceed, report the zero-DI share as a range |
| **≥ 4** | **≥ 12.2%** | **stop — extend the extractor before any headline number** |

The thresholds are not revisited after the data are seen.

## Not measured here

- S3/S4 prevalence in the detected-zero-DI stratum. That stratum has no detected
  DI by construction; Arm 1 bounds how much may be hiding there.
- A complete detector. A repository using an unnamed, in-house, or unpublished
  container with no import name, no non-FastAPI `Depends`, and no callable-class
  dependency is unreachable by any of these arms.
- False positives. Arm 1 measures false negatives. False positives rest on the
  structural argument in `docs/audit_preregistration.md` §7.
