# runovelhq/wolt

- GitHub: https://github.com/runovelhq/wolt
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 44 · commit: `fb6aa1162821`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection for authentication` | app/web/auth_routes.py#L169 | The route handler uses Depends(require_user) to inject an authenticated user, demonstrating FastAPI's dependency injection for authentication checks. |
| 2 | `Nested dependency injection` | app/web/identity_routes.py#L97 | require_owner depends on require_user via Depends(require_user), showing nested DI where higher-level dependencies build on lower-level ones. |
| 3 | `Service injection in route handlers` | app/web/host_routes.py#L60 | The status route injects an authenticated user via Depends(require_owner) and uses a service (call function) to handle the request, indicating DI for both authentication and business logic services. |
| 4 | `Contextual dependency injection` | app/web/identity_routes.py#L103 | The invite route injects user via Depends(require_owner) and uses service.invite_user(), showing DI for both authentication and service layer dependencies. |
| 5 | `Constructor-based dependency injection` | app/web/application.py#L97 | The create_app function injects database and settings into services like IdentityService and ObservabilityService via their constructors, demonstrating DI at the service creation level. |

## Pass 2 — reconcile with inventory of runovelhq/wolt

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true | **no (overturn)** | The code correctly uses FastAPI Depends for authentication checks (e.g., Depends(require_user) in auth_routes.py:169 and host_routes.py:60-64). The panel incorrectly labeled these as false positives. | app/web/auth_routes.py#L169 |
| `C4|DEF` | true | **no (overturn)** | The code correctly implements DI patterns like session management (connection.py:56) and service injection (application.py:97-131). The panel's false_pos label misclassifies valid DI usages. | app/web/application.py#L97 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 41 | **false_pos** | [app/web/auth_routes.py#L169](https://github.com/runovelhq/wolt/blob/fb6aa1162821e2a00c7f512022bb7ef12dfa626c/app/web/auth_routes.py#L169) |
| `C4|DEF` | C4 | 3 | **false_pos** | [app/infrastructure/database/connection.py#L56](https://github.com/runovelhq/wolt/blob/fb6aa1162821e2a00c7f512022bb7ef12dfa626c/app/infrastructure/database/connection.py#L56) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 41 · corpus total: 83548 · executor: x86_64
> example: [app/web/auth_routes.py#L169](https://github.com/runovelhq/wolt/blob/fb6aa1162821e2a00c7f512022bb7ef12dfa626c/app/web/auth_routes.py#L169)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [app/infrastructure/database/connection.py#L56](https://github.com/runovelhq/wolt/blob/fb6aa1162821e2a00c7f512022bb7ef12dfa626c/app/infrastructure/database/connection.py#L56)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

