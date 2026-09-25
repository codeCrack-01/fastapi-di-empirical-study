# Consensus Form — Peer Review Ground Rules (v1)

## Purpose
Two independent reviewers confirm the LLM-generated DI verdicts for the 327-repo
stratified sample. This form defines what a verdict means and how disagreements
are resolved, so the two reviewers work to the same standard.

## Verdict vocabulary
Exactly two verdicts may be chosen in the `MY_VERDICT` / `PEER_VERDICT` columns:

| Verdict | Meaning |
|---|---|
| **Agree with LLM** | The model's verdict is correct for this repo (DI present as described, or no DI as stated). |
| **Override** | The model's verdict is wrong. **Required**: a short reason in `NOTES`. |

## What counts as DI (confirm per `DI_pattern_gallery.md`)
- **C1** — `Depends(...)` in a function signature (positional/parameter dependency). **FastAPI**: https://fastapi.tiangolo.com/tutorial/dependencies/
- **C2** — `Security(...)` scoped security dependencies. **FastAPI**: https://fastapi.tiangolo.com/tutorial/security/
- **C3** — `Annotated[T, Depends(...)]` typed dependency syntax (`Annotated` = Python stdlib, DI = FastAPI).
- **C4** — generator/yield dependency (`def get_db(): ...: yield db`) used via FastAPI's machinery: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
- **Swappable** — *how C1–C4 relate, not a fifth type.* The four constructs are
  mutually swappable spellings of one injection mechanism (see gallery Part A).
  The Swappable category here = a provider written 2+ ways in one repo (e.g.
  `Depends(get_db)` vs `Annotated[Session, Depends(get_db)]`): genuine,
  interchangeable DI. This is the benchmark-relevant case.
- **Context-bound** — single-repo provider, non-plain argument, closure/parameterized dependency, or pass-2 non-native mechanism (container `@inject`, `app.state`, `thread-local`, lifespan/factory DI, etc.).
- **Over-capture** — labelled false_pos by the panel but often real DI (`C3|CLASS|BARE`, `C4|USED`). **Adjudicate on the code; do not auto-dismiss.**

See **Part A** of the gallery for what C1–C4 are (name, FastAPI-vs-Python origin, online
docs). See **Part B** for fingerprints: the `C1|BARE|SIG`-style strings are simply the
exact *spelling* of a C1–C4 occurrence — a finer view showing all the variants of the
four constructs, **not** extra categories. A fingerprint is still C1/C2/C3/C4; the panel's
`known / variant / novel / false_pos / external_di` label judges that spelling.

## No-DI repos (25 of 327)
- `llm_no_di_reason` already carries the model's stated basis (AST counts:
  `depends_total`, `annotated_depends_total`, `yield_dep_total` = 0 + explanation).
- Reviewer check: confirm no C1–C4 construct exists anywhere (see gallery for
  the shapes). If the model supplied no reason, that is acceptable — no rerun.
- If you find DI that the model said was absent → **Override**, cite the file:line.

## Overrides
- MUST carry a reason in `NOTES`, ideally with a file:line.
- An override on an **Over-capture** row is the *expected* outcome when the code
  clearly shows DI the panel mislabelled.

## Conflict resolution
- `FINAL_VERDICT` auto-computes: both verdicts equal → that verdict; both filled
  and different → **CONFLICTED**; either empty → blank (pending).
- **CONFLICTED** rows are re-read together by both reviewers, then a mutual
  verdict is recorded in `NOTES` (prefix `RESOLVED:`).
- Run `scripts/cohens_kappa.py` only after BOTH columns are fully filled.

## Inter-rater reliability
- κ computed on all paired rows (327 if both review everything).
- Landis & Koch (1977) bands: <0 poor · 0–0.20 slight · 0.21–0.40 fair ·
  0.41–0.60 moderate · 0.61–0.80 substantial · 0.81–1.00 almost perfect.
- **Target: κ ≥ 0.61 (substantial)** before reporting agreement; report the
  achieved band either way, with the matrix.

## Reporting
Report: total rows, # agree / # override / # conflicted, the 2×2 matrix, κ with
z/p, and the band. List all Override and CONFLICTED rows with their reason in
the paper's appendix.

---
*Keep this page open while reviewing. Point both reviewers here before starting.*