# qiuziyan1998/LMCache

- GitHub: https://github.com/qiuziyan1998/LMCache
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 205 · commit: `cb193c741be9`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `context managers for resource management` | examples/disagg_prefill/disagg_proxy_server.py#L82 | The lifespan context manager handles startup/shutdown logic, typical in FastAPI for lifecycle management, though not traditional DI. |
| 2 | `environment-based configuration injection` | examples/disagg_prefill/disagg_proxy_server.py#L475 | Variables like BOUND_CLIENT are set via os.getenv, indicating configuration is injected from the environment rather than hardcoded. |
| 3 | `context managers for profiling` | lmcache/observability.py#L164 | ProfileProcessTokens uses context managers to measure operation durations, a form of aspect-oriented resource management but not DI. |

## Pass 2 — reconcile with inventory of qiuziyan1998/LMCache

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts show environment variable configuration and FastAPI lifespan context managers, which are not dependency injection but rather configuration and lifecycle management. No actual DI p... | examples/disagg_prefill/disagg_proxy_server.py#L82 |

### Missed by inventory (1)
- `context managers for profiling` @ lmcache/observability.py#L164 — The code uses context managers for timing measurements (e.g., @contextmanager decorators), but these are profiling tools, not DI. The inventory may have misclassified them as DI.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 205 | **false_pos** | [examples/blend_kv_v1/blend.py#L62](https://github.com/qiuziyan1998/LMCache/blob/cb193c741be965178f8228ae6ce85d72ce7c8c44/examples/blend_kv_v1/blend.py#L62) |

## `C4|DEF` — **false_pos**
> occurrences here: 205 · corpus total: 56644 · executor: x86_64
> example: [examples/blend_kv_v1/blend.py#L62](https://github.com/qiuziyan1998/LMCache/blob/cb193c741be965178f8228ae6ce85d72ce7c8c44/examples/blend_kv_v1/blend.py#L62)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

