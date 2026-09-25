# Joulenap/joulenap

- GitHub: https://github.com/Joulenap/joulenap
- Stars: 44 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 97 · commit: `5bba11d71849`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection` | backend/app/api/devices.py#L143 | The code uses FastAPI's `Depends()` to inject dependencies like `ConfigStore` and `Scheduler` into route handlers. This is a clear example of FastAPI's built-in DI pattern, where dependencies are r... |
| 2 | `FastAPI Dependency Injection` | backend/app/api/guests.py#L44 | Similar to the devices module, this file uses `Depends(get_job_service)` and `Depends(get_session)` to inject dependencies. This reinforces the DI pattern across the codebase, ensuring that route h... |
| 3 | `FastAPI Dependency Injection` | backend/app/api/logs.py#L21 | The `get_logs` function uses `Depends(get_session)` to inject a database session. This is another instance of FastAPI's DI pattern, where the framework manages the lifecycle of the session, allowin... |

## Pass 2 — reconcile with inventory of Joulenap/joulenap

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection` | FastAPI's built-in dependency injection pattern | yes | Multiple route handlers use `Depends()` to inject dependencies like `ConfigStore`, `Scheduler`, and `JobService`, aligning with FastAPI's DI framework. | backend/app/api/devices.py#L143 |
| `fastapi_dependency_injection` | FastAPI's built-in dependency injection pattern | yes | The `list_guests` route uses `Depends(get_job_service)` and `Depends(get_session)`, demonstrating consistent DI usage across the codebase. | backend/app/api/guests.py#L44 |
| `fastapi_dependency_injection` | FastAPI's built-in dependency injection pattern | yes | The `get_logs` route uses `Depends(get_session)`, further confirming DI is used for database session management. | backend/app/api/logs.py#L21 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 67 | **false_pos** | [backend/app/api/auth.py#L46](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/api/auth.py#L46) |
| `C4|DEF` | C4 | 17 | **false_pos** | [backend/app/db/base.py#L103](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/db/base.py#L103) |
| `C1|BARE|PARAM` | C1 | 12 | **known** | [backend/app/api/config.py#L30](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/api/config.py#L30) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/base.py#L117](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/db/base.py#L117) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 67 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/auth.py#L46](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/api/auth.py#L46)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 17 · corpus total: 56644 · executor: x86_64
> example: [backend/app/db/base.py#L103](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/db/base.py#L103)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 12 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/config.py#L30](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/api/config.py#L30)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/base.py#L117](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/db/base.py#L117)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

