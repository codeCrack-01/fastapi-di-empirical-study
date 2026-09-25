# kristovatlas/somnus

- GitHub: https://github.com/kristovatlas/somnus
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 41 · commit: `3845fd9da551`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends(get_db)` | backend/routers/analysis.py#L35 | The function analysis_status uses db: Session = Depends(get_db) to inject a database session. This is a standard FastAPI pattern where get_db is a dependency provider that yields a SQLAlchemy Session. |
| 2 | `Consistent DI usage across routes` | backend/routers/daily_log.py#L71 | Multiple routes like upsert_daily_log use Depends(get_db) to obtain a database session, showing this is a widespread pattern in the codebase. |
| 3 | `Centralized DB session management` | backend/database.py#L67 | The get_db() function is defined here as a generator that creates and closes SQLAlchemy sessions, which is the source of the injected dependencies in the routes. |

## Pass 2 — reconcile with inventory of kristovatlas/somnus

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses Depends(get_db) for database session injection, which is a canonical FastAPI DI pattern. | backend/routers/analysis.py#L35 |
| `C4|DEF` | true_pos | **no (overturn)** | The code contains valid DI setup (init_db() in main.py and test DB overrides in conftest.py) that aligns with FastAPI's dependency injection model. | backend/main.py#L21 |
| `C4|USED` | true_pos | **no (overturn)** | The get_db() function is correctly implemented as a FastAPI dependency provider for database sessions. | backend/database.py#L67 |

### Missed by inventory (2)
- `Depends(get_db) in recommendation routes` @ backend/routers/recommendations.py#L30 — The inventory missed DI occurrences in get_recommendations() and create_experiment() routes that use Depends(get_db).
- `Depends(get_db) in settings routes` @ backend/routers/settings.py#L83 — The inventory missed DI usage in get_settings() and update_settings() routes that depend on get_db.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 33 | **false_pos** | [backend/routers/analysis.py#L35](https://github.com/kristovatlas/somnus/blob/3845fd9da551c7d7a9c9e3a99ecf9b129b44f2a9/backend/routers/analysis.py#L35) |
| `C4|DEF` | C4 | 5 | **false_pos** | [backend/main.py#L21](https://github.com/kristovatlas/somnus/blob/3845fd9da551c7d7a9c9e3a99ecf9b129b44f2a9/backend/main.py#L21) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [backend/routers/daily_log.py#L124](https://github.com/kristovatlas/somnus/blob/3845fd9da551c7d7a9c9e3a99ecf9b129b44f2a9/backend/routers/daily_log.py#L124) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database.py#L67](https://github.com/kristovatlas/somnus/blob/3845fd9da551c7d7a9c9e3a99ecf9b129b44f2a9/backend/database.py#L67) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 33 · corpus total: 83548 · executor: x86_64
> example: [backend/routers/analysis.py#L35](https://github.com/kristovatlas/somnus/blob/3845fd9da551c7d7a9c9e3a99ecf9b129b44f2a9/backend/routers/analysis.py#L35)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [backend/main.py#L21](https://github.com/kristovatlas/somnus/blob/3845fd9da551c7d7a9c9e3a99ecf9b129b44f2a9/backend/main.py#L21)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [backend/routers/daily_log.py#L124](https://github.com/kristovatlas/somnus/blob/3845fd9da551c7d7a9c9e3a99ecf9b129b44f2a9/backend/routers/daily_log.py#L124)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database.py#L67](https://github.com/kristovatlas/somnus/blob/3845fd9da551c7d7a9c9e3a99ecf9b129b44f2a9/backend/database.py#L67)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

