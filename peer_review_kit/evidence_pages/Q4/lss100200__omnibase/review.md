# lss100200/omnibase

- GitHub: https://github.com/lss100200/omnibase
- Stars: 54 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 306 · commit: `96711e8ef193`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI standard dependency injection` | backend/src/omnibase/agent_alpha/router.py#L56 | The `ctx: TenantContext = Depends(get_current_tenant)` pattern shows FastAPI's built-in DI via Depends() resolving tenant context. Similar patterns appear in multiple routes. |
| 2 | `Service dependency injection` | backend/src/omnibase/agent_registry/router.py#L141 | The `control: AgentRegistryControlService = Depends(get_registry_control_plane)` demonstrates injecting service objects through DI, with explicit naming of the service interface. |
| 3 | `Authentication context injection` | backend/src/omnibase/auth/router.py#L182 | The `principal: CurrentPrincipal = Depends(get_current_principal)` shows DI for authentication context, a common pattern in secured endpoints. |

## Pass 2 — reconcile with inventory of lss100200/omnibase

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection_tenant_context` | FastAPI standard dependency injection | yes | The code explicitly uses `Depends(get_current_tenant)` for tenant context injection in multiple routes, confirming the observation. | backend/src/omnibase/agent_alpha/router.py#L56 |
| `service_dependency_injection` | Service dependency injection | yes | The code uses `Depends(get_registry_control_plane)` to inject service objects, matching the observation. | backend/src/omnibase/agent_registry/router.py#L141 |
| `auth_context_injection` | Authentication context injection | yes | The code uses `Depends(get_current_principal)` for authentication context, confirming the observation. | backend/src/omnibase/auth/router.py#L182 |

### Missed by inventory (2)
- `database_session_dependency_injection` @ backend/src/omnibase/agent_skills/router.py#L139 — The code uses `db: Session = Depends(get_tenant_db)` for database session injection, which was not mentioned in the initial observations.
- `gateway_database_dependency_injection` @ backend/src/omnibase/capability_gateway/router.py#L149 — The code uses `session: Session = Depends(get_gateway_db)` for gateway database injection, which was not mentioned in the initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 190 | **false_pos** | [backend/src/omnibase/agent_alpha/router.py#L56](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/agent_alpha/router.py#L56) |
| `C4|DEF` | C4 | 76 | **false_pos** | [backend/src/omnibase/agent_alpha/router.py#L244](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/agent_alpha/router.py#L244) |
| `C1|BARE|PARAM` | C1 | 19 | **known** | [backend/src/omnibase/auth/router.py#L59](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/auth/router.py#L59) |
| `C3|CLASS|BARE` | C3 | 18 | **false_pos** | [backend/src/omnibase/core/rate_limit.py#L158](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/core/rate_limit.py#L158) |
| `C4|USED` | C4 | 3 | **false_pos** | [backend/src/omnibase/capability_gateway/router.py#L112](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/capability_gateway/router.py#L112) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 190 · corpus total: 83548 · executor: x86_64
> example: [backend/src/omnibase/agent_alpha/router.py#L56](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/agent_alpha/router.py#L56)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 76 · corpus total: 56644 · executor: x86_64
> example: [backend/src/omnibase/agent_alpha/router.py#L244](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/agent_alpha/router.py#L244)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 19 · corpus total: 18195 · executor: x86_64
> example: [backend/src/omnibase/auth/router.py#L59](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/auth/router.py#L59)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 18 · corpus total: 20139 · executor: x86_64
> example: [backend/src/omnibase/core/rate_limit.py#L158](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/core/rate_limit.py#L158)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 3 · corpus total: 1079 · executor: x86_64
> example: [backend/src/omnibase/capability_gateway/router.py#L112](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/capability_gateway/router.py#L112)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

