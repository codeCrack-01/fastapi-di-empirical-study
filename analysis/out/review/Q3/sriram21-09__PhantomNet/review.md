# sriram21-09/PhantomNet

- GitHub: https://github.com/sriram21-09/PhantomNet
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 178 · commit: `c39fa6f777cc`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=2 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection via Depends()` | backend/api/admin.py#L89 | The `Depends(get_db)` injects a database session, and `Depends(require_role("Admin"))` enforces role-based access control. This is FastAPI's standard DI pattern using `Depends()` to resolve depende... |
| 2 | `FastAPI built-in dependency injection via Depends()` | backend/api/admin.py#L121 | Same DI pattern as above, with `Depends(get_db)` for DB and `Depends(require_role("Admin"))` for authentication. |
| 3 | `FastAPI built-in dependency injection via Depends()` | backend/api/admin.py#L143 | Repeated use of `Depends(get_db)` and `Depends(require_role("Admin"))` in endpoint definitions, showing consistent DI usage across routes. |
| 4 | `FastAPI built-in dependency injection via Depends()` | backend/api/hunting.py#L65 | Dependency injection for `HuntingService(db)` via `Depends(get_db)`, though wrapped in a service class rather than directly using the DB session. |
| 5 | `FastAPI built-in dependency injection via Depends()` | backend/api/management.py#L77 | Use of `Depends(get_db)` and `Depends(get_api_key)` to inject both DB and API key validation, showing DI for authentication and data access. |

## Pass 2 — reconcile with inventory of sriram21-09/PhantomNet

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C2|BARE|ascopes`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true | **no (overturn)** | The code correctly uses FastAPI's Depends() for dependency injection (DB sessions and role-based access control), which aligns with the fingerprint's pattern. | backend/api/admin.py#L89 |
| `C4|DEF` | false_pos | yes | No contradictory code provided in the excerpts; the static instrument's label may be valid. | #L0 |

### Missed by inventory (1)
- `C1|BARE|PARAM` @ sentinel.py#L103 — No code excerpts provided for sentinel.py; cannot verify if this is a true positive or missed by inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 126 | **false_pos** | [backend/api/admin.py#L89](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/api/admin.py#L89) |
| `C4|DEF` | C4 | 48 | **false_pos** | [backend/main.py#L120](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/main.py#L120) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [backend/api/sentinel.py#L668](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/api/sentinel.py#L668) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [backend/api/management.py#L24](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/api/management.py#L24) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database/database.py#L143](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/database/database.py#L143) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 126 · corpus total: 83548 · executor: x86_64
> example: [backend/api/admin.py#L89](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/api/admin.py#L89)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 48 · corpus total: 56644 · executor: x86_64
> example: [backend/main.py#L120](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/main.py#L120)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [backend/api/sentinel.py#L668](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/api/sentinel.py#L668)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [backend/api/management.py#L24](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/api/management.py#L24)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database/database.py#L143](https://github.com/sriram21-09/PhantomNet/blob/c39fa6f777cc3544aed7b92f5f91e4df1ba9b7b6/backend/database/database.py#L143)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

