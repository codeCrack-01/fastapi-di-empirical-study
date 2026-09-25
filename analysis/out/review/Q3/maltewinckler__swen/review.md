# maltewinckler/swen

- GitHub: https://github.com/maltewinckler/swen
- Stars: 11 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 78 · commit: `157bc9b3b943`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=1 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI function-based dependency injection` | services/backend/src/swen/presentation/api/dependencies.py#L164 | The get_identity_adapter_factory function uses Depends(get_settings) to inject the Settings dependency, demonstrating FastAPI's function-based DI pattern where dependencies are resolved through asy... |
| 2 | `Annotated dependency types` | services/backend/src/swen/presentation/api/dependencies.py#L307 | The code defines DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)] which creates reusable annotated dependency types with type hints and injection logic, a common pattern in FastAPI f... |
| 3 | `Chained dependency resolution` | services/backend/src/swen/presentation/api/dependencies.py#L188 | The get_current_user function depends on both get_identity_repository_factory and get_identity_adapter_factory, showing a chain of dependencies where each function is injected with other dependency... |
| 4 | `Async dependency providers` | services/backend/src/swen/presentation/api/dependencies.py#L149 | The get_db_session function is async and yields an AsyncSession, demonstrating FastAPI's support for async dependency providers that manage resources like database sessions. |

## Pass 2 — reconcile with inventory of maltewinckler/swen

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`, `C3|ELLIPSIS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly uses dependency injection via RepositoryFactory and CounterAccountProposalPort in reclassify_drafts_command.py, which aligns with the C4|DEF pattern. | services/backend/src/swen/application/accounting/commands/reclassify_drafts_command.py#L112 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses Depends(get_settings) in get_identity_adapter_factory, which matches the C1|BARE|SIG pattern. | services/backend/src/swen/presentation/api/dependencies.py#L164 |
| `C1|BARE|PARAM` | known | yes | The code uses Annotated[AsyncSession, Depends(get_db_session)] which matches the C1|BARE|PARAM pattern. | services/backend/src/swen/presentation/api/dependencies.py#L307 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code uses Annotated[RepositoryFactory, Depends(get_repository_factory)] which matches the C3|CLASS|BARE pattern. | services/backend/src/swen/presentation/api/dependencies.py#L307 |
| `C4|USED` | true_pos | **no (overturn)** | The code uses Depends(get_db_session) in get_db_session, which matches the C4|USED pattern. | services/backend/src/swen/presentation/api/dependencies.py#L149 |
| `C3|ELLIPSIS|BARE` | variant | yes | The code uses an ellipsis in the dependency definition, which matches the C3|ELLIPSIS|BARE variant pattern. | services/backend/src/swen/presentation/api/dependencies.py#L327 |

### Missed by inventory (2)
- `Annotated dependency types with custom factory methods` @ services/backend/src/swen/presentation/api/dependencies.py#L307 — The inventory missed the pattern of using Annotated with custom factory methods (e.g., RepoFactoryDep) which is a common FastAPI pattern.
- `Async dependency providers with yield` @ services/backend/src/swen/presentation/api/dependencies.py#L149 — The inventory missed the pattern of async dependency providers that yield resources (e.g., get_db_session).

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 44 | **false_pos** | [services/backend/src/swen/application/accounting/commands/reclassify_drafts_command.py#L112](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/application/accounting/commands/reclassify_drafts_command.py#L112) |
| `C1|BARE|SIG` | C1 | 14 | **false_pos** | [services/backend/src/swen/presentation/api/dependencies.py#L164](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L164) |
| `C1|BARE|PARAM` | C1 | 9 | **known** | [services/backend/src/swen/presentation/api/dependencies.py#L307](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L307) |
| `C3|CLASS|BARE` | C3 | 8 | **false_pos** | [services/backend/src/swen/presentation/api/dependencies.py#L307](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L307) |
| `C4|USED` | C4 | 2 | **false_pos** | [services/backend/src/swen/presentation/api/dependencies.py#L149](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L149) |
| `C3|ELLIPSIS|BARE` | C3 | 1 | **variant** | [services/backend/src/swen/presentation/api/dependencies.py#L327](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L327) |

## `C4|DEF` — **false_pos**
> occurrences here: 44 · corpus total: 56644 · executor: x86_64
> example: [services/backend/src/swen/application/accounting/commands/reclassify_drafts_command.py#L112](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/application/accounting/commands/reclassify_drafts_command.py#L112)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 14 · corpus total: 83548 · executor: x86_64
> example: [services/backend/src/swen/presentation/api/dependencies.py#L164](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L164)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 9 · corpus total: 18195 · executor: x86_64
> example: [services/backend/src/swen/presentation/api/dependencies.py#L307](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L307)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 8 · corpus total: 20139 · executor: x86_64
> example: [services/backend/src/swen/presentation/api/dependencies.py#L307](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L307)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [services/backend/src/swen/presentation/api/dependencies.py#L149](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L149)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 1 · corpus total: 1113 · executor: x86_64
> example: [services/backend/src/swen/presentation/api/dependencies.py#L327](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L327)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

