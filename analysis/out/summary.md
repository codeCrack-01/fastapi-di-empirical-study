# Extraction summary

- Sample: 2179 of pool 2179 (full-corpus census (not a sample))
- Reports loaded: 2179

## RQ1 — construct prevalence (top rows)

| Construct | Repos | % | Total calls | Median (users) |
|---|---|---|---|---|
| Depends | 1371 | 62.9% | 98243 | 22 |
| Security | 104 | 4.8% | 620 | 1.0 |
| Annotated dependency | 384 | 17.6% | 23241 | 10.0 |
| Generator/yield dependency | 759 | 34.8% | 1003 | 1 |
| Non-FastAPI Depends sources | 10 | 0.5% | 22 |  |
| Repos using ZERO core DI constructs (no Depends/Security/Annotated) | 805 | 36.9% |  |  |

**Zero-DI cohort:** 805 repos (36.9%) use no Depends/Security/Annotated at all.

## RQ3 — dependency-graph complexity (clean nodes, non-empty graphs)

- Graph-bearing repos (clean): 1338 / 2179
- Nodes (clean): median 19.0, IQR (7.0, 49.0), max 1444
- Max depth: median 2.0, max 7
- Unresolved %: median 0.0

- Junk nodes filtered: 2656 across 425/2179 repos (module-scope file:line placeholders from the resolver)
