# Extraction summary

- Sample: 351 of pool 351 (full-corpus census (not a sample))
- Reports loaded: 351

## RQ1 — construct prevalence (top rows)

| Construct | Repos | % | Total calls | Median (users) |
|---|---|---|---|---|
| Depends | 262 | 74.6% | 22711 | 22.0 |
| Security | 33 | 9.4% | 143 | 1 |
| Annotated dependency | 88 | 25.1% | 4688 | 8.0 |
| Generator/yield dependency | 140 | 39.9% | 192 | 1.0 |
| Router-level dependency | 46 | 13.1% | 271 | 3.0 |
| App-level dependency | 10 | 2.8% | 10 | 1.0 |
| Dependency override | 6 | 1.7% | 34 | 1.0 |
| Callable class dependency | 2 | 0.6% | 3 | 1.5 |
| Non-FastAPI Depends sources | 2 | 0.6% | 2 |  |

**Zero-DI cohort:** 88 repos (25.1%) use no Depends/Security/Annotated at all.

## RQ2 — dependency-graph complexity (clean nodes, non-empty graphs)

- Graph-bearing repos (clean): 253 / 351
- Nodes (clean): median 21, IQR (8.0, 55.5), max 1444
- Max depth: median 2, max 7
- Unresolved %: median 0.0

- Junk nodes filtered: 610 across 103/351 repos (module-scope file:line placeholders from the resolver)
