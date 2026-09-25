# aXtr1o1/ConvAgent

- GitHub: https://github.com/aXtr1o1/ConvAgent
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 2 · commit: `95ee57f8bf58`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of aXtr1o1/ConvAgent

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No explicit code contradicts the label; the code appears to follow standard patterns for chat completion and document parsing without obvious misalignment. | backend/agents/casual_llm.py#L49 |
| `C4|DEF` | false_pos | yes | No explicit code contradicts the label; the code in pdf_parser.py aligns with standard document parsing logic. | ingestion/collectors/pdf_parser.py#L52 |

### Missed by inventory (1)
- `Structured data extraction (DTC, Sub-DTC, Steps) as described in comments` @ ingestion/collectors/pdf_parser.py#L52 — The comments in the code explicitly request structured data extraction (e.g., DTC → Sub-DTC → Steps) with specific JSON formatting requirements, but the actual implementation (iter_block_items, par...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/agents/casual_llm.py#L49](https://github.com/aXtr1o1/ConvAgent/blob/95ee57f8bf581a4b9478b58041da637e832dfa73/backend/agents/casual_llm.py#L49) |

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/agents/casual_llm.py#L49](https://github.com/aXtr1o1/ConvAgent/blob/95ee57f8bf581a4b9478b58041da637e832dfa73/backend/agents/casual_llm.py#L49)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

