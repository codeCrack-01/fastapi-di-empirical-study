# vstorm-co/agenticos

- GitHub: https://github.com/vstorm-co/agenticos
- Stars: 4 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 532 · commit: `7cff550b2fa5`
- Fingerprints touching this repo: 10
- Label mix: novel=0 variant=3 known=2 false_pos=5 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Annotated Types` | backend/app/api/deps.py#L30 | The code defines DBSession using Annotated[AsyncSession, Depends(get_db_session, scope="function")], showing FastAPI dependency injection with explicit scope control. The comment explains that scop... |
| 2 | `Service Dependency Factories` | backend/app/api/deps.py#L81 | The code defines factory functions like get_user_service(db: DBSession) -> UserService and annotates them as dependencies (UserSvc = Annotated[UserService, Depends(get_user_service)]). This pattern... |
| 3 | `Scoped Dependency Variants` | backend/app/api/deps.py#L45 | StreamingDBSession = Annotated[AsyncSession, Depends(get_db_session, scope="request")] creates a variant of the database session dependency with a different lifecycle scope, explicitly tailored for... |
| 4 | `Composed Dependency Chains` | backend/app/api/deps.py#L115 | Dependencies like OAuthExchangeSvc = Annotated[OAuthExchangeService, Depends(get_oauth_exchange_service)] show a chain where dependencies can themselves depend on other annotated dependencies (e.g.... |
| 5 | `Authentication Dependency` | backend/app/api/deps.py#L301 | The get_current_user function is defined as a dependency that uses Depends(oauth2_scheme) and other service dependencies, demonstrating a full authentication flow integrated into the dependency sys... |

## Pass 2 — reconcile with inventory of vstorm-co/agenticos

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`, `C1|CLASS|PARAM`, `C3|BARE|BARE`, `C3|CLASS|CLASS`, `C3|CLASS|EMPTY`, `C1|EMPTY|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `FastAPI Dependency Injection with Annotated Types` | FastAPI Dependency Injection with Annotated Types | yes | The code explicitly uses Annotated[AsyncSession, Depends(...)] with scope parameters, matching the observation. | backend/app/api/deps.py#L30 |
| `Service Dependency Factories` | Service Dependency Factories | yes | Factory functions like get_user_service() and their annotated dependencies (UserSvc) are present as described. | backend/app/api/deps.py#L81 |
| `Scoped Dependency Variants` | Scoped Dependency Variants | yes | StreamingDBSession with scope='request' and DBSession with scope='function' are explicitly defined. | backend/app/api/deps.py#L45 |
| `Composed Dependency Chains` | Composed Dependency Chains | yes | Dependencies like OAuthExchangeSvc depend on Redis via get_oauth_exchange_service(), matching the pattern. | backend/app/api/deps.py#L115 |
| `Authentication Dependency` | Authentication Dependency | yes | get_current_user() uses Depends(oauth2_scheme) and service dependencies as described. | backend/app/api/deps.py#L301 |

### Missed by inventory (1)
- `Permission-based dependency resolution via AuthContext` @ backend/app/api/deps.py#L579 — The get_auth_context() function builds an AuthContext object that downstream dependencies use for permission checks, but this pattern wasn't explicitly mentioned in the initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 279 | **false_pos** | [backend/app/agents/capabilities/budget/_capability.py#L366](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/agents/capabilities/budget/_capability.py#L366) |
| `C1|BARE|PARAM` | C1 | 174 | **known** | [backend/app/api/deps.py#L30](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L30) |
| `C3|CLASS|BARE` | C3 | 61 | **false_pos** | [backend/app/api/deps.py#L30](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L30) |
| `C3|ELLIPSIS|BARE` | C3 | 5 | **variant** | [backend/app/api/deps.py#L353](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L353) |
| `C1|CLASS|PARAM` | C1 | 3 | **known** | [backend/app/api/deps.py#L786](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L786) |
| `C3|BARE|BARE` | C3 | 3 | **variant** | [backend/app/api/deps.py#L301](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L301) |
| `C3|CLASS|CLASS` | C3 | 3 | **false_pos** | [backend/app/api/deps.py#L786](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L786) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [backend/app/api/routes/v1/auth.py#L46](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/routes/v1/auth.py#L46) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [backend/app/api/routes/v1/auth.py#L46](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/routes/v1/auth.py#L46) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/session.py#L105](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/db/session.py#L105) |

## `C4|DEF` — **false_pos**
> occurrences here: 279 · corpus total: 56644 · executor: x86_64
> example: [backend/app/agents/capabilities/budget/_capability.py#L366](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/agents/capabilities/budget/_capability.py#L366)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 174 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/deps.py#L30](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L30)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 61 · corpus total: 20139 · executor: x86_64
> example: [backend/app/api/deps.py#L30](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L30)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 5 · corpus total: 1113 · executor: x86_64
> example: [backend/app/api/deps.py#L353](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L353)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C1|CLASS|PARAM` — **known**
> occurrences here: 3 · corpus total: 72 · executor: x86_64
> example: [backend/app/api/deps.py#L786](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L786)
> **rule:** C1

> **evidence (model):** The examples show a class (COOKIE_SCHEME) being used as a dependency parameter in function signatures, consistent with C1 (Depends): function/object passed to Depends(...)

## `C3|BARE|BARE` — **variant**
> occurrences here: 3 · corpus total: 1316 · executor: x86_64
> example: [backend/app/api/deps.py#L301](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L301)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C3|CLASS|CLASS` — **false_pos**
> occurrences here: 3 · corpus total: 42 · executor: x86_64
> example: [backend/app/api/deps.py#L786](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L786)

> **evidence (model):** Annotated types are classes but no Depends/Security in metadata; extractor misclassified non-DI Annotated usage as C3

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [backend/app/api/routes/v1/auth.py#L46](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/routes/v1/auth.py#L46)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [backend/app/api/routes/v1/auth.py#L46](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/routes/v1/auth.py#L46)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/session.py#L105](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/db/session.py#L105)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

