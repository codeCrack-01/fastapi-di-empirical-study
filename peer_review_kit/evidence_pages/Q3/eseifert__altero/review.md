# eseifert/altero

- GitHub: https://github.com/eseifert/altero
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 57 · commit: `c198ef6a3aec`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=2 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Annotated and Depends` | src/altero/api/deps.py#L31 | The code defines SessionDep using Annotated[AsyncSession, Depends(get_session)], showing FastAPI's DI pattern where dependencies are created via annotated types with Depends() |
| 2 | `Chained dependency resolution` | src/altero/api/deps.py#L87 | LibraryDep depends on get_library which requires SessionDep, demonstrating layered dependencies where later dependencies can build on earlier ones |
| 3 | `Security-scoped dependencies` | src/altero/api/routes/web.py#L215 | CurrentUserDep is defined with Depends(get_current_user) and used in routes, showing authentication dependencies that enforce security boundaries |
| 4 | `Reusable dependency factories` | src/altero/api/deps.py#L71 | ApiKeyDep is created with Depends(get_api_key), showing how common authentication logic is encapsulated into reusable dependency factories |

## Pass 2 — reconcile with inventory of eseifert/altero

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`, `C3|BARE|BARE`, `C3|DOTTED|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection` | FastAPI dependency injection with Annotated and Depends | yes | The code explicitly uses Annotated[AsyncSession, Depends(get_session)] in src/altero/api/deps.py:31, demonstrating FastAPI's DI pattern. | src/altero/api/deps.py#L31 |
| `chained_dependencies` | Chained dependency resolution | yes | LibraryDep in src/altero/api/deps.py:87 depends on get_library, which requires SessionDep, showing layered dependencies. | src/altero/api/deps.py#L87 |
| `security_scoped_deps` | Security-scoped dependencies | yes | CurrentUserDep in src/altero/api/routes/web.py:215 enforces authentication boundaries via Depends(get_current_user). | src/altero/api/routes/web.py#L215 |
| `reusable_factories` | Reusable dependency factories | yes | ApiKeyDep in src/altero/api/deps.py:71 encapsulates authentication logic via Depends(get_api_key). | src/altero/api/deps.py#L71 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 26 | **false_pos** | [src/altero/app.py#L96](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/app.py#L96) |
| `C1|BARE|PARAM` | C1 | 15 | **known** | [src/altero/api/deps.py#L31](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L31) |
| `C3|CLASS|BARE` | C3 | 10 | **false_pos** | [src/altero/api/deps.py#L31](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L31) |
| `C3|ELLIPSIS|BARE` | C3 | 3 | **variant** | [src/altero/api/deps.py#L71](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L71) |
| `C3|BARE|BARE` | C3 | 1 | **variant** | [src/altero/api/deps.py#L153](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L153) |
| `C3|DOTTED|BARE` | C3 | 1 | **false_pos** | [src/altero/api/deps.py#L103](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L103) |
| `C4|USED` | C4 | 1 | **false_pos** | [src/altero/api/deps.py#L25](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L25) |

## `C4|DEF` — **false_pos**
> occurrences here: 26 · corpus total: 56644 · executor: x86_64
> example: [src/altero/app.py#L96](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/app.py#L96)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 15 · corpus total: 18195 · executor: x86_64
> example: [src/altero/api/deps.py#L31](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L31)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 10 · corpus total: 20139 · executor: x86_64
> example: [src/altero/api/deps.py#L31](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L31)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 3 · corpus total: 1113 · executor: x86_64
> example: [src/altero/api/deps.py#L71](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L71)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C3|BARE|BARE` — **variant**
> occurrences here: 1 · corpus total: 1316 · executor: x86_64
> example: [src/altero/api/deps.py#L153](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L153)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C3|DOTTED|BARE` — **false_pos**
> occurrences here: 1 · corpus total: 262 · executor: x86_64
> example: [src/altero/api/deps.py#L103](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L103)

> **evidence (model):** Annotated types (C3) require Depends(...) in the metadata, but examples show asyncpg.Connection without any dependency injection expression

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [src/altero/api/deps.py#L25](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/deps.py#L25)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

