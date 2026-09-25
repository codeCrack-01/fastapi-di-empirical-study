# prdariomarques-ship-it/ship-it

- GitHub: https://github.com/prdariomarques-ship-it/ship-it
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 132 · commit: `08958f1eda44`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=1 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Depends()` | backend/admin/router.py#L41 | The router is configured with dependencies=[Depends(require_admin)] to enforce admin access. This is a core FastAPI DI pattern for route-level authorization. |
| 2 | `Database Session Injection via Annotated` | backend/admin/router.py#L41 | DbSession is defined as Annotated[AsyncSession, Depends(get_db)], using FastAPI's Annotated type with Depends() to inject database sessions into route handlers. |
| 3 | `Custom Authentication Dependency` | backend/auth/dependencies.py#L18 | get_current_user is defined as an async dependency using Depends(bearer_scheme) and Depends(get_db), demonstrating a custom authentication DI chain. |
| 4 | `Permission Dependency Factory` | backend/auth/permissions.py#L12 | require_roles() returns a checker function with Depends(get_current_user), showing DI-based permission control. |
| 5 | `Service Dependency Injection` | backend/auth/router.py#L40 | Service is defined as Annotated[AuthService, Depends(get_auth_service)], illustrating injection of custom service classes. |
| 6 | `Reused Admin Dependency` | backend/gcalendar/router.py#L58 | The /connect endpoint uses dependencies=[Depends(require_admin)], showing the same admin permission dependency is reused across multiple routers. |

## Pass 2 — reconcile with inventory of prdariomarques-ship-it/ship-it

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`, `C3|ELLIPSIS|BARE`, `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | The code explicitly uses Depends(require_admin) in route definitions (e.g., dependencies=[Depends(require_admin)]) which matches the canonical pattern. | backend/admin/router.py#L41 |
| `C1|BARE|PARAM` | known | yes | DbSession is defined as Annotated[AsyncSession, Depends(get_db)] in multiple files, matching the canonical parameter injection pattern. | backend/admin/router.py#L41 |
| `C4|DEF` | false_pos | yes | No explicit contradictions found in the provided code excerpts; the static inventory's label may be correct. | backend/tests/conftest.py#L34 |
| `C3|ELLIPSIS|BARE` | variant | yes | The code uses standard Depends() syntax without ellipsis; the static inventory's variant label may be a misclassification. | backend/auth/dependencies.py#L18 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code uses Depends(get_current_user) in a permission checker function, which is a valid signal-based DI usage. | backend/auth/permissions.py#L12 |
| `C4|USED` | false_pos | yes | No explicit contradictions found in the provided code excerpts; the static inventory's label may be correct. | backend/database/session.py#L25 |

### Missed by inventory (2)
- `Reused admin permission dependency across routers` @ backend/gcalendar/router.py#L58 — The static inventory did not capture the cross-router reuse of Depends(require_admin) as a canonical pattern.
- `Service class injection with Annotated` @ backend/auth/router.py#L40 — The static inventory missed the Service = Annotated[AuthService, Depends(get_auth_service)] pattern as a canonical DI usage.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 51 | **false_pos** | [backend/admin/router.py#L44](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/admin/router.py#L44) |
| `C1|BARE|PARAM` | C1 | 50 | **known** | [backend/admin/router.py#L41](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/admin/router.py#L41) |
| `C4|DEF` | C4 | 27 | **false_pos** | [backend/main.py#L108](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/main.py#L108) |
| `C3|ELLIPSIS|BARE` | C3 | 2 | **variant** | [backend/auth/dependencies.py#L18](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/auth/dependencies.py#L18) |
| `C1|BARE|SIG` | C1 | 1 | **false_pos** | [backend/auth/permissions.py#L12](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/auth/permissions.py#L12) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database/session.py#L25](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/database/session.py#L25) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 51 · corpus total: 20139 · executor: x86_64
> example: [backend/admin/router.py#L44](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/admin/router.py#L44)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 50 · corpus total: 18195 · executor: x86_64
> example: [backend/admin/router.py#L41](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/admin/router.py#L41)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 27 · corpus total: 56644 · executor: x86_64
> example: [backend/main.py#L108](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/main.py#L108)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 2 · corpus total: 1113 · executor: x86_64
> example: [backend/auth/dependencies.py#L18](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/auth/dependencies.py#L18)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 1 · corpus total: 83548 · executor: x86_64
> example: [backend/auth/permissions.py#L12](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/auth/permissions.py#L12)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database/session.py#L25](https://github.com/prdariomarques-ship-it/ship-it/blob/08958f1eda440c19b2595441e2c2cfee03b59037/backend/database/session.py#L25)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

