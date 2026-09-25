# gmlrep/tasker

- GitHub: https://github.com/gmlrep/tasker
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 40 · commit: `ef99e4bdc591`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=2 known=2 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Custom Container with Provide and inject decorator` | app/api/v1/endpoints/auth.py#L22 | The code uses @inject decorator and Depends(Provide[Container.auth_service]) to inject AuthService. This shows a custom DI setup where Container provides services explicitly. |
| 2 | `Annotated Dependencies with Provide` | app/api/v1/endpoints/tasks.py#L22 | The TaskService is injected via Annotated[TaskService, Depends(Provide[Container.task_service])], demonstrating explicit dependency resolution through a container. |
| 3 | `Shared Container Usage` | app/core/dependencies.py#L20 | CurrentUserId is defined using Depends(get_current_user_id), showing a mix of standard FastAPI dependencies and container-based injection elsewhere in the codebase. |

## Pass 2 — reconcile with inventory of gmlrep/tasker

_Presented fingerprints:_ `C3|CLASS|ELLIPSIS`, `C1|ELLIPSIS|PARAM`, `C3|CLASS|EMPTY`, `C4|DEF`, `C1|EMPTY|PARAM`, `C1|BARE|PARAM`, `C3|BARE|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|ELLIPSIS` | known | yes | The code uses ellipsis in Annotated type hints for parameters (e.g., param: Annotated[SUserSignUp, Depends()]) as shown in auth.py:24 | app/api/v1/endpoints/auth.py#L24 |
| `C1|ELLIPSIS|PARAM` | false_pos | **no (overturn)** | The ellipsis in auth.py:24 is part of Annotated type hints, not a parameter ellipsis. The static instrument misclassified the type annotation as a parameter pattern. | app/api/v1/endpoints/auth.py#L24 |
| `C3|CLASS|EMPTY` | false_pos | **no (overturn)** | The 'empty' lines in auth.py:22-24 are function parameter declarations, not empty classes. The static instrument incorrectly labeled these as empty class patterns. | app/api/v1/endpoints/auth.py#L22 |
| `C4|DEF` | false_pos | **no (overturn)** | The code in database.py:36 defines a class with async methods (e.g., @asynccontextmanager), which is a valid DI pattern. The static instrument incorrectly flagged this as a false positive. | app/core/database.py#L36 |
| `C1|EMPTY|PARAM` | variant | **no (overturn)** | The parameters in auth.py:22-24 are explicitly named (e.g., 'param', 'request'), not empty. The static instrument misclassified these as empty parameters. | app/api/v1/endpoints/auth.py#L22 |
| `C1|BARE|PARAM` | known | yes | The code in dependencies.py:20 uses bare Depends() without Annotated (CurrentUserId = Annotated[int, Depends(...)]), matching the 'BARE|PARAM' pattern. | app/core/dependencies.py#L20 |
| `C3|BARE|BARE` | variant | yes | The code in dependencies.py:20 uses a bare Depends() in Annotated (CurrentUserId = Annotated[int, Depends(...)]), which is a variant of the BARE pattern. | app/core/dependencies.py#L20 |

### Missed by inventory (3)
- `Provide[Container.service] injection syntax` @ app/api/v1/endpoints/auth.py#L24 — The inventory did not capture the explicit use of Provide[Container.auth_service] in Annotated dependencies, which is a key DI pattern in this repo.
- `Container-based dependency resolution with @inject` @ app/api/v1/endpoints/auth.py#L22 — The inventory missed the use of @inject decorator combined with Provide[Container.service] for service injection.
- `Custom Annotated dependencies with Depends()` @ app/api/v1/endpoints/tasks.py#L22 — The inventory did not recognize the Annotated[TaskService, Depends(Provide[Container.task_service])] pattern as a distinct DI variant.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|ELLIPSIS` | C3 | 16 | **known** | [app/api/v1/endpoints/auth.py#L24](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/api/v1/endpoints/auth.py#L24) |
| `C1|ELLIPSIS|PARAM` | C1 | 8 | **false_pos** | [app/api/v1/endpoints/auth.py#L24](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/api/v1/endpoints/auth.py#L24) |
| `C3|CLASS|EMPTY` | C3 | 6 | **false_pos** | [app/api/v1/endpoints/auth.py#L22](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/api/v1/endpoints/auth.py#L22) |
| `C4|DEF` | C4 | 5 | **false_pos** | [app/core/database.py#L36](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/core/database.py#L36) |
| `C1|EMPTY|PARAM` | C1 | 3 | **variant** | [app/api/v1/endpoints/auth.py#L22](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/api/v1/endpoints/auth.py#L22) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [app/core/dependencies.py#L20](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/core/dependencies.py#L20) |
| `C3|BARE|BARE` | C3 | 1 | **variant** | [app/core/dependencies.py#L20](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/core/dependencies.py#L20) |

## `C3|CLASS|ELLIPSIS` — **known**
> occurrences here: 16 · corpus total: 477 · executor: x86_64
> example: [app/api/v1/endpoints/auth.py#L24](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/api/v1/endpoints/auth.py#L24)
> **rule:** C3

> **evidence (model):** Annotated[Type, Depends(...)] with class types (QueryBus, InterviewTemplateController) as annotated types

## `C1|ELLIPSIS|PARAM` — **false_pos**
> occurrences here: 8 · corpus total: 252 · executor: x86_64
> example: [app/api/v1/endpoints/auth.py#L24](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/api/v1/endpoints/auth.py#L24)

> **evidence (model):** The ellipsis (...) is not a valid FastAPI dependency construct; it appears as a placeholder or incomplete code rather than an actual dependency injection usage.

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 6 · corpus total: 89 · executor: x86_64
> example: [app/api/v1/endpoints/auth.py#L22](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/api/v1/endpoints/auth.py#L22)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [app/core/database.py#L36](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/core/database.py#L36)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 3 · corpus total: 45 · executor: x86_64
> example: [app/api/v1/endpoints/auth.py#L22](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/api/v1/endpoints/auth.py#L22)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [app/core/dependencies.py#L20](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/core/dependencies.py#L20)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|BARE|BARE` — **variant**
> occurrences here: 1 · corpus total: 1316 · executor: x86_64
> example: [app/core/dependencies.py#L20](https://github.com/gmlrep/tasker/blob/ef99e4bdc591b3053510147ec854e8241c0da12c/app/core/dependencies.py#L20)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

