# brcampidelli/chimera-agent

- GitHub: https://github.com/brcampidelli/chimera-agent
- Stars: 19 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 95 · commit: `91949b993ebd`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection (DI) via constructor parameters` | chimera/api/orchestration_api.py#L618 | The `register_orchestration_api` function accepts `backend_factory` as a parameter, allowing the API to depend on an external factory for creating backend instances rather than instantiating them d... |
| 2 | `Constructor Injection` | chimera/fusion/engine.py#L319 | The `FusionEngine` class receives a `backend` parameter in its constructor. This explicitly injects the dependency rather than creating it internally, enabling testability and modularity. |
| 3 | `Configuration Injection` | chimera/providers/gateway.py#L724 | The `LLMGateway` class accepts `settings` as a parameter, allowing configuration to be injected externally. This avoids hardcoding configuration within the class, adhering to DI by separating conce... |

## Pass 2 — reconcile with inventory of brcampidelli/chimera-agent

_Presented fingerprints:_ `C4|DEF`, `C1|ELLIPSIS|PARAM`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `DI via constructor parameter in register_orchestration_api` | Dependency Injection via constructor parameter | yes | The `register_orchestration_api` function accepts `backend_factory` as a parameter, decoupling the API from specific backend implementations. | chimera/api/orchestration_api.py#L618 |
| `Constructor Injection in FusionEngine` | Constructor Injection | yes | The `FusionEngine` class receives a `backend` parameter in its constructor, enabling testability and modularity. | chimera/fusion/engine.py#L319 |
| `Configuration Injection in LLMGateway` | Configuration Injection | yes | The `LLMGateway` class accepts `settings` as a parameter, allowing configuration to be injected externally. | chimera/providers/gateway.py#L724 |

### Missed by inventory (1)
- `FastAPI dependency injection via `guard` parameter` @ chimera/api/orchestration_api.py#L618 — The `guard` parameter in `register_orchestration_api` is part of FastAPI's dependency injection system but was not mentioned in the initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 92 | **false_pos** | [bench/right_hand_governance/run_terminal_vs_governed.py#L279](https://github.com/brcampidelli/chimera-agent/blob/91949b993ebd26cf9f68727f18f7600024bbe35d/bench/right_hand_governance/run_terminal_vs_governed.py#L279) |
| `C1|ELLIPSIS|PARAM` | C1 | 2 | **false_pos** | [tests/test_crew_respects_the_ceiling.py#L63](https://github.com/brcampidelli/chimera-agent/blob/91949b993ebd26cf9f68727f18f7600024bbe35d/tests/test_crew_respects_the_ceiling.py#L63) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [chimera/api/app.py#L580](https://github.com/brcampidelli/chimera-agent/blob/91949b993ebd26cf9f68727f18f7600024bbe35d/chimera/api/app.py#L580) |

## `C4|DEF` — **false_pos**
> occurrences here: 92 · corpus total: 56644 · executor: x86_64
> example: [bench/right_hand_governance/run_terminal_vs_governed.py#L279](https://github.com/brcampidelli/chimera-agent/blob/91949b993ebd26cf9f68727f18f7600024bbe35d/bench/right_hand_governance/run_terminal_vs_governed.py#L279)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|ELLIPSIS|PARAM` — **false_pos**
> occurrences here: 2 · corpus total: 252 · executor: x86_64
> example: [tests/test_crew_respects_the_ceiling.py#L63](https://github.com/brcampidelli/chimera-agent/blob/91949b993ebd26cf9f68727f18f7600024bbe35d/tests/test_crew_respects_the_ceiling.py#L63)

> **evidence (model):** The ellipsis (...) is not a valid FastAPI dependency construct; it appears as a placeholder or incomplete code rather than an actual dependency injection usage.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [chimera/api/app.py#L580](https://github.com/brcampidelli/chimera-agent/blob/91949b993ebd26cf9f68727f18f7600024bbe35d/chimera/api/app.py#L580)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

