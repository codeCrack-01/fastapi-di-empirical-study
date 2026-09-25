# Junping0645/TAB

- GitHub: https://github.com/Junping0645/TAB
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `eeb0a90d2ad7`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | orchestrator/agent.py#L39 | The code excerpt shows an async function `run_research` with regular parameters (topic, budget, etc.), but no use of FastAPI's `Depends` or any dependency injection patterns. The static summary con... |

## Pass 2 — reconcile with inventory of Junping0645/TAB

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No dependency injection patterns (e.g., FastAPI Depends) are present in the code excerpt. The function `run_research` uses standard async parameters without DI annotations. | orchestrator/agent.py#L39 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [orchestrator/agent.py#L39](https://github.com/Junping0645/TAB/blob/eeb0a90d2ad7bf237d387cab9d1ef530246a282a/orchestrator/agent.py#L39) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [orchestrator/agent.py#L39](https://github.com/Junping0645/TAB/blob/eeb0a90d2ad7bf237d387cab9d1ef530246a282a/orchestrator/agent.py#L39)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

