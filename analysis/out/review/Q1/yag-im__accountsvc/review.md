# yag-im/accountsvc

- GitHub: https://github.com/yag-im/accountsvc
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 21 · commit: `e8262aa8b5fd`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Annotated Dependencies with Depends` | src/accountsvc/api/dependencies.py#L39 | The code defines SessionDep as Annotated[AsyncSession, Depends(get_db_session)], showing FastAPI's annotated dependency pattern where dependencies are explicitly declared with type hints and inject... |
| 2 | `Dependency Chaining` | src/accountsvc/api/dependencies.py#L48 | get_user_service depends on get_user_repository, which itself depends on SessionDep. This creates a layered dependency chain (db session → repository → service) typical in FastAPI applications. |
| 3 | `Test Dependency Overriding` | tests/integration/conftest.py#L99 | The test fixture overrides get_db_session with a mock using app.dependency_overrides, demonstrating FastAPI's DI testability feature where dependencies can be replaced during testing. |

## Pass 2 — reconcile with inventory of yag-im/accountsvc

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | known | **no (overturn)** | SessionDep is explicitly defined with Annotated[AsyncSession, Depends(...)], which is a valid FastAPI dependency pattern | src/accountsvc/api/dependencies.py#L39 |
| `C1|BARE|PARAM` | known | yes | Parameters like session: SessionDep correctly use annotated dependencies | src/accountsvc/api/dependencies.py#L39 |
| `C4|DEF` | known | **no (overturn)** | lifespan.py defines a dependency handler (lifespan) and conftest.py defines test-specific dependencies (engine, db_connection) | src/accountsvc/core/lifespan.py#L18 |
| `C4|USED` | known | **no (overturn)** | get_db_session is a valid dependency used throughout the codebase | src/accountsvc/api/dependencies.py#L22 |

### Missed by inventory (1)
- `Test dependency overriding with app.dependency_overrides` @ tests/integration/conftest.py#L99 — The test fixture explicitly overrides get_db_session with a mock, demonstrating FastAPI's DI testability feature

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 8 | **false_pos** | [src/accountsvc/api/dependencies.py#L39](https://github.com/yag-im/accountsvc/blob/e8262aa8b5fd2fff9e9854dad89d845e033c454c/src/accountsvc/api/dependencies.py#L39) |
| `C1|BARE|PARAM` | C1 | 6 | **known** | [src/accountsvc/api/dependencies.py#L39](https://github.com/yag-im/accountsvc/blob/e8262aa8b5fd2fff9e9854dad89d845e033c454c/src/accountsvc/api/dependencies.py#L39) |
| `C4|DEF` | C4 | 6 | **false_pos** | [src/accountsvc/core/lifespan.py#L18](https://github.com/yag-im/accountsvc/blob/e8262aa8b5fd2fff9e9854dad89d845e033c454c/src/accountsvc/core/lifespan.py#L18) |
| `C4|USED` | C4 | 1 | **false_pos** | [src/accountsvc/api/dependencies.py#L22](https://github.com/yag-im/accountsvc/blob/e8262aa8b5fd2fff9e9854dad89d845e033c454c/src/accountsvc/api/dependencies.py#L22) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 8 · corpus total: 20139 · executor: x86_64
> example: [src/accountsvc/api/dependencies.py#L39](https://github.com/yag-im/accountsvc/blob/e8262aa8b5fd2fff9e9854dad89d845e033c454c/src/accountsvc/api/dependencies.py#L39)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 6 · corpus total: 18195 · executor: x86_64
> example: [src/accountsvc/api/dependencies.py#L39](https://github.com/yag-im/accountsvc/blob/e8262aa8b5fd2fff9e9854dad89d845e033c454c/src/accountsvc/api/dependencies.py#L39)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [src/accountsvc/core/lifespan.py#L18](https://github.com/yag-im/accountsvc/blob/e8262aa8b5fd2fff9e9854dad89d845e033c454c/src/accountsvc/core/lifespan.py#L18)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [src/accountsvc/api/dependencies.py#L22](https://github.com/yag-im/accountsvc/blob/e8262aa8b5fd2fff9e9854dad89d845e033c454c/src/accountsvc/api/dependencies.py#L22)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

