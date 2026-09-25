# Lukyyyyy/KairoCLI

- GitHub: https://github.com/Lukyyyyy/KairoCLI
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 83 · commit: `058f827b5114`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection (DI)` | src/kairocli/web_auth.py#L494 | The `make_require_admin` function injects the `get_current_user` dependency rather than hardcoding it, allowing the admin check to be decoupled from the authentication logic. |
| 2 | `Dependency Injection (DI)` | src/kairocli/web_app.py#L462 | The `get_current_user` function injects `user_store` and `jwt_secret` as parameters, making it reusable with different stores and secrets without modifying the function's internal logic. |
| 3 | `Dependency Injection (DI)` | src/kairocli/config.py#L493 | The `_config_file_lock` function injects `paths` as a parameter, allowing it to work with different configuration file paths without being tied to specific values. |
| 4 | `Dependency Injection (DI)` | src/kairocli/llm.py#L350 | The `create_llm_client` function injects `config` and `provider` parameters, enabling the creation of different LLM clients with varying configurations and providers. |

## Pass 2 — reconcile with inventory of Lukyyyyy/KairoCLI

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `DI_in_web_auth` | Dependency Injection (DI) | yes | The `make_require_admin` function correctly injects `get_current_user` as a dependency, decoupling admin checks from authentication logic. | src/kairocli/web_auth.py#L494 |
| `DI_in_web_app` | Dependency Injection (DI) | yes | The `get_current_user` function injects `user_store` and `jwt_secret` as parameters, enabling reuse with different stores and secrets. | src/kairocli/web_auth.py#L462 |
| `DI_in_config` | Dependency Injection (DI) | yes | The `_config_file_lock` function injects `paths` as a parameter, allowing flexibility with configuration file paths. | src/kairocli/config.py#L493 |
| `DI_in_llm` | Dependency Injection (DI) | yes | The `create_llm_client` function injects `config` and `provider` parameters, enabling dynamic LLM client creation. | src/kairocli/llm.py#L350 |

### Missed by inventory (2)
- `implicit_dependency_injection` @ src/kairocli/web_app.py#L1270 — The `update_wechat_channel` function uses `channel_store` and `wechat_hub` which may be injected via app context but are not explicitly passed as parameters.
- `implicit_dependency_injection` @ src/kairocli/web_app.py#L1282 — The `list_workspaces` function uses `selected_workspace_roots` which may be injected via app context but are not explicitly passed as parameters.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 43 | **false_pos** | [src/kairocli/agent/core.py#L440](https://github.com/Lukyyyyy/KairoCLI/blob/058f827b5114ca75676a22cf0d2b2c17581622d6/src/kairocli/agent/core.py#L440) |
| `C1|BARE|SIG` | C1 | 40 | **false_pos** | [src/kairocli/web_app.py#L781](https://github.com/Lukyyyyy/KairoCLI/blob/058f827b5114ca75676a22cf0d2b2c17581622d6/src/kairocli/web_app.py#L781) |

## `C4|DEF` — **false_pos**
> occurrences here: 43 · corpus total: 56644 · executor: x86_64
> example: [src/kairocli/agent/core.py#L440](https://github.com/Lukyyyyy/KairoCLI/blob/058f827b5114ca75676a22cf0d2b2c17581622d6/src/kairocli/agent/core.py#L440)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 40 · corpus total: 83548 · executor: x86_64
> example: [src/kairocli/web_app.py#L781](https://github.com/Lukyyyyy/KairoCLI/blob/058f827b5114ca75676a22cf0d2b2c17581622d6/src/kairocli/web_app.py#L781)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

