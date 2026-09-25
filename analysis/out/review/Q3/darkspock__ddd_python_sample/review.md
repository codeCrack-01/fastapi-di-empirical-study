# darkspock/ddd_python_sample

- GitHub: https://github.com/darkspock/ddd_python_sample
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 12 · commit: `a542d49b7846`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends with custom dependency resolvers` | adapters/http/api/bookings/routers/booking_router.py#L29 | The get_controller function is defined with Depends(get_session) and returns a BookingController with injected CommandBus/QueryBus. This is used in routes via controller: BookingController = Depend... |
| 2 | `FastAPI Depends with custom dependency resolvers` | adapters/http/api/clients/routers/client_router.py#L16 | Similar pattern to bookings: get_controller function creates ClientController with buses, injected via Depends(get_session) and used in routes. |
| 3 | `Generator-based dependency injection` | src/shared/infrastructure/database/session.py#L18 | get_session is a generator function yielding Session objects, used as a dependency via Depends(get_session) in controllers. |

## Pass 2 — reconcile with inventory of darkspock/ddd_python_sample

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI Depends with custom dependency resolvers (get_controller) that inject BookingController with CommandBus/QueryBus, matching the fingerprint's structural pattern. | adapters/http/api/bookings/routers/booking_router.py#L29 |
| `C4|DEF` | true_pos | **no (overturn)** | The get_session generator function in session.py is a valid dependency injection pattern used as a FastAPI dependency via Depends(get_session), contradicting the false_pos label. | src/shared/infrastructure/database/session.py#L18 |
| `C4|USED` | true_pos | **no (overturn)** | The test fixture in conftest.py defines a session dependency that matches the C4|USED pattern, contradicting the false_pos label. | tests/conftest.py#L10 |

### Missed by inventory (1)
- `FastAPI Depends with custom controller factories` @ adapters/http/api/clients/routers/client_router.py#L16 — The client_router.py file implements the same get_controller pattern as booking_router.py but was not included in the inventory's C1|BARE|SIG count.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 10 | **false_pos** | [adapters/http/api/bookings/routers/booking_router.py#L29](https://github.com/darkspock/ddd_python_sample/blob/a542d49b7846d93ea8f87eba914f0f17cb376a6d/adapters/http/api/bookings/routers/booking_router.py#L29) |
| `C4|DEF` | C4 | 1 | **false_pos** | [tests/conftest.py#L10](https://github.com/darkspock/ddd_python_sample/blob/a542d49b7846d93ea8f87eba914f0f17cb376a6d/tests/conftest.py#L10) |
| `C4|USED` | C4 | 1 | **false_pos** | [src/shared/infrastructure/database/session.py#L18](https://github.com/darkspock/ddd_python_sample/blob/a542d49b7846d93ea8f87eba914f0f17cb376a6d/src/shared/infrastructure/database/session.py#L18) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 10 · corpus total: 83548 · executor: x86_64
> example: [adapters/http/api/bookings/routers/booking_router.py#L29](https://github.com/darkspock/ddd_python_sample/blob/a542d49b7846d93ea8f87eba914f0f17cb376a6d/adapters/http/api/bookings/routers/booking_router.py#L29)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [tests/conftest.py#L10](https://github.com/darkspock/ddd_python_sample/blob/a542d49b7846d93ea8f87eba914f0f17cb376a6d/tests/conftest.py#L10)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [src/shared/infrastructure/database/session.py#L18](https://github.com/darkspock/ddd_python_sample/blob/a542d49b7846d93ea8f87eba914f0f17cb376a6d/src/shared/infrastructure/database/session.py#L18)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

