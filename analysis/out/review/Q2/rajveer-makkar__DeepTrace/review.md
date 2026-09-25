# rajveer-makkar/DeepTrace

- GitHub: https://github.com/rajveer-makkar/DeepTrace
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 13 · commit: `26ba24e54fa8`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection for database sessions` | backend/app/api/research.py#L23 | The `Depends(get_db)` pattern is used to inject an AsyncSession for database operations, as seen in `list_research` and other endpoints. |
| 2 | `Database session generator via async context manager` | backend/app/database.py#L10 | The `get_db` function uses `async with async_session()` to yield a database session, enabling dependency injection across routes. |

## Pass 2 — reconcile with inventory of rajveer-makkar/DeepTrace

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends(get_db)` pattern for database session injection, which is a canonical DI occurrence. | backend/app/api/research.py#L23 |
| `C4|DEF` | true_pos | **no (overturn)** | The `get_db` function in `database.py` is a proper DI definition that yields an async database session via `async_sessionmaker`. | backend/app/database.py#L10 |
| `C4|USED` | true_pos | **no (overturn)** | The `Depends(get_db)` pattern is used in multiple endpoints (e.g., `list_research`, `create_research`) as a canonical DI usage. | backend/app/api/research.py#L40 |

### Missed by inventory (2)
- `Multiple DI usages in research.py endpoints` @ backend/app/api/research.py#L48 — The inventory missed DI occurrences in `get_research`, `get_sources`, `get_claims`, etc., which all use `Depends(get_db)`.
- `Async DI session management` @ backend/app/database.py#L10 — The inventory did not capture the async DI pattern in `get_db` using `async with async_session()`.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 10 | **false_pos** | [backend/app/api/research.py#L23](https://github.com/rajveer-makkar/DeepTrace/blob/26ba24e54fa817ce5ac6b440ce0653d9204d01bc/backend/app/api/research.py#L23) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/app/api/research.py#L66](https://github.com/rajveer-makkar/DeepTrace/blob/26ba24e54fa817ce5ac6b440ce0653d9204d01bc/backend/app/api/research.py#L66) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/database.py#L10](https://github.com/rajveer-makkar/DeepTrace/blob/26ba24e54fa817ce5ac6b440ce0653d9204d01bc/backend/app/database.py#L10) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 10 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/research.py#L23](https://github.com/rajveer-makkar/DeepTrace/blob/26ba24e54fa817ce5ac6b440ce0653d9204d01bc/backend/app/api/research.py#L23)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/research.py#L66](https://github.com/rajveer-makkar/DeepTrace/blob/26ba24e54fa817ce5ac6b440ce0653d9204d01bc/backend/app/api/research.py#L66)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database.py#L10](https://github.com/rajveer-makkar/DeepTrace/blob/26ba24e54fa817ce5ac6b440ce0653d9204d01bc/backend/app/database.py#L10)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

