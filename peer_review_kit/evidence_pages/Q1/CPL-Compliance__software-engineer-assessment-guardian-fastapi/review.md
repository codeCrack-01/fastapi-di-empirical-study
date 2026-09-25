# CPL-Compliance/software-engineer-assessment-guardian-fastapi

- GitHub: https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 7 · commit: `557d2be35658`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Annotated and Depends` | src/db/session.py#L18 | The code defines SessionDep using Annotated[AsyncSession, Depends(get_session)], creating a typed dependency that injects a database session via the get_session async generator function. |
| 2 | `Test-specific dependency overriding` | tests/conftest.py#L34 | The test fixture overrides the get_session dependency using app.dependency_overrides, demonstrating FastAPI's ability to swap dependencies for testing with a mock session. |

## Pass 2 — reconcile with inventory of CPL-Compliance/software-engineer-assessment-guardian-fastapi

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The test fixture explicitly overrides a dependency using app.dependency_overrides, which is a valid FastAPI DI usage pattern. | tests/conftest.py#L34 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses Annotated[AsyncSession, Depends(...)] to define a typed dependency parameter. | src/db/session.py#L18 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code defines a class-level dependency using Annotated with Depends, which is a valid FastAPI DI pattern. | src/db/session.py#L18 |
| `C4|USED` | true_pos | **no (overturn)** | The code uses Annotated[AsyncSession, Depends(...)] to create a dependency that is actively used in route handlers. | src/db/session.py#L13 |

### Missed by inventory (1)
- `Test-specific dependency overriding` @ tests/conftest.py#L34 — The test fixture demonstrates a valid FastAPI DI usage pattern (dependency overriding) that was not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [main.py#L11](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/main.py#L11) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [src/db/session.py#L18](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/src/db/session.py#L18) |
| `C3|CLASS|BARE` | C3 | 1 | **false_pos** | [src/db/session.py#L18](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/src/db/session.py#L18) |
| `C4|USED` | C4 | 1 | **false_pos** | [src/db/session.py#L13](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/src/db/session.py#L13) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [main.py#L11](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/main.py#L11)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [src/db/session.py#L18](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/src/db/session.py#L18)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 1 · corpus total: 20139 · executor: x86_64
> example: [src/db/session.py#L18](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/src/db/session.py#L18)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [src/db/session.py#L13](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/src/db/session.py#L13)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

