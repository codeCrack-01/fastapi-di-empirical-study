# TryCaspian/caspian-sdk

- GitHub: https://github.com/TryCaspian/caspian-sdk
- Stars: 516 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 117 · commit: `718a96d6d04c`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | server/src/comm_gateway/auth.py#L21 | The get_project function uses Depends(get_session) to inject a database session, and is itself used as a dependency in routes via Depends(get_project). This creates a dependency chain where route h... |
| 2 | `Repeated dependency injection pattern` | server/src/comm_gateway/routes/api.py#L132 | Multiple route handlers (create_customer, list_customers, etc.) use the same injection pattern: project=Depends(get_project) and session=Depends(get_session). This shows a consistent DI approach ac... |

## Pass 2 — reconcile with inventory of TryCaspian/caspian-sdk

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | yes | The code correctly uses FastAPI's Depends injection pattern for both session and project dependencies, confirming the panel's assessment that this is a false positive. | server/src/comm_gateway/routes/api.py#L132 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 109 | **false_pos** | [server/src/comm_gateway/auth.py#L21](https://github.com/TryCaspian/caspian-sdk/blob/718a96d6d04cb76c7ccce942d2532fd4adbfd545/server/src/comm_gateway/auth.py#L21) |
| `C4|DEF` | C4 | 7 | **false_pos** | [server/src/comm_gateway/main.py#L104](https://github.com/TryCaspian/caspian-sdk/blob/718a96d6d04cb76c7ccce942d2532fd4adbfd545/server/src/comm_gateway/main.py#L104) |
| `C4|USED` | C4 | 1 | **false_pos** | [server/src/comm_gateway/auth.py#L15](https://github.com/TryCaspian/caspian-sdk/blob/718a96d6d04cb76c7ccce942d2532fd4adbfd545/server/src/comm_gateway/auth.py#L15) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 109 · corpus total: 83548 · executor: x86_64
> example: [server/src/comm_gateway/auth.py#L21](https://github.com/TryCaspian/caspian-sdk/blob/718a96d6d04cb76c7ccce942d2532fd4adbfd545/server/src/comm_gateway/auth.py#L21)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [server/src/comm_gateway/main.py#L104](https://github.com/TryCaspian/caspian-sdk/blob/718a96d6d04cb76c7ccce942d2532fd4adbfd545/server/src/comm_gateway/main.py#L104)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [server/src/comm_gateway/auth.py#L15](https://github.com/TryCaspian/caspian-sdk/blob/718a96d6d04cb76c7ccce942d2532fd4adbfd545/server/src/comm_gateway/auth.py#L15)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

