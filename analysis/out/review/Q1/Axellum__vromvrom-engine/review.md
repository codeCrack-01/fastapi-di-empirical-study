# Axellum/vromvrom-engine

- GitHub: https://github.com/Axellum/vromvrom-engine
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 71 · commit: `ce192569133d`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Adapter` | core/llm/providers/deepseek.py#L31 | Imports and uses OpenAI-compatible interfaces (e.g., SharedHTTPPool, filtrer_champs_prives) to adapt DeepSeek's API to a common LLMProvider interface, enabling interoperability with other providers... |
| 2 | `Decorator` | core/otel.py#L98 | The llm_span context manager wraps LLM calls to add tracing functionality without modifying the original generate_stream methods, demonstrating the Decorator pattern for cross-cutting concerns. |
| 3 | `Circuit Breaker` | core/llm/providers/deepseek.py#L899 | Implements a fallback mechanism with circuit breaker logic (cb.record_failure, backoff_delay) to handle provider failures gracefully, preventing cascading failures in the system. |
| 4 | `Strategy` | core/llm_gateway.py#L688 | The stream method uses FallbackProvider to dynamically switch between LLM providers based on availability, embodying the Strategy pattern for flexible provider selection. |
| 5 | `Template Method` | core/models_db.py#L291 | The _write_transaction context manager defines a standard transaction lifecycle (acquire, execute, commit/rollback) that concrete implementations must follow, aligning with the Template Method patt... |

## Pass 2 — reconcile with inventory of Axellum/vromvrom-engine

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `Adapter@core/llm/providers/deepseek.py:31` | Adapter | yes | DeepSeek uses OpenAI-compatible interfaces (SharedHTTPPool, filtrer_champs_prives) to adapt its API to a common LLMProvider interface, matching the Adapter pattern definition. | core/llm/providers/deepseek.py#L31 |
| `Decorator@core/otel.py:98` | Decorator | yes | llm_span context manager wraps LLM calls with tracing functionality without modifying generate_stream methods, fulfilling the Decorator pattern's cross-cutting concern requirement. | core/otel.py#L98 |
| `CircuitBreaker@core/llm/providers/deepseek.py:899` | CircuitBreaker | yes | Implements fallback mechanism with cb.record_failure and backoff_delay, matching circuit breaker pattern's failure handling and recovery characteristics. | core/llm/providers/deepseek.py#L899 |
| `Strategy@core/llm_gateway.py:688` | Strategy | yes | stream method uses FallbackProvider to dynamically switch between LLM providers, aligning with Strategy pattern's dynamic algorithm selection principle. | core/llm_gateway.py#L688 |
| `TemplateMethod@core/models_db.py:291` | TemplateMethod | yes | _write_transaction defines standard transaction lifecycle (acquire, execute, commit/rollback) that concrete implementations must follow, matching Template Method pattern's definition. | core/models_db.py#L291 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 60 | **false_pos** | [api/routes/openai_proxy.py#L401](https://github.com/Axellum/vromvrom-engine/blob/ce192569133d41f391baaed699d830607f032016/api/routes/openai_proxy.py#L401) |
| `C1|BARE|SIG` | C1 | 10 | **false_pos** | [api/routes/agents.py#L328](https://github.com/Axellum/vromvrom-engine/blob/ce192569133d41f391baaed699d830607f032016/api/routes/agents.py#L328) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [gui_server.py#L362](https://github.com/Axellum/vromvrom-engine/blob/ce192569133d41f391baaed699d830607f032016/gui_server.py#L362) |

## `C4|DEF` — **false_pos**
> occurrences here: 60 · corpus total: 56644 · executor: x86_64
> example: [api/routes/openai_proxy.py#L401](https://github.com/Axellum/vromvrom-engine/blob/ce192569133d41f391baaed699d830607f032016/api/routes/openai_proxy.py#L401)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 10 · corpus total: 83548 · executor: x86_64
> example: [api/routes/agents.py#L328](https://github.com/Axellum/vromvrom-engine/blob/ce192569133d41f391baaed699d830607f032016/api/routes/agents.py#L328)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [gui_server.py#L362](https://github.com/Axellum/vromvrom-engine/blob/ce192569133d41f391baaed699d830607f032016/gui_server.py#L362)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

