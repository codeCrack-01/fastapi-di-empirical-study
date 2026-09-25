# Turing222/dewflow

- GitHub: https://github.com/Turing222/dewflow
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 247 · commit: `37485f26b1db`
- Fingerprints touching this repo: 9
- Label mix: novel=0 variant=3 known=1 false_pos=5 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based DI with layered service composition` | backend/api/deps/ai.py#L30 | The get_rerank_service function uses Depends() to inject FeatureFlagService, demonstrating FastAPI's dependency injection. It conditionally returns None based on feature flags, showing DI integrati... |
| 2 | `Recursive dependency chains` | backend/api/deps/ai.py#L56 | get_vector_index_service depends on get_uow and get_rag_embedder, which itself depends on get_llm_model_config. This creates a chain of dependencies that are resolved hierarchically. |
| 3 | `Asynchronous DI with Depends` | backend/api/deps/ai.py#L67 | get_rag_service is an async function that uses Depends() to inject multiple services (uow, embedder, vector_index_service, reranker), showing async-aware dependency resolution. |
| 4 | `Cached singleton dependencies` | backend/api/deps/services.py#L36 | get_object_storage uses @lru_cache(maxsize=1) to create a process-level singleton, which is then injected into get_knowledge_service via Depends() as a shared dependency. |
| 5 | `Permission/service workflow composition` | backend/api/deps/workflows.py#L41 | get_chat_workflow injects 6+ dependencies (uow, dispatcher, redis, permission_service, etc.) to construct a complex workflow object, demonstrating DI's role in composing application layers. |

## Pass 2 — reconcile with inventory of Turing222/dewflow

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C1|BARE|SIG`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`, `C3|CLASS|EMPTY`, `C1|EMPTY|PARAM`, `C1|EMPTY|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | real | **no (overturn)** | The code explicitly uses Depends() for FeatureFlagService injection in get_rerank_service() | backend/api/deps/ai.py#L30 |
| `C1|BARE|PARAM` | known | yes | Multiple instances of explicit parameter injection with Depends() exist in the code | backend/api/deps/ai.py#L30 |
| `C1|BARE|SIG` | real | **no (overturn)** | Function signatures with Depends() parameter injection are present in the code | backend/api/deps/ai.py#L30 |
| `C3|CLASS|BARE` | real | **no (overturn)** | Class-based dependency injection patterns are implemented in the code | backend/api/deps/ai.py#L30 |
| `C3|CLASS|EMPTY` | false_pos | yes | The code contains empty class injection patterns as labeled | backend/api/deps/ai.py#L30 |
| `C1|EMPTY|PARAM` | variant | yes | The code contains parameter injection patterns matching the variant label | backend/api/deps/ai.py#L30 |
| `C1|EMPTY|SIG` | variant | yes | The code contains function signatures matching the variant label | backend/api/deps/ai.py#L30 |
| `C4|USED` | real | **no (overturn)** | The code contains used dependencies that contradict the false_pos label | backend/api/deps/infra.py#L1 |

### Missed by inventory (2)
- `Async dependency injection` @ backend/api/deps/ai.py#L67 — The inventory missed async DI patterns in get_rag_service()
- `Cached singleton dependencies` @ backend/api/deps/services.py#L36 — The inventory missed @lru_cache singleton patterns in get_object_storage()

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 97 | **false_pos** | [backend/ai/providers/llm/mock_provider.py#L31](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/ai/providers/llm/mock_provider.py#L31) |
| `C1|BARE|PARAM` | C1 | 54 | **known** | [backend/api/v1/api.py#L43](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/api.py#L43) |
| `C1|BARE|SIG` | C1 | 48 | **false_pos** | [backend/api/deps/ai.py#L30](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/deps/ai.py#L30) |
| `C3|CLASS|BARE` | C3 | 37 | **false_pos** | [backend/api/v1/endpoint/audit_api.py#L24](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/endpoint/audit_api.py#L24) |
| `C3|ELLIPSIS|BARE` | C3 | 6 | **variant** | [backend/api/v1/endpoint/chat_api.py#L78](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/endpoint/chat_api.py#L78) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [backend/api/v1/endpoint/user_api.py#L80](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/endpoint/user_api.py#L80) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [backend/api/v1/endpoint/user_api.py#L80](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/endpoint/user_api.py#L80) |
| `C1|EMPTY|SIG` | C1 | 1 | **variant** | [backend/api/deps/auth.py#L28](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/deps/auth.py#L28) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/api/deps/infra.py#L14](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/deps/infra.py#L14) |

## `C4|DEF` — **false_pos**
> occurrences here: 97 · corpus total: 56644 · executor: x86_64
> example: [backend/ai/providers/llm/mock_provider.py#L31](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/ai/providers/llm/mock_provider.py#L31)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 54 · corpus total: 18195 · executor: x86_64
> example: [backend/api/v1/api.py#L43](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/api.py#L43)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 48 · corpus total: 83548 · executor: x86_64
> example: [backend/api/deps/ai.py#L30](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/deps/ai.py#L30)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 37 · corpus total: 20139 · executor: x86_64
> example: [backend/api/v1/endpoint/audit_api.py#L24](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/endpoint/audit_api.py#L24)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 6 · corpus total: 1113 · executor: x86_64
> example: [backend/api/v1/endpoint/chat_api.py#L78](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/endpoint/chat_api.py#L78)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [backend/api/v1/endpoint/user_api.py#L80](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/endpoint/user_api.py#L80)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [backend/api/v1/endpoint/user_api.py#L80](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/v1/endpoint/user_api.py#L80)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 1 · corpus total: 254 · executor: x86_64
> example: [backend/api/deps/auth.py#L28](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/deps/auth.py#L28)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/api/deps/infra.py#L14](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/deps/infra.py#L14)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

