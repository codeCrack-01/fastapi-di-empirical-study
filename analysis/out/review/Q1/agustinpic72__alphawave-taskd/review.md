# agustinpic72/alphawave-taskd

- GitHub: https://github.com/agustinpic72/alphawave-taskd
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 213 · commit: `fefd82e65ae4`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Exception Handling` | backend/app/api/routes.py#L253 | Multiple endpoints use try-except blocks to catch ValueErrors and SecretStoreUnavailable exceptions, raising HTTPExceptions with consistent error handling. This pattern is repeated in save_openai_c... |

## Pass 2 — reconcile with inventory of agustinpic72/alphawave-taskd

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `exception_handling_pattern` | Exception Handling | yes | Multiple endpoints (save_openai_credentials, save_trello_manual_credentials, validate_trello_manual_credentials) use consistent try-except blocks for ValueError/SecretStoreUnavailable with HTTPExce... | backend/app/api/routes.py#L253 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 203 | **false_pos** | [backend/app/api/deps.py#L38](https://github.com/agustinpic72/alphawave-taskd/blob/fefd82e65ae4a235eecce0068389b41a97399dfc/backend/app/api/deps.py#L38) |
| `C4|DEF` | C4 | 8 | **false_pos** | [backend/app/main.py#L28](https://github.com/agustinpic72/alphawave-taskd/blob/fefd82e65ae4a235eecce0068389b41a97399dfc/backend/app/main.py#L28) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [backend/app/api/routes.py#L88](https://github.com/agustinpic72/alphawave-taskd/blob/fefd82e65ae4a235eecce0068389b41a97399dfc/backend/app/api/routes.py#L88) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/core/db.py#L274](https://github.com/agustinpic72/alphawave-taskd/blob/fefd82e65ae4a235eecce0068389b41a97399dfc/backend/app/core/db.py#L274) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 203 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/deps.py#L38](https://github.com/agustinpic72/alphawave-taskd/blob/fefd82e65ae4a235eecce0068389b41a97399dfc/backend/app/api/deps.py#L38)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 8 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L28](https://github.com/agustinpic72/alphawave-taskd/blob/fefd82e65ae4a235eecce0068389b41a97399dfc/backend/app/main.py#L28)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/routes.py#L88](https://github.com/agustinpic72/alphawave-taskd/blob/fefd82e65ae4a235eecce0068389b41a97399dfc/backend/app/api/routes.py#L88)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/core/db.py#L274](https://github.com/agustinpic72/alphawave-taskd/blob/fefd82e65ae4a235eecce0068389b41a97399dfc/backend/app/core/db.py#L274)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

