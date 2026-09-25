# teaching-practice-lab-oral/oral

- GitHub: https://github.com/teaching-practice-lab-oral/oral
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 204 · commit: `5f3ce05697ce`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Standard FastAPI Dependency Injection` | app/routers/admin/assignments.py#L15 | The code uses `Depends(get_current_admin)` and `Depends(get_db)` to inject dependencies, which is the standard FastAPI pattern. For example, in `send_reminder`, `admin: User = Depends(get_current_a... |
| 2 | `Reused Dependency Providers` | app/auth.py#L15 | The `get_current_admin` function is defined once but used across multiple routes (e.g., in `assignments.py` and `audit.py`). This shows a pattern of centralizing dependency providers (like authenti... |

## Pass 2 — reconcile with inventory of teaching-practice-lab-oral/oral

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `standard_fastapi_dependency_injection` | standard_fastapi_dependency_injection | yes | Code explicitly uses Depends(get_current_admin) and Depends(get_db) in multiple routes (e.g., reset_assignment_submissions, allow_retake), aligning with FastAPI's standard pattern. | app/routers/admin/assignments.py#L549 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 194 | **false_pos** | [app/auth.py#L99](https://github.com/teaching-practice-lab-oral/oral/blob/5f3ce05697cecd393e77a97fb25624086027d21d/app/auth.py#L99) |
| `C4|DEF` | C4 | 6 | **false_pos** | [app/main.py#L29](https://github.com/teaching-practice-lab-oral/oral/blob/5f3ce05697cecd393e77a97fb25624086027d21d/app/main.py#L29) |
| `C1|BARE|PARAM` | C1 | 3 | **known** | [app/worker_main.py#L73](https://github.com/teaching-practice-lab-oral/oral/blob/5f3ce05697cecd393e77a97fb25624086027d21d/app/worker_main.py#L73) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/database.py#L26](https://github.com/teaching-practice-lab-oral/oral/blob/5f3ce05697cecd393e77a97fb25624086027d21d/app/database.py#L26) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 194 · corpus total: 83548 · executor: x86_64
> example: [app/auth.py#L99](https://github.com/teaching-practice-lab-oral/oral/blob/5f3ce05697cecd393e77a97fb25624086027d21d/app/auth.py#L99)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [app/main.py#L29](https://github.com/teaching-practice-lab-oral/oral/blob/5f3ce05697cecd393e77a97fb25624086027d21d/app/main.py#L29)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 3 · corpus total: 18195 · executor: x86_64
> example: [app/worker_main.py#L73](https://github.com/teaching-practice-lab-oral/oral/blob/5f3ce05697cecd393e77a97fb25624086027d21d/app/worker_main.py#L73)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/database.py#L26](https://github.com/teaching-practice-lab-oral/oral/blob/5f3ce05697cecd393e77a97fb25624086027d21d/app/database.py#L26)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

