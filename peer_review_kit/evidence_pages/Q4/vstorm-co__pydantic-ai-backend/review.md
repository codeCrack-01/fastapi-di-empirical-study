# vstorm-co/pydantic-ai-backend

- GitHub: https://github.com/vstorm-co/pydantic-ai-backend
- Stars: 117 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 24 · commit: `8ac7b678b633`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Annotated and Depends` | src/pydantic_ai_backends/remote/server.py#L2064 | ServiceDep is defined as Annotated[_Service, Depends(_service_of)], showing explicit use of FastAPI's dependency injection system. This creates a typed dependency that pulls the service from applic... |
| 2 | `Nested dependency injection in route handlers` | src/pydantic_ai_backends/remote/server.py#L2083 | The _authorized_session function uses ServiceDep (defined earlier) and TokenHeader, demonstrating nested dependencies where route handlers depend on multiple injected services. |
| 3 | `Lifespan context manager for dependency setup` | src/pydantic_ai_backends/remote/server.py#L2414 | The lifespan asynccontextmanager is used to inject startup/shutdown logic into the FastAPI app, ensuring dependencies like the service are properly initialized and cleaned up. |

## Pass 2 — reconcile with inventory of vstorm-co/pydantic-ai-backend

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|BARE|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code at line 1500 in src/pydantic_ai_backends/remote/server.py defines a context manager (`observe`) but does not use FastAPI's dependency injection system (no `Annotated`, `Depends`, or parame... | src/pydantic_ai_backends/remote/server.py#L1500 |
| `C1|BARE|PARAM` | known | yes | The code at lines 2064, 2083, and 2084 in src/pydantic_ai_backends/remote/server.py explicitly uses `Annotated` and `Depends` for dependency injection (e.g., `ServiceDep = Annotated[_Service, Depen... | src/pydantic_ai_backends/remote/server.py#L2064 |
| `C3|BARE|BARE` | variant | yes | The code at lines 2064 and 2084 in src/pydantic_ai_backends/remote/server.py uses `Annotated` with `Depends` for bare dependencies (e.g., `ServiceDep`), consistent with the 'variant' label for this... | src/pydantic_ai_backends/remote/server.py#L2064 |

### Missed by inventory (1)
- `Lifespan context manager for dependency setup` @ src/pydantic_ai_backends/remote/server.py#L2414 — The inventory did not capture the `@asynccontextmanager` lifespan handler in `create_app`, which initializes and shuts down the service, a critical DI-related pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 19 | **false_pos** | [examples/predictive_analytics/server.py#L49](https://github.com/vstorm-co/pydantic-ai-backend/blob/8ac7b678b633aa51c054a884ce27d31b130b8110/examples/predictive_analytics/server.py#L49) |
| `C1|BARE|PARAM` | C1 | 3 | **known** | [src/pydantic_ai_backends/remote/server.py#L2064](https://github.com/vstorm-co/pydantic-ai-backend/blob/8ac7b678b633aa51c054a884ce27d31b130b8110/src/pydantic_ai_backends/remote/server.py#L2064) |
| `C3|BARE|BARE` | C3 | 2 | **variant** | [src/pydantic_ai_backends/remote/server.py#L2064](https://github.com/vstorm-co/pydantic-ai-backend/blob/8ac7b678b633aa51c054a884ce27d31b130b8110/src/pydantic_ai_backends/remote/server.py#L2064) |

## `C4|DEF` — **false_pos**
> occurrences here: 19 · corpus total: 56644 · executor: x86_64
> example: [examples/predictive_analytics/server.py#L49](https://github.com/vstorm-co/pydantic-ai-backend/blob/8ac7b678b633aa51c054a884ce27d31b130b8110/examples/predictive_analytics/server.py#L49)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 3 · corpus total: 18195 · executor: x86_64
> example: [src/pydantic_ai_backends/remote/server.py#L2064](https://github.com/vstorm-co/pydantic-ai-backend/blob/8ac7b678b633aa51c054a884ce27d31b130b8110/src/pydantic_ai_backends/remote/server.py#L2064)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|BARE|BARE` — **variant**
> occurrences here: 2 · corpus total: 1316 · executor: x86_64
> example: [src/pydantic_ai_backends/remote/server.py#L2064](https://github.com/vstorm-co/pydantic-ai-backend/blob/8ac7b678b633aa51c054a884ce27d31b130b8110/src/pydantic_ai_backends/remote/server.py#L2064)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

