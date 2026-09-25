# Addrick/agent-orchestrator

- GitHub: https://github.com/Addrick/agent-orchestrator
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 160 · commit: `7b870839cd30`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Strategy Pattern` | src/engine/providers/google.py#L369 | The `stream_google` function and similar methods in other provider files (e.g., `stream` in `local.py` and `stream_openai` in `openai.py`) implement provider-specific logic for streaming responses.... |
| 2 | `Context Manager for Dependency Lifecycle` | src/interfaces/kobold_engine_adapter.py#L210 | The `_lifespan` context manager in `kobold_engine_adapter.py` manages the MCP bridge's task group, ensuring proper initialization and cleanup. This is a common DI pattern for managing resource life... |
| 3 | `Context Manager for Transactional Resources` | src/memory/memory_manager.py#L209 | The `transaction` context manager in `memory_manager.py` handles SQLite database connections, ensuring transactions are committed or rolled back appropriately. This encapsulates resource management... |

## Pass 2 — reconcile with inventory of Addrick/agent-orchestrator

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `Strategy Pattern` | Strategy Pattern | yes | Provider classes (google.py, local.py, openai.py) implement dynamic algorithm selection via `matches()` and `limiters_for()` methods, aligning with the Strategy Pattern. | src/engine/providers/google.py#L369 |
| `Context Manager for Dependency Lifecycle` | Context Manager for Dependency Lifecycle | yes | The `_lifespan` context manager in kobold_engine_adapter.py properly manages MCP bridge task groups, ensuring resource lifecycle integrity. | src/interfaces/kobold_engine_adapter.py#L210 |
| `Context Manager for Transactional Resources` | Context Manager for Transactional Resources | yes | The `transaction` context manager in memory_manager.py encapsulates SQLite connection lifecycle with commit/rollback logic. | src/memory/memory_manager.py#L209 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 160 | **false_pos** | [eval_harnesses/framework/fixtures.py#L74](https://github.com/Addrick/agent-orchestrator/blob/7b870839cd30423eb239989c67cb35d503cf9fbc/eval_harnesses/framework/fixtures.py#L74) |

## `C4|DEF` — **false_pos**
> occurrences here: 160 · corpus total: 56644 · executor: x86_64
> example: [eval_harnesses/framework/fixtures.py#L74](https://github.com/Addrick/agent-orchestrator/blob/7b870839cd30423eb239989c67cb35d503cf9fbc/eval_harnesses/framework/fixtures.py#L74)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

