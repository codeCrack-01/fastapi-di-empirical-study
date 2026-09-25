# DevOpsAIguru123/awesome-agentic-devops

- GitHub: https://github.com/DevOpsAIguru123/awesome-agentic-devops
- Stars: 72 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 14 · commit: `d426b7df8977`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI Dependency Injection` | agents/container-image-release-advisor/adk/app/fast_api_app.py#L45 | The code defines a lifespan context manager but does not use FastAPI's @depend or @security decorators. Services are retrieved via function calls (services.get_session_service()) rather than inject... |
| 2 | `Test Mocking Not DI` | agents/container-image-release-advisor/claude/tests/test_agent.py#L73 | Test cases define fake_query functions as test doubles, not FastAPI dependencies. These are mocking implementations for testing, not part of FastAPI's dependency injection system. |

## Pass 2 — reconcile with inventory of DevOpsAIguru123/awesome-agentic-devops

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No FastAPI dependency injection patterns found in the cited code. The lifespan context manager and service retrieval via function calls (services.get_*) are not FastAPI DI constructs. | agents/container-image-release-advisor/adk/app/fast_api_app.py#L45 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 14 | **false_pos** | [agents/container-image-release-advisor/adk/app/fast_api_app.py#L45](https://github.com/DevOpsAIguru123/awesome-agentic-devops/blob/d426b7df8977930a683231c7dfae04e58c6e2238/agents/container-image-release-advisor/adk/app/fast_api_app.py#L45) |

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [agents/container-image-release-advisor/adk/app/fast_api_app.py#L45](https://github.com/DevOpsAIguru123/awesome-agentic-devops/blob/d426b7df8977930a683231c7dfae04e58c6e2238/agents/container-image-release-advisor/adk/app/fast_api_app.py#L45)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

