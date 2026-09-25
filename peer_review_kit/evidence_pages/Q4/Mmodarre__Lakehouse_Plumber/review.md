# Mmodarre/Lakehouse_Plumber

- GitHub: https://github.com/Mmodarre/Lakehouse_Plumber
- Stars: 65 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 257 · commit: `a0d784cbf758`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection` | src/lhp/webapp/routers/dependencies.py#L167 | The `Depends(get_dependency)` pattern is used to inject a `DependencyFacade` instance into route handlers. This is FastAPI's DI pattern where dependencies are resolved via `get_dependency` and inje... |
| 2 | `FastAPI Dependency Injection` | src/lhp/webapp/routers/environments.py#L67 | The `Depends(get_inspection)` pattern injects an `InspectionFacade` into route handlers. This follows FastAPI's DI model where dependencies are resolved by provider functions and injected into endp... |
| 3 | `FastAPI Dependency Injection` | src/lhp/webapp/routers/files.py#L179 | The `Depends(get_file_io_service)` pattern injects a `FileIOService` into route handlers. This is another example of FastAPI's DI system resolving services via provider functions. |

## Pass 2 — reconcile with inventory of Mmodarre/Lakehouse_Plumber

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection_1` | FastAPI Dependency Injection | yes | The code correctly uses `Depends(get_dependency)` to inject `DependencyFacade` into route handlers, aligning with FastAPI's DI pattern. | src/lhp/webapp/routers/dependencies.py#L167 |
| `fastapi_dependency_injection_2` | FastAPI Dependency Injection | yes | The code correctly uses `Depends(get_inspection)` to inject `InspectionFacade` into route handlers, following FastAPI's DI model. | src/lhp/webapp/routers/environments.py#L67 |
| `fastapi_dependency_injection_3` | FastAPI Dependency Injection | yes | The code correctly uses `Depends(get_file_io_service)` to inject `FileIOService` into route handlers, adhering to FastAPI's DI system. | src/lhp/webapp/routers/files.py#L179 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 191 | **false_pos** | [Example_Projects/acmi/data_sources/currency_api_source.py#L141](https://github.com/Mmodarre/Lakehouse_Plumber/blob/a0d784cbf758b5b98f2f03b72591f0b70b5e7fb5/Example_Projects/acmi/data_sources/currency_api_source.py#L141) |
| `C1|BARE|SIG` | C1 | 66 | **false_pos** | [src/lhp/webapp/routers/assistant.py#L162](https://github.com/Mmodarre/Lakehouse_Plumber/blob/a0d784cbf758b5b98f2f03b72591f0b70b5e7fb5/src/lhp/webapp/routers/assistant.py#L162) |

## `C4|DEF` — **false_pos**
> occurrences here: 191 · corpus total: 56644 · executor: x86_64
> example: [Example_Projects/acmi/data_sources/currency_api_source.py#L141](https://github.com/Mmodarre/Lakehouse_Plumber/blob/a0d784cbf758b5b98f2f03b72591f0b70b5e7fb5/Example_Projects/acmi/data_sources/currency_api_source.py#L141)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 66 · corpus total: 83548 · executor: x86_64
> example: [src/lhp/webapp/routers/assistant.py#L162](https://github.com/Mmodarre/Lakehouse_Plumber/blob/a0d784cbf758b5b98f2f03b72591f0b70b5e7fb5/src/lhp/webapp/routers/assistant.py#L162)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

