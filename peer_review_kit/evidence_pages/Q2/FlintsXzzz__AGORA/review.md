# FlintsXzzz/AGORA

- GitHub: https://github.com/FlintsXzzz/AGORA
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 8 · commit: `a00456988a62`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based DI with async/sync variants` | app/routers/whatsapp.py#L153 | The receive_message endpoint uses Depends(get_db) to inject an AsyncSession, demonstrating FastAPI's dependency injection pattern. |
| 2 | `DI provider function` | app/database.py#L57 | The async get_db() function is defined as a dependency provider, yielding AsyncSession instances for FastAPI routes. |
| 3 | `DI override in tests` | tests/test_endpoints.py#L24 | The test suite overrides get_db with a test-specific implementation using pytest fixtures, showing DI customization in testing. |
| 4 | `Dual DI variants` | database.py#L16 | Two get_db implementations exist: async (app/database.py) for async routes and sync (database.py) for synchronous endpoints. |

## Pass 2 — reconcile with inventory of FlintsXzzz/AGORA

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() to inject an AsyncSession, confirming DI usage. | app/routers/whatsapp.py#L153 |
| `C4|DEF` | true_pos | **no (overturn)** | The test files implement DI overrides (override_get_db) which are valid DI usages. | tests/test_endpoints.py#L24 |
| `C4|USED` | true_pos | **no (overturn)** | The async get_db() function in app/database.py is explicitly used as a DI provider for FastAPI routes. | app/database.py#L57 |

### Missed by inventory (1)
- `Dual DI variants (async/sync get_db implementations)` @ database.py#L16 — The repo contains both async (app/database.py) and sync (database.py) versions of get_db, a structural pattern not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 3 | **false_pos** | [app/routers/whatsapp.py#L153](https://github.com/FlintsXzzz/AGORA/blob/a00456988a627b70f8677790557ae9cde1e034a9/app/routers/whatsapp.py#L153) |
| `C4|DEF` | C4 | 3 | **false_pos** | [main.py#L22](https://github.com/FlintsXzzz/AGORA/blob/a00456988a627b70f8677790557ae9cde1e034a9/main.py#L22) |
| `C4|USED` | C4 | 2 | **false_pos** | [app/database.py#L57](https://github.com/FlintsXzzz/AGORA/blob/a00456988a627b70f8677790557ae9cde1e034a9/app/database.py#L57) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 83548 · executor: x86_64
> example: [app/routers/whatsapp.py#L153](https://github.com/FlintsXzzz/AGORA/blob/a00456988a627b70f8677790557ae9cde1e034a9/app/routers/whatsapp.py#L153)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [main.py#L22](https://github.com/FlintsXzzz/AGORA/blob/a00456988a627b70f8677790557ae9cde1e034a9/main.py#L22)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [app/database.py#L57](https://github.com/FlintsXzzz/AGORA/blob/a00456988a627b70f8677790557ae9cde1e034a9/app/database.py#L57)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

