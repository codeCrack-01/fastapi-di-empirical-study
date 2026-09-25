# Adejare-ml/News-Intelligence-System

- GitHub: https://github.com/Adejare-ml/News-Intelligence-System
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 13 · commit: `d1215b5c56d8`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=1 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI router-level dependency injection` | backend/app/api/routes.py#L31 | APIRouter is initialized with dependencies=[Depends(get_current_user)], demonstrating router-level DI where all routes under this router automatically inherit the get_current_user dependency for au... |
| 2 | `Nested dependency injection` | backend/app/core/security.py#L41 | The get_current_user function itself uses Depends(get_db) and Depends(oauth2_scheme), showing a nested DI pattern where a dependency (user authentication) relies on other injected services (databas... |
| 3 | `Database session generator dependency` | backend/app/db/session.py#L16 | The get_db() function is defined as a generator that yields a database session, which is used as a dependency via Depends(get_db) elsewhere. This is a standard FastAPI pattern for managing database... |
| 4 | `Route-specific dependency injection` | backend/app/api/routes.py#L60 | The login route explicitly injects dependencies via form_data: OAuth2PasswordRequestForm = Depends() and session: Session = Depends(get_db), showing route-level DI for authentication and database a... |

## Pass 2 — reconcile with inventory of Adejare-ml/News-Intelligence-System

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`, `C1|EMPTY|SIG`, `C4|USED`

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 7 | **false_pos** | [tests/test_bugfix_pack.py#L30](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/tests/test_bugfix_pack.py#L30) |
| `C1|BARE|SIG` | C1 | 3 | **false_pos** | [backend/app/api/routes.py#L60](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/backend/app/api/routes.py#L60) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [backend/app/api/routes.py#L31](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/backend/app/api/routes.py#L31) |
| `C1|EMPTY|SIG` | C1 | 1 | **variant** | [backend/app/api/routes.py#L59](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/backend/app/api/routes.py#L59) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/session.py#L16](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/backend/app/db/session.py#L16) |

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [tests/test_bugfix_pack.py#L30](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/tests/test_bugfix_pack.py#L30)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/routes.py#L60](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/backend/app/api/routes.py#L60)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/routes.py#L31](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/backend/app/api/routes.py#L31)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 1 · corpus total: 254 · executor: x86_64
> example: [backend/app/api/routes.py#L59](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/backend/app/api/routes.py#L59)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/session.py#L16](https://github.com/Adejare-ml/News-Intelligence-System/blob/d1215b5c56d8f8525b0e343763b0749557b51f68/backend/app/db/session.py#L16)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

