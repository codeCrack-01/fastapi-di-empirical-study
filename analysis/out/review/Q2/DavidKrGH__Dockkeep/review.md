# DavidKrGH/Dockkeep

- GitHub: https://github.com/DavidKrGH/Dockkeep
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 20 · commit: `eca6cda651d1`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `context managers for resource lifecycle` | src/core/locking.py#L72 | The `acquire` method in `SchedulerLock` uses a context manager to handle lock acquisition and release, ensuring proper resource management. |
| 2 | `lifespan management in FastAPI` | src/gui/app.py#L94 | The `_lifespan` async context manager in `create_app` handles startup/shutdown logic for the SchedulerOwnerManager, aligning with FastAPI's lifespan management pattern. |
| 3 | `transaction context managers` | src/services/appdata_schema.py#L195 | The `immediate_tx` context manager manages SQLite transactions, encapsulating connection setup/teardown. |

## Pass 2 — reconcile with inventory of DavidKrGH/Dockkeep

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true | **no (overturn)** | The code explicitly uses context managers for lock acquisition (e.g., `@contextmanager def acquire(...)`) and proper resource lifecycle management, contradicting the 'false_pos' label. | src/core/locking.py#L72 |

### Missed by inventory (2)
- `Async context manager for log streaming` @ src/services/logs.py#L188 — The `stream` method uses `@asynccontextmanager` to manage log stream lifecycle, but was not detected in pass 1.
- `Thread-local logging context manager` @ src/utils/logging.py#L43 — The `log_task_context` manager tracks nested logging contexts, but was not detected in pass 1.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 20 | **false_pos** | [src/core/job_runner.py#L288](https://github.com/DavidKrGH/Dockkeep/blob/eca6cda651d10162026239eaf7e2143442aad51d/src/core/job_runner.py#L288) |

## `C4|DEF` — **false_pos**
> occurrences here: 20 · corpus total: 56644 · executor: x86_64
> example: [src/core/job_runner.py#L288](https://github.com/DavidKrGH/Dockkeep/blob/eca6cda651d10162026239eaf7e2143442aad51d/src/core/job_runner.py#L288)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

