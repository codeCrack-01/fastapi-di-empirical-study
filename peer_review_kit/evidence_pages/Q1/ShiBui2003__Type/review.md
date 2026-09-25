# ShiBui2003/Type

- GitHub: https://github.com/ShiBui2003/Type
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 22 · commit: `0b975645bd25`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection with Depends()` | backend/routers/forms.py#L233 | The function list_forms uses db: Session = Depends(get_db) to inject a database session. This is a standard FastAPI pattern where dependencies are resolved using the Depends() function. |
| 2 | `Generator-based dependency provider` | backend/database.py#L24 | The get_db function is a generator that yields a new database session. This allows FastAPI to manage the lifecycle of the session, ensuring it is properly closed after use. |

## Pass 2 — reconcile with inventory of ShiBui2003/Type

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's Depends() for DI, which is a canonical pattern. The static inventory incorrectly labeled this as false_pos. | backend/routers/forms.py#L233 |
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly defines dependencies via Depends(get_db), which is standard in FastAPI. The static inventory's false_pos label is incorrect. | backend/routers/forms.py#L257 |
| `C4|USED` | true_pos | **no (overturn)** | The generator-based dependency provider (get_db) is correctly implemented and used throughout the code. The static inventory's false_pos label is incorrect. | backend/database.py#L24 |

### Missed by inventory (2)
- `FastAPI DI with Depends() in route handlers` @ backend/routers/forms.py#L267 — Multiple route handlers (e.g., create_form, get_form) use Depends(get_db) for DI, but the inventory missed these occurrences.
- `Generator-based dependency provider (get_db)` @ backend/database.py#L24 — The inventory missed the canonical implementation of a dependency provider using a generator function.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 18 | **false_pos** | [backend/routers/forms.py#L233](https://github.com/ShiBui2003/Type/blob/0b975645bd2514839f8fc2c0fd6ac3d31a587b82/backend/routers/forms.py#L233) |
| `C4|DEF` | C4 | 3 | **false_pos** | [backend/main.py#L16](https://github.com/ShiBui2003/Type/blob/0b975645bd2514839f8fc2c0fd6ac3d31a587b82/backend/main.py#L16) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database.py#L24](https://github.com/ShiBui2003/Type/blob/0b975645bd2514839f8fc2c0fd6ac3d31a587b82/backend/database.py#L24) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 18 · corpus total: 83548 · executor: x86_64
> example: [backend/routers/forms.py#L233](https://github.com/ShiBui2003/Type/blob/0b975645bd2514839f8fc2c0fd6ac3d31a587b82/backend/routers/forms.py#L233)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [backend/main.py#L16](https://github.com/ShiBui2003/Type/blob/0b975645bd2514839f8fc2c0fd6ac3d31a587b82/backend/main.py#L16)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database.py#L24](https://github.com/ShiBui2003/Type/blob/0b975645bd2514839f8fc2c0fd6ac3d31a587b82/backend/database.py#L24)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

