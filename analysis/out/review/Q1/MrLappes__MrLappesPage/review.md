# MrLappes/MrLappesPage

- GitHub: https://github.com/MrLappes/MrLappesPage
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 21 · commit: `b282ede5e7e8`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection via Depends()` | recipe-backend/app/routers/auth.py#L131 | The function challenge_password uses subject: str = Depends(get_challenge_subject) to inject a dependency. This is the standard FastAPI pattern where dependencies are resolved via the Depends() fun... |
| 2 | `Hierarchical dependency resolution` | recipe-backend/app/security.py#L105 | The get_current_admin function depends on _decode, which in turn uses get_settings(). This creates a chain of dependencies where each function relies on the output of another. |
| 3 | `Shared dependency injection for authentication` | recipe-backend/app/routers/ingredients.py#L79 | Multiple routes (e.g., admin_list_ingredients, admin_get_ingredient) use _: str = Depends(get_current_admin) to inject authentication context, showing a shared pattern for securing admin endpoints. |

## Pass 2 — reconcile with inventory of MrLappes/MrLappesPage

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's Depends() for dependency injection in auth routes (e.g., challenge_password depends on get_challenge_subject). This is a valid DI pattern, not a false positive. | recipe-backend/app/routers/auth.py#L131 |
| `C4|DEF` | true_pos | **no (overturn)** | The code in database.py (db_cursor context manager) and main.py (lifespan async context manager) correctly implements dependency management patterns. These are valid DI constructs, not false positi... | recipe-backend/app/database.py#L120 |

### Missed by inventory (2)
- `Hierarchical dependency chains (e.g., get_current_admin → _decode → get_settings())` @ recipe-backend/app/security.py#L105 — The inventory missed this multi-layered DI pattern where functions depend on other functions that themselves depend on configuration
- `Shared authentication dependency across admin routes (e.g., _: str = Depends(get_current_admin) in multiple routers)` @ recipe-backend/app/routers/ingredients.py#L79 — The inventory failed to capture this cross-router DI pattern for securing admin endpoints

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 19 | **false_pos** | [recipe-backend/app/routers/auth.py#L131](https://github.com/MrLappes/MrLappesPage/blob/b282ede5e7e8437f9a8bc64b15b3c7b4b9adcc14/recipe-backend/app/routers/auth.py#L131) |
| `C4|DEF` | C4 | 2 | **false_pos** | [recipe-backend/app/database.py#L120](https://github.com/MrLappes/MrLappesPage/blob/b282ede5e7e8437f9a8bc64b15b3c7b4b9adcc14/recipe-backend/app/database.py#L120) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 19 · corpus total: 83548 · executor: x86_64
> example: [recipe-backend/app/routers/auth.py#L131](https://github.com/MrLappes/MrLappesPage/blob/b282ede5e7e8437f9a8bc64b15b3c7b4b9adcc14/recipe-backend/app/routers/auth.py#L131)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [recipe-backend/app/database.py#L120](https://github.com/MrLappes/MrLappesPage/blob/b282ede5e7e8437f9a8bc64b15b3c7b4b9adcc14/recipe-backend/app/database.py#L120)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

