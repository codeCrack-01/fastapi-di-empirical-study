# roberjo/roomba-telemetry

- GitHub: https://github.com/roberjo/roomba-telemetry
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 5 · commit: `10e63d1f7fa0`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with generator-based resource management` | api/api/db.py#L25 | The get_db() function is a generator that yields a sqlite3.Connection object, closing it in a try-finally block. This pattern is used in 3 endpoints (errors.py:L19, missions.py:L19, status.py:L16) ... |

## Pass 2 — reconcile with inventory of roberjo/roomba-telemetry

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's dependency injection via Depends(get_db) to manage database connections, which aligns with the C1|BARE|SIG fingerprint (bare dependency injection with signal handl... | api/api/routers/errors.py#L19 |
| `C4|USED` | true_pos | **no (overturn)** | The get_db() function is a valid FastAPI dependency generator that yields and closes database connections, matching the C4|USED fingerprint (used dependency injection with resource management). The... | api/api/db.py#L25 |

### Missed by inventory (1)
- `FastAPI dependency injection usage` @ api/api/routers/status.py#L16 — The get_status endpoint uses Depends(get_db) but was not counted in the inventory's C1|BARE|SIG or C4|USED labels.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 4 | **false_pos** | [api/api/routers/errors.py#L19](https://github.com/roberjo/roomba-telemetry/blob/10e63d1f7fa0cfc395c27bbaec7995580845db63/api/api/routers/errors.py#L19) |
| `C4|USED` | C4 | 1 | **false_pos** | [api/api/db.py#L25](https://github.com/roberjo/roomba-telemetry/blob/10e63d1f7fa0cfc395c27bbaec7995580845db63/api/api/db.py#L25) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 4 · corpus total: 83548 · executor: x86_64
> example: [api/api/routers/errors.py#L19](https://github.com/roberjo/roomba-telemetry/blob/10e63d1f7fa0cfc395c27bbaec7995580845db63/api/api/routers/errors.py#L19)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [api/api/db.py#L25](https://github.com/roberjo/roomba-telemetry/blob/10e63d1f7fa0cfc395c27bbaec7995580845db63/api/api/db.py#L25)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

