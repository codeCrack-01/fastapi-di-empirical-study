# KikuAI-Lab/reliapi

- GitHub: https://github.com/KikuAI-Lab/reliapi
- Stars: 8 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 6 · commit: `5ad71d97faf7`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of KikuAI-Lab/reliapi

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly implements streaming chat functionality with async methods, payload handling, and proper return types (AsyncIterator). The 'supports_streaming' method explicitly returns True, co... | reliapi/adapters/llm/anthropic.py#L54 |

### Missed by inventory (1)
- `streaming coordination pattern in handle_llm_stream_generator` @ reliapi/app/services.py#L2073 — The function 'handle_llm_stream_generator' orchestrates streaming across multiple LLM adapters but was not captured in the initial fingerprint inventory. It contains critical logic for streaming co...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 6 | **false_pos** | [reliapi/adapters/llm/anthropic.py#L54](https://github.com/KikuAI-Lab/reliapi/blob/5ad71d97faf753dcfb6801b1333081de298168c8/reliapi/adapters/llm/anthropic.py#L54) |

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [reliapi/adapters/llm/anthropic.py#L54](https://github.com/KikuAI-Lab/reliapi/blob/5ad71d97faf753dcfb6801b1333081de298168c8/reliapi/adapters/llm/anthropic.py#L54)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

