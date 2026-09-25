# trghcj/TaskFlow

- GitHub: https://github.com/trghcj/TaskFlow
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 37 · commit: `4c9577aae52b`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection` | backend/auth.py#L26 | The verify_token function uses Depends(security) to inject an HTTPBearer authentication dependency, which is a standard FastAPI security mechanism. |
| 2 | `FastAPI built-in dependency injection` | backend/main.py#L55 | The get_tasks endpoint uses Depends(get_current_user) and Depends(get_db), demonstrating FastAPI's dependency injection for user authentication and database sessions. |
| 3 | `FastAPI built-in dependency injection` | backend/database.py#L16 | The get_db function is a generator that yields a database session, which is injected into routes via Depends(get_db), showing FastAPI's standard dependency injection pattern for database access. |

## Pass 2 — reconcile with inventory of trghcj/TaskFlow

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's built-in dependency injection (Depends(security), Depends(get_current_user)) for authentication and user resolution, which matches the fingerprint's structural pat... | backend/auth.py#L26 |
| `C4|DEF` | true_pos | **no (overturn)** | The lifespan function correctly implements FastAPI's async context manager pattern for startup/shutdown logic, which is a canonical DI usage pattern. | backend/main.py#L29 |
| `C4|USED` | true_pos | **no (overturn)** | The get_db function is a standard FastAPI dependency provider for database sessions, matching the fingerprint's structural pattern. | backend/database.py#L16 |

### Missed by inventory (2)
- `FastAPI lifespan context manager with Alembic migrations` @ backend/main.py#L29 — The inventory missed the combination of FastAPI's lifespan manager with Alembic database migration calls, which is a significant structural pattern in the code.
- `Cloudinary configuration via FastAPI dependency` @ backend/main.py#L29 — The inventory missed the FastAPI-level configuration of Cloudinary (via cloudinary.config()) as part of the application setup, which is a canonical pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 35 | **false_pos** | [backend/auth.py#L26](https://github.com/trghcj/TaskFlow/blob/4c9577aae52bf74c50995a292db84acf73bb98ef/backend/auth.py#L26) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/main.py#L29](https://github.com/trghcj/TaskFlow/blob/4c9577aae52bf74c50995a292db84acf73bb98ef/backend/main.py#L29) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database.py#L16](https://github.com/trghcj/TaskFlow/blob/4c9577aae52bf74c50995a292db84acf73bb98ef/backend/database.py#L16) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 35 · corpus total: 83548 · executor: x86_64
> example: [backend/auth.py#L26](https://github.com/trghcj/TaskFlow/blob/4c9577aae52bf74c50995a292db84acf73bb98ef/backend/auth.py#L26)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/main.py#L29](https://github.com/trghcj/TaskFlow/blob/4c9577aae52bf74c50995a292db84acf73bb98ef/backend/main.py#L29)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database.py#L16](https://github.com/trghcj/TaskFlow/blob/4c9577aae52bf74c50995a292db84acf73bb98ef/backend/database.py#L16)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

