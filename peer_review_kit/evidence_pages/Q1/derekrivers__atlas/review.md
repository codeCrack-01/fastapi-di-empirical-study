# derekrivers/atlas

- GitHub: https://github.com/derekrivers/atlas
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 90 · commit: `c80d8ce4f698`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=1 known=2 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Annotated Dependencies with Custom Resolvers` | atlas/api/dependencies.py#L110 | The code defines multiple annotated dependencies using Annotated[type, Depends(resolver)], where resolver functions like get_database() and get_operator_session_service() retrieve objects from requ... |
| 2 | `Chained Dependency Injection` | atlas/api/dependencies.py#L265 | Dependencies like AcceptanceWorkflowServicesDependency are built by combining multiple lower-level dependencies (DatabaseDependency, AcceptanceGitHubClientDependency, etc.) through a resolver funct... |
| 3 | `Security-Enhanced Dependencies` | atlas/api/dependencies.py#L121 | Security checks are integrated via Security() within Annotated dependencies (e.g., SessionCookieSecurity and CSRFHeaderSecurity), showing how authentication/authorization is woven into the dependen... |

## Pass 2 — reconcile with inventory of derekrivers/atlas

_Presented fingerprints:_ `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`, `C4|DEF`, `C2|CLASS|ascopes`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | Annotated dependencies with bare parameters (e.g., DatabaseDependency = Annotated[Database, Depends(...)]) are explicitly defined and used throughout the code. | atlas/api/dependencies.py#L110 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | Classes like OperatorSessionServiceDependency are valid annotated dependencies used as parameters in functions (e.g., create_operator_session_response(..., sessions: OperatorSessionServiceDependenc... | atlas/api/dependencies.py#L148 |
| `C3|ELLIPSIS|BARE` | variant | yes | No ellipsis (...) found in the provided code excerpts; the label may refer to a different pattern not visible in the given lines. | atlas/api/dependencies.py#L263 |
| `C4|DEF` | false_pos | **no (overturn)** | Function definitions (e.g., get_database, get_operator_session_service) are correctly used as dependency resolvers in Annotated[...], contradicting the false_pos label. | atlas/api/dependencies.py#L110 |
| `C2|CLASS|ascopes` | known | yes | Classes like AuthenticatedSessionDependency are explicitly defined with ascopes (e.g., Depends(resolve_authenticated_session)) and used as dependencies. | atlas/api/dependencies.py#L168 |

### Missed by inventory (1)
- `Security-Enhanced Dependencies (Security(...) within Annotated)` @ atlas/api/dependencies.py#L121 — The inventory did not account for Security(...) constructs integrated into Annotated dependencies (e.g., SessionCookieSecurity, CSRFHeaderSecurity).

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 41 | **known** | [atlas/api/dependencies.py#L110](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L110) |
| `C3|CLASS|BARE` | C3 | 31 | **false_pos** | [atlas/api/dependencies.py#L110](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L110) |
| `C3|ELLIPSIS|BARE` | C3 | 10 | **variant** | [atlas/api/dependencies.py#L263](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L263) |
| `C4|DEF` | C4 | 5 | **false_pos** | [atlas/api/app.py#L121](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/app.py#L121) |
| `C2|CLASS|ascopes` | C2 | 3 | **known** | [atlas/api/dependencies.py#L168](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L168) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 41 · corpus total: 18195 · executor: x86_64
> example: [atlas/api/dependencies.py#L110](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L110)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 31 · corpus total: 20139 · executor: x86_64
> example: [atlas/api/dependencies.py#L110](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L110)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 10 · corpus total: 1113 · executor: x86_64
> example: [atlas/api/dependencies.py#L263](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L263)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [atlas/api/app.py#L121](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/app.py#L121)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C2|CLASS|ascopes` — **known**
> occurrences here: 3 · corpus total: 26 · executor: x86_64
> example: [atlas/api/dependencies.py#L168](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L168)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in authentication/authorization contexts (API keys, webhook signatures), matching catalog rule C2.

