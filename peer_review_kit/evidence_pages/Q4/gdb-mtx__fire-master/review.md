# gdb-mtx/fire-master

- GitHub: https://github.com/gdb-mtx/fire-master
- Stars: 31 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 190 · commit: `96f131a6b57b`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection via Depends()` | backend/app/api/accounts.py#L22 | The `Depends(get_current_user)` and `Depends(get_db)` are used to inject authentication and database dependencies into route handlers, which is the standard FastAPI DI pattern. |
| 2 | `Manual constructor injection of dependencies` | backend/app/api/accounts.py#L33 | The `AssetHubEngine(db)` creates an instance with the database session passed explicitly, demonstrating manual DI where dependencies are injected via constructor parameters. |
| 3 | `FastAPI built-in dependency injection via Depends()` | backend/app/api/advisor.py#L28 | The `Depends(get_current_user)` and `Depends(get_db)` are used again in the `/advisor/chat` endpoint, showing consistent use of FastAPI's DI system across the codebase. |

## Pass 2 — reconcile with inventory of gdb-mtx/fire-master

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | yes | The code correctly uses FastAPI's built-in dependency injection via Depends() for authentication and database sessions, which aligns with standard practices. | backend/app/api/accounts.py#L22 |
| `C4|DEF` | false_pos | yes | The code consistently uses FastAPI's Depends() for dependency injection, as seen in advisor.py:28 and other endpoints, confirming proper DI usage. | backend/app/api/advisor.py#L28 |
| `C4|USED` | false_pos | yes | The panel's label is assumed correct due to lack of contradictory code evidence; however, the specific line (core/database.py:16) is not provided in the excerpt, making verification incomplete. | backend/app/core/database.py#L16 |

### Missed by inventory (2)
- `Manual DI via constructor injection` @ backend/app/api/accounts.py#L33 — The code explicitly injects dependencies via constructor (e.g., AssetHubEngine(db)), which is a valid DI pattern but may not have been captured by the inventory.
- `DI in cashflow.py endpoints` @ backend/app/api/cashflow.py#L26 — The code uses Depends() for authentication and database injection in cashflow.py, but this was not mentioned in pass1 observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 179 | **false_pos** | [backend/app/api/accounts.py#L21](https://github.com/gdb-mtx/fire-master/blob/96f131a6b57bc9dede96de707164a5de7c5d7694/backend/app/api/accounts.py#L21) |
| `C4|DEF` | C4 | 10 | **false_pos** | [backend/app/advisor/manager.py#L28](https://github.com/gdb-mtx/fire-master/blob/96f131a6b57bc9dede96de707164a5de7c5d7694/backend/app/advisor/manager.py#L28) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/core/database.py#L16](https://github.com/gdb-mtx/fire-master/blob/96f131a6b57bc9dede96de707164a5de7c5d7694/backend/app/core/database.py#L16) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 179 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/accounts.py#L21](https://github.com/gdb-mtx/fire-master/blob/96f131a6b57bc9dede96de707164a5de7c5d7694/backend/app/api/accounts.py#L21)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 10 · corpus total: 56644 · executor: x86_64
> example: [backend/app/advisor/manager.py#L28](https://github.com/gdb-mtx/fire-master/blob/96f131a6b57bc9dede96de707164a5de7c5d7694/backend/app/advisor/manager.py#L28)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/core/database.py#L16](https://github.com/gdb-mtx/fire-master/blob/96f131a6b57bc9dede96de707164a5de7c5d7694/backend/app/core/database.py#L16)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

