# Ocel-Labs/Osprey

- GitHub: https://github.com/Ocel-Labs/Osprey
- Stars: 38 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 1 · commit: `c95e56901ca9`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI Dependency Injection` | src/osprey/server/app.py#L11 | The code defines a lifespan manager for FastAPI but does not use FastAPI's dependency injection system (e.g., no Depends(), no injection of dependencies into routes/endpoints). The get_pipeline() f... |

## Pass 2 — reconcile with inventory of Ocel-Labs/Osprey

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code defines a FastAPI lifespan manager but does not use FastAPI's dependency injection system (no Depends() or dependency injection into routes/endpoints). The get_pipeline() function is calle... | src/osprey/server/app.py#L11 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [src/osprey/server/app.py#L11](https://github.com/Ocel-Labs/Osprey/blob/c95e56901ca992391808a158535573b69ea260e0/src/osprey/server/app.py#L11) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [src/osprey/server/app.py#L11](https://github.com/Ocel-Labs/Osprey/blob/c95e56901ca992391808a158535573b69ea260e0/src/osprey/server/app.py#L11)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

