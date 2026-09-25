# 7-Blocks/Kepler

- GitHub: https://github.com/7-Blocks/Kepler
- Stars: 29 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 27 · commit: `7497a93f6d82`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=1 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Database Session` | backend/api/v1/endpoints/agents.py#L46 | The parameter `db: Session = Depends(get_db)` demonstrates FastAPI's dependency injection system, where `get_db` is a dependency provider that yields a SQLAlchemy database session. This pattern is ... |
| 2 | `Database Session Lifecycle Management` | backend/database/session.py#L26 | The `get_db` function uses a generator (`yield db`) to provide a database session, ensuring proper cleanup via `db.close()` in the `finally` block. This is a standard practice in FastAPI for managi... |

## Pass 2 — reconcile with inventory of 7-Blocks/Kepler

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|EMPTY|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's dependency injection with `Depends(get_db)` in multiple endpoints (e.g., `trigger_agent_mitigation_workflow` in agents.py). This is a valid DI pattern. | backend/api/v1/endpoints/agents.py#L46 |
| `C4|DEF` | true_pos | **no (overturn)** | Test fixtures like `sqlite_db` in test_ingestion.py and test_providers.py correctly implement database session setup for testing, which is a valid DI usage. | backend/tests/test_ingestion.py#L29 |
| `C1|EMPTY|SIG` | true_pos | **no (overturn)** | The `login_for_access_token` endpoint in auth.py uses `Depends(get_db)` correctly, which is a standard DI pattern. | backend/api/v1/endpoints/auth.py#L109 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db` function in session.py is a valid DI provider for database sessions, correctly managing the session lifecycle. | backend/database/session.py#L26 |

### Missed by inventory (1)
- `FastAPI DI usage in endpoints like `get_agent_runs` and `get_agent_run_details`` @ backend/api/v1/endpoints/agents.py#L63 — The inventory may have missed additional DI instances in endpoints that use `Depends(get_db)` for database sessions.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 22 | **false_pos** | [backend/api/v1/endpoints/agents.py#L46](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/api/v1/endpoints/agents.py#L46) |
| `C4|DEF` | C4 | 3 | **false_pos** | [backend/tests/test_ingestion.py#L29](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/tests/test_ingestion.py#L29) |
| `C1|EMPTY|SIG` | C1 | 1 | **variant** | [backend/api/v1/endpoints/auth.py#L109](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/api/v1/endpoints/auth.py#L109) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database/session.py#L26](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/database/session.py#L26) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 22 · corpus total: 83548 · executor: x86_64
> example: [backend/api/v1/endpoints/agents.py#L46](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/api/v1/endpoints/agents.py#L46)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [backend/tests/test_ingestion.py#L29](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/tests/test_ingestion.py#L29)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 1 · corpus total: 254 · executor: x86_64
> example: [backend/api/v1/endpoints/auth.py#L109](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/api/v1/endpoints/auth.py#L109)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database/session.py#L26](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/database/session.py#L26)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

