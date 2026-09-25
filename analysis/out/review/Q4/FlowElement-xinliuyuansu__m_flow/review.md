# FlowElement-xinliuyuansu/m_flow

- GitHub: https://github.com/FlowElement-xinliuyuansu/m_flow
- Stars: 4440 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 164 · commit: `0d585cda2f58`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based authentication injection` | m_flow/api/v1/activity/routers/get_activity_router.py#L67 | The list_activities endpoint uses Depends(_auth_dep()) to inject an authenticated User object, a common pattern in FastAPI for authentication dependencies. |
| 2 | `Variadic authentication dependencies` | m_flow/api/v1/add/routers/get_add_router.py#L78 | The ingest_data endpoint uses Depends(_auth()) which appears to be a different authentication dependency implementation than _auth_dep() used elsewhere, suggesting multiple authentication strategie... |
| 3 | `Consistent dependency naming convention` | m_flow/api/v1/coreference/routers.py#L117 | Multiple endpoints use Depends(_auth_dep()), indicating a standardized naming convention for authentication dependencies across different API modules. |
| 4 | `Service-specific dependencies` | m_flow/api/v1/datasets/routers/get_datasets_router.py#L155 | The list_datasets endpoint uses Depends(_get_auth_user()), showing a variation in dependency naming that likely corresponds to specific service requirements. |

## Pass 2 — reconcile with inventory of FlowElement-xinliuyuansu/m_flow

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true | **no (overturn)** | The code explicitly uses FastAPI's Depends() for authentication injection, which is a valid DI pattern. | m_flow/api/v1/activity/routers/get_activity_router.py#L67 |
| `C1|BARE|SIG` | true | **no (overturn)** | The code uses Depends() with parameterized authentication dependencies, which is a standard DI implementation in FastAPI. | m_flow/api/v1/add/routers/get_add_router.py#L78 |
| `C4|USED` | false_pos | yes | No explicit DI usage visible in provided code excerpts for the cited locations. | m_flow/adapters/relational/get_async_session.py#L16 |

### Missed by inventory (2)
- `Variadic authentication dependencies` @ m_flow/api/v1/add/routers/get_add_router.py#L78 — The use of different authentication dependency implementations (e.g., _auth() vs _auth_dep()) was not captured by the inventory.
- `Consistent dependency naming` @ m_flow/api/v1/coreference/routers.py#L117 — Standardized naming convention for authentication dependencies was not detected by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 82 | **false_pos** | [examples/relational_db_with_dlt/relational_db_and_dlt.py#L27](https://github.com/FlowElement-xinliuyuansu/m_flow/blob/0d585cda2f588af69fb872ae6914caba0c217816/examples/relational_db_with_dlt/relational_db_and_dlt.py#L27) |
| `C1|BARE|SIG` | C1 | 78 | **false_pos** | [m_flow/api/v1/activity/routers/get_activity_router.py#L67](https://github.com/FlowElement-xinliuyuansu/m_flow/blob/0d585cda2f588af69fb872ae6914caba0c217816/m_flow/api/v1/activity/routers/get_activity_router.py#L67) |
| `C4|USED` | C4 | 4 | **false_pos** | [m_flow/adapters/relational/get_async_session.py#L16](https://github.com/FlowElement-xinliuyuansu/m_flow/blob/0d585cda2f588af69fb872ae6914caba0c217816/m_flow/adapters/relational/get_async_session.py#L16) |

## `C4|DEF` — **false_pos**
> occurrences here: 82 · corpus total: 56644 · executor: x86_64
> example: [examples/relational_db_with_dlt/relational_db_and_dlt.py#L27](https://github.com/FlowElement-xinliuyuansu/m_flow/blob/0d585cda2f588af69fb872ae6914caba0c217816/examples/relational_db_with_dlt/relational_db_and_dlt.py#L27)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 78 · corpus total: 83548 · executor: x86_64
> example: [m_flow/api/v1/activity/routers/get_activity_router.py#L67](https://github.com/FlowElement-xinliuyuansu/m_flow/blob/0d585cda2f588af69fb872ae6914caba0c217816/m_flow/api/v1/activity/routers/get_activity_router.py#L67)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 4 · corpus total: 1079 · executor: x86_64
> example: [m_flow/adapters/relational/get_async_session.py#L16](https://github.com/FlowElement-xinliuyuansu/m_flow/blob/0d585cda2f588af69fb872ae6914caba0c217816/m_flow/adapters/relational/get_async_session.py#L16)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

