# Git-me-Harish/Mentora

- GitHub: https://github.com/Git-me-Harish/Mentora
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 123 · commit: `8d5115980c43`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=1 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Centralized Dependency Injection with Annotated` | ai_service/routers/auth.py#L850 | The code uses Depends(get_db) and Depends(get_redis) in route parameters, demonstrating FastAPI's dependency injection pattern. These dependencies are defined in ai_service/dependencies.py and reus... |
| 2 | `Reusable Dependency Aliases` | ai_service/dependencies.py#L8 | Type aliases like CurrentUser = Annotated[dict, Depends(get_current_user)] are defined to encapsulate common dependencies, enabling consistent injection across routes without repeating Depends() ca... |
| 3 | `Authentication Dependency Chain` | ai_service/dependencies.py#L2 | get_current_user combines Depends(security) and Depends(get_db) to create a layered authentication flow, showing complex dependency composition. |

## Pass 2 — reconcile with inventory of Git-me-Harish/Mentora

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|DOTTED|BARE`, `C3|BARE|BARE`

### Missed by inventory (4)
- `duplicate code block in mfa_verify` @ ai_service/routers/auth.py#L779 — Identical code block appears twice in the same function, likely a copy-paste error
- `undefined variable 'secret' in mfa_setup` @ ai_service/routers/auth.py#L778 — The 'secret' variable is used in the return statement but not defined in the function scope
- `incomplete error handling in mfa_disable` @ ai_service/routers/auth.py#L810 — The code raises HTTPException but does not handle potential exceptions from database operations
- `duplicate code in mfa_status` @ ai_service/routers/auth.py#L835 — The same code block appears in two different functions without clear separation

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 95 | **false_pos** | [ai_service/dependencies.py#L46](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L46) |
| `C4|DEF` | C4 | 17 | **false_pos** | [ai_service/dependencies.py#L24](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L24) |
| `C1|BARE|PARAM` | C1 | 5 | **known** | [ai_service/dependencies.py#L45](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L45) |
| `C3|CLASS|BARE` | C3 | 3 | **false_pos** | [ai_service/dependencies.py#L45](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L45) |
| `C3|DOTTED|BARE` | C3 | 2 | **false_pos** | [ai_service/dependencies.py#L81](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L81) |
| `C3|BARE|BARE` | C3 | 1 | **variant** | [ai_service/dependencies.py#L80](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L80) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 95 · corpus total: 83548 · executor: x86_64
> example: [ai_service/dependencies.py#L46](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L46)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 17 · corpus total: 56644 · executor: x86_64
> example: [ai_service/dependencies.py#L24](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L24)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 5 · corpus total: 18195 · executor: x86_64
> example: [ai_service/dependencies.py#L45](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L45)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 3 · corpus total: 20139 · executor: x86_64
> example: [ai_service/dependencies.py#L45](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L45)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|DOTTED|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 262 · executor: x86_64
> example: [ai_service/dependencies.py#L81](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L81)

> **evidence (model):** Annotated types (C3) require Depends(...) in the metadata, but examples show asyncpg.Connection without any dependency injection expression

## `C3|BARE|BARE` — **variant**
> occurrences here: 1 · corpus total: 1316 · executor: x86_64
> example: [ai_service/dependencies.py#L80](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L80)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

