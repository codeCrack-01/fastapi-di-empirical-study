# nerdai/llm-agents-from-scratch

- GitHub: https://github.com/nerdai/llm-agents-from-scratch
- Stars: 176 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 19 · commit: `dabe7e54f3e5`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of nerdai/llm-agents-from-scratch

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts are test utility functions creating mock clients and message handlers using MagicMock/AsyncMock, which are standard test doubles, not actual dependency injection points in product... | tests/a2a/client/test_tools.py#L38 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 19 | **false_pos** | [tests/a2a/client/test_tools.py#L39](https://github.com/nerdai/llm-agents-from-scratch/blob/dabe7e54f3e5e8df4320afd9f1eef1a86ba5ff66/tests/a2a/client/test_tools.py#L39) |

## `C4|DEF` — **false_pos**
> occurrences here: 19 · corpus total: 56644 · executor: x86_64
> example: [tests/a2a/client/test_tools.py#L39](https://github.com/nerdai/llm-agents-from-scratch/blob/dabe7e54f3e5e8df4320afd9f1eef1a86ba5ff66/tests/a2a/client/test_tools.py#L39)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

