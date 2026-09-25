# pafful/fastapi-app-main

- GitHub: https://github.com/pafful/fastapi-app-main
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 18 · commit: `439247f16d70`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=2 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Annotated dependencies with Depends` | backend/app/api/deps.py#L26 | SessionDep is defined as Annotated[Session, Depends(get_db)], demonstrating FastAPI's pattern of using Annotated to type-hint dependencies while injecting them via Depends(). This is used throughou... |
| 2 | `Dependency chaining` | backend/app/api/deps.py#L49 | CurrentUser is defined as Annotated[User, Depends(get_current_user)], which itself depends on SessionDep and TokenDep. This creates a layered dependency chain: get_current_user → SessionDep/TokenDe... |
| 3 | `Generator-based dependency` | backend/app/api/deps.py#L21 | get_db() is a generator function yielding Session objects, typical for FastAPI's dependency injection to manage database session lifecycles via Depends(get_db). |
| 4 | `Route-level dependency injection` | backend/app/api/routes/users.py#L34 | The /users endpoint uses dependencies=[Depends(get_current_active_superuser)], showing how route handlers explicitly declare dependencies via the Depends() function. |
| 5 | `Reused annotated dependencies` | backend/app/api/routes/login.py#L25 | login_access_token uses session: SessionDep, demonstrating reuse of the annotated SessionDep dependency across multiple route handlers. |

## Pass 2 — reconcile with inventory of pafful/fastapi-app-main

_Presented fingerprints:_ `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|CLASS|EMPTY`, `C4|DEF`, `C1|EMPTY|PARAM`, `C3|BARE|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | SessionDep and TokenDep in deps.py are annotated dependencies with Depends(), matching the BARE|PARAM pattern. | backend/app/api/deps.py#L26 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | SessionDep and TokenDep are Annotated dependencies, not classes. The static instrument incorrectly labeled them as classes. | backend/app/api/deps.py#L26 |
| `C3|CLASS|EMPTY` | false_pos | **no (overturn)** | login.py line 25 uses SessionDep (an annotated dependency), not an empty class. The label is incorrect. | backend/app/api/routes/login.py#L25 |
| `C4|DEF` | false_pos | **no (overturn)** | conftest.py line 16 defines a generator function 'db' used via Depends(), not a DEF pattern. The label is incorrect. | backend/tests/conftest.py#L16 |
| `C1|EMPTY|PARAM` | variant | yes | login.py line 25 uses session: SessionDep (a parameter with no default), matching the EMPTY|PARAM variant. | backend/app/api/routes/login.py#L25 |
| `C3|BARE|BARE` | variant | yes | deps.py line 27 defines TokenDep as Annotated[str, Depends(...)], matching the BARE|BARE variant. | backend/app/api/deps.py#L27 |
| `C4|USED` | false_pos | **no (overturn)** | deps.py line 21 defines get_db() as a generator used via Depends(), not a USED pattern. The label is incorrect. | backend/app/api/deps.py#L21 |

### Missed by inventory (2)
- `Dependency chaining (e.g., CurrentUser depends on SessionDep/TokenDep)` @ backend/app/api/deps.py#L49 — The inventory did not capture the layered dependency chain (CurrentUser → SessionDep/TokenDep → get_db/reusable_oauth2).
- `Repeated use of Annotated[Type, Depends(...)] across routes` @ backend/app/api/routes/users.py#L34 — The inventory missed the widespread reuse of annotated dependencies (e.g., SessionDep in multiple route handlers).

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 9 | **known** | [backend/app/api/deps.py#L26](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/deps.py#L26) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [backend/app/api/deps.py#L26](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/deps.py#L26) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [backend/app/api/routes/login.py#L25](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/routes/login.py#L25) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/tests/conftest.py#L16](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/tests/conftest.py#L16) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [backend/app/api/routes/login.py#L25](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/routes/login.py#L25) |
| `C3|BARE|BARE` | C3 | 1 | **variant** | [backend/app/api/deps.py#L27](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/deps.py#L27) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/api/deps.py#L21](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/deps.py#L21) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 9 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/deps.py#L26](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/deps.py#L26)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [backend/app/api/deps.py#L26](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/deps.py#L26)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [backend/app/api/routes/login.py#L25](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/routes/login.py#L25)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/tests/conftest.py#L16](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/tests/conftest.py#L16)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [backend/app/api/routes/login.py#L25](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/routes/login.py#L25)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C3|BARE|BARE` — **variant**
> occurrences here: 1 · corpus total: 1316 · executor: x86_64
> example: [backend/app/api/deps.py#L27](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/deps.py#L27)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/api/deps.py#L21](https://github.com/pafful/fastapi-app-main/blob/439247f16d70753cff265d4232a86c98192447d0/backend/app/api/deps.py#L21)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

