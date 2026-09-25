# sofi-280/autorepair-voice-agent

- GitHub: https://github.com/sofi-280/autorepair-voice-agent
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `573d08908940`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | server.py#L112 | The code defines a lifespan context manager for FastAPI but does not use FastAPI's dependency injection system (e.g., no Depends() calls, no dependency providers, no service injection patterns). Th... |

## Pass 2 — reconcile with inventory of sofi-280/autorepair-voice-agent

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code at server.py:112 defines a FastAPI lifespan context manager but does not implement any dependency injection patterns (no Depends(), providers, or service injection). The static analysis co... | server.py#L112 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [server.py#L112](https://github.com/sofi-280/autorepair-voice-agent/blob/573d08908940665d824352c46762b215ac8c5182/server.py#L112) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [server.py#L112](https://github.com/sofi-280/autorepair-voice-agent/blob/573d08908940665d824352c46762b215ac8c5182/server.py#L112)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

