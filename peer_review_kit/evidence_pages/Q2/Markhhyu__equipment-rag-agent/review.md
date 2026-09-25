# Markhhyu/equipment-rag-agent

- GitHub: https://github.com/Markhhyu/equipment-rag-agent
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 58 · commit: `0218cb9b20b3`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=2 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Role-based dependency injection with FastAPI Depends` | app/modules/ingestion/api/knowledge_routes.py#L26 | The route uses Depends(require_role("admin")) to inject a principal object with admin role validation. This pattern is repeated in 7 other routes across the repo, always using Principal = Depends(r... |
| 2 | `Service locator pattern for stateless dependencies` | app/modules/ingestion/api/knowledge_routes.py#L26 | Functions like get_document_registry() and get_milvus_client() are called directly in route handlers without being injected via Depends(), indicating a service locator approach where dependencies a... |
| 3 | `Custom dependency generation` | app/platform/security/auth.py#L120 | The require_role() function generates custom dependencies that wrap the authenticate() function, creating a reusable pattern for role-based access control across all routes in the application. |

## Pass 2 — reconcile with inventory of Markhhyu/equipment-rag-agent

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C2|BARE|ascopes`, `C3|CLASS|BARE`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `role-based-dependency-injection` | Role-based dependency injection with FastAPI Depends | yes | Multiple routes use Depends(require_role(...)) for role validation, confirmed in app/modules/qa/api/session_routes.py:101 and other files. | app/modules/qa/api/session_routes.py#L101 |
| `service-locator-pattern` | Service locator pattern for stateless dependencies | yes | Dependencies like get_document_registry() are called directly in route handlers, confirmed in app/modules/ingestion/api/knowledge_routes.py:26. | app/modules/ingestion/api/knowledge_routes.py#L26 |
| `custom-dependency-generation` | Custom dependency generation with require_role() | yes | require_role() generates dependencies that wrap authenticate(), confirmed in app/platform/security/auth.py:120. | app/platform/security/auth.py#L120 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 40 | **false_pos** | [app/modules/ingestion/api/knowledge_routes.py#L26](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/modules/ingestion/api/knowledge_routes.py#L26) |
| `C4|DEF` | C4 | 13 | **false_pos** | [app/modules/ingestion/api/routes.py#L50](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/modules/ingestion/api/routes.py#L50) |
| `C2|BARE|ascopes` | C2 | 2 | **known** | [app/platform/security/auth.py#L36](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/platform/security/auth.py#L36) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [app/platform/security/auth.py#L120](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/platform/security/auth.py#L120) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [app/platform/security/auth.py#L120](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/platform/security/auth.py#L120) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 40 · corpus total: 83548 · executor: x86_64
> example: [app/modules/ingestion/api/knowledge_routes.py#L26](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/modules/ingestion/api/knowledge_routes.py#L26)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 13 · corpus total: 56644 · executor: x86_64
> example: [app/modules/ingestion/api/routes.py#L50](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/modules/ingestion/api/routes.py#L50)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C2|BARE|ascopes` — **known**
> occurrences here: 2 · corpus total: 504 · executor: x86_64
> example: [app/platform/security/auth.py#L36](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/platform/security/auth.py#L36)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [app/platform/security/auth.py#L120](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/platform/security/auth.py#L120)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [app/platform/security/auth.py#L120](https://github.com/Markhhyu/equipment-rag-agent/blob/0218cb9b20b3d02176f86085e81915efd63d3a09/app/platform/security/auth.py#L120)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

