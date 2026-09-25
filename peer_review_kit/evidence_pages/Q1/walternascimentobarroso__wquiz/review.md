# walternascimentobarroso/wquiz

- GitHub: https://github.com/walternascimentobarroso/wquiz
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 37 · commit: `5e08d6a440b5`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=1 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | backend/app/api/admin.py#L100 | Multiple routes use Depends(get_db) for database sessions and Depends(get_current_admin) for authentication, showing standard FastAPI dependency injection. |
| 2 | `Composed dependencies` | backend/app/api/deps.py#L36 | get_current_admin depends on get_current_user, demonstrating layered dependency composition. |
| 3 | `Generator-based dependency` | backend/app/core/database.py#L24 | get_db uses a generator to yield database sessions, a common pattern for resource management in FastAPI. |

## Pass 2 — reconcile with inventory of walternascimentobarroso/wquiz

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|EMPTY|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code at admin.py:99-100 correctly uses FastAPI's Depends(get_db) for database injection, which is a valid pattern. The static instrument's 'false_pos' label is incorrect. | backend/app/api/admin.py#L100 |
| `C1|EMPTY|SIG` | variant | **no (overturn)** | The code at auth.py:17 is not empty; it defines a valid FastAPI route with proper dependency injection (Depends(get_db)). The 'variant' label is incorrect. | backend/app/api/auth.py#L17 |
| `C4|DEF` | false_pos | **no (overturn)** | The code at main.py:15 correctly defines a lifespan context manager for FastAPI, which is a standard practice. The 'false_pos' label is incorrect. | backend/app/main.py#L15 |
| `C4|USED` | false_pos | **no (overturn)** | The code at database.py:24 correctly implements a generator-based dependency for database sessions, which is a valid FastAPI pattern. The 'false_pos' label is incorrect. | backend/app/core/database.py#L24 |

### Missed by inventory (2)
- `Composed dependencies (e.g., get_current_admin depends on get_current_user)` @ backend/app/api/deps.py#L36 — The inventory did not capture layered dependency composition patterns like get_current_admin relying on get_current_user.
- `Generator-based dependency injection (get_db)` @ backend/app/core/database.py#L24 — The inventory missed the use of generator functions for managing database sessions.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 34 | **false_pos** | [backend/app/api/admin.py#L99](https://github.com/walternascimentobarroso/wquiz/blob/5e08d6a440b585932bbbb61957f3bd01fa153a56/backend/app/api/admin.py#L99) |
| `C1|EMPTY|SIG` | C1 | 1 | **variant** | [backend/app/api/auth.py#L17](https://github.com/walternascimentobarroso/wquiz/blob/5e08d6a440b585932bbbb61957f3bd01fa153a56/backend/app/api/auth.py#L17) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/main.py#L15](https://github.com/walternascimentobarroso/wquiz/blob/5e08d6a440b585932bbbb61957f3bd01fa153a56/backend/app/main.py#L15) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/core/database.py#L24](https://github.com/walternascimentobarroso/wquiz/blob/5e08d6a440b585932bbbb61957f3bd01fa153a56/backend/app/core/database.py#L24) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 34 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/admin.py#L99](https://github.com/walternascimentobarroso/wquiz/blob/5e08d6a440b585932bbbb61957f3bd01fa153a56/backend/app/api/admin.py#L99)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 1 · corpus total: 254 · executor: x86_64
> example: [backend/app/api/auth.py#L17](https://github.com/walternascimentobarroso/wquiz/blob/5e08d6a440b585932bbbb61957f3bd01fa153a56/backend/app/api/auth.py#L17)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L15](https://github.com/walternascimentobarroso/wquiz/blob/5e08d6a440b585932bbbb61957f3bd01fa153a56/backend/app/main.py#L15)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/core/database.py#L24](https://github.com/walternascimentobarroso/wquiz/blob/5e08d6a440b585932bbbb61957f3bd01fa153a56/backend/app/core/database.py#L24)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

