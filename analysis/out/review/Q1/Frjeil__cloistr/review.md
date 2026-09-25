# Frjeil/cloistr

- GitHub: https://github.com/Frjeil/cloistr
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `647f569b6c56`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection Pattern Found` | backend/app/main.py#L14 | The code uses FastAPI's lifespan context manager for lifecycle management (connect_mongodb, start_scheduler, close_mongodb, stop_scheduler), but does not employ any FastAPI dependency injection con... |

## Pass 2 — reconcile with inventory of Frjeil/cloistr

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code uses FastAPI's lifespan context manager for lifecycle management (connect_mongodb, start_scheduler, close_mongodb, stop_scheduler), but contains no FastAPI dependency injection constructs ... | backend/app/main.py#L14 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/main.py#L14](https://github.com/Frjeil/cloistr/blob/647f569b6c564ba10d34f87fc615901f0ff0491c/backend/app/main.py#L14) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L14](https://github.com/Frjeil/cloistr/blob/647f569b6c564ba10d34f87fc615901f0ff0491c/backend/app/main.py#L14)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

