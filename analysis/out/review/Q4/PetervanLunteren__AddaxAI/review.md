# PetervanLunteren/AddaxAI

- GitHub: https://github.com/PetervanLunteren/AddaxAI
- Stars: 189 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 171 · commit: `34b62da2ce00`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends Injection` | backend/app/api/routers/detections.py#L183 | The `Depends(get_db)` pattern injects a database session into the route handler, decoupling the detection crop logic from database connection details. This follows the Dependency Injection principl... |
| 2 | `FastAPI Depends Injection` | backend/app/api/routers/detections.py#L234 | The `Depends(get_db)` pattern is used again in the verification endpoint, demonstrating consistent DI for database access across different route handlers. |
| 3 | `FastAPI Depends Injection` | backend/app/api/routers/events.py#L132 | The `Depends(get_db)` pattern is applied in event generation routes, showing DI is standardized across the codebase for database dependencies. |

## Pass 2 — reconcile with inventory of PetervanLunteren/AddaxAI

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `detections.py:183` | FastAPI Depends Injection | yes | Code consistently uses Depends(get_db) for database session injection in detection routes | backend/app/api/routers/detections.py#L183 |
| `detections.py:234` | FastAPI Depends Injection | yes | Verification endpoint correctly uses Depends(get_db) for database access | backend/app/api/routers/detections.py#L234 |
| `events.py:132` | FastAPI Depends Injection | yes | Event generation routes properly use Depends(get_db) for database dependency injection | backend/app/api/routers/events.py#L132 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 133 | **false_pos** | [backend/app/api/routers/deployment_queue.py#L85](https://github.com/PetervanLunteren/AddaxAI/blob/34b62da2ce000e81bc3fb51057c7fecb11a217e3/backend/app/api/routers/deployment_queue.py#L85) |
| `C4|DEF` | C4 | 37 | **false_pos** | [backend/app/core/job_cancellation.py#L99](https://github.com/PetervanLunteren/AddaxAI/blob/34b62da2ce000e81bc3fb51057c7fecb11a217e3/backend/app/core/job_cancellation.py#L99) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/base.py#L150](https://github.com/PetervanLunteren/AddaxAI/blob/34b62da2ce000e81bc3fb51057c7fecb11a217e3/backend/app/db/base.py#L150) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 133 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/routers/deployment_queue.py#L85](https://github.com/PetervanLunteren/AddaxAI/blob/34b62da2ce000e81bc3fb51057c7fecb11a217e3/backend/app/api/routers/deployment_queue.py#L85)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 37 · corpus total: 56644 · executor: x86_64
> example: [backend/app/core/job_cancellation.py#L99](https://github.com/PetervanLunteren/AddaxAI/blob/34b62da2ce000e81bc3fb51057c7fecb11a217e3/backend/app/core/job_cancellation.py#L99)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/base.py#L150](https://github.com/PetervanLunteren/AddaxAI/blob/34b62da2ce000e81bc3fb51057c7fecb11a217e3/backend/app/db/base.py#L150)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

