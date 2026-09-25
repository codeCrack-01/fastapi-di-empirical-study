# lm-webui/lm-webui

- GitHub: https://github.com/lm-webui/lm-webui
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 144 · commit: `bbe1362ad62b`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection` | backend/app/routes/api_tokens.py#L44 | The `Depends(get_current_user)` pattern is used to inject user authentication into the route, ensuring only authenticated users can create tokens. This is a core FastAPI DI pattern for handling aut... |
| 2 | `FastAPI Dependency Injection` | backend/app/routes/artifacts.py#L36 | The `Depends(get_current_user)` pattern is used to inject user authentication into artifact listing, ensuring only authenticated users can access artifacts. This is a core FastAPI DI pattern for ha... |
| 3 | `FastAPI Dependency Injection` | backend/app/routes/gguf.py#L21 | The `Depends(require_permission("models.install"))` pattern is used to inject permission checks into GGUF model routes, ensuring only authorized users can perform model operations. This is a core F... |

## Pass 2 — reconcile with inventory of lm-webui/lm-webui

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection_auth` | FastAPI Dependency Injection for Authentication | yes | The code uses `Depends(get_current_user)` consistently in routes requiring user authentication, aligning with FastAPI's standard pattern for injecting authentication dependencies. | backend/app/routes/api_tokens.py#L44 |
| `fastapi_dependency_injection_auth_artifacts` | FastAPI Dependency Injection for Authentication | yes | The `Depends(get_current_user)` pattern is correctly applied in artifact routes to enforce user authentication, matching FastAPI's standard practice. | backend/app/routes/artifacts.py#L36 |
| `fastapi_dependency_injection_authorization` | FastAPI Dependency Injection for Authorization | yes | The `Depends(require_permission("models.install"))` pattern is used in GGUF model routes to enforce authorization, consistent with FastAPI's custom dependency pattern for role-based access control. | backend/app/routes/gguf.py#L21 |

### Missed by inventory (2)
- `FastAPI Dependency Injection for Authentication` @ backend/app/routes/chat.py#L29 — The `chat_completion` and `chat_stream` routes use `Depends(get_current_user)` for authentication but were not cited in initial observations.
- `FastAPI Dependency Injection for Authentication` @ backend/app/routes/auth.py#L166 — The `get_current_user_info` route uses `Depends(get_current_user)` for authentication but was not cited in initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 102 | **false_pos** | [backend/app/routes/admin.py#L44](https://github.com/lm-webui/lm-webui/blob/bbe1362ad62b91cf924e6664198e9d5ab2165fde/backend/app/routes/admin.py#L44) |
| `C4|DEF` | C4 | 25 | **false_pos** | [backend/app/agents/runner.py#L87](https://github.com/lm-webui/lm-webui/blob/bbe1362ad62b91cf924e6664198e9d5ab2165fde/backend/app/agents/runner.py#L87) |
| `C1|BARE|PARAM` | C1 | 17 | **known** | [backend/app/routes/agents.py#L59](https://github.com/lm-webui/lm-webui/blob/bbe1362ad62b91cf924e6664198e9d5ab2165fde/backend/app/routes/agents.py#L59) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 102 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routes/admin.py#L44](https://github.com/lm-webui/lm-webui/blob/bbe1362ad62b91cf924e6664198e9d5ab2165fde/backend/app/routes/admin.py#L44)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 25 · corpus total: 56644 · executor: x86_64
> example: [backend/app/agents/runner.py#L87](https://github.com/lm-webui/lm-webui/blob/bbe1362ad62b91cf924e6664198e9d5ab2165fde/backend/app/agents/runner.py#L87)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 17 · corpus total: 18195 · executor: x86_64
> example: [backend/app/routes/agents.py#L59](https://github.com/lm-webui/lm-webui/blob/bbe1362ad62b91cf924e6664198e9d5ab2165fde/backend/app/routes/agents.py#L59)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

