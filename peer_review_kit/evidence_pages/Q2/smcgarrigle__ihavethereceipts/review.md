# smcgarrigle/ihavethereceipts

- GitHub: https://github.com/smcgarrigle/ihavethereceipts
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 104 · commit: `2ac2ac82898f`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection for database sessions` | backend/app/api/analytics.py#L45 | The function `ingredient_stats` uses `db: Session = Depends(get_db)` to inject a database session. This is a standard FastAPI dependency injection pattern where `get_db` is a dependency provider th... |
| 2 | `Repeated FastAPI Depends usage across endpoints` | backend/app/api/analytics.py#L81 | The `spending_by_category` endpoint also uses `db: Session = Depends(get_db)`, showing this pattern is consistently applied across multiple API routes in the repository. |
| 3 | `Database session injection in multiple files` | backend/app/api/bulk.py#L25 | The `bulk_upload_receipts` function in `bulk.py` uses `db: Session = Depends(get_db)`, confirming this dependency injection pattern is used throughout the codebase, not just in `analytics.py`. |

## Pass 2 — reconcile with inventory of smcgarrigle/ihavethereceipts

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | FastAPI Depends injection for database sessions | yes | The code confirms standard FastAPI dependency injection via `Depends(get_db)` in `ingredient_stats`. | backend/app/api/analytics.py#L45 |
| `C4|DEF` | Repeated FastAPI Depends usage across endpoints | yes | Multiple endpoints like `spending_by_category` use `Depends(get_db)` consistently. | backend/app/api/analytics.py#L81 |
| `C4|DEF` | Database session injection in multiple files | yes | The pattern appears in `bulk.py` and other files beyond `analytics.py`. | backend/app/api/bulk.py#L25 |

### Missed by inventory (3)
- `Depends(get_db) in categories.py` @ backend/app/api/categories.py#L17 — Inventory did not capture usage in `categories.py`
- `Depends(get_db) in items.py` @ backend/app/api/items.py#L34 — Inventory missed dependency injection in `items.py`
- `Depends(get_db) in export.py` @ backend/app/api/export.py#L106 — Inventory did not note usage in `export.py`

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 97 | **false_pos** | [backend/app/api/analytics.py#L45](https://github.com/smcgarrigle/ihavethereceipts/blob/2ac2ac82898fddefd2a1510006ed381aa8f12a01/backend/app/api/analytics.py#L45) |
| `C4|DEF` | C4 | 6 | **false_pos** | [backend/app/main.py#L64](https://github.com/smcgarrigle/ihavethereceipts/blob/2ac2ac82898fddefd2a1510006ed381aa8f12a01/backend/app/main.py#L64) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/database.py#L43](https://github.com/smcgarrigle/ihavethereceipts/blob/2ac2ac82898fddefd2a1510006ed381aa8f12a01/backend/app/database.py#L43) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 97 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/analytics.py#L45](https://github.com/smcgarrigle/ihavethereceipts/blob/2ac2ac82898fddefd2a1510006ed381aa8f12a01/backend/app/api/analytics.py#L45)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L64](https://github.com/smcgarrigle/ihavethereceipts/blob/2ac2ac82898fddefd2a1510006ed381aa8f12a01/backend/app/main.py#L64)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database.py#L43](https://github.com/smcgarrigle/ihavethereceipts/blob/2ac2ac82898fddefd2a1510006ed381aa8f12a01/backend/app/database.py#L43)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

