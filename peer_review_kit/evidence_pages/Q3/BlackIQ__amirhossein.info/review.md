# BlackIQ/amirhossein.info

- GitHub: https://github.com/BlackIQ/amirhossein.info
- Stars: 15 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 46 · commit: `aa477ae2b695`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | backend/dependencies/token.py#L37 | The `get_current_user` function uses `Depends(oauth2_schema)` and `Depends(get_db)` to inject authentication and database dependencies. |
| 2 | `FastAPI Depends-based injection` | backend/routers/experience.py#L29 | The `all_experiences` endpoint uses `Depends(get_db)` to inject a database session. |
| 3 | `FastAPI Depends-based injection` | backend/routers/experience.py#L46 | The `create_experience` endpoint uses `Depends(get_current_user)` for authentication and `Depends(get_db)` for database access. |
| 4 | `Generator-based dependency` | backend/dependencies/database.py#L6 | The `get_db` function uses `yield` to provide a database session, enabling context management via FastAPI's dependency system. |

## Pass 2 — reconcile with inventory of BlackIQ/amirhossein.info

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses `Depends(...)` in multiple endpoints (e.g., `get_current_user` in token.py and `create_experience` in experience.py), which are valid FastAPI dependency injections. | backend/dependencies/token.py#L37 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db` function in database.py uses a generator with `yield` to manage database sessions, which is a canonical pattern for FastAPI dependencies. | backend/dependencies/database.py#L6 |

### Missed by inventory (2)
- `FastAPI `Depends` usage in endpoints (e.g., `current_user: str = Depends(get_current_user)`)` @ backend/routers/experience.py#L46 — The inventory missed labeling the widespread use of `Depends(...)` in CRUD endpoints across multiple routers (experience.py, message.py, resume.py, etc.).
- `Generator-based dependency (`yield` in `get_db`)` @ backend/dependencies/database.py#L6 — The inventory did not capture the `yield`-based context management in `get_db`, which is a core FastAPI dependency pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 45 | **false_pos** | [backend/dependencies/token.py#L37](https://github.com/BlackIQ/amirhossein.info/blob/aa477ae2b6958de9ec3be256fe97c234439f7b9c/backend/dependencies/token.py#L37) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/dependencies/database.py#L6](https://github.com/BlackIQ/amirhossein.info/blob/aa477ae2b6958de9ec3be256fe97c234439f7b9c/backend/dependencies/database.py#L6) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 45 · corpus total: 83548 · executor: x86_64
> example: [backend/dependencies/token.py#L37](https://github.com/BlackIQ/amirhossein.info/blob/aa477ae2b6958de9ec3be256fe97c234439f7b9c/backend/dependencies/token.py#L37)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/dependencies/database.py#L6](https://github.com/BlackIQ/amirhossein.info/blob/aa477ae2b6958de9ec3be256fe97c234439f7b9c/backend/dependencies/database.py#L6)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

