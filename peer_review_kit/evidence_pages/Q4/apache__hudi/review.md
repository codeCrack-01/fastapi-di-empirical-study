# apache/hudi

- GitHub: https://github.com/apache/hudi
- Stars: 6209 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 10 · commit: `1f5a4fe53aaa`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Manual state-based dependency injection` | hudi-agent-gateway/src/hudi_agent_gateway/app.py#L57 | The lifespan context manager explicitly injects dependencies into app.state (e.g., app.state.trino_client, app.state.registry) which are later accessed via request.app.state in API routes. |
| 2 | `Manual state-based dependency injection` | hudi-agent-gateway/src/hudi_agent_gateway/api/chat.py#L127 | The _stream_chat function retrieves dependencies from request.app.state.agents, demonstrating access to manually injected state objects. |

## Pass 2 — reconcile with inventory of apache/hudi

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses manual state-based DI via app.state and request.app.state, which matches the fingerprint's structural pattern. | hudi-agent-gateway/src/hudi_agent_gateway/app.py#L57 |

### Missed by inventory (2)
- `Test fixture setup with dependency injection` @ hudi-agent-gateway/tests/conftest.py#L92 — Test fixtures inject dependencies (e.g., fake_trino) into app.state, but these were not captured as DI occurrences in the inventory.
- `Test agent loop with stateful dependencies` @ hudi-agent-gateway/tests/test_agent_loop.py#L89 — Test cases involving AgentCache and stateful session management were not flagged as DI occurrences.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 10 | **false_pos** | [hudi-agent-gateway/src/hudi_agent_gateway/api/chat.py#L127](https://github.com/apache/hudi/blob/1f5a4fe53aaadd69d91a208a833ace990ae06122/hudi-agent-gateway/src/hudi_agent_gateway/api/chat.py#L127) |

## `C4|DEF` — **false_pos**
> occurrences here: 10 · corpus total: 56644 · executor: x86_64
> example: [hudi-agent-gateway/src/hudi_agent_gateway/api/chat.py#L127](https://github.com/apache/hudi/blob/1f5a4fe53aaadd69d91a208a833ace990ae06122/hudi-agent-gateway/src/hudi_agent_gateway/api/chat.py#L127)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

