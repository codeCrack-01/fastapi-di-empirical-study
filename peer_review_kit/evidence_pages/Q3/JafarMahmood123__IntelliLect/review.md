# JafarMahmood123/IntelliLect

- GitHub: https://github.com/JafarMahmood123/IntelliLect
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 124 · commit: `a7e19a4fd26b`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection` | backend/RagService/app/api/dependencies.py#L286 | The code uses FastAPI's `Depends` and `Annotated` to define dependencies, which is a core part of FastAPI's DI system. For example, `DocumentRepositoryDep = Annotated[DocumentRepository, Depends(ge... |

## Pass 2 — reconcile with inventory of JafarMahmood123/IntelliLect

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection_pattern` | fastapi_dependency_injection_pattern | yes | The code correctly uses FastAPI's `Depends` and `Annotated` for dependency injection, with resolvers like `get_document_repository` and `get_embedding_provider`. | backend/RagService/app/api/dependencies.py#L286 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 57 | **false_pos** | [backend/LiveAssistantService/app/api/main.py#L30](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/LiveAssistantService/app/api/main.py#L30) |
| `C1|BARE|PARAM` | C1 | 38 | **known** | [backend/LiveAssistantService/app/api/dependencies.py#L74](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/LiveAssistantService/app/api/dependencies.py#L74) |
| `C3|CLASS|BARE` | C3 | 28 | **false_pos** | [backend/LiveAssistantService/app/api/dependencies.py#L74](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/LiveAssistantService/app/api/dependencies.py#L74) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/RagService/app/infrastructure/persistence/database.py#L42](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/RagService/app/infrastructure/persistence/database.py#L42) |

## `C4|DEF` — **false_pos**
> occurrences here: 57 · corpus total: 56644 · executor: x86_64
> example: [backend/LiveAssistantService/app/api/main.py#L30](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/LiveAssistantService/app/api/main.py#L30)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 38 · corpus total: 18195 · executor: x86_64
> example: [backend/LiveAssistantService/app/api/dependencies.py#L74](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/LiveAssistantService/app/api/dependencies.py#L74)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 28 · corpus total: 20139 · executor: x86_64
> example: [backend/LiveAssistantService/app/api/dependencies.py#L74](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/LiveAssistantService/app/api/dependencies.py#L74)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/RagService/app/infrastructure/persistence/database.py#L42](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/RagService/app/infrastructure/persistence/database.py#L42)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

