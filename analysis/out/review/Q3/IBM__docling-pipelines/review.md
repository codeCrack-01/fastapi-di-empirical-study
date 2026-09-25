# IBM/docling-pipelines

- GitHub: https://github.com/IBM/docling-pipelines
- Stars: 10 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 195 · commit: `1fa3dda3bcee`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=2 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Depends and Annotated` | src/docpipe/api/auth/dependencies.py#L33 | The code uses FastAPI's Depends() to inject dependencies into async functions like get_current_user, which requires credentials and jwt_config obtained via Depends(security) and Depends(get_jwt_con... |
| 2 | `Nested Dependency Resolution` | src/docpipe/api/auth/dependencies.py#L79 | get_current_user_oauth2 depends on both oauth2_scheme and get_jwt_config, showing a nested DI pattern where multiple dependencies are resolved and combined in a single endpoint. |
| 3 | `Service Composition via DI` | src/docpipe/api/routes/document_libraries.py#L260 | get_document_library_service composes DocumentLibraryService by injecting DocumentSetService and DocumentLibraryRepository via Depends(), demonstrating DI-driven service composition. |
| 4 | `Reused Dependency Aliases` | src/docpipe/api/routes/document_libraries.py#L278 | DocumentLibraryServiceDep and DocumentSetServiceDep are defined as Annotated types with Depends(), enabling consistent reuse of DI dependencies across route handlers. |
| 5 | `Authentication DI Chain` | src/docpipe/api/main.py#L378 | The /auth/me endpoint uses Depends(get_current_user) to inject an authenticated User object, showing a DI chain from authentication to business logic. |

## Pass 2 — reconcile with inventory of IBM/docling-pipelines

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|BARE|BARE`, `C3|ELLIPSIS|BARE`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code correctly uses Depends() in the /auth/me endpoint for DI, contradicting the false_pos label. | src/docpipe/api/main.py#L378 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | The code at src/docpipe/api/auth/dependencies.py:L33 correctly uses Annotated with Depends(), contradicting the false_pos label. | src/docpipe/api/auth/dependencies.py#L33 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code at src/docpipe/api/routes/document_libraries.py:L260 correctly uses Annotated with Depends(), contradicting the false_pos label. | src/docpipe/api/routes/document_libraries.py#L260 |

### Missed by inventory (2)
- `Annotated with Depends() in service composition` @ src/docpipe/api/routes/document_libraries.py#L260 — The inventory missed DI patterns in service composition via Annotated[DocumentLibraryService, Depends(...)]
- `Nested DI in OAuth2 flows` @ src/docpipe/api/auth/dependencies.py#L79 — The inventory missed nested DI patterns in get_current_user_oauth2, which combines oauth2_scheme and get_jwt_config

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 95 | **false_pos** | [src/docpipe/api/main.py#L103](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/main.py#L103) |
| `C1|BARE|PARAM` | C1 | 35 | **known** | [src/docpipe/api/auth/dependencies.py#L33](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/auth/dependencies.py#L33) |
| `C3|CLASS|BARE` | C3 | 35 | **false_pos** | [src/docpipe/api/auth/dependencies.py#L33](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/auth/dependencies.py#L33) |
| `C3|BARE|BARE` | C3 | 14 | **variant** | [src/docpipe/api/routes/document_libraries.py#L279](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/routes/document_libraries.py#L279) |
| `C3|ELLIPSIS|BARE` | C3 | 9 | **variant** | [src/docpipe/api/auth/dependencies.py#L79](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/auth/dependencies.py#L79) |
| `C1|BARE|SIG` | C1 | 7 | **false_pos** | [src/docpipe/api/routes/document_libraries.py#L260](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/routes/document_libraries.py#L260) |

## `C4|DEF` — **false_pos**
> occurrences here: 95 · corpus total: 56644 · executor: x86_64
> example: [src/docpipe/api/main.py#L103](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/main.py#L103)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 35 · corpus total: 18195 · executor: x86_64
> example: [src/docpipe/api/auth/dependencies.py#L33](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/auth/dependencies.py#L33)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 35 · corpus total: 20139 · executor: x86_64
> example: [src/docpipe/api/auth/dependencies.py#L33](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/auth/dependencies.py#L33)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|BARE|BARE` — **variant**
> occurrences here: 14 · corpus total: 1316 · executor: x86_64
> example: [src/docpipe/api/routes/document_libraries.py#L279](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/routes/document_libraries.py#L279)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 9 · corpus total: 1113 · executor: x86_64
> example: [src/docpipe/api/auth/dependencies.py#L79](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/auth/dependencies.py#L79)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 7 · corpus total: 83548 · executor: x86_64
> example: [src/docpipe/api/routes/document_libraries.py#L260](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/routes/document_libraries.py#L260)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

