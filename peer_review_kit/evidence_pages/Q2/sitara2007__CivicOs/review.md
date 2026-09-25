# sitara2007/CivicOs

- GitHub: https://github.com/sitara2007/CivicOs
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 6 · commit: `3fe5f961431a`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection` | app/api/v1/history.py#L20 | The 'Depends(get_db_session)' is used to inject an AsyncSession into the route handler, demonstrating FastAPI's dependency injection mechanism where dependencies are resolved and injected automatic... |
| 2 | `Centralized dependency provider` | app/api/deps.py#L13 | The 'get_db_session' function is defined here as a dependency provider that yields a database session, which is then used across multiple routes via 'Depends(get_db_session)'. |
| 3 | `Async generator for resource management` | app/api/deps.py#L13 | The 'get_db_session' function is an async generator that yields an AsyncSession, ensuring proper lifecycle management of database connections. |

## Pass 2 — reconcile with inventory of sitara2007/CivicOs

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's dependency injection via Depends(get_db_session) in multiple routes, confirming DI usage. | app/api/v1/history.py#L20 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code uses Depends(get_db_session) in process_document, demonstrating DI. | app/api/v1/process.py#L37 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code uses Depends(get_db_session) in poll_process, confirming DI. | app/api/v1/process.py#L106 |
| `C4|DEF` | true_pos | **no (overturn)** | get_session is a centralized dependency provider used across the app, confirming DI. | app/db/session.py#L16 |
| `C4|DEF` | true_pos | **no (overturn)** | The lifespan function in main.py uses get_settings, a dependency provider for configuration. | app/main.py#L35 |
| `C4|USED` | true_pos | **no (overturn)** | get_db_session is a centralized dependency provider used in multiple routes. | app/api/deps.py#L13 |

### Missed by inventory (2)
- `Async generator for session management` @ app/api/deps.py#L13 — The async generator pattern in get_db_session ensures proper resource lifecycle management, a key DI aspect.
- `Centralized dependency provider with async context` @ app/db/session.py#L16 — The get_session function is a centralized provider with async context management, missed by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 3 | **false_pos** | [app/api/v1/history.py#L20](https://github.com/sitara2007/CivicOs/blob/3fe5f961431a39e25704473958d30f438114dae5/app/api/v1/history.py#L20) |
| `C4|DEF` | C4 | 2 | **false_pos** | [app/db/session.py#L16](https://github.com/sitara2007/CivicOs/blob/3fe5f961431a39e25704473958d30f438114dae5/app/db/session.py#L16) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/api/deps.py#L13](https://github.com/sitara2007/CivicOs/blob/3fe5f961431a39e25704473958d30f438114dae5/app/api/deps.py#L13) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 83548 · executor: x86_64
> example: [app/api/v1/history.py#L20](https://github.com/sitara2007/CivicOs/blob/3fe5f961431a39e25704473958d30f438114dae5/app/api/v1/history.py#L20)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [app/db/session.py#L16](https://github.com/sitara2007/CivicOs/blob/3fe5f961431a39e25704473958d30f438114dae5/app/db/session.py#L16)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/api/deps.py#L13](https://github.com/sitara2007/CivicOs/blob/3fe5f961431a39e25704473958d30f438114dae5/app/api/deps.py#L13)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

