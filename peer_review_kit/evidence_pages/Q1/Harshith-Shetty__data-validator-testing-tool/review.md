# Harshith-Shetty/data-validator-testing-tool

- GitHub: https://github.com/Harshith-Shetty/data-validator-testing-tool
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `b5b4ca41e55e`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI dependency injection usage detected` | backend/tests/test_api.py#L14 | The code shows a pytest fixture creating a TestClient for FastAPI, but there are no instances of FastAPI's dependency injection constructs like Depends(), Security(), or annotated dependencies. The... |

## Pass 2 — reconcile with inventory of Harshith-Shetty/data-validator-testing-tool

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code at the cited location does not contain FastAPI dependency injection constructs (e.g., Depends(), annotated dependencies, or yield-based dependencies), confirming the static analysis' false... | backend/tests/test_api.py#L14 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/tests/test_api.py#L14](https://github.com/Harshith-Shetty/data-validator-testing-tool/blob/b5b4ca41e55ec5f9d98819d13bfe38ca02ff84c3/backend/tests/test_api.py#L14) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/tests/test_api.py#L14](https://github.com/Harshith-Shetty/data-validator-testing-tool/blob/b5b4ca41e55ec5f9d98819d13bfe38ca02ff84c3/backend/tests/test_api.py#L14)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

