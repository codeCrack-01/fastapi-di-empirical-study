# fwerkor/local-shell-mcp

- GitHub: https://github.com/fwerkor/local-shell-mcp
- Stars: 41 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 39 · commit: `2306ebfc5f54`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends usage` | src/local_shell_mcp/http_app.py#L82 | The code explicitly uses FastAPI's Depends() to inject a dependency (principal_dep) into an endpoint. This is a direct example of FastAPI's dependency injection system where PRINCIPAL_DEP is define... |

## Pass 2 — reconcile with inventory of fwerkor/local-shell-mcp

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code uses context managers for audit suppression and state management, but does not implement FastAPI-style dependency injection (e.g., no Depends() usage or parameterized dependency resolution... | src/local_shell_mcp/audit.py#L1134 |
| `C1|BARE|PARAM` | known | yes | The code explicitly uses FastAPI's Depends() to inject a dependency (principal_dep) into an endpoint, matching the 'known' label for this fingerprint. | src/local_shell_mcp/http_app.py#L82 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 38 | **false_pos** | [src/local_shell_mcp/audit.py#L1134](https://github.com/fwerkor/local-shell-mcp/blob/2306ebfc5f5440b5375a3c4f2c9fe520643186ee/src/local_shell_mcp/audit.py#L1134) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [src/local_shell_mcp/http_app.py#L82](https://github.com/fwerkor/local-shell-mcp/blob/2306ebfc5f5440b5375a3c4f2c9fe520643186ee/src/local_shell_mcp/http_app.py#L82) |

## `C4|DEF` — **false_pos**
> occurrences here: 38 · corpus total: 56644 · executor: x86_64
> example: [src/local_shell_mcp/audit.py#L1134](https://github.com/fwerkor/local-shell-mcp/blob/2306ebfc5f5440b5375a3c4f2c9fe520643186ee/src/local_shell_mcp/audit.py#L1134)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [src/local_shell_mcp/http_app.py#L82](https://github.com/fwerkor/local-shell-mcp/blob/2306ebfc5f5440b5375a3c4f2c9fe520643186ee/src/local_shell_mcp/http_app.py#L82)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

