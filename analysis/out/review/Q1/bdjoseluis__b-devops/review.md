# bdjoseluis/b-devops

- GitHub: https://github.com/bdjoseluis/b-devops
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 27 · commit: `244a35be620d`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Function-based dependency injection with FastAPI Depends` | backend/routers/ai_router.py#L7 | The router is configured with dependencies=[Depends(auth_required)], demonstrating use of FastAPI's Depends() for injecting an authentication dependency imported from auth_router. |
| 2 | `Function-based dependency injection with FastAPI Depends` | backend/routers/clients_router.py#L96 | The create_client endpoint uses user=Depends(auth_required) to inject the same authentication dependency, showing this pattern is repeated across multiple routers. |
| 3 | `Function-based dependency injection with FastAPI Depends` | backend/routers/osint_router.py#L19 | The router includes both Depends(osint_limiter) and Depends(auth_required), showing multiple dependencies injected via Depends() for rate limiting and authentication. |

## Pass 2 — reconcile with inventory of bdjoseluis/b-devops

_Presented fingerprints:_ `C1|BARE|PARAM`, `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | Multiple routers (ai_router.py, audit_router.py, devops_router.py) use Depends(auth_required) in router dependencies, matching the canonical fingerprint. | backend/routers/ai_router.py#L7 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code uses function parameters with Depends(auth_required), not signals. The panel incorrectly labeled this as false_pos when it's actually C1|BARE|PARAM. | backend/routers/clients_router.py#L96 |
| `C4|DEF` | false_pos | yes | The db.py code uses a global pool and context manager, not a class-based dependency definition. The panel's label is correct as the code does not match C4|DEF. | backend/db.py#L25 |

### Missed by inventory (1)
- `Multiple instances of Depends(auth_required) in function parameters across routers` @ backend/routers/clients_router.py#L96 — The inventory missed labeling these as C1|BARE|PARAM, but they were correctly identified in the panel's C1|BARE|PARAM label.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 13 | **known** | [backend/routers/ai_router.py#L7](https://github.com/bdjoseluis/b-devops/blob/244a35be620d2b20c25b040dd90f895b50e8f3cb/backend/routers/ai_router.py#L7) |
| `C1|BARE|SIG` | C1 | 7 | **false_pos** | [backend/routers/clients_router.py#L86](https://github.com/bdjoseluis/b-devops/blob/244a35be620d2b20c25b040dd90f895b50e8f3cb/backend/routers/clients_router.py#L86) |
| `C4|DEF` | C4 | 7 | **false_pos** | [backend/db.py#L25](https://github.com/bdjoseluis/b-devops/blob/244a35be620d2b20c25b040dd90f895b50e8f3cb/backend/db.py#L25) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 13 · corpus total: 18195 · executor: x86_64
> example: [backend/routers/ai_router.py#L7](https://github.com/bdjoseluis/b-devops/blob/244a35be620d2b20c25b040dd90f895b50e8f3cb/backend/routers/ai_router.py#L7)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 7 · corpus total: 83548 · executor: x86_64
> example: [backend/routers/clients_router.py#L86](https://github.com/bdjoseluis/b-devops/blob/244a35be620d2b20c25b040dd90f895b50e8f3cb/backend/routers/clients_router.py#L86)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [backend/db.py#L25](https://github.com/bdjoseluis/b-devops/blob/244a35be620d2b20c25b040dd90f895b50e8f3cb/backend/db.py#L25)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

