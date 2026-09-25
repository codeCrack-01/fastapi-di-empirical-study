# Extraction summary

- Sample: 327 of pool 2179 (stratified_random, seed=42)
- Reports loaded: 327

## RQ1 — construct prevalence (top rows)

| Construct | Repos | % | Total calls | Median (users) |
|---|---|---|---|---|
| Depends | 222 | 67.9% | 16768 | 24.5 |
| Security | 18 | 5.5% | 103 | 1.5 |
| Annotated dependency | 67 | 20.5% | 1539 | 9 |
| Generator/yield dependency | 116 | 35.5% | 153 | 1.0 |
| Non-FastAPI Depends sources | 3 | 0.9% | 6 |  |
| Repos using ZERO core DI constructs (no Depends/Security/Annotated) | 105 | 32.1% |  |  |

**Zero-DI cohort:** 105 repos (32.1%) use no Depends/Security/Annotated at all.

## RQ3 — dependency-graph complexity (clean nodes, non-empty graphs)

- Graph-bearing repos (clean): 215 / 327
- Nodes (clean): median 20, IQR (6.0, 50.0), max 636
- Max depth: median 2, max 7
- Unresolved %: median 0.0

- Junk nodes filtered: 560 across 76/327 repos (module-scope file:line placeholders from the resolver)
