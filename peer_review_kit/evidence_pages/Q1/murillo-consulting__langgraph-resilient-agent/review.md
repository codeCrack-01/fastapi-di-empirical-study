# murillo-consulting/langgraph-resilient-agent

- GitHub: https://github.com/murillo-consulting/langgraph-resilient-agent
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 26 · commit: `0dfc29c8c8f6`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI function-based dependency injection` | src/resilient_agent/app.py#L49 | The code uses FastAPI's `Depends()` to inject dependencies. For example, `run_service: Annotated[RunService, Depends(service)]` injects a `RunService` instance via the `service()` function that ret... |
| 2 | `Shared state-based dependency resolution` | src/resilient_agent/app.py#L21 | The `lifespan` function initializes `app.state.service` as a shared RunService instance, which is then accessed by the `service()` dependency function across multiple routes (e.g., `start_run`, `ge... |

## Pass 2 — reconcile with inventory of murillo-consulting/langgraph-resilient-agent

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | known | **no (overturn)** | The code explicitly uses FastAPI's `Depends()` for dependency injection (e.g., `run_service: Annotated[RunService, Depends(service)]`), which is a valid DI pattern. The panel's 'false_pos' label is... | src/resilient_agent/app.py#L49 |
| `C1|BARE|PARAM` | known | yes | The code uses `Annotated[...]` with `Depends()` and `Header()` for parameterized dependencies (e.g., `idempotency_key: Annotated[str, Header(...)]`), aligning with the 'known' label. | src/resilient_agent/app.py#L49 |
| `C4|DEF` | known | **no (overturn)** | The `lifespan` function in `app.py` defines a shared `RunService` instance via `app.state.service`, which is accessed by `Depends(service)` elsewhere. This is a valid DI pattern, contradicting the ... | src/resilient_agent/app.py#L21 |

### Missed by inventory (2)
- `Annotated[...] with Depends(...) for route parameters` @ src/resilient_agent/app.py#L49 — The inventory missed multiple instances of `Annotated[...]` with `Depends(...)` in route parameters (e.g., `run_service: Annotated[RunService, Depends(service)]`), which are clear DI points.
- `Shared state initialization via lifespan context manager` @ src/resilient_agent/app.py#L21 — The inventory did not capture the DI pattern of initializing shared state (`app.state.service`) in the `lifespan` context manager, which is critical for dependency resolution.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 16 | **false_pos** | [src/resilient_agent/app.py#L49](https://github.com/murillo-consulting/langgraph-resilient-agent/blob/0dfc29c8c8f6a6ea02812a69ae9a63b8bd7b43f5/src/resilient_agent/app.py#L49) |
| `C1|BARE|PARAM` | C1 | 8 | **known** | [src/resilient_agent/app.py#L49](https://github.com/murillo-consulting/langgraph-resilient-agent/blob/0dfc29c8c8f6a6ea02812a69ae9a63b8bd7b43f5/src/resilient_agent/app.py#L49) |
| `C4|DEF` | C4 | 2 | **false_pos** | [src/resilient_agent/app.py#L21](https://github.com/murillo-consulting/langgraph-resilient-agent/blob/0dfc29c8c8f6a6ea02812a69ae9a63b8bd7b43f5/src/resilient_agent/app.py#L21) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 16 · corpus total: 20139 · executor: x86_64
> example: [src/resilient_agent/app.py#L49](https://github.com/murillo-consulting/langgraph-resilient-agent/blob/0dfc29c8c8f6a6ea02812a69ae9a63b8bd7b43f5/src/resilient_agent/app.py#L49)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 8 · corpus total: 18195 · executor: x86_64
> example: [src/resilient_agent/app.py#L49](https://github.com/murillo-consulting/langgraph-resilient-agent/blob/0dfc29c8c8f6a6ea02812a69ae9a63b8bd7b43f5/src/resilient_agent/app.py#L49)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [src/resilient_agent/app.py#L21](https://github.com/murillo-consulting/langgraph-resilient-agent/blob/0dfc29c8c8f6a6ea02812a69ae9a63b8bd7b43f5/src/resilient_agent/app.py#L21)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

