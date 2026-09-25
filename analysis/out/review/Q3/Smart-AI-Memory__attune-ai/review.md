# Smart-AI-Memory/attune-ai

- GitHub: https://github.com/Smart-AI-Memory/attune-ai
- Stars: 10 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 385 · commit: `fe08f282fb0a`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection` | src/attune/ops/routes/curator.py#L102 | The `curator_dismiss` route uses `Depends(require_client_token)` to inject a client authentication dependency. This is FastAPI's standard DI pattern where dependencies are resolved via the `Depends... |
| 2 | `Reused authentication dependency` | src/attune/ops/routes/health_library.py#L115 | The `health_library_refresh` route also uses `Depends(require_client_token)`, indicating this is a shared authentication dependency used across multiple endpoints. |
| 3 | `Minimal DI usage` | src/attune/ops/routes/runner.py#L281 | Only one dependency (`require_client_token`) is visible in the code, suggesting DI is used sparingly and focused on authentication rather than broader dependency management. |

## Pass 2 — reconcile with inventory of Smart-AI-Memory/attune-ai

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_di_auth` | FastAPI DI usage for authentication | yes | Code confirms `require_client_token` is injected via `Depends()` in multiple routes (curator, health_library, runner) | src/attune/ops/routes/curator.py#L102 |
| `sparse_di_usage` | Minimal DI usage focused on authentication | yes | Only `require_client_token` dependency visible across all routes | src/attune/ops/routes/runner.py#L281 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 377 | **false_pos** | [agents/compliance_db.py#L70](https://github.com/Smart-AI-Memory/attune-ai/blob/fe08f282fb0ad9cbb7eedf75af2597336576578e/agents/compliance_db.py#L70) |
| `C1|BARE|SIG` | C1 | 8 | **false_pos** | [src/attune/ops/routes/curator.py#L102](https://github.com/Smart-AI-Memory/attune-ai/blob/fe08f282fb0ad9cbb7eedf75af2597336576578e/src/attune/ops/routes/curator.py#L102) |

## `C4|DEF` — **false_pos**
> occurrences here: 377 · corpus total: 56644 · executor: x86_64
> example: [agents/compliance_db.py#L70](https://github.com/Smart-AI-Memory/attune-ai/blob/fe08f282fb0ad9cbb7eedf75af2597336576578e/agents/compliance_db.py#L70)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 8 · corpus total: 83548 · executor: x86_64
> example: [src/attune/ops/routes/curator.py#L102](https://github.com/Smart-AI-Memory/attune-ai/blob/fe08f282fb0ad9cbb7eedf75af2597336576578e/src/attune/ops/routes/curator.py#L102)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

