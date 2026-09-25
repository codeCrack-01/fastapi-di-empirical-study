# mic1on/onestep

- GitHub: https://github.com/mic1on/onestep
- Stars: 23 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 133 · commit: `59e12c573631`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=2 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | apps/control-plane/backend/src/onestep_control_plane_api/api/routers/agent_ws.py#L350 | The code uses FastAPI's Depends() for dependency injection, as seen in 'auth: WebSocketIngestAuth = Depends(require_websocket_ingest_token)' and 'db: Session = Depends(get_db_session)'. |
| 2 | `FastAPI Depends injection` | apps/control-plane/backend/src/onestep_control_plane_api/api/routers/auth.py#L47 | The 'get_console_session' endpoint uses 'db: Session = Depends(get_db_session)' to inject a database session dependency. |
| 3 | `FastAPI Depends injection` | apps/control-plane/backend/src/onestep_control_plane_api/api/routers/commands.py#L38 | The router is configured with 'dependencies=[Depends(require_console_auth)]', applying an authentication dependency to all routes under this router. |
| 4 | `FastAPI Depends injection` | apps/control-plane/backend/src/onestep_control_plane_api/api/routers/connectors.py#L37 | The 'list_connectors_endpoint' uses 'db: Session = Depends(get_db_session)' to inject a database session dependency. |

## Pass 2 — reconcile with inventory of mic1on/onestep

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|DEF`, `C2|BARE|ascopes`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | known | **no (overturn)** | The code explicitly uses FastAPI's Depends() for dependency injection (e.g., 'db: Session = Depends(get_db_session)'). This matches the pattern of parameter injection, contradicting the 'false_pos'... | apps/control-plane/backend/src/onestep_control_plane_api/api/routers/agent_ws.py#L350 |
| `C4|DEF` | missed | **no (overturn)** | The inventory links reference files (ui_ws.py, main.py) not present in the provided code excerpts. This suggests the inventory missed these files entirely. | apps/control-plane/backend/src/onestep_control_plane_api/api/routers/ui_ws.py#L22 |

### Missed by inventory (1)
- `FastAPI Depends injection in routers not covered by code excerpts` @ apps/control-plane/backend/src/onestep_control_plane_api/api/routers/ui_ws.py#L22 — The inventory flagged this file for C4|DEF, but no code excerpt was provided to verify the pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 76 | **false_pos** | [apps/control-plane/backend/src/onestep_control_plane_api/api/routers/agent_ws.py#L349](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/routers/agent_ws.py#L349) |
| `C1|BARE|PARAM` | C1 | 28 | **known** | [apps/control-plane/backend/src/onestep_control_plane_api/api/routers/commands.py#L38](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/routers/commands.py#L38) |
| `C4|DEF` | C4 | 26 | **false_pos** | [apps/control-plane/backend/src/onestep_control_plane_api/api/routers/ui_ws.py#L22](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/routers/ui_ws.py#L22) |
| `C2|BARE|ascopes` | C2 | 2 | **known** | [apps/control-plane/backend/src/onestep_control_plane_api/api/security.py#L94](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/security.py#L94) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/control-plane/backend/src/onestep_control_plane_api/db/session.py#L45](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/db/session.py#L45) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 76 · corpus total: 83548 · executor: x86_64
> example: [apps/control-plane/backend/src/onestep_control_plane_api/api/routers/agent_ws.py#L349](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/routers/agent_ws.py#L349)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 28 · corpus total: 18195 · executor: x86_64
> example: [apps/control-plane/backend/src/onestep_control_plane_api/api/routers/commands.py#L38](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/routers/commands.py#L38)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 26 · corpus total: 56644 · executor: x86_64
> example: [apps/control-plane/backend/src/onestep_control_plane_api/api/routers/ui_ws.py#L22](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/routers/ui_ws.py#L22)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C2|BARE|ascopes` — **known**
> occurrences here: 2 · corpus total: 504 · executor: x86_64
> example: [apps/control-plane/backend/src/onestep_control_plane_api/api/security.py#L94](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/security.py#L94)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/control-plane/backend/src/onestep_control_plane_api/db/session.py#L45](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/db/session.py#L45)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

