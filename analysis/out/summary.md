# Extraction summary

- Sample: 100 of pool 351 (random, seed=42)
- Reports loaded: 100

## RQ1 — construct prevalence (top rows)

| Construct | Repos | % | Total calls | Median (users) |
|---|---|---|---|---|
| Depends | 75 | 75.0% | 3779 | 17 |
| Security | 12 | 12.0% | 26 | 1.0 |
| Annotated dependency | 24 | 24.0% | 830 | 7.5 |
| Generator/yield dependency | 37 | 37.0% | 43 | 1 |
| Router-level dependency | 17 | 17.0% | 90 | 4 |
| App-level dependency | 2 | 2.0% | 2 | 1.0 |
| Dependency override | 1 | 1.0% | 1 | 1 |
| Callable class dependency | 2 | 2.0% | 3 | 1.5 |
| Dynamic framework wrappers | 82 | 82.0% | 5706 |  |

**Zero-DI cohort:** 25 repos (25.0%) use no Depends/Security/Annotated at all.

## RQ4 — dependency-graph complexity (repos with non-empty graphs)

- Graph-bearing repos: 71 / 100
- Nodes: median 24, IQR (9.0, 53.0), max 259
- Max depth: median 2, max 5
- Unresolved %: median 0.0
