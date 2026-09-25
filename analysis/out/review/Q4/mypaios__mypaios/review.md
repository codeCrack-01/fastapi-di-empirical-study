# mypaios/mypaios

- GitHub: https://github.com/mypaios/mypaios
- Stars: 67 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 217 · commit: `78ef0676242f`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection via FastAPI Depends()` | routes/contacts_routes.py#L747 | The 'export_contacts' route uses 'Depends(require_admin)' to inject an admin authentication dependency, following FastAPI's DI pattern where dependencies are explicitly declared and managed separat... |
| 2 | `Dependency Injection via FastAPI Depends()` | routes/email_routes.py#L972 | The 'list_emails' route injects 'owner' via 'Depends(require_owner)', decoupling email listing logic from user authentication implementation, a hallmark of FastAPI's DI approach. |
| 3 | `Service Layer Injection` | routes/contacts_routes.py#L774 | The '_validate_carddav_url' function is called within 'update_config', indicating injection of a validation service to handle URL validation, separating configuration logic from validation concerns. |

## Pass 2 — reconcile with inventory of mypaios/mypaios

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `dependency_injection_contacts_export` | Dependency Injection via FastAPI Depends() | yes | The 'export_contacts' route correctly uses 'Depends(require_admin)' for admin authentication, aligning with FastAPI's DI pattern. | routes/contacts_routes.py#L747 |
| `dependency_injection_email_list` | Dependency Injection via FastAPI Depends() | yes | The 'list_emails' route properly injects 'owner' via 'Depends(require_owner)', decoupling email listing logic from authentication. | routes/email_routes.py#L972 |
| `service_layer_injection_update_config` | Service Layer Injection | yes | The 'update_config' route correctly calls '_validate_carddav_url' as a validation service, separating configuration logic from validation concerns. | routes/contacts_routes.py#L774 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 138 | **false_pos** | [routes/activity_routes.py#L26](https://github.com/mypaios/mypaios/blob/78ef0676242f9f77dba7d1d6149b4b1ad0c30d56/routes/activity_routes.py#L26) |
| `C4|DEF` | C4 | 78 | **false_pos** | [app.py#L982](https://github.com/mypaios/mypaios/blob/78ef0676242f9f77dba7d1d6149b4b1ad0c30d56/app.py#L982) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [routes/embedding_routes.py#L118](https://github.com/mypaios/mypaios/blob/78ef0676242f9f77dba7d1d6149b4b1ad0c30d56/routes/embedding_routes.py#L118) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 138 · corpus total: 83548 · executor: x86_64
> example: [routes/activity_routes.py#L26](https://github.com/mypaios/mypaios/blob/78ef0676242f9f77dba7d1d6149b4b1ad0c30d56/routes/activity_routes.py#L26)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 78 · corpus total: 56644 · executor: x86_64
> example: [app.py#L982](https://github.com/mypaios/mypaios/blob/78ef0676242f9f77dba7d1d6149b4b1ad0c30d56/app.py#L982)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [routes/embedding_routes.py#L118](https://github.com/mypaios/mypaios/blob/78ef0676242f9f77dba7d1d6149b4b1ad0c30d56/routes/embedding_routes.py#L118)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

