# aws-samples/sample-agent-platform-with-agentcore

- GitHub: https://github.com/aws-samples/sample-agent-platform-with-agentcore
- Stars: 16 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 77 · commit: `3a886e4448e2`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection for authentication` | backend/app/api/agents.py#L22 | The `Depends(get_current_user)` is used to inject user authentication into the `list_agents` endpoint, ensuring only authenticated users can access the endpoint. |
| 2 | `FastAPI Depends injection for admin access` | backend/app/api/channels.py#L24 | The `Depends(require_admin)` is applied to the `list_channels` endpoint, restricting access to admin users only via FastAPI's dependency injection system. |
| 3 | `Recurring Depends usage in route parameters` | backend/app/api/ecosystem.py#L17 | Multiple endpoints use `Depends(get_current_user)` and `Depends(require_admin)` to manage authentication and authorization, showing a consistent pattern of dependency injection across routes. |

## Pass 2 — reconcile with inventory of aws-samples/sample-agent-platform-with-agentcore

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | yes | The code uses FastAPI Depends for authentication/authorization parameters (e.g., `Depends(get_current_user)`), which are BARE parameters, not signatures. The inventory likely misclassified these as... | backend/app/api/agents.py#L22 |
| `C1|BARE|PARAM` | true | yes | The code explicitly uses `Depends(...)` in route parameters (e.g., `user: str = Depends(get_current_user)`), confirming BARE parameter injection. | backend/app/api/agents.py#L22 |
| `C1|BARE|PARAM` | true | yes | Admin access is enforced via `Depends(require_admin)` in route parameters, consistent with BARE parameter usage. | backend/app/api/channels.py#L24 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 70 | **false_pos** | [backend/app/api/agents.py#L22](https://github.com/aws-samples/sample-agent-platform-with-agentcore/blob/3a886e4448e2facb2cff56e9a5c8dc765e8c1596/backend/app/api/agents.py#L22) |
| `C1|BARE|PARAM` | C1 | 6 | **known** | [backend/app/api/evals.py#L10](https://github.com/aws-samples/sample-agent-platform-with-agentcore/blob/3a886e4448e2facb2cff56e9a5c8dc765e8c1596/backend/app/api/evals.py#L10) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/main.py#L37](https://github.com/aws-samples/sample-agent-platform-with-agentcore/blob/3a886e4448e2facb2cff56e9a5c8dc765e8c1596/backend/app/main.py#L37) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 70 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/agents.py#L22](https://github.com/aws-samples/sample-agent-platform-with-agentcore/blob/3a886e4448e2facb2cff56e9a5c8dc765e8c1596/backend/app/api/agents.py#L22)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 6 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/evals.py#L10](https://github.com/aws-samples/sample-agent-platform-with-agentcore/blob/3a886e4448e2facb2cff56e9a5c8dc765e8c1596/backend/app/api/evals.py#L10)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L37](https://github.com/aws-samples/sample-agent-platform-with-agentcore/blob/3a886e4448e2facb2cff56e9a5c8dc765e8c1596/backend/app/main.py#L37)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

