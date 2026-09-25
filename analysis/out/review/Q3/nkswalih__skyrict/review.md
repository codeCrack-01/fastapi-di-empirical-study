# nkswalih/skyrict

- GitHub: https://github.com/nkswalih/skyrict
- Stars: 4 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 1421 · commit: `0fae7284f79b`
- Fingerprints touching this repo: 8
- Label mix: novel=0 variant=2 known=1 false_pos=5 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Depends` | services/ai-agent/src/ai_agent/api/deps.py#L12 | The `get_current_user` function uses `Depends(security)` to inject authentication security checks into route handlers, a core FastAPI DI pattern. |
| 2 | `Service Dependency Injection` | services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L15 | The `get_abc_service` function creates a dependency on `get_inventory_gateway` and injects it into route handlers via `Annotated[AbcService, Depends(get_abc_service)]`, demonstrating layered servic... |
| 3 | `Runtime Dependency Injection` | services/ai-agent/src/ai_agent/api/v1/routers/agents.py#L25 | The `get_runtime` function provides an `AgentRuntime` dependency that is injected into route handlers via `Annotated[SupervisorRuntime, Depends(get_supervisor_runtime)]`, showing runtime-specific DI. |
| 4 | `Rate Limiting Dependency` | services/ai-agent/src/ai_agent/api/v1/routers/chat.py#L265 | The `stream_chat` route uses `Depends(get_supervisor_runtime)` which likely includes a rate-limiting dependency enforced before streaming starts. |

## Pass 2 — reconcile with inventory of nkswalih/skyrict

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`, `C4|DEF`, `C3|DOTTED|BARE`, `C4|USED`, `C3|BARE|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `resolve_anomaly_decision` | resolved | yes | The function explicitly marks anomalies as resolved with 'decision="resolved"' in the service.review call. | services/ai-agent/src/ai_agent/api/v1/routers/anomalies.py#L168 |
| `dismiss_anomaly_decision` | dismissed | yes | The function explicitly marks anomalies as dismissed with 'decision="dismissed"' in the service.review call. | services/ai-agent/src/ai_agent/api/v1/routers/anomalies.py#L169 |
| `escalate_anomaly_decision` | escalated | yes | The function explicitly escalates anomalies with 'decision="escalated"' in the service.review call. | services/ai-agent/src/ai_agent/api/v1/routers/anomalies.py#L190 |
| `chat_rate_limiting` | enforced_before_streaming | yes | The code enforces rate limits before streaming starts using limiter.enforce() | services/ai-agent/src/ai_agent/api/v1/routers/chat.py#L265 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 813 | **false_pos** | [services/ai-agent/src/ai_agent/api/deps.py#L29](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/deps.py#L29) |
| `C1|BARE|PARAM` | C1 | 188 | **known** | [services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L37](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L37) |
| `C3|CLASS|BARE` | C3 | 170 | **false_pos** | [services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L37](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L37) |
| `C3|ELLIPSIS|BARE` | C3 | 157 | **variant** | [services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L47](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L47) |
| `C4|DEF` | C4 | 82 | **false_pos** | [services/ai-agent/src/ai_agent/api/lifespan.py#L41](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/lifespan.py#L41) |
| `C3|DOTTED|BARE` | C3 | 4 | **false_pos** | [services/core/src/core/features/ai/router.py#L124](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/core/src/core/features/ai/router.py#L124) |
| `C4|USED` | C4 | 4 | **false_pos** | [services/ai-agent/src/ai_agent/db/session.py#L58](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/db/session.py#L58) |
| `C3|BARE|BARE` | C3 | 3 | **variant** | [services/ai-agent/src/ai_agent/api/v1/routers/narrator.py#L71](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/v1/routers/narrator.py#L71) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 813 · corpus total: 83548 · executor: x86_64
> example: [services/ai-agent/src/ai_agent/api/deps.py#L29](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/deps.py#L29)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 188 · corpus total: 18195 · executor: x86_64
> example: [services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L37](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L37)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 170 · corpus total: 20139 · executor: x86_64
> example: [services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L37](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L37)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 157 · corpus total: 1113 · executor: x86_64
> example: [services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L47](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/v1/routers/abc.py#L47)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C4|DEF` — **false_pos**
> occurrences here: 82 · corpus total: 56644 · executor: x86_64
> example: [services/ai-agent/src/ai_agent/api/lifespan.py#L41](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/lifespan.py#L41)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|DOTTED|BARE` — **false_pos**
> occurrences here: 4 · corpus total: 262 · executor: x86_64
> example: [services/core/src/core/features/ai/router.py#L124](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/core/src/core/features/ai/router.py#L124)

> **evidence (model):** Annotated types (C3) require Depends(...) in the metadata, but examples show asyncpg.Connection without any dependency injection expression

## `C4|USED` — **false_pos**
> occurrences here: 4 · corpus total: 1079 · executor: x86_64
> example: [services/ai-agent/src/ai_agent/db/session.py#L58](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/db/session.py#L58)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C3|BARE|BARE` — **variant**
> occurrences here: 3 · corpus total: 1316 · executor: x86_64
> example: [services/ai-agent/src/ai_agent/api/v1/routers/narrator.py#L71](https://github.com/nkswalih/skyrict/blob/0fae7284f79b2487ebc57eb40ce2a163a674d11c/services/ai-agent/src/ai_agent/api/v1/routers/narrator.py#L71)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

