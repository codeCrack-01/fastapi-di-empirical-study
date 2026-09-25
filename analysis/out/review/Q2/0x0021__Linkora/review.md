# 0x0021/Linkora

- GitHub: https://github.com/0x0021/Linkora
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 36 · commit: `ba6d54387788`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency with yield` | web/dependencies.py#L224 | The function get_store_dep uses yield syntax and try-finally block to manage resource cleanup, which is characteristic of FastAPI dependency injection. This is seen in the code: 'def get_store_dep(... |

## Pass 2 — reconcile with inventory of 0x0021/Linkora

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code in web/dependencies.py:224 correctly implements FastAPI dependency injection with yield, which matches the structural fingerprint. The panel's 'false_pos' label is incorrect. | web/dependencies.py#L224 |

### Missed by inventory (1)
- `Context manager with explicit resource cleanup in FastAPI dependencies` @ web/dependencies.py#L224 — The inventory may have missed this specific pattern of yield-based dependency injection with try-finally cleanup, which is a valid and idiomatic FastAPI usage.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 36 | **false_pos** | [src/llm/agent_steps/stream.py#L27](https://github.com/0x0021/Linkora/blob/ba6d5438778808d5c675f58480c099ad7bbf1f87/src/llm/agent_steps/stream.py#L27) |

## `C4|DEF` — **false_pos**
> occurrences here: 36 · corpus total: 56644 · executor: x86_64
> example: [src/llm/agent_steps/stream.py#L27](https://github.com/0x0021/Linkora/blob/ba6d5438778808d5c675f58480c099ad7bbf1f87/src/llm/agent_steps/stream.py#L27)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

