# gradoslovar/la-vie-en-rose

- GitHub: https://github.com/gradoslovar/la-vie-en-rose
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 3 · commit: `5d198860f053`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Async context manager for dependency provision` | backend/app/core/db.py#L11 | The get_session() function uses asynccontextmanager to yield database sessions, which is a common pattern for providing dependencies in FastAPI via async context managers. |
| 2 | `Lifespan hook for background task management` | backend/app/main.py#L16 | The lifespan() function uses @asynccontextmanager to manage background worker tasks, which is part of FastAPI's application lifecycle management rather than traditional dependency injection. |
| 3 | `Test-specific dependency setup` | backend/tests/conftest.py#L28 | The db() fixture provides a database connection for tests using asynccontextmanager, showing a test-specific pattern for dependency management not tied to FastAPI's DI system. |

## Pass 2 — reconcile with inventory of gradoslovar/la-vie-en-rose

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true | **no (overturn)** | The get_session() function in db.py:11 is a canonical DI pattern using async context managers to provide database sessions in FastAPI, which aligns with C4|DEF's structural fingerprint. | backend/app/core/db.py#L11 |
| `C4|DEF` | false_pos | yes | The lifespan() function in main.py:16 is FastAPI's lifecycle management, not traditional DI, matching the false_pos label. | backend/app/main.py#L16 |
| `C4|DEF` | false_pos | yes | The db() fixture in conftest.py:28 is test-specific setup, not part of FastAPI's DI system, matching the false_pos label. | backend/tests/conftest.py#L28 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 3 | **false_pos** | [backend/app/core/db.py#L11](https://github.com/gradoslovar/la-vie-en-rose/blob/5d198860f053d48584a7ab03b32102cacec4ac4c/backend/app/core/db.py#L11) |

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [backend/app/core/db.py#L11](https://github.com/gradoslovar/la-vie-en-rose/blob/5d198860f053d48584a7ab03b32102cacec4ac4c/backend/app/core/db.py#L11)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

