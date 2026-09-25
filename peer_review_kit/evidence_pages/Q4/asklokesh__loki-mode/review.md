# asklokesh/loki-mode

- GitHub: https://github.com/asklokesh/loki-mode
- Stars: 1031 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 326 · commit: `d405f5a7f92b`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=1 known=2 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Depends` | dashboard/api_v2.py#L465 | Multiple route handlers use Depends() to inject auth scopes (e.g., auth.require_scope("control")) and tenant context (resolve_tenant_context). This is FastAPI's core DI pattern where dependencies a... |
| 2 | `Custom Dependency Scopes` | dashboard/api_v2.py#L488 | The auth module implements scope-based access control through require_scope(), which is used as a dependency in routes like list_runs() with Depends(auth.require_scope("read")). This creates a reus... |
| 3 | `Tenant Context Injection` | dashboard/api_v2.py#L465 | The resolve_tenant_context dependency is used across multiple routes to inject tenant-specific context, enabling scoped access control as seen in create_run() and get_run() functions. |

## Pass 2 — reconcile with inventory of asklokesh/loki-mode

_Presented fingerprints:_ `C1|DOTTED|PARAM`, `C4|DEF`, `C1|BARE|SIG`, `C1|DOTTED|SIG`, `C1|BARE|PARAM`, `C2|BARE|ascopes`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `tenant_context_enforcement` | tenant_context_enforcement | yes | All routes using tenant_ctx enforce tenant boundaries via tenant_ctx.enforce() or _enforce_project_tenant/_enforce_run_tenant | dashboard/api_v2.py#L465 |
| `audit_logging_pattern` | audit_logging_pattern | yes | All CRUD operations use audit.log_event() with consistent parameters (action, resource_type, resource_id) | dashboard/api_v2.py#L429 |
| `scoped_access_control` | scoped_access_control | yes | Dependencies like auth.require_scope() and tenant_ctx enforcement implement multi-layered access control | dashboard/api_v2.py#L488 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|DOTTED|PARAM` | C1 | 175 | **variant** | [collab/api.py#L62](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/collab/api.py#L62) |
| `C4|DEF` | C4 | 75 | **false_pos** | [autonomy/lib/assets_bundle.py#L126](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/autonomy/lib/assets_bundle.py#L126) |
| `C1|BARE|SIG` | C1 | 45 | **false_pos** | [dashboard/api_v2.py#L325](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/dashboard/api_v2.py#L325) |
| `C1|DOTTED|SIG` | C1 | 24 | **false_pos** | [dashboard/api_v2.py#L235](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/dashboard/api_v2.py#L235) |
| `C1|BARE|PARAM` | C1 | 3 | **known** | [collab/api.py#L68](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/collab/api.py#L68) |
| `C2|BARE|ascopes` | C2 | 2 | **known** | [dashboard/auth.py#L735](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/dashboard/auth.py#L735) |
| `C4|USED` | C4 | 2 | **false_pos** | [dashboard/database.py#L110](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/dashboard/database.py#L110) |

## `C1|DOTTED|PARAM` — **variant**
> occurrences here: 175 · corpus total: 422 · executor: x86_64
> example: [collab/api.py#L62](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/collab/api.py#L62)
> **rule:** C1

> **evidence (model):** Dotted paths (e.g., 'deps.db') used as dependencies in parameters, which is a structural variation of C1 (Depends call arguments) but not the standard bare function reference.

## `C4|DEF` — **false_pos**
> occurrences here: 75 · corpus total: 56644 · executor: x86_64
> example: [autonomy/lib/assets_bundle.py#L126](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/autonomy/lib/assets_bundle.py#L126)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 45 · corpus total: 83548 · executor: x86_64
> example: [dashboard/api_v2.py#L325](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/dashboard/api_v2.py#L325)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|DOTTED|SIG` — **false_pos**
> occurrences here: 24 · corpus total: 2178 · executor: x86_64
> example: [dashboard/api_v2.py#L235](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/dashboard/api_v2.py#L235)
> **rule:** C1

> **evidence (model):** Parameters use dotted names (core.current_principal) but are not wrapped in Depends/Security calls, indicating standard function parameters rather than FastAPI DI dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 3 · corpus total: 18195 · executor: x86_64
> example: [collab/api.py#L68](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/collab/api.py#L68)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C2|BARE|ascopes` — **known**
> occurrences here: 2 · corpus total: 504 · executor: x86_64
> example: [dashboard/auth.py#L735](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/dashboard/auth.py#L735)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [dashboard/database.py#L110](https://github.com/asklokesh/loki-mode/blob/d405f5a7f92ba0b7cf8208263279c956fdbcbdc8/dashboard/database.py#L110)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

