# commercialbrainz/CommercialBrainz

- GitHub: https://github.com/commercialbrainz/CommercialBrainz
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 281 · commit: `8ff044622499`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | backend/app/api/v1/admin.py#L97 | The function admin_stats uses Depends(get_db) and Depends(require_admin) to inject database session and admin authentication dependencies. This is FastAPI's standard DI pattern where dependencies a... |
| 2 | `Repeated use of authentication dependency` | backend/app/api/v1/admin.py#L139 | The list_users function also uses Depends(require_admin) to enforce admin authentication, showing this is a common pattern across multiple endpoints. |
| 3 | `Database session injection` | backend/app/api/v1/admin.py#L159 | Every endpoint in this file uses Depends(get_db) to inject an AsyncSession for database operations, demonstrating consistent DI usage for database access. |

## Pass 2 — reconcile with inventory of commercialbrainz/CommercialBrainz

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 278 | **false_pos** | [backend/app/api/v1/admin.py#L96](https://github.com/commercialbrainz/CommercialBrainz/blob/8ff0446224991c01eac470558351ecfaccb1f0fc/backend/app/api/v1/admin.py#L96) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/app/main.py#L18](https://github.com/commercialbrainz/CommercialBrainz/blob/8ff0446224991c01eac470558351ecfaccb1f0fc/backend/app/main.py#L18) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/database.py#L22](https://github.com/commercialbrainz/CommercialBrainz/blob/8ff0446224991c01eac470558351ecfaccb1f0fc/backend/app/database.py#L22) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 278 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/v1/admin.py#L96](https://github.com/commercialbrainz/CommercialBrainz/blob/8ff0446224991c01eac470558351ecfaccb1f0fc/backend/app/api/v1/admin.py#L96)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L18](https://github.com/commercialbrainz/CommercialBrainz/blob/8ff0446224991c01eac470558351ecfaccb1f0fc/backend/app/main.py#L18)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database.py#L22](https://github.com/commercialbrainz/CommercialBrainz/blob/8ff0446224991c01eac470558351ecfaccb1f0fc/backend/app/database.py#L22)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

