# Peer-Review Kit — FastAPI DI empirical study (327-repo stratified sample)

This folder is the full evidence package for the human peer-review pass.
Two reviewers independently confirm the LLM verdict per repo; disagreements are
resolved via the FINAL column and a re-check.

## What's inside

| File / dir | What it is |
|---|---|
| `peer_review.xlsx` | **The workbook you work in.** One row per repo (327). Columns: repo metadata, LLM verdict summary, example & evidence links, LLM "no DI" reason, `MY_VERDICT` / `PEER_VERDICT` dropdowns, `FINAL_VERDICT` (auto: matches → shown, differs → **CONFLICTED**), `NOTES`. |
| `LLM_verdicts.xlsx` / `.tsv` | Read-only copy of the model's per-repo verdict table (same data as the workbook's LLM columns, for reference). |
| `DI_pattern_gallery.md` | **Shared "what am I confirming?" reference.** Real source code showing each DI type (C1 `Depends`, C2 `Security`, C3 `Annotated`, C4 generator/yield) and the three catalog types (Swappable / Context-bound / Over-capture). |
| `evidence_pages/` | 327 per-repo evidence pages (`Q* / owner__repo / review.md`) — pass-1 observations, pass-2 reconciliations/overturns, missed-by-inventory, fingerprint labels, citation links. The `evidence` column in the workbook points here. |
| `scripts/cohens_kappa.py` | After both reviewers finish, computes agreement matrix + Cohen's κ + Landis & Koch band. |

## How to work the review (ground rules)

1. Open `peer_review.xlsx`. Freeze panes are on thumb; an autofilter is applied.
2. For each row, look at the **LLM summary columns**, open the linked **example**
   or the **evidence page** under `evidence_pages/`, and — when unsure — the
   repo on GitHub at its pinned commit (`github_url`).
3. Pick a verdict from the dropdown:
   - **Agree with LLM** — the model's verdict matches what you see.
   - **Override** — you disagree. **You must write a short reason in `NOTES`.**
4. `FINAL_VERDICT` is a formula: both filled + same → verdict; both filled +
   different → **CONFLICTED** (red). Conflicts are re-checked together, then a
   mutual final verdict is typed into `NOTES` (recognised convention: leave
   `FINAL_VERDICT` showing the agreed value, or note `RESOLVED:` in `NOTES`).
5. For **no-DI repos** (`llm_n_di` is empty/0): the `llm_no_di_reason` column
   carries the model's stated reason (AST counts + explanation). Verify no
   C1–C4 pattern exists per the gallery; if the model did not supply a reason,
   that is fine — no rerun needed, just check the code.
6. The two reviewers do **not** compare notes until both have finished their
   column. Only then run `scripts/cohens_kappa.py`.

## After both reviewers finish

```bash
.venv/bin/python peer_review_kit/scripts/cohens_kappa.py --xlsx peer_review_kit/peer_review.xlsx
```

Reports the 2×2 agreement matrix, observed agreement po, **both** Cohen's κ and
**Gwet's AC1** (with z/p), and the Landis & Koch (1977) band. **Landis & Koch
bands:** <0 poor · 0–0.20 slight · 0.21–0.40 fair · 0.41–0.60 moderate ·
0.61–0.80 substantial · 0.81–1.00 almost perfect.

AC1 is reported because the verdict split is dominated by "Agree with LLM" —
a prevalence skew that mechanically deflates Cohen's κ (1−pe in the
denominator grows with the dominant category). **Preregistered pass rule:** raw
agreement po ≥ 0.90 **and** κ ≥ 0.40 (moderate). AC1 is the robustness check:
a "moderate κ + high AC1" pair is the *expected* outcome under a dominant
agree-majority, not a failure.

## Method note (for the methods section)

Judge = qwen3:14b (temperature 0, fixed seed), two passes: blind pass-1
observations + pass-2 confrontation against the fingerprint inventory
(agree/overturn/missed). Prompts are pinned in the repo at
`analysis/novelty/prompt.py` (byte-stable); model *reasoning traces* were not
captured (Ollama `think` not enabled) — structured evidence and cited
file:line were required of the model in its output schema instead. Human
peer-review + Cohen's κ is the trust layer.

## Regenerating the workbook

```bash
.venv/bin/python scripts/build_review_workbook.py   # builds analysis/out/review/peer_review.xlsx
```