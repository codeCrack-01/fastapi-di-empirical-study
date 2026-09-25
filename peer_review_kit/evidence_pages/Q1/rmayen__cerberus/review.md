# rmayen/cerberus

- GitHub: https://github.com/rmayen/cerberus
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 54 · commit: `53fe4b1ac02d`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends for database and authentication` | backend/app/api/auth.py#L28 | The 'login' function uses 'Depends(get_db)' to inject a database session and 'Depends(get_current_user)' for authentication, demonstrating FastAPI's dependency injection pattern. |
| 2 | `Role-based dependency injection` | backend/app/api/cases.py#L18 | The 'create_case' function uses 'Depends(require_role(...))' to enforce role-based access control, showing a custom dependency for authorization. |
| 3 | `Reused database dependency` | backend/app/api/jobs.py#L26 | Multiple routes use 'Depends(get_db)' to inject a database session, indicating a consistent pattern for database access across the application. |

## Pass 2 — reconcile with inventory of rmayen/cerberus

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's Depends() for database and authentication injection in login/refresh/logout functions. | backend/app/api/auth.py#L28 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The refresh function properly uses Depends() for dependency injection. | backend/app/api/auth.py#L38 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The logout function demonstrates valid use of Depends() for database and authentication dependencies. | backend/app/api/auth.py#L50 |

### Missed by inventory (3)
- `Role-based dependency injection` @ backend/app/api/cases.py#L18 — The create_case function uses Depends(require_role(...)) for authorization, a DI pattern not captured by the inventory.
- `Database dependency injection` @ backend/app/api/jobs.py#L26 — Multiple routes use Depends(get_db) consistently for database access, indicating a pattern missed by the inventory.
- `Custom authentication dependency` @ backend/app/deps.py#L16 — The get_current_user function uses Depends(get_db) for authentication, a DI pattern not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 50 | **false_pos** | [backend/app/api/auth.py#L28](https://github.com/rmayen/cerberus/blob/53fe4b1ac02d0468a4fc79b5830b37e95f1b049c/backend/app/api/auth.py#L28) |
| `C4|DEF` | C4 | 3 | **false_pos** | [backend/tests/conftest.py#L27](https://github.com/rmayen/cerberus/blob/53fe4b1ac02d0468a4fc79b5830b37e95f1b049c/backend/tests/conftest.py#L27) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/database.py#L32](https://github.com/rmayen/cerberus/blob/53fe4b1ac02d0468a4fc79b5830b37e95f1b049c/backend/app/database.py#L32) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 50 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/auth.py#L28](https://github.com/rmayen/cerberus/blob/53fe4b1ac02d0468a4fc79b5830b37e95f1b049c/backend/app/api/auth.py#L28)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [backend/tests/conftest.py#L27](https://github.com/rmayen/cerberus/blob/53fe4b1ac02d0468a4fc79b5830b37e95f1b049c/backend/tests/conftest.py#L27)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database.py#L32](https://github.com/rmayen/cerberus/blob/53fe4b1ac02d0468a4fc79b5830b37e95f1b049c/backend/app/database.py#L32)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

