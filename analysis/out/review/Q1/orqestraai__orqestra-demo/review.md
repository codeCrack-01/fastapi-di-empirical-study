# orqestraai/orqestra-demo

- GitHub: https://github.com/orqestraai/orqestra-demo
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 18 · commit: `323ab2840e20`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=2 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Annotated and Depends` | app/app/api/deps.py#L27 | Defines SessionDep (Annotated[Session, Depends(get_db)]) and TokenDep (Annotated[str, Depends(reusable_oauth2)]) to inject database sessions and OAuth2 tokens. These are used throughout the codebas... |
| 2 | `Nested dependency resolution` | app/app/api/deps.py#L53 | CurrentUser = Annotated[User, Depends(get_current_user)] creates a dependency that itself depends on SessionDep and TokenDep, enabling layered authentication checks (e.g., get_current_active_superu... |
| 3 | `Dependency reuse in route handlers` | app/app/api/routes/users.py#L34 | Endpoints use Depends(get_current_active_superuser) and SessionDep directly, showing how dependencies are composed across multiple routes without code duplication. |

## Pass 2 — reconcile with inventory of orqestraai/orqestra-demo

_Presented fingerprints:_ `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|CLASS|EMPTY`, `C4|DEF`, `C1|EMPTY|PARAM`, `C3|BARE|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | SessionDep and TokenDep are valid annotated parameters with Depends() in deps.py | app/app/api/deps.py#L27 |
| `C3|CLASS|BARE` | false_pos | yes | SessionDep and TokenDep are Annotated types, not classes | app/app/api/deps.py#L27 |
| `C3|CLASS|EMPTY` | false_pos | yes | No empty class dependencies found at login.py:L25 (import statements) | app/app/api/routes/login.py#L25 |
| `C4|DEF` | false_pos | **no (overturn)** | db fixture in conftest.py is a valid DEF with dependency logic | app/tests/conftest.py#L16 |
| `C1|EMPTY|PARAM` | variant | **no (overturn)** | No empty parameters found at login.py:L25 (import statements) | app/app/api/routes/login.py#L25 |
| `C3|BARE|BARE` | variant | **no (overturn)** | TokenDep uses Depends(reusable_oauth2), not bare annotations | app/app/api/deps.py#L28 |
| `C4|USED` | false_pos | **no (overturn)** | get_db() is explicitly used in deps.py for dependency injection | app/app/api/deps.py#L22 |

### Missed by inventory (2)
- `Nested dependency resolution (CurrentUser depends on SessionDep/TokenDep)` @ app/app/api/deps.py#L53 — Inventory missed layered dependency patterns like CurrentUser → get_current_user → SessionDep/TokenDep
- `Dependency reuse across routes (Depends(get_current_active_superuser) in users.py/login.py)` @ app/app/api/routes/users.py#L34 — Inventory did not track cross-route dependency composition patterns

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 9 | **known** | [app/app/api/deps.py#L27](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/deps.py#L27) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [app/app/api/deps.py#L27](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/deps.py#L27) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [app/app/api/routes/login.py#L25](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/routes/login.py#L25) |
| `C4|DEF` | C4 | 2 | **false_pos** | [app/tests/conftest.py#L16](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/tests/conftest.py#L16) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [app/app/api/routes/login.py#L25](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/routes/login.py#L25) |
| `C3|BARE|BARE` | C3 | 1 | **variant** | [app/app/api/deps.py#L28](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/deps.py#L28) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/app/api/deps.py#L22](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/deps.py#L22) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 9 · corpus total: 18195 · executor: x86_64
> example: [app/app/api/deps.py#L27](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/deps.py#L27)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [app/app/api/deps.py#L27](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/deps.py#L27)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [app/app/api/routes/login.py#L25](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/routes/login.py#L25)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [app/tests/conftest.py#L16](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/tests/conftest.py#L16)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [app/app/api/routes/login.py#L25](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/routes/login.py#L25)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C3|BARE|BARE` — **variant**
> occurrences here: 1 · corpus total: 1316 · executor: x86_64
> example: [app/app/api/deps.py#L28](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/deps.py#L28)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/app/api/deps.py#L22](https://github.com/orqestraai/orqestra-demo/blob/323ab2840e20246eb0f97abbe520f03928eb0d64/app/app/api/deps.py#L22)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

