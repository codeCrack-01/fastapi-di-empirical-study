# acgs-ai/enhanced-agent-bus

- GitHub: https://github.com/acgs-ai/enhanced-agent-bus
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 548 · commit: `e4ecaf56b31a`
- Fingerprints touching this repo: 9
- Label mix: novel=0 variant=1 known=4 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | api/routes/agent_health.py#L185 | The function get_agent_health uses Depends() to inject operator and store dependencies, demonstrating FastAPI's built-in DI system. |
| 2 | `Nested dependency resolution` | api/routes/governance.py#L815 | _get_maci_enforcer depends on _get_maci_registry, showing nested DI where one dependency resolves another. |
| 3 | `Optional dependencies with fallback` | api/routes/governance.py#L1128 | The store parameter in get_maci_record has a default value of None, allowing optional DI with fallback behavior. |
| 4 | `Service abstraction through DI` | api/routes/messages.py#L394 | The bus parameter in send_message uses Depends(get_agent_bus), abstracting the message processor implementation. |

## Pass 2 — reconcile with inventory of acgs-ai/enhanced-agent-bus

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C3|ELLIPSIS|BARE`, `C1|DOTTED|SIG`, `C1|CLASS|SIG`, `C2|BARE|ascopes`, `C2|CLASS|ascopes`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection_agent_health` | FastAPI dependency injection via Depends() | **no (overturn)** | No code for 'agent_health.py' is present in the provided repository files | api/routes/agent_health.py#L185 |
| `nested_dependency_resolution_governance` | Nested dependency resolution | yes | _get_maci_enforcer depends on _get_maci_registry as shown in governance.py | api/routes/governance.py#L815 |
| `optional_dependency_fallback_governance` | Optional dependencies with fallback | yes | store parameter in get_maci_record has None default via Depends() | api/routes/governance.py#L1128 |
| `service_abstraction_di_messages` | Service abstraction through DI | yes | bus parameter in send_message uses Depends(get_agent_bus) | api/routes/messages.py#L394 |

### Missed by inventory (1)
- `FastAPI dependency injection via Depends()` @ api/routes/agent_health.py#L185 — No code for 'agent_health.py' is present in the provided repository files

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 335 | **false_pos** | [_compat/database/session.py#L23](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/_compat/database/session.py#L23) |
| `C1|BARE|SIG` | C1 | 96 | **false_pos** | [api/routes/agent_health.py#L185](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/agent_health.py#L185) |
| `C3|CLASS|BARE` | C3 | 58 | **false_pos** | [api/routes/governance.py#L815](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/governance.py#L815) |
| `C1|BARE|PARAM` | C1 | 39 | **known** | [api/routes/governance.py#L815](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/governance.py#L815) |
| `C3|ELLIPSIS|BARE` | C3 | 14 | **variant** | [api/routes/governance.py#L915](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/governance.py#L915) |
| `C1|DOTTED|SIG` | C1 | 3 | **false_pos** | [collaboration/api_integration.py#L300](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/collaboration/api_integration.py#L300) |
| `C1|CLASS|SIG` | C1 | 1 | **known** | [collaboration/api_integration.py#L131](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/collaboration/api_integration.py#L131) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [api/routes/z3.py#L82](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/z3.py#L82) |
| `C2|CLASS|ascopes` | C2 | 1 | **known** | [api/api_key_auth.py#L200](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/api_key_auth.py#L200) |

## `C4|DEF` — **false_pos**
> occurrences here: 335 · corpus total: 56644 · executor: x86_64
> example: [_compat/database/session.py#L23](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/_compat/database/session.py#L23)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 96 · corpus total: 83548 · executor: x86_64
> example: [api/routes/agent_health.py#L185](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/agent_health.py#L185)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 58 · corpus total: 20139 · executor: x86_64
> example: [api/routes/governance.py#L815](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/governance.py#L815)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 39 · corpus total: 18195 · executor: x86_64
> example: [api/routes/governance.py#L815](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/governance.py#L815)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 14 · corpus total: 1113 · executor: x86_64
> example: [api/routes/governance.py#L915](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/governance.py#L915)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C1|DOTTED|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 2178 · executor: x86_64
> example: [collaboration/api_integration.py#L300](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/collaboration/api_integration.py#L300)
> **rule:** C1

> **evidence (model):** Parameters use dotted names (core.current_principal) but are not wrapped in Depends/Security calls, indicating standard function parameters rather than FastAPI DI dependencies

## `C1|CLASS|SIG` — **known**
> occurrences here: 1 · corpus total: 149 · executor: x86_64
> example: [collaboration/api_integration.py#L131](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/collaboration/api_integration.py#L131)
> **rule:** C1

> **evidence (model):** Examples show classes (HTTPBearer, CRSParams, RoleChecker) passed to Depends, which fits C1 (function/object passed to Depends) since classes are objects in Python.

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [api/routes/z3.py#L82](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/routes/z3.py#L82)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C2|CLASS|ascopes` — **known**
> occurrences here: 1 · corpus total: 26 · executor: x86_64
> example: [api/api_key_auth.py#L200](https://github.com/acgs-ai/enhanced-agent-bus/blob/e4ecaf56b31aeed2e93c91ab0ce26424ae197e54/api/api_key_auth.py#L200)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in authentication/authorization contexts (API keys, webhook signatures), matching catalog rule C2.

