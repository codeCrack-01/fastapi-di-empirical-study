# DockVault/vault

- GitHub: https://github.com/DockVault/vault
- Stars: 4 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 412 · commit: `cf65c2cbc10c`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection via FastAPI Depends` | app/api/api_server.py#L2697 | Multiple endpoints use Depends() to inject dependencies like current_user, db, and audit logger. This decouples business logic from HTTP handling, enabling testability and modularity. For example, ... |

## Pass 2 — reconcile with inventory of DockVault/vault

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `dependency_injection_via_depends` | dependency_injection_via_depends | yes | The code consistently uses FastAPI Depends() for injecting dependencies like current_user, db, and audit logger across multiple endpoints (e.g., create_log_token, upload_brand_asset, get_zk_enabled... | app/api/api_server.py#L2697 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 303 | **false_pos** | [app/api/api_server.py#L1045](https://github.com/DockVault/vault/blob/cf65c2cbc10c3e695f041a7331cd0242c3bb7db2/app/api/api_server.py#L1045) |
| `C4|DEF` | C4 | 108 | **false_pos** | [app/api/api_server.py#L9977](https://github.com/DockVault/vault/blob/cf65c2cbc10c3e695f041a7331cd0242c3bb7db2/app/api/api_server.py#L9977) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/core/database.py#L122](https://github.com/DockVault/vault/blob/cf65c2cbc10c3e695f041a7331cd0242c3bb7db2/app/core/database.py#L122) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 303 · corpus total: 83548 · executor: x86_64
> example: [app/api/api_server.py#L1045](https://github.com/DockVault/vault/blob/cf65c2cbc10c3e695f041a7331cd0242c3bb7db2/app/api/api_server.py#L1045)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 108 · corpus total: 56644 · executor: x86_64
> example: [app/api/api_server.py#L9977](https://github.com/DockVault/vault/blob/cf65c2cbc10c3e695f041a7331cd0242c3bb7db2/app/api/api_server.py#L9977)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/core/database.py#L122](https://github.com/DockVault/vault/blob/cf65c2cbc10c3e695f041a7331cd0242c3bb7db2/app/core/database.py#L122)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

