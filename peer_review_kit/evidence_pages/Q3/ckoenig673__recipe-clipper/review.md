# ckoenig673/recipe-clipper

- GitHub: https://github.com/ckoenig673/recipe-clipper
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 58 · commit: `96d5f515b64d`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends Injection` | backend/app/main.py#L8 | The require_admin function uses Depends(require_user) to inject user authentication dependency. This creates a dependency chain where admin endpoints depend on user authentication first. |
| 2 | `Endpoint Dependency Injection` | backend/app/main.py#L10398 | The import_text_recipe endpoint uses Depends(require_user) to inject authenticated user context, demonstrating how FastAPI routes leverage dependency injection for authorization. |
| 3 | `Nested Dependency Chain` | backend/app/main.py#L8 | require_admin depends on require_user, creating a nested dependency chain that ensures admin endpoints first verify user authentication before checking administrative privileges. |

## Pass 2 — reconcile with inventory of ckoenig673/recipe-clipper

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_depends_injection_8` | FastAPI Depends Injection @ backend/app/main.py:8 | yes | require_admin correctly uses Depends(require_user) for nested authentication chain | backend/app/main.py#L8 |
| `endpoint_dependency_injection_10398` | Endpoint Dependency Injection @ backend/app/main.py:10398 | yes | import_text_recipe properly injects require_user dependency | backend/app/main.py#L10398 |
| `nested_dependency_chain_8` | Nested Dependency Chain @ backend/app/main.py:8 | yes | require_admin's dependency on require_user creates valid authentication hierarchy | backend/app/main.py#L8 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 52 | **false_pos** | [backend/app/main.py#L8197](https://github.com/ckoenig673/recipe-clipper/blob/96d5f515b64df89ad73deb4fcd259ba377ed035e/backend/app/main.py#L8197) |
| `C4|DEF` | C4 | 6 | **false_pos** | [backend/app/main.py#L3187](https://github.com/ckoenig673/recipe-clipper/blob/96d5f515b64df89ad73deb4fcd259ba377ed035e/backend/app/main.py#L3187) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 52 · corpus total: 83548 · executor: x86_64
> example: [backend/app/main.py#L8197](https://github.com/ckoenig673/recipe-clipper/blob/96d5f515b64df89ad73deb4fcd259ba377ed035e/backend/app/main.py#L8197)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L3187](https://github.com/ckoenig673/recipe-clipper/blob/96d5f515b64df89ad73deb4fcd259ba377ed035e/backend/app/main.py#L3187)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

