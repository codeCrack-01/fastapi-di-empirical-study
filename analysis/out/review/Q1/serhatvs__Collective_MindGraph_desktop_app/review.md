# serhatvs/Collective_MindGraph_desktop_app

- GitHub: https://github.com/serhatvs/Collective_MindGraph_desktop_app
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 18 · commit: `80d0b1b25e2e`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Lifespan Context Managers for Dependency Injection` | src/collective_mindgraph/engine/main.py#L36 | The lifespan context manager in create_app() initializes logging, builds engine context, and stores settings in app.state, demonstrating FastAPI's lifecycle-based dependency injection. |
| 2 | `Lifespan Context Managers for Dependency Injection` | src/collective_mindgraph/sync_server/app.py#L50 | The lifespan context manager in create_sync_app() sets up database, identities, and initializes SyncService, storing dependencies in app.state, aligning with FastAPI's lifecycle DI pattern. |

## Pass 2 — reconcile with inventory of serhatvs/Collective_MindGraph_desktop_app

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses lifespan context managers for dependency injection (e.g., initializing logging, building engine context, and storing settings in app.state). This matches the structural fin... | src/collective_mindgraph/engine/main.py#L36 |

### Missed by inventory (2)
- `Async context manager for database transactions` @ src/collective_mindgraph/sync_server/database.py#L32 — The `begin` method uses `@asynccontextmanager` to manage database transactions, which is a DI pattern missed by the inventory.
- `Context manager for SQLite connections` @ src/collective_mindgraph/infrastructure/persistence/sqlite_database.py#L18 — The `connect` method uses a `@contextmanager` to handle SQLite connections, representing another DI pattern not captured in the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 18 | **false_pos** | [scripts/benchmarks/asr_benchmark_common.py#L148](https://github.com/serhatvs/Collective_MindGraph_desktop_app/blob/80d0b1b25e2e324dfdfec2fd8963785977fc3f2e/scripts/benchmarks/asr_benchmark_common.py#L148) |

## `C4|DEF` — **false_pos**
> occurrences here: 18 · corpus total: 56644 · executor: x86_64
> example: [scripts/benchmarks/asr_benchmark_common.py#L148](https://github.com/serhatvs/Collective_MindGraph_desktop_app/blob/80d0b1b25e2e324dfdfec2fd8963785977fc3f2e/scripts/benchmarks/asr_benchmark_common.py#L148)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

