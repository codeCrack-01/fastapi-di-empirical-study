# GregB712/Loomi-Brain

- GitHub: https://github.com/GregB712/Loomi-Brain
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 23 · commit: `6ddba737683f`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Annotated Depends` | apps/api/src/loomi_api/api/dependencies.py#L12 | DbSession is defined as Annotated[AsyncSession, Depends(get_db_session)], showing FastAPI dependency injection with Annotated and Depends. |
| 2 | `Chained Dependency Injection` | apps/api/src/loomi_api/api/dependencies.py#L28 | OwnerContext = Annotated[AuthenticatedOwner, Depends(require_owner)] creates a dependency chain where require_owner itself depends on DbSession. |
| 3 | `Dependency Injection in Route Handlers` | apps/api/src/loomi_api/api/agent_runs.py#L134 | Route handler parameters include session: DbSession and owner: OwnerContext, demonstrating injected dependencies in API endpoints. |

## Pass 2 — reconcile with inventory of GregB712/Loomi-Brain

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly uses FastAPI's `Depends` for dependency injection (e.g., `DbSession = Annotated[AsyncSession, Depends(get_db_session)]` in dependencies.py:12). The static label 'false_pos' is in... | apps/api/src/loomi_api/api/dependencies.py#L12 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses `Annotated` with `Depends` for parameterized dependencies (e.g., `DbSession = Annotated[AsyncSession, Depends(...)]`). The label 'known' is accurate. | apps/api/src/loomi_api/api/dependencies.py#L12 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code uses `Annotated` with `Depends` for class-based dependencies (e.g., `OwnerContext = Annotated[AuthenticatedOwner, Depends(...)]`). The static label 'false_pos' is incorrect. | apps/api/src/loomi_api/api/dependencies.py#L28 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db_session` function is correctly used as a dependency (e.g., in dependencies.py:12). The static label 'false_pos' is incorrect. | apps/api/src/loomi_api/db/session.py#L30 |

### Missed by inventory (2)
- `Chained dependency injection (e.g., `OwnerContext` depends on `require_owner`, which depends on `DbSession`)` @ apps/api/src/loomi_api/api/dependencies.py#L28 — The inventory did not capture the chained dependency pattern where `OwnerContext` depends on `require_owner`, which itself depends on `DbSession`.
- `Dependency injection in route handlers (e.g., `session: DbSession`, `owner: OwnerContext`)` @ apps/api/src/loomi_api/api/agent_runs.py#L134 — The inventory missed the use of injected dependencies in route handlers, such as `session: DbSession` and `owner: OwnerContext`.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 16 | **false_pos** | [apps/api/src/loomi_api/api/agent_runs.py#L134](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/api/agent_runs.py#L134) |
| `C1|BARE|PARAM` | C1 | 3 | **known** | [apps/api/src/loomi_api/api/dependencies.py#L12](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/api/dependencies.py#L12) |
| `C3|CLASS|BARE` | C3 | 3 | **false_pos** | [apps/api/src/loomi_api/api/dependencies.py#L12](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/api/dependencies.py#L12) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/api/src/loomi_api/db/session.py#L30](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/db/session.py#L30) |

## `C4|DEF` — **false_pos**
> occurrences here: 16 · corpus total: 56644 · executor: x86_64
> example: [apps/api/src/loomi_api/api/agent_runs.py#L134](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/api/agent_runs.py#L134)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 3 · corpus total: 18195 · executor: x86_64
> example: [apps/api/src/loomi_api/api/dependencies.py#L12](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/api/dependencies.py#L12)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 3 · corpus total: 20139 · executor: x86_64
> example: [apps/api/src/loomi_api/api/dependencies.py#L12](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/api/dependencies.py#L12)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/api/src/loomi_api/db/session.py#L30](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/db/session.py#L30)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

