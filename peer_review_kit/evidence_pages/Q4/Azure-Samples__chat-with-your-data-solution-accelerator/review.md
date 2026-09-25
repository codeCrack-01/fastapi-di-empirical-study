# Azure-Samples/chat-with-your-data-solution-accelerator

- GitHub: https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator
- Stars: 1172 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 81 · commit: `b5848ecb1bfa`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=2 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Annotated and Depends` | src/backend/core/providers/llm/base.py#L90 | The code uses FastAPI's `Depends` to inject dependencies into async methods, e.g., `complete` method uses `Depends` for dependency resolution. This is evident in the `complete` method's parameters ... |
| 2 | `Centralized dependency retrieval via app.state` | src/backend/core/providers/llm/foundry_iq.py#L367 | Dependencies like `credential` are retrieved from `app.state` in methods such as `chat_stream`, indicating a centralized setup during application lifespan. This is seen in the use of `app.state` to... |
| 3 | `Optional dependencies with type unions` | src/backend/core/providers/orchestrators/agent_framework.py#L185 | Dependencies like `SearchProvider` are defined with optional types (e.g., `BaseSearch | None`), allowing for graceful handling of missing services. This is demonstrated in the `run` method's parame... |

## Pass 2 — reconcile with inventory of Azure-Samples/chat-with-your-data-solution-accelerator

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`, `C3|BARE|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection` | FastAPI dependency injection with Annotated and Depends | yes | The `complete` method in `base.py:90` uses `Annotated` and `Depends` for dependency injection, confirming the observation. | src/backend/core/providers/llm/base.py#L90 |
| `centralized_dependency_retrieval` | Centralized dependency retrieval via app.state | yes | The `chat_stream` method in `foundry_iq.py:367` retrieves dependencies from `app.state`, confirming centralized management. | src/backend/core/providers/llm/foundry_iq.py#L367 |
| `optional_dependencies_with_type_unions` | Optional dependencies with type unions | yes | The `run` method in `agent_framework.py:185` uses `BaseSearch | None` for optional dependencies, confirming the observation. | src/backend/core/providers/orchestrators/agent_framework.py#L185 |

### Missed by inventory (1)
- `Context manager for dependency lifecycle management` @ src/functions/core/storage_clients.py#L37 — The `storage_clients` function uses `@asynccontextmanager` to manage the lifecycle of storage clients, which was not mentioned in the initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 59 | **false_pos** | [src/backend/app.py#L65](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/app.py#L65) |
| `C1|BARE|PARAM` | C1 | 11 | **known** | [src/backend/dependencies.py#L41](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/dependencies.py#L41) |
| `C3|CLASS|BARE` | C3 | 6 | **false_pos** | [src/backend/dependencies.py#L41](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/dependencies.py#L41) |
| `C3|ELLIPSIS|BARE` | C3 | 4 | **variant** | [src/backend/dependencies.py#L108](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/dependencies.py#L108) |
| `C3|BARE|BARE` | C3 | 1 | **variant** | [src/backend/dependencies.py#L289](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/dependencies.py#L289) |

## `C4|DEF` — **false_pos**
> occurrences here: 59 · corpus total: 56644 · executor: x86_64
> example: [src/backend/app.py#L65](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/app.py#L65)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 11 · corpus total: 18195 · executor: x86_64
> example: [src/backend/dependencies.py#L41](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/dependencies.py#L41)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 6 · corpus total: 20139 · executor: x86_64
> example: [src/backend/dependencies.py#L41](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/dependencies.py#L41)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 4 · corpus total: 1113 · executor: x86_64
> example: [src/backend/dependencies.py#L108](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/dependencies.py#L108)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C3|BARE|BARE` — **variant**
> occurrences here: 1 · corpus total: 1316 · executor: x86_64
> example: [src/backend/dependencies.py#L289](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/b5848ecb1bfa1b5056cfc8d0f451d22022118c3f/src/backend/dependencies.py#L289)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

