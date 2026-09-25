# tanvir14012/JwtAuth

- GitHub: https://github.com/tanvir14012/JwtAuth
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 39 · commit: `836c796da9fa`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI standard dependency injection with Depends()` | Python/backend/app/deps.py#L14 | The get_db function is a dependency provider that yields a database session, closed via a generator. It is used via Depends(get_db) in routes (e.g., account.py:44, profile.py:66). |
| 2 | `Chained dependencies` | Python/backend/app/deps.py#L33 | get_current_user depends on both get_current_payload (auth) and get_db (database), showing layered dependency resolution (account.py:33). |
| 3 | `Reusable auth dependencies` | Python/backend/app/deps.py#L42 | require_unlocked and require_admin are reused across routes (e.g., account.py:163, profile.py:97) to enforce business rules via Depends(). |
| 4 | `Dependency injection in route handlers` | Python/backend/app/routers/account.py#L44 | The signup route uses db: Session = Depends(get_db) to inject a database session, demonstrating standard FastAPI DI usage. |

## Pass 2 — reconcile with inventory of tanvir14012/JwtAuth

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_positive | **no (overturn)** | The code correctly implements FastAPI dependency injection for authentication (HTTPBearer) and database sessions via Depends(). The panel's 'false_pos' label incorrectly dismisses valid DI usage. | Python/backend/app/deps.py#L23 |
| `C1|BARE|SIG` | true_positive | **no (overturn)** | Chained dependencies (get_current_user depending on get_current_payload and get_db) are valid FastAPI patterns for layered authentication and database access. | Python/backend/app/deps.py#L33 |
| `C4|USED` | true_positive | **no (overturn)** | get_db is a standard FastAPI dependency provider for database sessions, correctly implemented as a generator function with proper cleanup. | Python/backend/app/deps.py#L14 |

### Missed by inventory (3)
- `Custom dependency reuse (require_unlocked/require_admin)` @ Python/backend/app/deps.py#L42 — The inventory missed reusable business rule dependencies that enforce session locking/admin checks across multiple routes (e.g., account.py:163, profile.py:97).
- `Dependency injection in route handlers` @ Python/backend/app/routers/account.py#L44 — The inventory missed explicit DI usage in route handlers (db: Session = Depends(get_db)) which is central to FastAPI's architecture.
- `Nested dependency chains` @ Python/backend/app/routers/profile.py#L66 — Complex dependency chains (e.g., update_details requiring require_unlocked, get_current_user, and get_db) were not captured in the initial fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 38 | **false_pos** | [Python/backend/app/deps.py#L23](https://github.com/tanvir14012/JwtAuth/blob/836c796da9fa11a8bfba9fb30bcc90154b84c40e/Python/backend/app/deps.py#L23) |
| `C4|USED` | C4 | 1 | **false_pos** | [Python/backend/app/deps.py#L14](https://github.com/tanvir14012/JwtAuth/blob/836c796da9fa11a8bfba9fb30bcc90154b84c40e/Python/backend/app/deps.py#L14) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 38 · corpus total: 83548 · executor: x86_64
> example: [Python/backend/app/deps.py#L23](https://github.com/tanvir14012/JwtAuth/blob/836c796da9fa11a8bfba9fb30bcc90154b84c40e/Python/backend/app/deps.py#L23)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [Python/backend/app/deps.py#L14](https://github.com/tanvir14012/JwtAuth/blob/836c796da9fa11a8bfba9fb30bcc90154b84c40e/Python/backend/app/deps.py#L14)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

