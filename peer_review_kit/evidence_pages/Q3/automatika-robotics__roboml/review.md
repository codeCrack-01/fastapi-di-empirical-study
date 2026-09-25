# automatika-robotics/roboml

- GitHub: https://github.com/automatika-robotics/roboml
- Stars: 11 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 5 · commit: `4aad5f66aea8`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection Found` | src/roboml/models/llm.py#L141 | The code shows method parameters (e.g., 'streamer: TextIteratorStreamer') but no FastAPI dependency injection patterns like 'Depends()' or annotated dependencies. |
| 2 | `No Dependency Injection Found` | src/roboml/ray/node.py#L160 | The code uses an 'AsyncGenerator' parameter but lacks any FastAPI DI constructs such as 'Depends()' or security-related dependencies. |
| 3 | `No Dependency Injection Found` | tests/test_download.py#L12 | The pytest fixture uses setup/teardown logic but this is test infrastructure, not FastAPI dependency injection. |

## Pass 2 — reconcile with inventory of automatika-robotics/roboml

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No FastAPI dependency injection patterns (e.g., Depends(), security dependencies) are present in the code excerpts. The parameters identified (e.g., 'streamer: TextIteratorStreamer', 'AsyncGenerato... | src/roboml/models/llm.py#L141 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 5 | **false_pos** | [src/roboml/models/llm.py#L141](https://github.com/automatika-robotics/roboml/blob/4aad5f66aea830b5593c510e24dbe3295170ac2f/src/roboml/models/llm.py#L141) |

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [src/roboml/models/llm.py#L141](https://github.com/automatika-robotics/roboml/blob/4aad5f66aea830b5593c510e24dbe3295170ac2f/src/roboml/models/llm.py#L141)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

