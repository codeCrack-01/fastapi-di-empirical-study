# BlackIQ/tgju-api

- GitHub: https://github.com/BlackIQ/tgju-api
- Stars: 12 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 1 · commit: `168d64e56f59`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Generator-based dependency provider` | dependencies/database.py#L6 | The get_db() function is a generator that yields a database session, which is a common FastAPI pattern for providing dependencies. The session is obtained via 'core.database.session()' and closed i... |

## Pass 2 — reconcile with inventory of BlackIQ/tgju-api

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly implements a generator-based dependency provider for database sessions, a standard pattern in FastAPI for managing database connections as context managers. | dependencies/database.py#L6 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [dependencies/database.py#L6](https://github.com/BlackIQ/tgju-api/blob/168d64e56f590a8ff981bae4dcb24ea6f9703102/dependencies/database.py#L6) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [dependencies/database.py#L6](https://github.com/BlackIQ/tgju-api/blob/168d64e56f590a8ff981bae4dcb24ea6f9703102/dependencies/database.py#L6)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

