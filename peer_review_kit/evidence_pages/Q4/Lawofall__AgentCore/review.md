# Lawofall/AgentCore

- GitHub: https://github.com/Lawofall/AgentCore
- Stars: 30 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 1654 · commit: `306d88cc2597`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=1 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with layered service/repository dependencies` | apps/server/agentcore/api/dependencies.py#L142 | The code defines a clear dependency injection hierarchy using FastAPI's Depends() mechanism. get_db provides a database session, which is injected into repositories (get_user_repo, get_admin_mfa_re... |
| 2 | `Annotated dependencies for request-scoped injection` | apps/server/agentcore/api/dependencies.py#L355 | The code uses Annotated[User, Depends(get_current_user)] to create typed dependency annotations. This pattern allows route handlers to directly receive authenticated users as parameters, demonstrat... |
| 3 | `Async generator dependency for database sessions` | apps/server/agentcore/api/dependencies.py#L146 | The get_db() function is defined as an async generator that yields AsyncSession instances. This is a standard FastAPI pattern for managing database connections in async contexts, with other depende... |

## Pass 2 — reconcile with inventory of Lawofall/AgentCore

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C3|ELLIPSIS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_positive | **no (overturn)** | The code correctly uses Depends() for dependency injection (e.g., get_user_repo(session: AsyncSession = Depends(get_db)) demonstrates proper FastAPI dependency resolution) | apps/server/agentcore/api/dependencies.py#L142 |
| `C1|BARE|SIG` | true_positive | **no (overturn)** | The code uses explicit signature-based dependencies (e.g., get_admin_mfa_service(mfa_repo: AdminMfaRepository = Depends(...)) which aligns with the fingerprint's pattern | apps/server/agentcore/api/dependencies.py#L146 |
| `C3|CLASS|BARE` | true_positive | **no (overturn)** | Class-based dependency patterns are present (e.g., AdminService constructor injection via get_admin_service(...)) | apps/server/agentcore/api/dependencies.py#L142 |
| `C4|USED` | true_positive | **no (overturn)** | The get_db async generator is explicitly used throughout the codebase (e.g., in search_account_conversations(session: AsyncSession = Depends(get_db)) | apps/server/agentcore/api/routes/account.py#L115 |

### Missed by inventory (2)
- `Annotated[Type, Depends(...)] pattern for request-scoped injection` @ apps/server/agentcore/api/dependencies.py#L355 — The inventory did not capture the use of Annotated[User, Depends(get_current_user)] for typed dependency resolution
- `Async generator dependency pattern` @ apps/server/agentcore/api/dependencies.py#L146 — The inventory missed the async generator pattern in get_db() which is central to the dependency architecture

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1042 | **false_pos** | [apps/server/agentcore/account/credentials.py#L65](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/account/credentials.py#L65) |
| `C1|BARE|SIG` | C1 | 590 | **false_pos** | [apps/server/agentcore/api/dependencies.py#L142](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L142) |
| `C3|CLASS|BARE` | C3 | 11 | **false_pos** | [apps/server/agentcore/api/dependencies.py#L475](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L475) |
| `C1|BARE|PARAM` | C1 | 9 | **known** | [apps/server/agentcore/api/dependencies.py#L475](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L475) |
| `C3|ELLIPSIS|BARE` | C3 | 1 | **variant** | [apps/server/agentcore/api/dependencies.py#L478](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L478) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/server/agentcore/api/dependencies.py#L136](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L136) |

## `C4|DEF` — **false_pos**
> occurrences here: 1042 · corpus total: 56644 · executor: x86_64
> example: [apps/server/agentcore/account/credentials.py#L65](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/account/credentials.py#L65)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 590 · corpus total: 83548 · executor: x86_64
> example: [apps/server/agentcore/api/dependencies.py#L142](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L142)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 11 · corpus total: 20139 · executor: x86_64
> example: [apps/server/agentcore/api/dependencies.py#L475](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L475)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 9 · corpus total: 18195 · executor: x86_64
> example: [apps/server/agentcore/api/dependencies.py#L475](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L475)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 1 · corpus total: 1113 · executor: x86_64
> example: [apps/server/agentcore/api/dependencies.py#L478](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L478)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/server/agentcore/api/dependencies.py#L136](https://github.com/Lawofall/AgentCore/blob/306d88cc2597ea130f1637c8eb90e79eff29b5d4/apps/server/agentcore/api/dependencies.py#L136)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

