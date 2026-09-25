# transformerlab/nebula-tower

- GitHub: https://github.com/transformerlab/nebula-tower
- Stars: 46 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 20 · commit: `61819660f743`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection with Depends()` | api.py#L71 | The function get_user_db uses Depends(get_async_session) to inject an AsyncSession, demonstrating FastAPI's native DI system where dependencies are resolved via the Depends() syntax. |
| 2 | `Chained dependency providers` | api.py#L82 | get_user_manager depends on get_user_db, which itself depends on get_async_session, forming a chain of dependency providers that yield resources like database sessions and user managers. |
| 3 | `Route-level dependency injection` | api.py#L160 | The app.include_router calls use dependencies=[Depends(current_superuser)] to enforce authentication checks, showing DI applied at the route level for access control. |
| 4 | `Async context managers with yield` | api.py#L67 | get_async_session is an async generator function using yield to provide an AsyncSession, a common pattern in FastAPI for managing async resources via dependencies. |

## Pass 2 — reconcile with inventory of transformerlab/nebula-tower

_Presented fingerprints:_ `C1|BARE|PARAM`, `C1|BARE|SIG`, `C4|USED`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | The code at api.py:L160, L165, L170 shows explicit use of Depends(current_superuser) in route definitions, which matches the 'known' label for parameter injection. | api.py#L160 |
| `C1|BARE|SIG` | true | **no (overturn)** | The code at api.py:L71 (Depends(get_async_session)), L82 (Depends(get_user_db)), and L220 (Depends(current_superuser)) demonstrates valid signal dependencies via Depends(), contradicting the 'false... | api.py#L71 |
| `C4|USED` | true | **no (overturn)** | The code at api.py:L67 (get_async_session used in get_user_db at L71) and L82 (get_user_db used in get_user_manager) shows actual usage, contradicting the 'false_pos' label. | api.py#L67 |
| `C4|DEF` | true | **no (overturn)** | The code at api.py:L110 defines fastapi_users and current_superuser, which are dependency providers, contradicting the 'false_pos' label. | api.py#L110 |

### Missed by inventory (2)
- `Async context managers with yield` @ api.py#L67 — The inventory missed the async generator pattern in get_async_session (yielding AsyncSession), a key DI mechanism in FastAPI.
- `Chained dependency providers` @ api.py#L82 — The inventory missed the nested dependency chain: get_user_manager → get_user_db → get_async_session, a common DI pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 9 | **known** | [api.py#L160](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L160) |
| `C1|BARE|SIG` | C1 | 7 | **false_pos** | [api.py#L71](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L71) |
| `C4|USED` | C4 | 3 | **false_pos** | [api.py#L67](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L67) |
| `C4|DEF` | C4 | 1 | **false_pos** | [api.py#L110](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L110) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 9 · corpus total: 18195 · executor: x86_64
> example: [api.py#L160](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L160)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 7 · corpus total: 83548 · executor: x86_64
> example: [api.py#L71](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L71)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 3 · corpus total: 1079 · executor: x86_64
> example: [api.py#L67](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L67)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [api.py#L110](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L110)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

