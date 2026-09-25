# Devathmaj/VoucherBot

- GitHub: https://github.com/Devathmaj/VoucherBot
- Stars: 14 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 14 · commit: `4e5d823175aa`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | voucherbot/api/routers/health.py#L13 | The health_check function uses Depends(get_session) to inject an AsyncSession, and Depends(health_rate_limit) as a route-level dependency. This is FastAPI's standard DI pattern. |
| 2 | `Test dependency override` | tests/test_main.py#L24 | The _override_db_session fixture uses app.dependency_overrides to replace get_session with a mock, demonstrating FastAPI's testing DI capabilities. |

## Pass 2 — reconcile with inventory of Devathmaj/VoucherBot

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | Test fixtures (e.g., tests/conftest.py#L7) are not FastAPI DI occurrences but pytest fixtures, aligning with the label. | tests/conftest.py#L7 |
| `C1|BARE|PARAM` | known | yes | Depends(get_session) in voucherbot/api/routers/health.py#L11-12 is valid FastAPI parameter injection. | voucherbot/api/routers/health.py#L11 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | health_check's session parameter (voucherbot/api/routers/health.py#L13) uses Depends correctly as a FastAPI DI occurrence. | voucherbot/api/routers/health.py#L13 |
| `C4|USED` | false_pos | **no (overturn)** | get_session (voucherbot/database/connection.py#L64) is a FastAPI dependency used in route handlers. | voucherbot/database/connection.py#L64 |

### Missed by inventory (2)
- `FastAPI route-level dependency injection` @ voucherbot/api/routers/health.py#L13 — Dependencies=[Depends(health_rate_limit)] in route decorators were not inventoried.
- `Test dependency override via app.dependency_overrides` @ tests/test_main.py#L24 — The _override_db_session fixture's use of app.dependency_overrides was not inventoried.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 10 | **false_pos** | [tests/conftest.py#L7](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/tests/conftest.py#L7) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [voucherbot/api/routers/health.py#L11](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/voucherbot/api/routers/health.py#L11) |
| `C1|BARE|SIG` | C1 | 1 | **false_pos** | [voucherbot/api/routers/health.py#L13](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/voucherbot/api/routers/health.py#L13) |
| `C4|USED` | C4 | 1 | **false_pos** | [voucherbot/database/connection.py#L64](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/voucherbot/database/connection.py#L64) |

## `C4|DEF` — **false_pos**
> occurrences here: 10 · corpus total: 56644 · executor: x86_64
> example: [tests/conftest.py#L7](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/tests/conftest.py#L7)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [voucherbot/api/routers/health.py#L11](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/voucherbot/api/routers/health.py#L11)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 1 · corpus total: 83548 · executor: x86_64
> example: [voucherbot/api/routers/health.py#L13](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/voucherbot/api/routers/health.py#L13)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [voucherbot/database/connection.py#L64](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/voucherbot/database/connection.py#L64)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

