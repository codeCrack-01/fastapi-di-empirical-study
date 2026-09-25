# oodaooda/watchTower

- GitHub: https://github.com/oodaooda/watchTower
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 77 · commit: `1018a8146361`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | app/routers/companies.py#L30 | The `db: Session = Depends(get_db)` pattern is used to inject a database session into the `list_companies` endpoint, demonstrating FastAPI's built-in dependency injection system. |
| 2 | `FastAPI Depends injection` | app/routers/definitions.py#L26 | The `db: Session = Depends(get_db)` pattern is used in `list_definitions`, showing consistent use of FastAPI's dependency injection for database sessions across multiple routers. |
| 3 | `Multiple dependencies` | app/routers/openclaw.py#L51 | The `openclaw_qa` endpoint injects two dependencies (`db` and `qa_db`) using `Depends(get_db)` and `Depends(get_qa_db)`, indicating separate database connections or purposes. |

## Pass 2 — reconcile with inventory of oodaooda/watchTower

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends(get_db)` pattern for dependency injection, as seen in `app/routers/companies.py:30` and other files. | app/routers/companies.py#L30 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code consistently uses `Depends(get_db)` across multiple routers (e.g., `app/routers/definitions.py:26`), confirming valid DI usage. | app/routers/definitions.py#L26 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | Multiple dependencies are injected via `Depends` in `app/routers/openclaw.py:51`, demonstrating DI patterns the inventory may have missed. | app/routers/openclaw.py#L51 |

### Missed by inventory (2)
- `Multiple `Depends` injection in a single endpoint` @ app/routers/openclaw.py#L51 — The inventory may not have accounted for endpoints injecting multiple dependencies (e.g., `db` and `qa_db`) via `Depends`.
- `Consistent use of `Depends(get_db)` across routers` @ app/routers/companies.py#L30 — The inventory may have overlooked the widespread use of `Depends(get_db)` in multiple routers, indicating a systemic DI pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 60 | **false_pos** | [app/routers/companies.py#L30](https://github.com/oodaooda/watchTower/blob/1018a8146361b527ce2d3268a6eb546ebab21d38/app/routers/companies.py#L30) |
| `C4|DEF` | C4 | 15 | **false_pos** | [app/routers/signals.py#L120](https://github.com/oodaooda/watchTower/blob/1018a8146361b527ce2d3268a6eb546ebab21d38/app/routers/signals.py#L120) |
| `C4|USED` | C4 | 2 | **false_pos** | [app/core/db.py#L37](https://github.com/oodaooda/watchTower/blob/1018a8146361b527ce2d3268a6eb546ebab21d38/app/core/db.py#L37) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 60 · corpus total: 83548 · executor: x86_64
> example: [app/routers/companies.py#L30](https://github.com/oodaooda/watchTower/blob/1018a8146361b527ce2d3268a6eb546ebab21d38/app/routers/companies.py#L30)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 15 · corpus total: 56644 · executor: x86_64
> example: [app/routers/signals.py#L120](https://github.com/oodaooda/watchTower/blob/1018a8146361b527ce2d3268a6eb546ebab21d38/app/routers/signals.py#L120)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [app/core/db.py#L37](https://github.com/oodaooda/watchTower/blob/1018a8146361b527ce2d3268a6eb546ebab21d38/app/core/db.py#L37)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

