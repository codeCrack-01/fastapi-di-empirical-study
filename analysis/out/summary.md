# Extraction summary

- Sample: 402 of pool 402 (full-corpus census (not a sample))
- Reports loaded: 402

## RQ1 — construct prevalence (top rows)

| Construct | Repos | % | Total calls | Median (users) |
|---|---|---|---|---|
| Depends | 303 | 75.4% | 25166 | 22 |
| Security | 42 | 10.4% | 163 | 1.0 |
| Annotated dependency | 104 | 25.9% | 5913 | 11.0 |
| Generator/yield dependency | 162 | 40.3% | 216 | 1.0 |
| Router-level dependency | 58 | 14.4% | 297 | 3.0 |
| App-level dependency | 10 | 2.5% | 10 | 1.0 |
| Dependency override | 7 | 1.7% | 35 | 1 |
| Callable class dependency | 2 | 0.5% | 3 | 1.5 |
| Non-FastAPI Depends sources | 2 | 0.5% | 2 |  |

**Zero-DI cohort:** 98 repos (24.4%) use no Depends/Security/Annotated at all.

## RQ3 — dependency-graph complexity (clean nodes, non-empty graphs)

- Graph-bearing repos (clean): 294 / 402
- Nodes (clean): median 19.5, IQR (8.0, 54.25), max 1444
- Max depth: median 2.0, max 7
- Unresolved %: median 0.0

- Junk nodes filtered: 713 across 122/402 repos (module-scope file:line placeholders from the resolver)
