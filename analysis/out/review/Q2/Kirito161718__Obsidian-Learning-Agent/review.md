# Kirito161718/Obsidian-Learning-Agent

- GitHub: https://github.com/Kirito161718/Obsidian-Learning-Agent
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 129 · commit: `020d428dc399`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends Injection` | app/routers/agent.py#L15 | The `db: Session = Depends(get_db)` pattern injects a database session via FastAPI's dependency system, abstracting database connection management. |
| 2 | `Service Dependency Injection` | app/routers/obsidian.py#L36 | Injects `service: ObsidianIndexService = Depends(get_obsidian_index_service)` to decouple route logic from service creation. |
| 3 | `Cached Dependency Provider` | app/routers/obsidian.py#L35 | Uses `@lru_cache` on `get_obsidian_index_service()` to memoize service instances, ensuring singleton-like behavior for dependencies. |

## Pass 2 — reconcile with inventory of Kirito161718/Obsidian-Learning-Agent

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_depends_injection` | FastAPI Depends Injection | yes | The code correctly uses FastAPI's dependency injection system for database sessions and services. | app/routers/learning.py#L75 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 110 | **false_pos** | [app/routers/agent.py#L62](https://github.com/Kirito161718/Obsidian-Learning-Agent/blob/020d428dc399b52bae5fbf0c54dca7c73ce0e083/app/routers/agent.py#L62) |
| `C4|DEF` | C4 | 18 | **false_pos** | [app/graphs/official_checkpoint.py#L63](https://github.com/Kirito161718/Obsidian-Learning-Agent/blob/020d428dc399b52bae5fbf0c54dca7c73ce0e083/app/graphs/official_checkpoint.py#L63) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/db/database.py#L17](https://github.com/Kirito161718/Obsidian-Learning-Agent/blob/020d428dc399b52bae5fbf0c54dca7c73ce0e083/app/db/database.py#L17) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 110 · corpus total: 83548 · executor: x86_64
> example: [app/routers/agent.py#L62](https://github.com/Kirito161718/Obsidian-Learning-Agent/blob/020d428dc399b52bae5fbf0c54dca7c73ce0e083/app/routers/agent.py#L62)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 18 · corpus total: 56644 · executor: x86_64
> example: [app/graphs/official_checkpoint.py#L63](https://github.com/Kirito161718/Obsidian-Learning-Agent/blob/020d428dc399b52bae5fbf0c54dca7c73ce0e083/app/graphs/official_checkpoint.py#L63)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/db/database.py#L17](https://github.com/Kirito161718/Obsidian-Learning-Agent/blob/020d428dc399b52bae5fbf0c54dca7c73ce0e083/app/db/database.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

