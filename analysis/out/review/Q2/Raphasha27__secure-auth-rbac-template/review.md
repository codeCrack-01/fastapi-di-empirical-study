# Raphasha27/secure-auth-rbac-template

- GitHub: https://github.com/Raphasha27/secure-auth-rbac-template
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 21 · commit: `7f9bf8431416`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection with custom dependency wrappers` | app/dependencies/__init__.py#L47 | The get_current_user function uses Depends(security) and Depends(get_db) to inject authentication credentials and database sessions. This is standard FastAPI dependency injection. The require_role ... |
| 2 | `Database session generator dependency` | app/dependencies/__init__.py#L20 | The get_db function is an async generator that yields AsyncSession instances, providing database sessions per request. This is a common pattern for managing database connections in FastAPI. |
| 3 | `Decorator-style dependency creation` | app/dependencies/__init__.py#L81 | The require_role function returns a closure (_check_role) that uses Depends(get_current_user), creating a reusable dependency that enforces role-based access control. |
| 4 | `Dependency composition in route handlers` | app/routers/admin.py#L19 | The list_users endpoint composes multiple dependencies: Depends(require_role("admin")) for authorization and Depends(get_db) for database access, demonstrating layered dependency injection. |

## Pass 2 — reconcile with inventory of Raphasha27/secure-auth-rbac-template

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly defines signature-based dependencies (e.g., `Depends(security)` in `get_current_user`) that align with the fingerprint's structural pattern. | app/dependencies/__init__.py#L47 |
| `C4|DEF` | true_pos | **no (overturn)** | The `get_db` function in `app/dependencies/__init__.py` is a valid dependency definition, and `setup_db` in tests/conftest.py correctly initializes database dependencies. | app/dependencies/__init__.py#L20 |
| `C1|BARE|PARAM` | known | yes | The `require_role` and `require_permission` dependencies in `app/routers/content.py` correctly use `Depends(...)` with parameters, matching the known label. | app/routers/content.py#L15 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db` dependency is explicitly used in route handlers (e.g., `Depends(get_db)` in `app/routers/admin.py`), contradicting the false_pos label. | app/routers/admin.py#L19 |

### Missed by inventory (2)
- `Decorator-style dependency creation with role/permission checks` @ app/dependencies/__init__.py#L81 — The inventory missed the `require_role` and `require_permission` decorators, which dynamically generate dependencies using `Depends(get_current_user)`.
- `Test-specific dependency overrides` @ tests/conftest.py#L29 — The inventory did not capture the test fixture `override_db` that replaces `get_db` with a test-specific implementation.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 13 | **false_pos** | [app/dependencies/__init__.py#L47](https://github.com/Raphasha27/secure-auth-rbac-template/blob/7f9bf84314167fe5b79fb1836abc698f149bb024/app/dependencies/__init__.py#L47) |
| `C4|DEF` | C4 | 4 | **false_pos** | [app/main.py#L16](https://github.com/Raphasha27/secure-auth-rbac-template/blob/7f9bf84314167fe5b79fb1836abc698f149bb024/app/main.py#L16) |
| `C1|BARE|PARAM` | C1 | 3 | **known** | [app/routers/content.py#L15](https://github.com/Raphasha27/secure-auth-rbac-template/blob/7f9bf84314167fe5b79fb1836abc698f149bb024/app/routers/content.py#L15) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/dependencies/__init__.py#L20](https://github.com/Raphasha27/secure-auth-rbac-template/blob/7f9bf84314167fe5b79fb1836abc698f149bb024/app/dependencies/__init__.py#L20) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 13 · corpus total: 83548 · executor: x86_64
> example: [app/dependencies/__init__.py#L47](https://github.com/Raphasha27/secure-auth-rbac-template/blob/7f9bf84314167fe5b79fb1836abc698f149bb024/app/dependencies/__init__.py#L47)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [app/main.py#L16](https://github.com/Raphasha27/secure-auth-rbac-template/blob/7f9bf84314167fe5b79fb1836abc698f149bb024/app/main.py#L16)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 3 · corpus total: 18195 · executor: x86_64
> example: [app/routers/content.py#L15](https://github.com/Raphasha27/secure-auth-rbac-template/blob/7f9bf84314167fe5b79fb1836abc698f149bb024/app/routers/content.py#L15)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/dependencies/__init__.py#L20](https://github.com/Raphasha27/secure-auth-rbac-template/blob/7f9bf84314167fe5b79fb1836abc698f149bb024/app/dependencies/__init__.py#L20)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

