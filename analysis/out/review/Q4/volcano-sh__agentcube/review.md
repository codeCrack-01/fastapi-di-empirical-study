# volcano-sh/agentcube

- GitHub: https://github.com/volcano-sh/agentcube
- Stars: 163 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 2 · commit: `7a85d4f76a8e`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | integrations/dify-plugin/tools/agentcube-code-interpreter.py#L24 | The code shows a class method `execute` with parameters like `router_url` and `workload_manager_url`, but no dependencies are injected via FastAPI's `Depends` or similar mechanisms. The class `Agen... |
| 2 | `No Dependency Injection` | test/e2e/test_mcp_code_interpreter.py#L74 | The async context manager `_mcp_client_session` uses `httpx2` and `mcp` libraries directly but does not demonstrate any dependency injection patterns. Parameters are passed explicitly, not injected. |

## Pass 2 — reconcile with inventory of volcano-sh/agentcube

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts show no dependency injection patterns (e.g., no use of FastAPI Depends, inject, or similar constructs). The parameters in the methods are explicitly passed, not injected. | integrations/dify-plugin/tools/agentcube-code-interpreter.py#L24 |
| `C4|DEF` | false_pos | yes | The test file shows direct library usage (httpx2, mcp) with explicit parameters, not dependency injection. No DI-specific constructs are present. | test/e2e/test_mcp_code_interpreter.py#L74 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 2 | **false_pos** | [integrations/dify-plugin/tools/agentcube-code-interpreter.py#L24](https://github.com/volcano-sh/agentcube/blob/7a85d4f76a8e167eecbf293d99fd51a01d6cef6a/integrations/dify-plugin/tools/agentcube-code-interpreter.py#L24) |

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [integrations/dify-plugin/tools/agentcube-code-interpreter.py#L24](https://github.com/volcano-sh/agentcube/blob/7a85d4f76a8e167eecbf293d99fd51a01d6cef6a/integrations/dify-plugin/tools/agentcube-code-interpreter.py#L24)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

