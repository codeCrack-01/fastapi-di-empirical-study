# Fergana-Labs/stash

- GitHub: https://github.com/Fergana-Labs/stash
- Stars: 297 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 481 · commit: `c56f81c961c3`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=2 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection (DI)` | backend/routers/admin.py#L145 | The `Depends(require_admin_token)` decorator injects authentication logic into route handlers, decoupling authorization checks from business logic. This follows the DI pattern by externalizing depe... |
| 2 | `Data Transfer Object (DTO)` | backend/routers/admin.py#L163 | The `RepoRequest` Pydantic model validates and structures incoming HTTP requests, embodying the DTO pattern to ensure clean, type-safe data transfer between client and server. |
| 3 | `Service Layer Abstraction` | backend/routers/admin.py#L145 | Route handlers delegate to `admin_analytics_service` and `github_skill_import` services, encapsulating business logic in separate layers. This aligns with the Service Layer pattern, promoting separ... |

## Pass 2 — reconcile with inventory of Fergana-Labs/stash

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C1|CLASS|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `DTO_PATTERN` | Data Transfer Object (DTO) Pattern | yes | Pydantic models like RepoRequest and AgentFields validate and structure HTTP payloads, embodying DTOs for type-safe data transfer. | backend/routers/admin.py#L163 |
| `SERVICE_LAYER` | Service Layer Abstraction | yes | Route handlers delegate to services (e.g., admin_analytics_service, github_skill_import) to encapsulate business logic, following the Service Layer pattern. | backend/routers/admin.py#L145 |
| `DEPENDENCY_INJECTION` | Dependency Injection | yes | Depends(require_admin_token) and Depends(get_current_user) inject auth/user logic into routes, decoupling handlers from implementation details. | backend/routers/admin.py#L145 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 395 | **false_pos** | [backend/auth.py#L243](https://github.com/Fergana-Labs/stash/blob/c56f81c961c3382f2b37734142ee982555d2e69d/backend/auth.py#L243) |
| `C4|DEF` | C4 | 58 | **false_pos** | [backend/exports/native/aspose_builder.py#L285](https://github.com/Fergana-Labs/stash/blob/c56f81c961c3382f2b37734142ee982555d2e69d/backend/exports/native/aspose_builder.py#L285) |
| `C1|BARE|PARAM` | C1 | 27 | **known** | [backend/routers/admin.py#L77](https://github.com/Fergana-Labs/stash/blob/c56f81c961c3382f2b37734142ee982555d2e69d/backend/routers/admin.py#L77) |
| `C1|CLASS|SIG` | C1 | 1 | **known** | [backend/auth.py#L287](https://github.com/Fergana-Labs/stash/blob/c56f81c961c3382f2b37734142ee982555d2e69d/backend/auth.py#L287) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 395 · corpus total: 83548 · executor: x86_64
> example: [backend/auth.py#L243](https://github.com/Fergana-Labs/stash/blob/c56f81c961c3382f2b37734142ee982555d2e69d/backend/auth.py#L243)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 58 · corpus total: 56644 · executor: x86_64
> example: [backend/exports/native/aspose_builder.py#L285](https://github.com/Fergana-Labs/stash/blob/c56f81c961c3382f2b37734142ee982555d2e69d/backend/exports/native/aspose_builder.py#L285)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 27 · corpus total: 18195 · executor: x86_64
> example: [backend/routers/admin.py#L77](https://github.com/Fergana-Labs/stash/blob/c56f81c961c3382f2b37734142ee982555d2e69d/backend/routers/admin.py#L77)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|CLASS|SIG` — **known**
> occurrences here: 1 · corpus total: 149 · executor: x86_64
> example: [backend/auth.py#L287](https://github.com/Fergana-Labs/stash/blob/c56f81c961c3382f2b37734142ee982555d2e69d/backend/auth.py#L287)
> **rule:** C1

> **evidence (model):** Examples show classes (HTTPBearer, CRSParams, RoleChecker) passed to Depends, which fits C1 (function/object passed to Depends) since classes are objects in Python.

