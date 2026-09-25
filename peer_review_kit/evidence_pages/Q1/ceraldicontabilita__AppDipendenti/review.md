# ceraldicontabilita/AppDipendenti

- GitHub: https://github.com/ceraldicontabilita/AppDipendenti
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 76 · commit: `be7a3063e0cc`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=2 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection via FastAPI's Depends()` | backend/app/routers/portale_buste.py#L321 | The 'identity' parameter uses Depends(get_identity), which is FastAPI's DI mechanism to inject authentication context into route handlers. |
| 2 | `Dependency Injection via FastAPI's Depends()` | backend/app/routers/portale_documenti.py#L104 | The 'identity' parameter uses Depends(get_identity) to inject authentication context for document upload operations. |
| 3 | `Role-based DI with Depends()` | backend/app/routers/richieste.py#L228 | The 'identity' parameter uses Depends(require_roles(...)) to inject role-validated authentication context for request resolution. |

## Pass 2 — reconcile with inventory of ceraldicontabilita/AppDipendenti

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C1|CLASS|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `Dependency Injection via FastAPI's Depends() @ backend/app/routers/portale_buste.py:321` | Dependency Injection via FastAPI's Depends() | yes | The code explicitly uses Depends(get_identity) to inject authentication context into the route handler for accetta_busta. | backend/app/routers/portale_buste.py#L321 |
| `Dependency Injection via FastAPI's Depends() @ backend/app/routers/portale_documenti.py:104` | Dependency Injection via FastAPI's Depends() | yes | The code confirms the use of Depends(get_identity) in the upload_documento route handler for document upload operations. | backend/app/routers/portale_documenti.py#L104 |
| `Role-based DI with Depends() @ backend/app/routers/richieste.py:228` | Role-based DI with Depends() | yes | The code uses Depends(require_roles(...)) to inject role-validated authentication context for the risolvi_richiesta endpoint. | backend/app/routers/richieste.py#L228 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 71 | **false_pos** | [backend/app/routers/employees/accessi.py#L17](https://github.com/ceraldicontabilita/AppDipendenti/blob/be7a3063e0ccb23ca045bdb13ab75f4698c3094a/backend/app/routers/employees/accessi.py#L17) |
| `C1|BARE|PARAM` | C1 | 3 | **known** | [backend/app/main.py#L74](https://github.com/ceraldicontabilita/AppDipendenti/blob/be7a3063e0ccb23ca045bdb13ab75f4698c3094a/backend/app/main.py#L74) |
| `C1|CLASS|SIG` | C1 | 1 | **known** | [backend/app/utils/dependencies.py#L108](https://github.com/ceraldicontabilita/AppDipendenti/blob/be7a3063e0ccb23ca045bdb13ab75f4698c3094a/backend/app/utils/dependencies.py#L108) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/main.py#L18](https://github.com/ceraldicontabilita/AppDipendenti/blob/be7a3063e0ccb23ca045bdb13ab75f4698c3094a/backend/app/main.py#L18) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 71 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routers/employees/accessi.py#L17](https://github.com/ceraldicontabilita/AppDipendenti/blob/be7a3063e0ccb23ca045bdb13ab75f4698c3094a/backend/app/routers/employees/accessi.py#L17)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 3 · corpus total: 18195 · executor: x86_64
> example: [backend/app/main.py#L74](https://github.com/ceraldicontabilita/AppDipendenti/blob/be7a3063e0ccb23ca045bdb13ab75f4698c3094a/backend/app/main.py#L74)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|CLASS|SIG` — **known**
> occurrences here: 1 · corpus total: 149 · executor: x86_64
> example: [backend/app/utils/dependencies.py#L108](https://github.com/ceraldicontabilita/AppDipendenti/blob/be7a3063e0ccb23ca045bdb13ab75f4698c3094a/backend/app/utils/dependencies.py#L108)
> **rule:** C1

> **evidence (model):** Examples show classes (HTTPBearer, CRSParams, RoleChecker) passed to Depends, which fits C1 (function/object passed to Depends) since classes are objects in Python.

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L18](https://github.com/ceraldicontabilita/AppDipendenti/blob/be7a3063e0ccb23ca045bdb13ab75f4698c3094a/backend/app/main.py#L18)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

