# moranch/grok-register

- GitHub: https://github.com/moranch/grok-register
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 81 · commit: `39595f4a6e3a`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection with stateful resolvers` | apps/console/api/captcha.py#L22 | The APIRouter uses dependencies=[Depends(check_auth)] to inject an authentication check function. This is a standard FastAPI dependency injection pattern where check_auth is resolved at request time. |
| 2 | `Stateful service retrieval via custom dependency functions` | vendor/grok2api/app/products/web/admin/assets.py#L99 | The endpoint uses repo: "AccountRepository" = Depends(get_repo) where get_repo is a function that retrieves a singleton AccountRepository from request.app.state. This shows a layered DI pattern whe... |
| 3 | `Multiple service injection in endpoints` | vendor/grok2api/app/products/web/admin/batch.py#L241 | The batch_refresh endpoint injects both repo and refresh_svc through Depends(), demonstrating injection of multiple services (repository and refresh service) into a single endpoint. |

## Pass 2 — reconcile with inventory of moranch/grok-register

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code correctly uses FastAPI Depends() for authentication injection in captcha.py:22, exporters.py:32, and platforms.py:27. These are valid DI patterns, not false positives. | apps/console/api/captcha.py#L22 |
| `C1|BARE|PARAM` | known | yes | The code in captcha.py:22, exporters.py:32, and platforms.py:27 correctly uses Depends() with stateful resolvers. These match the 'known' label for parameterized DI. | apps/console/api/exporters.py#L32 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code in assets.py:69, 99, 112 correctly uses Depends() for service injection (get_repo). This is valid DI, not a false positive. | vendor/grok2api/app/products/web/admin/assets.py#L99 |

### Missed by inventory (2)
- `Multiple service injection in endpoints` @ vendor/grok2api/app/products/web/admin/batch.py#L241 — The batch_refresh endpoint injects both repo and refresh_svc via Depends(), demonstrating a DI pattern not captured by the inventory.
- `Stateful service retrieval via custom dependency functions` @ vendor/grok2api/app/products/web/admin/assets.py#L99 — The use of get_repo() to retrieve stateful services from request.app.state is a DI pattern not identified by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 47 | **false_pos** | [apps/console/_vendor_aar/application/task_commands.py#L32](https://github.com/moranch/grok-register/blob/39595f4a6e3a6b13d9e88efa3df73bc7f6b24340/apps/console/_vendor_aar/application/task_commands.py#L32) |
| `C1|BARE|PARAM` | C1 | 17 | **known** | [apps/console/api/captcha.py#L22](https://github.com/moranch/grok-register/blob/39595f4a6e3a6b13d9e88efa3df73bc7f6b24340/apps/console/api/captcha.py#L22) |
| `C1|BARE|SIG` | C1 | 17 | **false_pos** | [vendor/grok2api/app/products/web/admin/assets.py#L69](https://github.com/moranch/grok-register/blob/39595f4a6e3a6b13d9e88efa3df73bc7f6b24340/vendor/grok2api/app/products/web/admin/assets.py#L69) |

## `C4|DEF` — **false_pos**
> occurrences here: 47 · corpus total: 56644 · executor: x86_64
> example: [apps/console/_vendor_aar/application/task_commands.py#L32](https://github.com/moranch/grok-register/blob/39595f4a6e3a6b13d9e88efa3df73bc7f6b24340/apps/console/_vendor_aar/application/task_commands.py#L32)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 17 · corpus total: 18195 · executor: x86_64
> example: [apps/console/api/captcha.py#L22](https://github.com/moranch/grok-register/blob/39595f4a6e3a6b13d9e88efa3df73bc7f6b24340/apps/console/api/captcha.py#L22)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 17 · corpus total: 83548 · executor: x86_64
> example: [vendor/grok2api/app/products/web/admin/assets.py#L69](https://github.com/moranch/grok-register/blob/39595f4a6e3a6b13d9e88efa3df73bc7f6b24340/vendor/grok2api/app/products/web/admin/assets.py#L69)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

