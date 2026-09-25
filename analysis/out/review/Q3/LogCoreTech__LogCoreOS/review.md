# LogCoreTech/LogCoreOS

- GitHub: https://github.com/LogCoreTech/LogCoreOS
- Stars: 4 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 810 · commit: `9d8b29375511`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection via FastAPI Depends()` | app/backend/module_packages/automations/backend/router.py#L333 | The code uses FastAPI's Depends() to inject dependencies like _require_automations, get_workspace, and _write_limit into route handlers. This follows the Dependency Injection pattern by decoupling ... |
| 2 | `Dependency Injection via FastAPI Depends()` | app/backend/module_packages/calendar/backend/router.py#L33 | The code uses Depends(_require_calendar) and Depends(get_workspace) to inject authentication and workspace dependencies into route handlers, adhering to DI principles by separating concerns between... |

## Pass 2 — reconcile with inventory of LogCoreTech/LogCoreOS

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_depends_injection` | Dependency Injection via FastAPI Depends() | yes | The code explicitly uses FastAPI's Depends() to inject dependencies like authentication, workspace resolution, and rate-limiting into route handlers, decoupling route logic from dependency implemen... | app/backend/module_packages/automations/backend/router.py#L333 |
| `fastapi_depends_injection` | Dependency Injection via FastAPI Depends() | yes | The code uses Depends() for authentication and workspace dependencies in calendar routes, adhering to DI principles by separating concerns between route logic and dependency resolution. | app/backend/module_packages/calendar/backend/router.py#L33 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 776 | **false_pos** | [app/backend/module_packages/automations/backend/router.py#L87](https://github.com/LogCoreTech/LogCoreOS/blob/9d8b2937551115c4099a378669d43310a8219c92/app/backend/module_packages/automations/backend/router.py#L87) |
| `C4|DEF` | C4 | 34 | **false_pos** | [app/backend/conftest.py#L56](https://github.com/LogCoreTech/LogCoreOS/blob/9d8b2937551115c4099a378669d43310a8219c92/app/backend/conftest.py#L56) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 776 · corpus total: 83548 · executor: x86_64
> example: [app/backend/module_packages/automations/backend/router.py#L87](https://github.com/LogCoreTech/LogCoreOS/blob/9d8b2937551115c4099a378669d43310a8219c92/app/backend/module_packages/automations/backend/router.py#L87)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 34 · corpus total: 56644 · executor: x86_64
> example: [app/backend/conftest.py#L56](https://github.com/LogCoreTech/LogCoreOS/blob/9d8b2937551115c4099a378669d43310a8219c92/app/backend/conftest.py#L56)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

