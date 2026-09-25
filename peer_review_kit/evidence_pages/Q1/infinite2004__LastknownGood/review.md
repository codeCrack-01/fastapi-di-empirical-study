# infinite2004/LastknownGood

- GitHub: https://github.com/infinite2004/LastknownGood
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 65 · commit: `70cdef1f8014`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Repeated Error Handling` | apps/backend/app/api/routes/all_routes.py#L560 | Multiple endpoints (e.g., delete_evidence, get_job, get_diagnosis) use the same pattern of checking if a resource exists and raising HTTPException(404) if not. This violates DRY and could be abstra... |
| 2 | `Redundant File Existence Check` | apps/backend/app/api/routes/all_routes.py#L560 | The code checks if evidence.file_path exists before attempting to delete it, but Path(...).unlink(missing_ok=True) already handles missing files. The check may be redundant, though evidence.file_pa... |
| 3 | `Workflow State Guard Cloning` | apps/backend/app/api/routes/all_routes.py#L594 | The workflow state check (can(WorkflowState(...), WorkflowEvent.DIAGNOSIS_REQUESTED)) is duplicated in create_diagnosis and create_diagnosis_job. This logic could be centralized into a utility func... |

## Pass 2 — reconcile with inventory of infinite2004/LastknownGood

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `repeated_error_handling` | DRY Violation: Repeated 404 Handling | yes | Multiple endpoints (delete_evidence, get_job, get_diagnosis) duplicate null-check logic for resources. Centralizing this into a helper function would improve maintainability. | apps/backend/app/api/routes/all_routes.py#L560 |
| `redundant_file_check` | Redundant File Existence Check | yes | The explicit existence check for evidence.file_path is unnecessary since Path(...).unlink(missing_ok=True) already handles missing files safely. | apps/backend/app/api/routes/all_routes.py#L560 |
| `workflow_state_clone` | Duplicated Workflow State Guard | yes | The workflow state validation logic in create_diagnosis and create_diagnosis_job is identical and should be centralized into a shared utility function. | apps/backend/app/api/routes/all_routes.py#L594 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 57 | **false_pos** | [apps/backend/app/api/routes/all_routes.py#L118](https://github.com/infinite2004/LastknownGood/blob/70cdef1f80145ee8cfa973a9bfec30d8a660c802/apps/backend/app/api/routes/all_routes.py#L118) |
| `C4|DEF` | C4 | 7 | **false_pos** | [apps/backend/app/main.py#L78](https://github.com/infinite2004/LastknownGood/blob/70cdef1f80145ee8cfa973a9bfec30d8a660c802/apps/backend/app/main.py#L78) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/backend/app/db/session.py#L57](https://github.com/infinite2004/LastknownGood/blob/70cdef1f80145ee8cfa973a9bfec30d8a660c802/apps/backend/app/db/session.py#L57) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 57 · corpus total: 83548 · executor: x86_64
> example: [apps/backend/app/api/routes/all_routes.py#L118](https://github.com/infinite2004/LastknownGood/blob/70cdef1f80145ee8cfa973a9bfec30d8a660c802/apps/backend/app/api/routes/all_routes.py#L118)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [apps/backend/app/main.py#L78](https://github.com/infinite2004/LastknownGood/blob/70cdef1f80145ee8cfa973a9bfec30d8a660c802/apps/backend/app/main.py#L78)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/backend/app/db/session.py#L57](https://github.com/infinite2004/LastknownGood/blob/70cdef1f80145ee8cfa973a9bfec30d8a660c802/apps/backend/app/db/session.py#L57)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

