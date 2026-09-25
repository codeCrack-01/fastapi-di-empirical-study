# Jzy258/canteen-recommendation-agent

- GitHub: https://github.com/Jzy258/canteen-recommendation-agent
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 29 · commit: `13cbf44a4ae5`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in Depends for authentication/authorization` | backend/auth/deps.py#L59 | require_admin function uses Depends(get_current_user) to enforce admin role checks, demonstrating FastAPI's dependency injection for authorization. This is used in routes like /users and /dishes to... |
| 2 | `FastAPI route-level dependencies` | backend/auth/admin.py#L40 | The /stats endpoint uses dependencies=[Depends(require_admin)] to inject admin authentication check directly into the route, showing FastAPI's route-level dependency injection pattern. |
| 3 | `Optional dependencies with fallback` | backend/main.py#L103 | The /trend endpoint uses user: dict | None = Depends(get_optional_user) to handle both authenticated and unauthenticated users, demonstrating optional dependency injection with fallback behavior. |

## Pass 2 — reconcile with inventory of Jzy258/canteen-recommendation-agent

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends` for authentication/authorization (e.g., `dependencies=[Depends(require_admin)]` in `/users` routes), which matches the BARE|SIG fingerprint's structural... | backend/auth/admin.py#L40 |
| `C1|BARE|PARAM` | known | yes | The code uses `Query` and `Field` for parameter validation (e.g., `limit: int = Query(50, ge=1, le=200)`), which aligns with the BARE|PARAM fingerprint's pattern of explicit parameter handling. | backend/auth/admin.py#L40 |
| `C4|DEF` | true_pos | **no (overturn)** | The code defines context managers (`@contextmanager`) and async generators (`async def gen()`) in `db.py` and `main.py`, which match the C4|DEF fingerprint's pattern of structural definition patterns. | backend/db/db.py#L344 |

### Missed by inventory (2)
- `Async generator usage with FastAPI streaming` @ backend/main.py#L205 — The inventory missed the async generator pattern in `_stream_reply` which uses `async def gen()` for real-time token streaming, a structural definition not captured in the initial fingerprinting.
- `Context manager for database connections` @ backend/db/db.py#L344 — The inventory missed the `@contextmanager` pattern in `_connect` which handles SQLite connections, a structural definition not captured in the initial fingerprinting.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 15 | **false_pos** | [backend/auth/admin.py#L65](https://github.com/Jzy258/canteen-recommendation-agent/blob/13cbf44a4ae5f6b97de484b626a756852ac49321/backend/auth/admin.py#L65) |
| `C1|BARE|PARAM` | C1 | 10 | **known** | [backend/auth/admin.py#L40](https://github.com/Jzy258/canteen-recommendation-agent/blob/13cbf44a4ae5f6b97de484b626a756852ac49321/backend/auth/admin.py#L40) |
| `C4|DEF` | C4 | 4 | **false_pos** | [backend/db/db.py#L344](https://github.com/Jzy258/canteen-recommendation-agent/blob/13cbf44a4ae5f6b97de484b626a756852ac49321/backend/db/db.py#L344) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 15 · corpus total: 83548 · executor: x86_64
> example: [backend/auth/admin.py#L65](https://github.com/Jzy258/canteen-recommendation-agent/blob/13cbf44a4ae5f6b97de484b626a756852ac49321/backend/auth/admin.py#L65)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 10 · corpus total: 18195 · executor: x86_64
> example: [backend/auth/admin.py#L40](https://github.com/Jzy258/canteen-recommendation-agent/blob/13cbf44a4ae5f6b97de484b626a756852ac49321/backend/auth/admin.py#L40)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [backend/db/db.py#L344](https://github.com/Jzy258/canteen-recommendation-agent/blob/13cbf44a4ae5f6b97de484b626a756852ac49321/backend/db/db.py#L344)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

