# mayldute/tour-pass-api

- GitHub: https://github.com/mayldute/tour-pass-api
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 9 · commit: `3d15b8a36866`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Annotated Dependency Injection` | tourpass/api/dependencies.py#L10 | Defines DatabaseSession as Annotated[Session, Depends(get_db)] to inject database sessions via FastAPI's dependency system. This creates a reusable dependency that can be injected into routes or ot... |
| 2 | `Chained Dependency Injection` | tourpass/api/dependencies.py#L17 | get_pass_service depends on DatabaseSession (injected via get_db) to create a PassService, which is then wrapped in another Annotated dependency PassServiceDependency. This shows layered dependency... |
| 3 | `Test Dependency Overriding` | tests/conftest.py#L46 | Overrides get_db in tests using app.dependency_overrides to inject a test database session (from the db fixture), demonstrating how FastAPI dependencies can be mocked in testing. |

## Pass 2 — reconcile with inventory of mayldute/tour-pass-api

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code in tests/conftest.py demonstrates valid test dependency overriding using app.dependency_overrides, which is a legitimate use of FastAPI's DI system in testing. | tests/conftest.py#L46 |
| `C1|BARE|PARAM` | known | yes | The Annotated[Session, Depends(get_db)] pattern in tourpass/api/dependencies.py is a standard FastAPI dependency injection setup for parameterized dependencies. | tourpass/api/dependencies.py#L10 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code does not show a class-level bare dependency; it shows Annotated type usage for dependency injection, not a class being used as a bare dependency. | tourpass/api/dependencies.py#L10 |
| `C4|USED` | true_pos | **no (overturn)** | The get_db() function in tourpass/db/session.py is a standard FastAPI dependency that provides database sessions, which is a valid use of DI. | tourpass/db/session.py#L29 |

### Missed by inventory (2)
- `Chained Dependency Injection (PassServiceDependency depends on get_pass_service which depends on get_db)` @ tourpass/api/dependencies.py#L17 — The layered dependency injection pattern (PassServiceDependency → get_pass_service → get_db) was not captured in the fingerprint inventory.
- `Test Dependency Overriding (app.dependency_overrides in tests/conftest.py)` @ tests/conftest.py#L46 — The test-specific dependency overriding technique was not recognized as a canonical DI pattern in the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [tests/conftest.py#L28](https://github.com/mayldute/tour-pass-api/blob/3d15b8a36866677a491aacb9628223f5a621007e/tests/conftest.py#L28) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [tourpass/api/dependencies.py#L10](https://github.com/mayldute/tour-pass-api/blob/3d15b8a36866677a491aacb9628223f5a621007e/tourpass/api/dependencies.py#L10) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [tourpass/api/dependencies.py#L10](https://github.com/mayldute/tour-pass-api/blob/3d15b8a36866677a491aacb9628223f5a621007e/tourpass/api/dependencies.py#L10) |
| `C4|USED` | C4 | 1 | **false_pos** | [tourpass/db/session.py#L29](https://github.com/mayldute/tour-pass-api/blob/3d15b8a36866677a491aacb9628223f5a621007e/tourpass/db/session.py#L29) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [tests/conftest.py#L28](https://github.com/mayldute/tour-pass-api/blob/3d15b8a36866677a491aacb9628223f5a621007e/tests/conftest.py#L28)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [tourpass/api/dependencies.py#L10](https://github.com/mayldute/tour-pass-api/blob/3d15b8a36866677a491aacb9628223f5a621007e/tourpass/api/dependencies.py#L10)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [tourpass/api/dependencies.py#L10](https://github.com/mayldute/tour-pass-api/blob/3d15b8a36866677a491aacb9628223f5a621007e/tourpass/api/dependencies.py#L10)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [tourpass/db/session.py#L29](https://github.com/mayldute/tour-pass-api/blob/3d15b8a36866677a491aacb9628223f5a621007e/tourpass/db/session.py#L29)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

