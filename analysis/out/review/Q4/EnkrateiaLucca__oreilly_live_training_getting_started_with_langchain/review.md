# EnkrateiaLucca/oreilly_live_training_getting_started_with_langchain

- GitHub: https://github.com/EnkrateiaLucca/oreilly_live_training_getting_started_with_langchain
- Stars: 81 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 2 · commit: `e4044aa11f76`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of EnkrateiaLucca/oreilly_live_training_getting_started_with_langchain

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code at both cited locations (L31 and L178) correctly implements standard LangChain patterns for LLM streaming and RAG retrieval chains. No contradictions to the 'false_pos' label are found in ... | archive/scripts/rag_methods.py#L31 |
| `C4|DEF` | false_pos | yes | The code at both cited locations (L31 and L178) correctly implements standard LangChain patterns for LLM streaming and RAG retrieval chains. No contradictions to the 'false_pos' label are found in ... | archive/scripts/rag_methods.py#L178 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 2 | **false_pos** | [archive/scripts/rag_methods.py#L31](https://github.com/EnkrateiaLucca/oreilly_live_training_getting_started_with_langchain/blob/e4044aa11f76fe8016b1ee260317354ac5056506/archive/scripts/rag_methods.py#L31) |

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [archive/scripts/rag_methods.py#L31](https://github.com/EnkrateiaLucca/oreilly_live_training_getting_started_with_langchain/blob/e4044aa11f76fe8016b1ee260317354ac5056506/archive/scripts/rag_methods.py#L31)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

