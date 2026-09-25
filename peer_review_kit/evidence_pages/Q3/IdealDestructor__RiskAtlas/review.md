# IdealDestructor/RiskAtlas

- GitHub: https://github.com/IdealDestructor/RiskAtlas
- Stars: 10 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 3 · commit: `00a256194208`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | apps/api/app/llm/gateway.py#L175 | The code uses direct attribute access (self._client) and method calls without any explicit dependency injection patterns. The LLMGateway class appears to be managing its own dependencies internally... |
| 2 | `No Dependency Injection` | apps/api/app/pipeline/reporter.py#L91 | The stream_report function accepts LLMGateway as a parameter, but this is a regular function argument rather than an injected dependency. There is no use of FastAPI's Depends() or similar DI mechan... |

## Pass 2 — reconcile with inventory of IdealDestructor/RiskAtlas

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No DI patterns found in the code excerpts; dependencies are managed internally via self._client and function parameters without FastAPI's DI mechanisms. | apps/api/app/llm/gateway.py#L175 |
| `C4|DEF` | false_pos | yes | No DI patterns found in the code excerpts; the function uses internal state and no dependency injection mechanisms. | apps/api/app/pipeline/orchestrator.py#L318 |
| `C4|DEF` | false_pos | yes | No DI patterns found in the code excerpts; the function accepts LLMGateway as a regular parameter, not via FastAPI's DI system. | apps/api/app/pipeline/reporter.py#L91 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 3 | **false_pos** | [apps/api/app/llm/gateway.py#L175](https://github.com/IdealDestructor/RiskAtlas/blob/00a256194208d25101ad1ef333cd88cee48a78d5/apps/api/app/llm/gateway.py#L175) |

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [apps/api/app/llm/gateway.py#L175](https://github.com/IdealDestructor/RiskAtlas/blob/00a256194208d25101ad1ef333cd88cee48a78d5/apps/api/app/llm/gateway.py#L175)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

