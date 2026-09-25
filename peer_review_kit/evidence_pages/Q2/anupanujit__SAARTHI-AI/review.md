# anupanujit/SAARTHI-AI

- GitHub: https://github.com/anupanujit/SAARTHI-AI
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 52 · commit: `a522a87d5c37`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Role-Based Access Control (RBAC)` | backend/routers/brief_router.py#L84 | The code checks if an FSR user has access to an outlet via 'outlet.assigned_fsr_id == user.id' (line 84), enforcing role-specific permissions. Similar checks exist in 'cached_brief' and 'brief_hist... |
| 2 | `Caching Strategy` | backend/routers/brief_router.py#L145 | The 'cached_brief' endpoint retrieves precomputed AgenticBrief records from the database, indicating a caching layer to avoid redundant AI generation (line 145-146). |
| 3 | `Real-Time Alerting` | backend/routers/manager_router.py#L33 | The 'alerts' endpoint queries live outlet data for low stock alerts (line 33-40), demonstrating real-time monitoring and alert generation for operational risks. |
| 4 | `Data Aggregation for Analytics` | backend/routers/manager_router.py#L99 | The 'field_performance' endpoint aggregates FSR performance metrics (line 99-115), enabling management to track team productivity and completion rates. |
| 5 | `Permissions Enforcement` | backend/routers/outlets_router.py#L48 | The '_visible_outlets' helper filters outlets by FSR assignment (line 48), ensuring users only see data they're authorized to access. |

## Pass 2 — reconcile with inventory of anupanujit/SAARTHI-AI

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `role-based-access-control` | Role-Based Access Control (RBAC) | yes | Code enforces FSR-specific outlet access via 'outlet.assigned_fsr_id == user.id' in multiple endpoints (brief_router.py:84, cached_brief, brief_history). | backend/routers/brief_router.py#L84 |
| `caching-strategy` | Caching Strategy | yes | cached_brief endpoint retrieves precomputed AgenticBrief records (brief_router.py:145-146), avoiding redundant AI generation. | backend/routers/brief_router.py#L145 |
| `real-time-alerting` | Real-Time Alerting | yes | alerts endpoint queries live outlet data for low stock alerts (manager_router.py:33-40), demonstrating real-time monitoring. | backend/routers/manager_router.py#L33 |
| `data-aggregation` | Data Aggregation for Analytics | yes | field_performance endpoint aggregates FSR metrics (manager_router.py:99-115), enabling productivity tracking. | backend/routers/manager_router.py#L99 |
| `permissions-enforcement` | Permissions Enforcement | yes | _visible_outlets filters outlets by FSR assignment (outlets_router.py:48), ensuring data visibility rules. | backend/routers/outlets_router.py#L48 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 49 | **false_pos** | [backend/auth.py#L59](https://github.com/anupanujit/SAARTHI-AI/blob/a522a87d5c3701b5876354cb80432e97e96998ef/backend/auth.py#L59) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [backend/routers/admin_competitor_router.py#L21](https://github.com/anupanujit/SAARTHI-AI/blob/a522a87d5c3701b5876354cb80432e97e96998ef/backend/routers/admin_competitor_router.py#L21) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database.py#L16](https://github.com/anupanujit/SAARTHI-AI/blob/a522a87d5c3701b5876354cb80432e97e96998ef/backend/database.py#L16) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 49 · corpus total: 83548 · executor: x86_64
> example: [backend/auth.py#L59](https://github.com/anupanujit/SAARTHI-AI/blob/a522a87d5c3701b5876354cb80432e97e96998ef/backend/auth.py#L59)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [backend/routers/admin_competitor_router.py#L21](https://github.com/anupanujit/SAARTHI-AI/blob/a522a87d5c3701b5876354cb80432e97e96998ef/backend/routers/admin_competitor_router.py#L21)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database.py#L16](https://github.com/anupanujit/SAARTHI-AI/blob/a522a87d5c3701b5876354cb80432e97e96998ef/backend/database.py#L16)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

