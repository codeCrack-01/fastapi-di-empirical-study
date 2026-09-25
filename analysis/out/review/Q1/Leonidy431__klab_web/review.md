# Leonidy431/klab_web

- GitHub: https://github.com/Leonidy431/klab_web
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 50 · commit: `cd41b440ba25`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI standard dependency injection via Depends` | backend/app/api/v1/endpoints/blueos.py#L45 | The get_rov_status function uses Depends(get_blueos_client) to inject a BlueOSClient instance, demonstrating FastAPI's standard DI pattern where dependencies are resolved through callable providers. |
| 2 | `Database session injection` | backend/app/api/v1/endpoints/forum.py#L48 | The get_categories function uses Depends(get_db) to inject an AsyncSession, showing how database connections are managed as dependencies across multiple endpoints. |
| 3 | `Service dependency injection` | backend/app/api/v1/endpoints/shop.py#L217 | The add_to_cart function uses Depends(get_cart_service) to inject a CartService, illustrating injection of business logic services rather than raw database connections. |

## Pass 2 — reconcile with inventory of Leonidy431/klab_web

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's Depends() for dependency injection (e.g., Depends(get_blueos_client) in blueos.py:45). The panel's 'false_pos' label contradicts standard DI usage observed in the ... | backend/app/api/v1/endpoints/blueos.py#L45 |
| `C4|DEF` | true_pos | **no (overturn)** | The code properly defines database session dependencies (e.g., get_db in database.py:42). The panel's 'false_pos' label incorrectly dismisses valid DI patterns. | backend/app/core/database.py#L42 |
| `C4|USED` | true_pos | **no (overturn)** | The code uses database session injection via Depends(get_db) in multiple endpoints (e.g., forum.py:48). The panel's 'false_pos' label fails to recognize this valid DI usage. | backend/app/api/v1/endpoints/forum.py#L48 |

### Missed by inventory (1)
- `Service dependency injection (e.g., Depends(get_cart_service))` @ backend/app/api/v1/endpoints/shop.py#L217 — The inventory did not capture service-level DI patterns like Depends(get_cart_service) used in shop.py:217, which represents a distinct DI fingerprint.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 35 | **false_pos** | [backend/app/api/v1/endpoints/blueos.py#L45](https://github.com/Leonidy431/klab_web/blob/cd41b440ba254eafde920c60354f6c62c6397296/backend/app/api/v1/endpoints/blueos.py#L45) |
| `C4|DEF` | C4 | 14 | **false_pos** | [backend/app/core/database.py#L63](https://github.com/Leonidy431/klab_web/blob/cd41b440ba254eafde920c60354f6c62c6397296/backend/app/core/database.py#L63) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/core/database.py#L42](https://github.com/Leonidy431/klab_web/blob/cd41b440ba254eafde920c60354f6c62c6397296/backend/app/core/database.py#L42) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 35 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/v1/endpoints/blueos.py#L45](https://github.com/Leonidy431/klab_web/blob/cd41b440ba254eafde920c60354f6c62c6397296/backend/app/api/v1/endpoints/blueos.py#L45)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [backend/app/core/database.py#L63](https://github.com/Leonidy431/klab_web/blob/cd41b440ba254eafde920c60354f6c62c6397296/backend/app/core/database.py#L63)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/core/database.py#L42](https://github.com/Leonidy431/klab_web/blob/cd41b440ba254eafde920c60354f6c62c6397296/backend/app/core/database.py#L42)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

