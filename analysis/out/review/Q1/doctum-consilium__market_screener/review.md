# doctum-consilium/market_screener

- GitHub: https://github.com/doctum-consilium/market_screener
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 16 · commit: `ec2457910a73`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | backend/app/routes.py#L29 | The route handler uses `db: AsyncSession = Depends(get_db)` to inject a database session. This is FastAPI's standard DI pattern where `get_db` is a dependency provider function defined in `database... |
| 2 | `Centralized dependency provider` | backend/app/database.py#L43 | The `get_db()` async generator function is defined here, yielding `AsyncSession` instances. It is used as the source of database sessions across multiple routes via `Depends(get_db)`. |
| 3 | `Repeated DI usage across routes` | backend/app/routes.py#L68 | Multiple route handlers (e.g., `/screen_quick`, `/filters`, `/ai/analyze`) use `Depends(get_db)` to inject the same database dependency, showing consistent DI pattern application. |

## Pass 2 — reconcile with inventory of doctum-consilium/market_screener

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's DI via Depends(get_db) in route handlers (e.g., /screen, /filters, /ai/analyze). The static label incorrectly marked this as a false positive. | backend/app/routes.py#L29 |
| `C4|DEF` | true_pos | **no (overturn)** | The code in main.py defines a proper lifespan handler for FastAPI, which is part of the application's DI setup. The static label incorrectly marked this as a false positive. | backend/app/main.py#L29 |
| `C4|USED` | true_pos | **no (overturn)** | The database.py file correctly defines get_db() as an async generator providing database sessions via FastAPI's dependency injection. The static label incorrectly marked this as a false positive. | backend/app/database.py#L43 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 14 | **false_pos** | [backend/app/routes.py#L29](https://github.com/doctum-consilium/market_screener/blob/ec2457910a73a1a32080f10c16f8d4f48f3aaa75/backend/app/routes.py#L29) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/main.py#L29](https://github.com/doctum-consilium/market_screener/blob/ec2457910a73a1a32080f10c16f8d4f48f3aaa75/backend/app/main.py#L29) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/database.py#L43](https://github.com/doctum-consilium/market_screener/blob/ec2457910a73a1a32080f10c16f8d4f48f3aaa75/backend/app/database.py#L43) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 14 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routes.py#L29](https://github.com/doctum-consilium/market_screener/blob/ec2457910a73a1a32080f10c16f8d4f48f3aaa75/backend/app/routes.py#L29)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L29](https://github.com/doctum-consilium/market_screener/blob/ec2457910a73a1a32080f10c16f8d4f48f3aaa75/backend/app/main.py#L29)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database.py#L43](https://github.com/doctum-consilium/market_screener/blob/ec2457910a73a1a32080f10c16f8d4f48f3aaa75/backend/app/database.py#L43)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

