# AristaLabs/smeme

- GitHub: https://github.com/AristaLabs/smeme
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 164 · commit: `5ac62e9ff6b4`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=2 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | smeme/api/health.py#L28 | Uses `Depends(get_db)` to inject database session into `/health/db` endpoint |
| 2 | `Annotated dependency aliases` | smeme/core/dependencies.py#L48 | Defines `AsyncSessionDep = Annotated[AsyncSession, Depends(_get_db)]` and similar aliases for common dependencies |
| 3 | `User authentication injection` | smeme/auth/users.py#L24 | Injects `current_active_user` via `Depends(current_active_user)` in multiple endpoints |
| 4 | `Nested dependency chains` | smeme/auth/manager.py#L38 | Shows `get_user_db` depends on `get_db`, which is then used by `get_user_manager` |
| 5 | `Type-annotated dependencies` | smeme/decision_tree/editor/routes.py#L88 | Uses `CurrentUser = Annotated[User, Depends(current_active_user)]` for route parameters |

## Pass 2 — reconcile with inventory of AristaLabs/smeme

_Presented fingerprints:_ `C4|DEF`, `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C1|BARE|SIG`, `C1|EMPTY|SIG`, `C4|USED`, `C3|ELLIPSIS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | valid_dependency | **no (overturn)** | The code examples (e.g., smeme/api/health.py:28) show correct usage of Depends(get_db) for database injection, contradicting the static tool's false_pos label. | smeme/api/health.py#L28 |
| `C3|CLASS|BARE` | valid_dependency_alias | **no (overturn)** | Annotated dependency aliases (e.g., smeme/core/dependencies.py:48) are valid and correctly implemented, contradicting the static tool's false_pos label. | smeme/core/dependencies.py#L48 |

### Missed by inventory (2)
- `Annotated dependency aliases with Depends` @ smeme/decision_tree/editor/routes.py#L88 — The inventory did not capture the use of Annotated[User, Depends(...)] for route parameters, which is a valid pattern.
- `Nested dependency chains` @ smeme/auth/manager.py#L38 — The inventory missed the nested dependency chain (get_user_db → get_db → get_user_manager), which is a valid and common practice.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 60 | **false_pos** | [scripts/check_no_qnr_product_refs.py#L141](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/scripts/check_no_qnr_product_refs.py#L141) |
| `C3|CLASS|BARE` | C3 | 48 | **false_pos** | [smeme/core/dependencies.py#L48](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L48) |
| `C1|BARE|PARAM` | C1 | 31 | **known** | [smeme/core/dependencies.py#L48](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L48) |
| `C1|BARE|SIG` | C1 | 14 | **false_pos** | [smeme/api/health.py#L28](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/api/health.py#L28) |
| `C1|EMPTY|SIG` | C1 | 7 | **variant** | [smeme/decision_tree/editor/routes.py#L449](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/decision_tree/editor/routes.py#L449) |
| `C4|USED` | C4 | 3 | **false_pos** | [smeme/auth/manager.py#L38](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/auth/manager.py#L38) |
| `C3|ELLIPSIS|BARE` | C3 | 1 | **variant** | [smeme/core/dependencies.py#L60](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L60) |

## `C4|DEF` — **false_pos**
> occurrences here: 60 · corpus total: 56644 · executor: x86_64
> example: [scripts/check_no_qnr_product_refs.py#L141](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/scripts/check_no_qnr_product_refs.py#L141)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 48 · corpus total: 20139 · executor: x86_64
> example: [smeme/core/dependencies.py#L48](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L48)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 31 · corpus total: 18195 · executor: x86_64
> example: [smeme/core/dependencies.py#L48](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L48)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 14 · corpus total: 83548 · executor: x86_64
> example: [smeme/api/health.py#L28](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/api/health.py#L28)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 7 · corpus total: 254 · executor: x86_64
> example: [smeme/decision_tree/editor/routes.py#L449](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/decision_tree/editor/routes.py#L449)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

## `C4|USED` — **false_pos**
> occurrences here: 3 · corpus total: 1079 · executor: x86_64
> example: [smeme/auth/manager.py#L38](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/auth/manager.py#L38)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 1 · corpus total: 1113 · executor: x86_64
> example: [smeme/core/dependencies.py#L60](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L60)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

