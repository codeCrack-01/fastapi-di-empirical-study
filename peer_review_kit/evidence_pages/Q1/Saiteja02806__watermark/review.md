# Saiteja02806/watermark

- GitHub: https://github.com/Saiteja02806/watermark
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 8 · commit: `2e001986efa2`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | apps/api/database/sqlite.py#L17 | The code defines a context manager for database connections but does not use FastAPI's @depends decorator or any DI-specific patterns. The connection is managed via a utility function rather than i... |
| 2 | `No Dependency Injection` | apps/api/main.py#L25 | The lifespan handler uses FastAPI's asynccontextmanager for lifecycle management, but this is not dependency injection. No dependencies are injected into the application or its routes. |
| 3 | `No Dependency Injection` | apps/api/services/event_service.py#L11 | Services like project_service and process_supervisor are imported directly and used within functions, indicating direct coupling rather than injected dependencies. |
| 4 | `No Dependency Injection` | tests/test_api.py#L19 | The test setup uses FastAPI's TestClient but does not demonstrate dependency injection in the application code under test. |
| 5 | `No Dependency Injection` | workers/inpainting_worker/validate_output.py#L159 | Functions like inspect_rendered_frames and inspect_encoded_video use utility functions directly without any DI mechanism, relying on direct imports and function calls. |

## Pass 2 — reconcile with inventory of Saiteja02806/watermark

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code does not use FastAPI's @depends or any DI-specific patterns; dependencies are managed via utility functions and direct imports. | apps/api/database/sqlite.py#L17 |
| `C4|DEF` | false_pos | yes | Lifespan handler uses FastAPI's asynccontextmanager for lifecycle management, not dependency injection. | apps/api/main.py#L25 |
| `C4|DEF` | false_pos | yes | Services are imported directly and used within functions, indicating direct coupling rather than injected dependencies. | apps/api/services/event_service.py#L11 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 8 | **false_pos** | [apps/api/database/sqlite.py#L17](https://github.com/Saiteja02806/watermark/blob/2e001986efa221ed28f68dae3a092ae14e310e94/apps/api/database/sqlite.py#L17) |

## `C4|DEF` — **false_pos**
> occurrences here: 8 · corpus total: 56644 · executor: x86_64
> example: [apps/api/database/sqlite.py#L17](https://github.com/Saiteja02806/watermark/blob/2e001986efa221ed28f68dae3a092ae14e310e94/apps/api/database/sqlite.py#L17)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

