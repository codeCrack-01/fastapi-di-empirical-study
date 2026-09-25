# erhel-czc/asco2

- GitHub: https://github.com/erhel-czc/asco2
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 23 · commit: `fa29a11a86f3`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends for database session injection` | backend/routers/associations.py#L20 | The 'session: Session = Depends(get_db)' pattern is used in multiple endpoints to inject a database session. The 'get_db' function is defined in 'backend/db.py' and yields a Session object via a ge... |
| 2 | `FastAPI Depends for user authentication` | backend/routers/associations.py#L105 | The 'current_user: User = Depends(get_current_user)' pattern is used to inject the authenticated user into endpoints. The 'get_current_user' function is imported from 'backend/routers/auth.py' and ... |
| 3 | `Generator-based dependency provider` | backend/db.py#L17 | The 'get_db' function uses a generator pattern with 'yield session' to provide database sessions. This is a standard FastAPI pattern for managing database connections as dependencies. |

## Pass 2 — reconcile with inventory of erhel-czc/asco2

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The 'Depends(get_db)' pattern is correctly used for database session injection in FastAPI endpoints. The static instrument incorrectly labeled these as false positives. | backend/routers/associations.py#L20 |
| `C4|DEF` | true_pos | **no (overturn)** | The test code correctly overrides 'get_db' with a test session using 'override_get_db()', which is a valid testing pattern. The static instrument's false_pos label is incorrect. | tests/conftest.py#L33 |
| `C4|USED` | true_pos | **no (overturn)** | The 'get_db' generator in 'backend/db.py' is a standard FastAPI pattern for dependency injection. The static instrument's false_pos label is incorrect. | backend/db.py#L17 |

### Missed by inventory (1)
- `Depends(get_current_user) for authentication` @ backend/routers/associations.py#L105 — The use of 'Depends(get_current_user)' for user authentication was not captured in the fingerprint inventory but is a critical security pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 19 | **false_pos** | [backend/routers/associations.py#L20](https://github.com/erhel-czc/asco2/blob/fa29a11a86f3083a1cf83c7de7d35b0809ff7aa3/backend/routers/associations.py#L20) |
| `C4|DEF` | C4 | 3 | **false_pos** | [tests/conftest.py#L19](https://github.com/erhel-czc/asco2/blob/fa29a11a86f3083a1cf83c7de7d35b0809ff7aa3/tests/conftest.py#L19) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/db.py#L17](https://github.com/erhel-czc/asco2/blob/fa29a11a86f3083a1cf83c7de7d35b0809ff7aa3/backend/db.py#L17) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 19 · corpus total: 83548 · executor: x86_64
> example: [backend/routers/associations.py#L20](https://github.com/erhel-czc/asco2/blob/fa29a11a86f3083a1cf83c7de7d35b0809ff7aa3/backend/routers/associations.py#L20)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [tests/conftest.py#L19](https://github.com/erhel-czc/asco2/blob/fa29a11a86f3083a1cf83c7de7d35b0809ff7aa3/tests/conftest.py#L19)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/db.py#L17](https://github.com/erhel-czc/asco2/blob/fa29a11a86f3083a1cf83c7de7d35b0809ff7aa3/backend/db.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

