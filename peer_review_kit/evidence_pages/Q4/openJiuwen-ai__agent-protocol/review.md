# openJiuwen-ai/agent-protocol

- GitHub: https://github.com/openJiuwen-ai/agent-protocol
- Stars: 81 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 80 · commit: `79201fe4c1bd`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection (DI)` | AgentRegistry/a2x_registry/backend/routers/dataset.py#L697 | The code uses `get_registry_service()` to retrieve services, indicating a service locator pattern. This allows decoupling of service creation from usage, a core DI principle. |
| 2 | `Dependency Injection` | AgentRegistry/a2x_registry/cluster/router.py#L106 | ClusterStore is injected via `Depends(require_cluster_store)`, demonstrating explicit DI for cluster management dependencies. |
| 3 | `Strategy Pattern` | AgentRegistry/a2x_registry/backend/routers/dataset.py#L697 | The `_run` function wraps service calls, suggesting a strategy for executing operations with potential cross-cutting concerns like error handling. |
| 4 | `DTO (Data Transfer Object)` | AgentRegistry/a2x_registry/backend/routers/dataset.py#L715 | Pydantic models like `ReservationRequest` validate incoming data, encapsulating request payloads as DTOs for clean separation of concerns. |

## Pass 2 — reconcile with inventory of openJiuwen-ai/agent-protocol

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `Dependency Injection (DI)` | Dependency Injection (DI) | yes | Both dataset.py and cluster/router.py demonstrate DI through service locators and explicit injection. | AgentRegistry/a2x_registry/backend/routers/dataset.py#L697 |
| `Strategy Pattern` | Strategy Pattern | yes | _run function in dataset.py encapsulates service operation strategies. | AgentRegistry/a2x_registry/backend/routers/dataset.py#L697 |
| `DTO (Data Transfer Object)` | DTO (Data Transfer Object) | yes | ReservationRequest in dataset.py uses Pydantic for DTO validation. | AgentRegistry/a2x_registry/backend/routers/dataset.py#L715 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 58 | **false_pos** | [AgentRegistry/a2x_registry/auth/deps.py#L146](https://github.com/openJiuwen-ai/agent-protocol/blob/79201fe4c1bd1c8696f3ef750004969a906ccfcb/AgentRegistry/a2x_registry/auth/deps.py#L146) |
| `C4|DEF` | C4 | 21 | **false_pos** | [AgentRegistry/a2x_registry/a2x/search/a2x_search.py#L217](https://github.com/openJiuwen-ai/agent-protocol/blob/79201fe4c1bd1c8696f3ef750004969a906ccfcb/AgentRegistry/a2x_registry/a2x/search/a2x_search.py#L217) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [AgentRegistry/a2x_registry/auth/router.py#L68](https://github.com/openJiuwen-ai/agent-protocol/blob/79201fe4c1bd1c8696f3ef750004969a906ccfcb/AgentRegistry/a2x_registry/auth/router.py#L68) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 58 · corpus total: 83548 · executor: x86_64
> example: [AgentRegistry/a2x_registry/auth/deps.py#L146](https://github.com/openJiuwen-ai/agent-protocol/blob/79201fe4c1bd1c8696f3ef750004969a906ccfcb/AgentRegistry/a2x_registry/auth/deps.py#L146)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 21 · corpus total: 56644 · executor: x86_64
> example: [AgentRegistry/a2x_registry/a2x/search/a2x_search.py#L217](https://github.com/openJiuwen-ai/agent-protocol/blob/79201fe4c1bd1c8696f3ef750004969a906ccfcb/AgentRegistry/a2x_registry/a2x/search/a2x_search.py#L217)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [AgentRegistry/a2x_registry/auth/router.py#L68](https://github.com/openJiuwen-ai/agent-protocol/blob/79201fe4c1bd1c8696f3ef750004969a906ccfcb/AgentRegistry/a2x_registry/auth/router.py#L68)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

