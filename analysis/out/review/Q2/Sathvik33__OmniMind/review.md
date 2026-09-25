# Sathvik33/OmniMind

- GitHub: https://github.com/Sathvik33/OmniMind
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 36 · commit: `7f6204c43152`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Depends` | backend/app/api/auth.py#L62 | The signup route uses `db: Session = Depends(get_db)` to inject a database session. This is a standard FastAPI pattern where dependencies are resolved via the `Depends` function. |
| 2 | `FastAPI Dependency Injection with Depends` | backend/app/api/deps.py#L17 | The `get_current_user` function is defined with dependencies on `_bearer` and `get_db`, demonstrating how dependencies can be composed and reused across routes. |
| 3 | `FastAPI Dependency Injection with Depends` | backend/app/api/chats.py#L100 | The `list_chats` route uses both `Depends(get_current_user)` and `Depends(get_db)` to inject the authenticated user and database session, showing multi-dependency injection in a single endpoint. |

## Pass 2 — reconcile with inventory of Sathvik33/OmniMind

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses Depends() for database session injection in auth.py routes (signup, login, me). This is standard FastAPI DI usage. | backend/app/api/auth.py#L62 |
| `C4|DEF` | true_pos | **no (overturn)** | The query.py endpoint correctly uses Depends(get_db) for database injection in both synchronous and streaming query endpoints. | backend/app/api/query.py#L103 |
| `C4|USED` | true_pos | **no (overturn)** | The database.py get_db() function is a valid FastAPI dependency provider that yields sessions via context manager. | backend/app/db/database.py#L20 |

### Missed by inventory (3)
- `Multiple Depends() usage in single endpoint` @ backend/app/api/chats.py#L100 — The list_chats() endpoint simultaneously uses Depends(get_current_user) and Depends(get_db) - a pattern not captured in the inventory
- `Dependency composition in auth middleware` @ backend/app/api/deps.py#L17 — The get_current_user() dependency combines HTTPBearer and database injection - a composite pattern not inventoried
- `Streaming endpoint DI` @ backend/app/api/query.py#L87 — The query_stream() endpoint uses Depends() in a streaming context - a usage pattern not captured in the inventory

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 24 | **false_pos** | [backend/app/api/auth.py#L62](https://github.com/Sathvik33/OmniMind/blob/7f6204c431527bc888bb590b6b15728c3b79274b/backend/app/api/auth.py#L62) |
| `C4|DEF` | C4 | 11 | **false_pos** | [backend/app/api/query.py#L103](https://github.com/Sathvik33/OmniMind/blob/7f6204c431527bc888bb590b6b15728c3b79274b/backend/app/api/query.py#L103) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/database.py#L20](https://github.com/Sathvik33/OmniMind/blob/7f6204c431527bc888bb590b6b15728c3b79274b/backend/app/db/database.py#L20) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 24 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/auth.py#L62](https://github.com/Sathvik33/OmniMind/blob/7f6204c431527bc888bb590b6b15728c3b79274b/backend/app/api/auth.py#L62)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 11 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/query.py#L103](https://github.com/Sathvik33/OmniMind/blob/7f6204c431527bc888bb590b6b15728c3b79274b/backend/app/api/query.py#L103)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/database.py#L20](https://github.com/Sathvik33/OmniMind/blob/7f6204c431527bc888bb590b6b15728c3b79274b/backend/app/db/database.py#L20)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

