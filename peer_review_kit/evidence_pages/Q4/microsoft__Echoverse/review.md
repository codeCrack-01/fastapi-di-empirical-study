# microsoft/Echoverse

- GitHub: https://github.com/microsoft/Echoverse
- Stars: 36 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 185 · commit: `a60d030fed02`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | envs/datepickers/backend/routes.py#L110 | The `submit_answer` function uses `session: Session = Depends(get_session)` to inject a database session. This is a core FastAPI pattern where dependencies are resolved at request time. |
| 2 | `FastAPI dependency injection via Depends()` | envs/echoforge/backend/routes.py#L626 | The `register` endpoint uses `session: Session = Depends(get_session)` to inject a database session, demonstrating centralized session management through FastAPI dependencies. |
| 3 | `Authentication dependency injection` | envs/echoforge/backend/routes.py#L678 | The `auth_me` endpoint uses `current_user_id: int = Depends(get_current_user_id)` to inject authenticated user information, showing DI for security contexts. |

## Pass 2 — reconcile with inventory of microsoft/Echoverse

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true | **no (overturn)** | The code explicitly uses FastAPI's Depends() for dependency injection (e.g., `session: Session = Depends(get_session)` in envs/datepickers/backend/routes.py:110), which is a valid DI pattern. | envs/datepickers/backend/routes.py#L110 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 177 | **false_pos** | [envs/datepickers/backend/routes.py#L110](https://github.com/microsoft/Echoverse/blob/a60d030fed0267f993a1355ffe9ce845eae05f9e/envs/datepickers/backend/routes.py#L110) |
| `C4|DEF` | C4 | 4 | **false_pos** | [envs/datepickers/backend/app.py#L46](https://github.com/microsoft/Echoverse/blob/a60d030fed0267f993a1355ffe9ce845eae05f9e/envs/datepickers/backend/app.py#L46) |
| `C4|USED` | C4 | 4 | **false_pos** | [envs/datepickers/backend/database.py#L110](https://github.com/microsoft/Echoverse/blob/a60d030fed0267f993a1355ffe9ce845eae05f9e/envs/datepickers/backend/database.py#L110) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 177 · corpus total: 83548 · executor: x86_64
> example: [envs/datepickers/backend/routes.py#L110](https://github.com/microsoft/Echoverse/blob/a60d030fed0267f993a1355ffe9ce845eae05f9e/envs/datepickers/backend/routes.py#L110)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [envs/datepickers/backend/app.py#L46](https://github.com/microsoft/Echoverse/blob/a60d030fed0267f993a1355ffe9ce845eae05f9e/envs/datepickers/backend/app.py#L46)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 4 · corpus total: 1079 · executor: x86_64
> example: [envs/datepickers/backend/database.py#L110](https://github.com/microsoft/Echoverse/blob/a60d030fed0267f993a1355ffe9ce845eae05f9e/envs/datepickers/backend/database.py#L110)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

