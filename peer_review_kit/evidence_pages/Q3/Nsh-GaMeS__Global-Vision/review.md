# Nsh-GaMeS/Global-Vision

- GitHub: https://github.com/Nsh-GaMeS/Global-Vision
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 10 · commit: `9daf5f55c676`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection with Depends()` | routers/auth.py#L106 | The `get_current_user` function uses `Depends(oauth2_bearer)` to inject an OAuth2 bearer token dependency, and `create_new_user` uses `Depends(get_db)` to inject a database session dependency. |
| 2 | `Generator-based dependency provider` | routers/auth.py#L50 | The `get_db` function is defined as a generator with `yield db`, which is the standard FastAPI pattern for creating reusable database session dependencies that automatically close resources. |
| 3 | `Nested dependency injection` | routers/resourceurl.py#L95 | The `get_resourceurl` route uses both `Depends(get_current_user)` and `Depends(get_db)`, showing layered dependency injection where authentication depends on database access. |
| 4 | `Duplicate dependency implementation` | routers/resourceurl.py#L32 | A separate `get_db` generator is implemented in `resourceurl.py`, duplicating the same pattern seen in `auth.py` for database session management. |

## Pass 2 — reconcile with inventory of Nsh-GaMeS/Global-Vision

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses Depends() for DI (e.g., get_current_user(token: str = Depends(oauth2_bearer)) in auth.py:93, which is a valid DI occurrence. | routers/auth.py#L93 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code uses Depends(get_db) in create_new_user (auth.py:106), confirming DI usage. | routers/auth.py#L106 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code uses Depends(get_current_user) in get_resourceurl (resourceurl.py:95), confirming DI usage. | routers/resourceurl.py#L95 |
| `C4|USED` | true_pos | **no (overturn)** | The get_db generator in auth.py:50 is a valid DI dependency provider, as it yields a database session. | routers/auth.py#L50 |
| `C4|USED` | true_pos | **no (overturn)** | The duplicate get_db generator in resourceurl.py:32 is also a valid DI dependency provider, though redundant. | routers/resourceurl.py#L32 |

### Missed by inventory (2)
- `Duplicate dependency implementation (get_db in both auth.py and resourceurl.py)` @ routers/auth.py#L50 — The inventory did not flag the duplication of the same DI pattern across multiple modules.
- `Nested dependency injection (get_resourceurl uses both Depends(get_current_user) and Depends(get_db))` @ routers/resourceurl.py#L95 — The inventory did not capture the layered DI usage in this route.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 8 | **false_pos** | [routers/auth.py#L93](https://github.com/Nsh-GaMeS/Global-Vision/blob/9daf5f55c676dcc4d5f42f7c633e6455b9c014c5/routers/auth.py#L93) |
| `C4|USED` | C4 | 2 | **false_pos** | [routers/auth.py#L50](https://github.com/Nsh-GaMeS/Global-Vision/blob/9daf5f55c676dcc4d5f42f7c633e6455b9c014c5/routers/auth.py#L50) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 8 · corpus total: 83548 · executor: x86_64
> example: [routers/auth.py#L93](https://github.com/Nsh-GaMeS/Global-Vision/blob/9daf5f55c676dcc4d5f42f7c633e6455b9c014c5/routers/auth.py#L93)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [routers/auth.py#L50](https://github.com/Nsh-GaMeS/Global-Vision/blob/9daf5f55c676dcc4d5f42f7c633e6455b9c014c5/routers/auth.py#L50)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

