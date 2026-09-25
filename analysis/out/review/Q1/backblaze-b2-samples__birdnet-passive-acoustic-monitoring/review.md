# backblaze-b2-samples/birdnet-passive-acoustic-monitoring

- GitHub: https://github.com/backblaze-b2-samples/birdnet-passive-acoustic-monitoring
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 7 · commit: `d90ebb99fbbf`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI dependency injection detected` | services/api/main.py#L49 | The code defines a lifespan hook for FastAPI but does not use any dependency injection patterns like Depends() or custom dependency classes. The static summary confirms depends_total=0 and annotate... |
| 2 | `No FastAPI dependency injection detected` | services/api/tests/conftest.py#L8 | Test fixtures create an AsyncClient for testing but do not demonstrate FastAPI dependency injection. The static summary confirms yield_dep_total=0 and no DI-related AST nodes. |

## Pass 2 — reconcile with inventory of backblaze-b2-samples/birdnet-passive-acoustic-monitoring

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts confirm no FastAPI dependency injection patterns (e.g., Depends(), custom dependencies) are present in the cited locations. The lifespan hook in main.py:49 and test fixtures in co... | services/api/main.py#L49 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 7 | **false_pos** | [services/api/main.py#L49](https://github.com/backblaze-b2-samples/birdnet-passive-acoustic-monitoring/blob/d90ebb99fbbfbbf8056491fced98c40b2e563307/services/api/main.py#L49) |

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [services/api/main.py#L49](https://github.com/backblaze-b2-samples/birdnet-passive-acoustic-monitoring/blob/d90ebb99fbbfbbf8056491fced98c40b2e563307/services/api/main.py#L49)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

