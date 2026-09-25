# sessojunior/silo

- GitHub: https://github.com/sessojunior/silo
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 356 · commit: `97c5d85b2503`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Custom Dependencies` | apps/backend/src/silo/api/dependencies.py#L61 | The get_current_user function uses Depends(get_db) to inject a database connection, demonstrating FastAPI's dependency injection system. This is a core pattern where dependencies are resolved and i... |
| 2 | `Permission-Based Dependencies` | apps/backend/src/silo/api/dependencies.py#L86 | The require_admin function depends on get_current_user and get_db, showing a layered dependency pattern for authorization. This is a common practice to enforce access control through composed depen... |
| 3 | `Reusable Dependency Factories` | apps/backend/src/silo/api/dependencies.py#L97 | The require_permission function creates a closure that uses Depends(get_current_user) and Depends(get_db), illustrating how custom dependency factories can be built for reusable permission checks. |
| 4 | `Annotated Dependencies in Route Handlers` | apps/backend/src/silo/api/routers/ai_assistant.py#L37 | The AssistantUser type is defined with Annotated[CurrentUser, Depends(require_permission(...))], showing how FastAPI's annotated dependencies are used to type-check and inject dependencies directly... |
| 5 | `Database Connection Dependency` | apps/backend/src/silo/api/routers/auth.py#L42 | The login_password route uses Annotated[Connection, Depends(get_db)] for the db parameter, demonstrating the standard pattern of injecting database connections through dependencies. |

## Pass 2 — reconcile with inventory of sessojunior/silo

_Presented fingerprints:_ `C1|BARE|SIG`, `C3|CLASS|BARE`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true | **no (overturn)** | The code explicitly uses require_permission as a valid dependency in route handlers (e.g., contacts.py:23-34). The static instrument incorrectly labeled this as false_pos. | apps/backend/src/silo/api/routers/contacts.py#L23 |
| `C3|CLASS|BARE` | false_pos | yes | The code in dependencies.py uses standalone functions (not class methods) with Depends, matching the static instrument's label. | apps/backend/src/silo/api/dependencies.py#L61 |
| `C4|DEF` | false_pos | yes | No clear DEF-pattern dependencies are present in the code excerpts provided. | apps/backend/src/silo/api/dependencies.py#L61 |

### Missed by inventory (1)
- `Annotated[CurrentUser, Depends(...)] in route parameters` @ apps/backend/src/silo/api/routers/ai_assistant.py#L37 — The static inventory did not capture the use of Annotated dependencies for typed injection in route handlers.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 242 | **false_pos** | [apps/backend/src/silo/api/routers/contacts.py#L23](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/api/routers/contacts.py#L23) |
| `C3|CLASS|BARE` | C3 | 51 | **false_pos** | [apps/backend/src/silo/api/dependencies.py#L61](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/api/dependencies.py#L61) |
| `C4|DEF` | C4 | 31 | **false_pos** | [apps/backend/src/silo/ai/assistant_runtime.py#L134](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/ai/assistant_runtime.py#L134) |
| `C1|BARE|PARAM` | C1 | 30 | **known** | [apps/backend/src/silo/api/dependencies.py#L61](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/api/dependencies.py#L61) |
| `C4|USED` | C4 | 2 | **false_pos** | [apps/backend/src/silo/api/dependencies.py#L39](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/api/dependencies.py#L39) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 242 · corpus total: 83548 · executor: x86_64
> example: [apps/backend/src/silo/api/routers/contacts.py#L23](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/api/routers/contacts.py#L23)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 51 · corpus total: 20139 · executor: x86_64
> example: [apps/backend/src/silo/api/dependencies.py#L61](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/api/dependencies.py#L61)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|DEF` — **false_pos**
> occurrences here: 31 · corpus total: 56644 · executor: x86_64
> example: [apps/backend/src/silo/ai/assistant_runtime.py#L134](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/ai/assistant_runtime.py#L134)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 30 · corpus total: 18195 · executor: x86_64
> example: [apps/backend/src/silo/api/dependencies.py#L61](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/api/dependencies.py#L61)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [apps/backend/src/silo/api/dependencies.py#L39](https://github.com/sessojunior/silo/blob/97c5d85b250314e8eec492ef6ad36528b31993c7/apps/backend/src/silo/api/dependencies.py#L39)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

