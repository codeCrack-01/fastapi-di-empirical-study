# GiZano/QuakeGuard

- GitHub: https://github.com/GiZano/QuakeGuard
- Stars: 18 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 39 · commit: `90d678bdc776`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=2 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Depends()` | backend/src/main.py#L416 | The route @app.post("/zones/") uses dependencies=[Depends(verify_api_key)] to inject an API key verification dependency. This is a core FastAPI pattern where dependencies are declared using Depends... |
| 2 | `Database Session Injection via get_db` | backend/src/main.py#L415 | The parameter db: Session = Depends(get_db) shows a common DI pattern where a database session is injected into route handlers via the get_db dependency. This function is defined in database.py and... |
| 3 | `Nested Dependency Injection` | backend/src/main.py#L520 | The route @app.post("/readings/") uses Depends(validate_iot_payload) which itself depends on Depends(verify_api_key) and Depends(get_db), demonstrating nested dependency resolution. |
| 4 | `Generator-based Dependency` | backend/src/database.py#L51 | The get_db function is a generator that yields a database session, fulfilling the dependency requirements of routes that depend on it. This is indicated by the yield statement in the function. |

## Pass 2 — reconcile with inventory of GiZano/QuakeGuard

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|DEF`, `C2|BARE|ascopes`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | real_dependency | **no (overturn)** | The verify_api_key dependency is explicitly used in route handlers (e.g., @app.post("/zones/") with dependencies=[Depends(verify_api_key)]). This is a valid FastAPI DI pattern, not a false positive. | backend/src/main.py#L416 |
| `C1|BARE|PARAM` | known | yes | The db: Session = Depends(get_db) pattern is correctly identified as a known parameter injection. The get_db generator is explicitly used in route handlers. | backend/src/main.py#L415 |
| `C4|DEF` | real_dependency | **no (overturn)** | The get_db function is a real dependency injected into routes (e.g., @app.post("/readings/") with Depends(validate_iot_payload) which internally uses get_db). The static label incorrectly marks thi... | backend/src/main.py#L520 |
| `C2|BARE|ascopes` | known | yes | The verify_api_key function is a valid dependency used in route handlers (e.g., @app.post("/zones/") with dependencies=[Depends(verify_api_key)]). The static label correctly identifies this as a kn... | backend/src/security.py#L31 |
| `C4|USED` | real_dependency | **no (overturn)** | The get_db generator is explicitly used in route handlers (e.g., @app.post("/readings/") with Depends(validate_iot_payload) which internally uses get_db). The static label incorrectly marks this as... | backend/src/database.py#L51 |

### Missed by inventory (2)
- `Nested dependency chains (e.g., Depends(validate_iot_payload) → Depends(verify_api_key) → Depends(get_db))` @ backend/src/main.py#L520 — The inventory failed to capture multi-level dependency resolution in route handlers.
- `Generator-based dependency injection (get_db yields a session)` @ backend/src/database.py#L51 — The inventory did not explicitly recognize the generator pattern in get_db.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 15 | **false_pos** | [backend/src/main.py#L416](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/main.py#L416) |
| `C1|BARE|PARAM` | C1 | 13 | **known** | [backend/src/main.py#L299](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/main.py#L299) |
| `C4|DEF` | C4 | 9 | **false_pos** | [backend/src/main.py#L127](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/main.py#L127) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [backend/src/security.py#L31](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/security.py#L31) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/src/database.py#L51](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/database.py#L51) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 15 · corpus total: 83548 · executor: x86_64
> example: [backend/src/main.py#L416](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/main.py#L416)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 13 · corpus total: 18195 · executor: x86_64
> example: [backend/src/main.py#L299](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/main.py#L299)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 9 · corpus total: 56644 · executor: x86_64
> example: [backend/src/main.py#L127](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/main.py#L127)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [backend/src/security.py#L31](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/security.py#L31)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/src/database.py#L51](https://github.com/GiZano/QuakeGuard/blob/90d678bdc7762b285102a33fa6c58a8d86003496/backend/src/database.py#L51)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

