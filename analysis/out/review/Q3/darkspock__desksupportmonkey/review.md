# darkspock/desksupportmonkey

- GitHub: https://github.com/darkspock/desksupportmonkey
- Stars: 21 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 1192 · commit: `40552d70a4c2`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI function-based dependency injection` | adapters/http/api/addresses/dependencies.py#L11 | The `get_address_repo` function uses `Depends(get_db)` to inject a database session, then returns a `ShippingAddressRepository` instance. This is a factory function that provides a repository depen... |
| 2 | `FastAPI route parameter injection` | adapters/http/api/addresses/routers.py#L94 | The `create_address` route uses `address_repo: ShippingAddressRepository = Depends(get_address_repo)` to inject a repository instance, demonstrating dependency injection in route handlers. |
| 3 | `Multi-layered dependency chain` | adapters/http/api/appointments/routers.py#L125 | The `create_appointment` route injects multiple dependencies (`appointment_repo`, `db`, `event_bus`) via `Depends()`, showing a layered DI approach with repositories, databases, and event buses. |
| 4 | `Role-based dependency injection` | adapters/http/api/appointments/routers.py#L256 | The `confirm_appointment` route uses `Depends(require_role(UserRole.TECHNICIAN))` to inject user authentication with role-based access control. |

## Pass 2 — reconcile with inventory of darkspock/desksupportmonkey

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's Depends() for repository injection (e.g., adapters/http/api/addresses/routers.py:94 shows proper DI in route handlers) | adapters/http/api/addresses/routers.py#L94 |
| `C4|DEF` | false_pos | yes | No contradictory code found in tests/conftest.py (inventory may have correctly identified test-related DI as false positives) | tests/conftest.py#L41 |
| `C4|USED` | false_pos | yes | No contradictory code found in core/database.py (inventory may have correctly identified basic DB dependency as false positive) | core/database.py#L32 |

### Missed by inventory (1)
- `Multi-layered DI with repositories, databases, and event buses` @ adapters/http/api/appointments/routers.py#L125 — The inventory may have missed complex dependency chains involving multiple injected services

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 1154 | **false_pos** | [adapters/http/api/addresses/dependencies.py#L11](https://github.com/darkspock/desksupportmonkey/blob/40552d70a4c2b76fa736fbcd3dc6014edfb59a74/adapters/http/api/addresses/dependencies.py#L11) |
| `C4|DEF` | C4 | 37 | **false_pos** | [tests/conftest.py#L41](https://github.com/darkspock/desksupportmonkey/blob/40552d70a4c2b76fa736fbcd3dc6014edfb59a74/tests/conftest.py#L41) |
| `C4|USED` | C4 | 1 | **false_pos** | [core/database.py#L32](https://github.com/darkspock/desksupportmonkey/blob/40552d70a4c2b76fa736fbcd3dc6014edfb59a74/core/database.py#L32) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 1154 · corpus total: 83548 · executor: x86_64
> example: [adapters/http/api/addresses/dependencies.py#L11](https://github.com/darkspock/desksupportmonkey/blob/40552d70a4c2b76fa736fbcd3dc6014edfb59a74/adapters/http/api/addresses/dependencies.py#L11)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 37 · corpus total: 56644 · executor: x86_64
> example: [tests/conftest.py#L41](https://github.com/darkspock/desksupportmonkey/blob/40552d70a4c2b76fa736fbcd3dc6014edfb59a74/tests/conftest.py#L41)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [core/database.py#L32](https://github.com/darkspock/desksupportmonkey/blob/40552d70a4c2b76fa736fbcd3dc6014edfb59a74/core/database.py#L32)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

