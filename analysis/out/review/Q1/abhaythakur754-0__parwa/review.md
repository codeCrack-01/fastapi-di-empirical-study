# abhaythakur754-0/parwa

- GitHub: https://github.com/abhaythakur754-0/parwa
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1412 · commit: `9279105e8d33`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | backend/app/api/admin.py#L104 | The 'list_clients' function uses 'Depends(require_platform_admin)' and 'Depends(get_db)' to inject user authentication and database session dependencies. This is a standard FastAPI pattern where de... |
| 2 | `Role-based injection` | backend/app/api/ai_agent.py#L136 | The 'list_agents' function uses 'Depends(require_roles("owner", "admin"))' to inject role-based access control. This shows a variation of DI that enforces specific user roles as a dependency. |
| 3 | `Scoped dependency injection` | backend/app/api/ai_agent.py#L138 | The 'company_id' parameter uses 'Depends(get_company_id)' to inject a company-scoped identifier. This demonstrates DI for contextual scoping rather than just authentication or database access. |

## Pass 2 — reconcile with inventory of abhaythakur754-0/parwa

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|ELLIPSIS|SIG`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true | **no (overturn)** | The code explicitly uses FastAPI Depends() for dependency injection (e.g., Depends(require_platform_admin), Depends(get_db)), which matches the fingerprint's pattern of bare signal DI. | backend/app/api/admin.py#L104 |
| `C1|BARE|SIG` | true | **no (overturn)** | The code uses Depends() for role-based access control (Depends(require_roles(...))) and scoped dependencies (Depends(get_company_id)), which are valid DI patterns. | backend/app/api/ai_agent.py#L136 |

### Missed by inventory (2)
- `Role-based DI with Depends(require_roles(...))` @ backend/app/api/ai_agent.py#L136 — The inventory likely missed DI patterns involving role-based access control, which is a valid form of dependency injection.
- `Scoped DI with Depends(get_company_id)` @ backend/app/api/ai_agent.py#L138 — The inventory may not have captured DI patterns that inject contextual scoping (e.g., company_id) via Depends().

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 1245 | **false_pos** | [backend/app/api/admin.py#L104](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/app/api/admin.py#L104) |
| `C4|DEF` | C4 | 152 | **false_pos** | [backend/app/api/sse.py#L84](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/app/api/sse.py#L84) |
| `C1|ELLIPSIS|SIG` | C1 | 9 | **false_pos** | [backend/app/api/superglue_actions.py#L58](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/app/api/superglue_actions.py#L58) |
| `C1|BARE|PARAM` | C1 | 5 | **known** | [backend/app/api/crm_webhooks.py#L264](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/app/api/crm_webhooks.py#L264) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database/base.py#L91](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/database/base.py#L91) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 1245 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/admin.py#L104](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/app/api/admin.py#L104)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 152 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/sse.py#L84](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/app/api/sse.py#L84)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|ELLIPSIS|SIG` — **false_pos**
> occurrences here: 9 · corpus total: 201 · executor: x86_64
> example: [backend/app/api/superglue_actions.py#L58](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/app/api/superglue_actions.py#L58)

> **evidence (model):** Ellipsis (...) as a dependency argument is not a valid FastAPI DI construct; it appears to be a placeholder or incomplete code rather than an actual dependency injection usage.

## `C1|BARE|PARAM` — **known**
> occurrences here: 5 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/crm_webhooks.py#L264](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/app/api/crm_webhooks.py#L264)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database/base.py#L91](https://github.com/abhaythakur754-0/parwa/blob/9279105e8d335f5778549d8c296e0e7045e2f017/backend/database/base.py#L91)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

