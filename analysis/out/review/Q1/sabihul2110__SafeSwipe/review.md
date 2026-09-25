# sabihul2110/SafeSwipe

- GitHub: https://github.com/sabihul2110/SafeSwipe
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 4 · commit: `f1a901171ab4`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based DI` | backend/routers/transactions.py#L20 | The `Depends(get_db)` syntax explicitly uses FastAPI's dependency injection system to inject a database session. The `get_db` function is imported from `core/database.py` and provides a database co... |
| 2 | `FastAPI Depends-based DI` | backend/routers/transactions.py#L26 | The `list_transactions` function also uses `Depends(get_db)` to inject the database session, following the same pattern as `check_transaction`. |
| 3 | `FastAPI Depends-based DI` | backend/routers/transactions.py#L31 | The `clear_transactions` function similarly uses `Depends(get_db)` to inject the database session, demonstrating consistent use of this DI pattern across multiple endpoints. |
| 4 | `Generator-based dependency` | backend/core/database.py#L14 | The `get_db` function uses a generator with `yield db` to provide a database session. This is a common FastAPI pattern for managing resources like database connections, ensuring proper cleanup via ... |

## Pass 2 — reconcile with inventory of sabihul2110/SafeSwipe

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends(get_db)` pattern for dependency injection in endpoints (check_transaction, list_transactions, clear_transactions), which matches the fingerprint's struct... | backend/routers/transactions.py#L20 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db` function in database.py implements a generator-based dependency injection pattern (via `yield db`), which is a canonical form of USED DI in FastAPI applications. | backend/core/database.py#L14 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 3 | **false_pos** | [backend/routers/transactions.py#L20](https://github.com/sabihul2110/SafeSwipe/blob/f1a901171ab4a9904a556ad0aa9d3958a8bce677/backend/routers/transactions.py#L20) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/core/database.py#L14](https://github.com/sabihul2110/SafeSwipe/blob/f1a901171ab4a9904a556ad0aa9d3958a8bce677/backend/core/database.py#L14) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 83548 · executor: x86_64
> example: [backend/routers/transactions.py#L20](https://github.com/sabihul2110/SafeSwipe/blob/f1a901171ab4a9904a556ad0aa9d3958a8bce677/backend/routers/transactions.py#L20)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/core/database.py#L14](https://github.com/sabihul2110/SafeSwipe/blob/f1a901171ab4a9904a556ad0aa9d3958a8bce677/backend/core/database.py#L14)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

