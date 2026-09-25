# misears/Storyteller-AI-Agent

- GitHub: https://github.com/misears/Storyteller-AI-Agent
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 4 · commit: `cb5351ad94b7`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | storyteller_ai/backend/main-BlackDragon.py#L14 | The code defines a lifespan context manager for FastAPI, but this is unrelated to dependency injection. No Depends() or annotated dependencies are present. |
| 2 | `No Dependency Injection` | storyteller_ai/backend/main.py#L14 | Similar to main-BlackDragon.py, this file defines a lifespan context manager but contains no dependency injection constructs. |
| 3 | `No Dependency Injection` | storyteller_ai/backend/services/llm_client.py#L83 | The stream method is an async generator, but no dependency injection is used. Dependencies are not injected via FastAPI's Depends() or similar mechanisms. |

## Pass 2 — reconcile with inventory of misears/Storyteller-AI-Agent

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code defines a lifespan context manager for FastAPI, which is unrelated to dependency injection. No DI constructs like Depends() are present. | storyteller_ai/backend/main-BlackDragon.py#L14 |
| `C4|DEF` | false_pos | yes | Similar to main-BlackDragon.py, this file defines a lifespan context manager but contains no dependency injection constructs. | storyteller_ai/backend/main.py#L14 |
| `C4|DEF` | false_pos | yes | The stream method is an async generator, but no dependency injection is used. Dependencies are not injected via FastAPI's Depends() or similar mechanisms. | storyteller_ai/backend/services/llm_client.py#L83 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [storyteller_ai/backend/main-BlackDragon.py#L14](https://github.com/misears/Storyteller-AI-Agent/blob/cb5351ad94b7d8db2bca5574351621570b88fe74/storyteller_ai/backend/main-BlackDragon.py#L14) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [storyteller_ai/backend/main-BlackDragon.py#L14](https://github.com/misears/Storyteller-AI-Agent/blob/cb5351ad94b7d8db2bca5574351621570b88fe74/storyteller_ai/backend/main-BlackDragon.py#L14)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

