# skyones-0/kimi-mcp

- GitHub: https://github.com/skyones-0/kimi-mcp
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `041671769b54`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Manual Dependency Initialization in Lifespan` | src/rest_api.py#L97 | The code defines an async lifespan context manager that manually initializes dependencies (e.g., state.indexer = get_indexer(), state.retriever = get_retriever()) and performs cleanup. This approac... |

## Pass 2 — reconcile with inventory of skyones-0/kimi-mcp

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code manually initializes dependencies in the lifespan context manager (e.g., state.indexer = get_indexer()) without using FastAPI's explicit DI system (e.g., Depends()), aligning with the labe... | src/rest_api.py#L97 |

### Missed by inventory (1)
- `Manual Dependency Initialization in Lifespan` @ src/rest_api.py#L97 — The inventory may have missed capturing this custom lifecycle-based DI pattern, which is distinct from FastAPI's explicit DI system but still constitutes a form of manual dependency management.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [src/rest_api.py#L97](https://github.com/skyones-0/kimi-mcp/blob/041671769b54082c5ed7bc5860b5552ac1cd9dbe/src/rest_api.py#L97) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [src/rest_api.py#L97](https://github.com/skyones-0/kimi-mcp/blob/041671769b54082c5ed7bc5860b5552ac1cd9dbe/src/rest_api.py#L97)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

