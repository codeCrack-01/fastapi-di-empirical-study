# ifelsedotonestd/lens

- GitHub: https://github.com/ifelsedotonestd/lens
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 125 · commit: `4b01d2e290d2`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Custom Scopes` | apps/api/src/lens_api/routers.py#L500 | The code uses Depends(require_scope(Scope.WRITE)) to inject scope-based authentication dependencies into endpoints. This pattern creates reusable authorization checks that validate API keys against... |
| 2 | `Service Layer Injection via Composition` | apps/api/src/lens_api/routers.py#L523 | The Composition object is injected through Depends(_composition) to decouple business logic from routes. This is evident in list_urls (line 523) where the service layer handles URL filtering and pa... |
| 3 | `Nested Dependency Factories` | apps/api/src/lens_api/auth.py#L15 | The require_scope function creates a dependency factory that returns a scoped dependency checker. This is used in routers.py to generate access control dependencies for different endpoints. |

## Pass 2 — reconcile with inventory of ifelsedotonestd/lens

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection` | FastAPI Dependency Injection with Custom Scopes | yes | Code explicitly uses Depends(require_scope(...)) in endpoints like create_url (line 500) and delete_category (line 491) for scope-based authentication. | apps/api/src/lens_api/routers.py#L500 |
| `service_layer_injection` | Service Layer Injection via Composition | yes | Composition is injected via Depends(_composition) in endpoints like list_urls (line 523) and used to execute business logic. | apps/api/src/lens_api/routers.py#L523 |
| `nested_dependency_factories` | Nested Dependency Factories | yes | require_scope(...) is used as a dependency factory in routers.py, consistent with auth.py's implementation (line 15). | apps/api/src/lens_api/routers.py#L500 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 118 | **false_pos** | [apps/api/src/lens_api/auth.py#L83](https://github.com/ifelsedotonestd/lens/blob/4b01d2e290d21bec584812a2fc93980aa4116b10/apps/api/src/lens_api/auth.py#L83) |
| `C4|DEF` | C4 | 7 | **false_pos** | [apps/api/tests/test_api.py#L248](https://github.com/ifelsedotonestd/lens/blob/4b01d2e290d21bec584812a2fc93980aa4116b10/apps/api/tests/test_api.py#L248) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 118 · corpus total: 83548 · executor: x86_64
> example: [apps/api/src/lens_api/auth.py#L83](https://github.com/ifelsedotonestd/lens/blob/4b01d2e290d21bec584812a2fc93980aa4116b10/apps/api/src/lens_api/auth.py#L83)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [apps/api/tests/test_api.py#L248](https://github.com/ifelsedotonestd/lens/blob/4b01d2e290d21bec584812a2fc93980aa4116b10/apps/api/tests/test_api.py#L248)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

