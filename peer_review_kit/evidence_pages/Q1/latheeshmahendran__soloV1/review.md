# latheeshmahendran/soloV1

- GitHub: https://github.com/latheeshmahendran/soloV1
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 26 · commit: `c86c2c89fe3c`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection with custom factory functions` | backend/api/v1/endpoints/conversation.py#L40 | The _get_conversation_service function is a factory that returns a ConversationService instance with dependencies injected from app.state (settings, model_manager, etc.) and the database session. T... |
| 2 | `Database session injection via Depends()` | backend/api/v1/endpoints/conversation.py#L78 | The chat endpoint uses Depends(get_db_session) to inject an AsyncSession, demonstrating FastAPI's standard pattern for database connection management. |
| 3 | `App state-based dependency sharing` | backend/api/v1/endpoints/conversation.py#L96 | The _get_streaming_service factory accesses app.state to retrieve shared components like settings, model_manager, and task_router, showing how stateful dependencies are managed across the application. |
| 4 | `Test dependency overriding` | tests/conftest.py#L113 | The client fixture overrides get_db_session and get_settings using FastAPI's dependency_overrides, demonstrating how DI is used in testing with mock dependencies. |

## Pass 2 — reconcile with inventory of latheeshmahendran/soloV1

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's DI via Depends() and app.state for dependency injection, contradicting the false_pos label. | backend/api/v1/endpoints/conversation.py#L40 |
| `C4|DEF` | true_pos | **no (overturn)** | The code uses DI patterns (e.g., app.state.model_manager, Depends(get_db_session), and self._llm.generate) that contradict the false_pos label. | backend/main.py#L32 |
| `C4|USED` | true_pos | **no (overturn)** | The code defines get_db_session as a FastAPI dependency generator, which is a valid DI usage contradicting the false_pos label. | backend/database/connection.py#L92 |

### Missed by inventory (3)
- `Test dependency overriding with pytest_asyncio fixtures` @ tests/conftest.py#L113 — The inventory missed DI patterns in test fixtures using dependency_overrides and mock dependencies.
- `App.state-based dependency sharing across modules` @ backend/api/v1/endpoints/conversation.py#L96 — The inventory missed DI patterns where app.state is used to share model_manager, settings, and other services.
- `StreamingService DI with multiple injected components` @ backend/streaming/streaming_service.py#L62 — The inventory missed DI patterns where StreamingService is initialized with 8+ injected dependencies via the constructor.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 16 | **false_pos** | [backend/api/v1/endpoints/conversation.py#L40](https://github.com/latheeshmahendran/soloV1/blob/c86c2c89fe3ce18e39c078b8bffb63b3f4f3f3fb/backend/api/v1/endpoints/conversation.py#L40) |
| `C4|DEF` | C4 | 9 | **false_pos** | [backend/brain/model_manager.py#L321](https://github.com/latheeshmahendran/soloV1/blob/c86c2c89fe3ce18e39c078b8bffb63b3f4f3f3fb/backend/brain/model_manager.py#L321) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/database/connection.py#L92](https://github.com/latheeshmahendran/soloV1/blob/c86c2c89fe3ce18e39c078b8bffb63b3f4f3f3fb/backend/database/connection.py#L92) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 16 · corpus total: 83548 · executor: x86_64
> example: [backend/api/v1/endpoints/conversation.py#L40](https://github.com/latheeshmahendran/soloV1/blob/c86c2c89fe3ce18e39c078b8bffb63b3f4f3f3fb/backend/api/v1/endpoints/conversation.py#L40)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 9 · corpus total: 56644 · executor: x86_64
> example: [backend/brain/model_manager.py#L321](https://github.com/latheeshmahendran/soloV1/blob/c86c2c89fe3ce18e39c078b8bffb63b3f4f3f3fb/backend/brain/model_manager.py#L321)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/database/connection.py#L92](https://github.com/latheeshmahendran/soloV1/blob/c86c2c89fe3ce18e39c078b8bffb63b3f4f3f3fb/backend/database/connection.py#L92)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

