# johnsonhk88/AI-Bank-Statement-Document-Automation-By-LLM-And-Personal-Finanical-Analysis-Prediction

- GitHub: https://github.com/johnsonhk88/AI-Bank-Statement-Document-Automation-By-LLM-And-Personal-Finanical-Analysis-Prediction
- Stars: 616 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 27 · commit: `60e673939bc1`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI function-based dependency injection` | api/app/api/agent_runs.py#L30 | The `Depends(get_db)` and `Depends(get_current_user)` patterns are used to inject database sessions and user authentication into endpoint functions. |
| 2 | `Reusable dependency providers` | api/app/deps.py#L9 | The `get_db` and `get_current_user` functions are defined as reusable dependencies, with `get_db` depending on `_get_session` from the database module. |
| 3 | `Authentication dependency chain` | api/app/deps.py#L14 | The `get_current_user` dependency uses `Depends(bearer)` for token validation and `Depends(get_db)` to query the database for the authenticated user. |

## Pass 2 — reconcile with inventory of johnsonhk88/AI-Bank-Statement-Document-Automation-By-LLM-And-Personal-Finanical-Analysis-Prediction

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses `Depends(get_db)` and `Depends(get_current_user)` in multiple endpoints (e.g., `create_agent_run`, `list_agent_runs`), which aligns with the structural fingerprint of FastA... | api/app/api/agent_runs.py#L30 |
| `C4|DEF` | true_pos | **no (overturn)** | The code in `get_session` (line 7) and `lifespan` (line 10) defines async session management and application lifecycle hooks, which match the structural fingerprint of database session and applicat... | api/app/db/session.py#L7 |

### Missed by inventory (2)
- `FastAPI middleware for error handling` @ api/app/main.py#L10 — The `error_middleware` function is not captured by the inventory, despite being a critical part of the application's error handling infrastructure.
- `Reusable dependency providers with async context managers` @ api/app/deps.py#L9 — The `get_db` and `get_current_user` dependencies use `asynccontextmanager` and are not explicitly labeled in the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 25 | **false_pos** | [api/app/api/agent_runs.py#L29](https://github.com/johnsonhk88/AI-Bank-Statement-Document-Automation-By-LLM-And-Personal-Finanical-Analysis-Prediction/blob/60e673939bc12dfcccd2d74e90d9963a71518de9/api/app/api/agent_runs.py#L29) |
| `C4|DEF` | C4 | 2 | **false_pos** | [api/app/db/session.py#L7](https://github.com/johnsonhk88/AI-Bank-Statement-Document-Automation-By-LLM-And-Personal-Finanical-Analysis-Prediction/blob/60e673939bc12dfcccd2d74e90d9963a71518de9/api/app/db/session.py#L7) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 25 · corpus total: 83548 · executor: x86_64
> example: [api/app/api/agent_runs.py#L29](https://github.com/johnsonhk88/AI-Bank-Statement-Document-Automation-By-LLM-And-Personal-Finanical-Analysis-Prediction/blob/60e673939bc12dfcccd2d74e90d9963a71518de9/api/app/api/agent_runs.py#L29)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [api/app/db/session.py#L7](https://github.com/johnsonhk88/AI-Bank-Statement-Document-Automation-By-LLM-And-Personal-Finanical-Analysis-Prediction/blob/60e673939bc12dfcccd2d74e90d9963a71518de9/api/app/db/session.py#L7)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

