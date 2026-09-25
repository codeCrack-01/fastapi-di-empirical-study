# Upties/Geoatlas-x-NOS

- GitHub: https://github.com/Upties/Geoatlas-x-NOS
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 203 · commit: `af4235c3d0f3`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=0 known=2 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Repeated Code` | backend/app/main.py#L695 | The code for handling plan updates (portal_admin_update_plan) is duplicated in multiple places, leading to potential maintenance issues. For example, the same logic for checking duplicates and upda... |
| 2 | `Inefficient Query Construction` | backend/app/main.py#L707 | The portal_admin_invoices endpoint constructs a query with multiple joins and filters, but the use of 'desc(PortalInvoice.issued_at)' without explicit indexing could lead to performance issues if t... |
| 3 | `Lack of Input Validation` | backend/app/main.py#L719 | The portal_admin_create_invoice function directly uses payload.user_id without validating it against a Pydantic model, which could allow invalid or unexpected input types to reach the database layer. |

## Pass 2 — reconcile with inventory of Upties/Geoatlas-x-NOS

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C1|ELLIPSIS|SIG`, `C4|USED`, `C2|BARE|ascopes`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `repeated_code_plan_update` | Repeated Code @ backend/app/main.py:695 | **no (overturn)** | The code for handling plan updates is not duplicated in the provided code snippet. The logic appears only once in the portal_admin_update_plan function. | backend/app/main.py#L695 |
| `inefficient_query_invoice` | Inefficient Query Construction @ backend/app/main.py:707 | yes | The portal_admin_invoices endpoint uses 'desc(PortalInvoice.issued_at)' without explicit indexing, which could lead to performance issues if the dataset grows large. | backend/app/main.py#L707 |
| `input_validation_invoice` | Lack of Input Validation @ backend/app/main.py:719 | **no (overturn)** | The portal_admin_create_invoice function uses 'payload.user_id' which is validated via the Pydantic model 'PortalInvoiceCreateRequest'. Input validation is present through the model. | backend/app/main.py#L719 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 128 | **false_pos** | [backend/app/main.py#L343](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/backend/app/main.py#L343) |
| `C1|BARE|PARAM` | C1 | 69 | **known** | [backend/app/main.py#L799](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/backend/app/main.py#L799) |
| `C1|ELLIPSIS|SIG` | C1 | 2 | **false_pos** | [commercial_portal/backend/app/auth.py#L146](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/commercial_portal/backend/app/auth.py#L146) |
| `C4|USED` | C4 | 2 | **false_pos** | [backend/app/database.py#L60](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/backend/app/database.py#L60) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [backend/app/public_api_keys.py#L56](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/backend/app/public_api_keys.py#L56) |
| `C4|DEF` | C4 | 1 | **false_pos** | [commercial_portal/backend/app/main.py#L48](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/commercial_portal/backend/app/main.py#L48) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 128 · corpus total: 83548 · executor: x86_64
> example: [backend/app/main.py#L343](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/backend/app/main.py#L343)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 69 · corpus total: 18195 · executor: x86_64
> example: [backend/app/main.py#L799](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/backend/app/main.py#L799)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|ELLIPSIS|SIG` — **false_pos**
> occurrences here: 2 · corpus total: 201 · executor: x86_64
> example: [commercial_portal/backend/app/auth.py#L146](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/commercial_portal/backend/app/auth.py#L146)

> **evidence (model):** Ellipsis (...) as a dependency argument is not a valid FastAPI DI construct; it appears to be a placeholder or incomplete code rather than an actual dependency injection usage.

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database.py#L60](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/backend/app/database.py#L60)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [backend/app/public_api_keys.py#L56](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/backend/app/public_api_keys.py#L56)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [commercial_portal/backend/app/main.py#L48](https://github.com/Upties/Geoatlas-x-NOS/blob/af4235c3d0f3c070701d2d316ef539f0b9301f43/commercial_portal/backend/app/main.py#L48)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

