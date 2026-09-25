# xinvxueyuan/orbital-marketplace

- GitHub: https://github.com/xinvxueyuan/orbital-marketplace
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 18 · commit: `f3e7c1d9a0f0`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based DI for database sessions` | backend/app/routers/apps.py#L18 | The `db: Session = Depends(get_db)` parameter in `get_apps` uses FastAPI's dependency injection to inject a database session. The `get_db` function is defined in `database.py` (file: backend/app/da... |
| 2 | `Yield-based dependency provider` | backend/app/database.py#L12 | The `get_db` function uses a `yield` statement to provide a database session to dependent routes. This is a standard FastAPI pattern for context-managed dependencies, ensuring sessions are properly... |

## Pass 2 — reconcile with inventory of xinvxueyuan/orbital-marketplace

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends(get_db)` for database session injection, which is a canonical DI pattern. The `get_db` function in `database.py` is a proper dependency provider. | backend/app/routers/apps.py#L18 |
| `C4|DEF` | false_pos | yes | The `lifespan` context manager in `main.py` is not a dependency injection occurrence but application lifecycle management. It does not inject dependencies into route handlers. | backend/app/main.py#L25 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db` function in `database.py` is a standard FastAPI DI provider using `yield` to manage database sessions. This is a canonical DI pattern. | backend/app/database.py#L12 |

### Missed by inventory (1)
- `Consistent use of `Depends(get_db)` across multiple routers (apps, cards, docs, library, orders)` @ backend/app/routers/docs.py#L14 — The inventory may have missed DI occurrences in `docs.py` and other routers beyond the explicitly listed links.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 16 | **false_pos** | [backend/app/routers/apps.py#L18](https://github.com/xinvxueyuan/orbital-marketplace/blob/f3e7c1d9a0f0696e53170fa7f280830c7812a9be/backend/app/routers/apps.py#L18) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/main.py#L25](https://github.com/xinvxueyuan/orbital-marketplace/blob/f3e7c1d9a0f0696e53170fa7f280830c7812a9be/backend/app/main.py#L25) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/database.py#L12](https://github.com/xinvxueyuan/orbital-marketplace/blob/f3e7c1d9a0f0696e53170fa7f280830c7812a9be/backend/app/database.py#L12) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 16 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routers/apps.py#L18](https://github.com/xinvxueyuan/orbital-marketplace/blob/f3e7c1d9a0f0696e53170fa7f280830c7812a9be/backend/app/routers/apps.py#L18)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L25](https://github.com/xinvxueyuan/orbital-marketplace/blob/f3e7c1d9a0f0696e53170fa7f280830c7812a9be/backend/app/main.py#L25)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database.py#L12](https://github.com/xinvxueyuan/orbital-marketplace/blob/f3e7c1d9a0f0696e53170fa7f280830c7812a9be/backend/app/database.py#L12)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

