# yezz123/ormdantic

- GitHub: https://github.com/yezz123/ormdantic
- Stars: 151 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 28 · commit: `178d6fa2c811`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Depends` | examples/todo_app/app/routes.py#L34 | The code defines a dependency `get_service` that retrieves `TodoService` from the application state, and uses `Depends(get_service)` to inject it into endpoints via an `Annotated` type hint. This i... |

## Pass 2 — reconcile with inventory of yezz123/ormdantic

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code in benchmark/datasets.py defines utility functions for generating benchmark data (tuples, dicts, etc.), which are not dependency injection occurrences but simple data generation logic. | benchmark/datasets.py#L26 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses FastAPI's `Depends` for dependency injection via `Annotated[TodoService, Depends(...)]`, which aligns with the 'known' label. | examples/todo_app/app/routes.py#L34 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | The code defines a valid FastAPI dependency (`Service = Annotated[TodoService, Depends(...)]`) that is correctly used in endpoints, contradicting the 'false_pos' label. | examples/todo_app/app/routes.py#L34 |

### Missed by inventory (1)
- `FastAPI lifespan context manager with dependency injection` @ examples/todo_app/app/main.py#L23 — The `lifespan` context manager in `create_app` initializes `TodoService` via `Depends`, which is a DI occurrence not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 26 | **false_pos** | [benchmark/datasets.py#L26](https://github.com/yezz123/ormdantic/blob/178d6fa2c811fd2218288ce2d680545a4a2bfd3f/benchmark/datasets.py#L26) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [examples/todo_app/app/routes.py#L34](https://github.com/yezz123/ormdantic/blob/178d6fa2c811fd2218288ce2d680545a4a2bfd3f/examples/todo_app/app/routes.py#L34) |
| `C3|CLASS|BARE` | C3 | 1 | **false_pos** | [examples/todo_app/app/routes.py#L34](https://github.com/yezz123/ormdantic/blob/178d6fa2c811fd2218288ce2d680545a4a2bfd3f/examples/todo_app/app/routes.py#L34) |

## `C4|DEF` — **false_pos**
> occurrences here: 26 · corpus total: 56644 · executor: x86_64
> example: [benchmark/datasets.py#L26](https://github.com/yezz123/ormdantic/blob/178d6fa2c811fd2218288ce2d680545a4a2bfd3f/benchmark/datasets.py#L26)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [examples/todo_app/app/routes.py#L34](https://github.com/yezz123/ormdantic/blob/178d6fa2c811fd2218288ce2d680545a4a2bfd3f/examples/todo_app/app/routes.py#L34)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 1 · corpus total: 20139 · executor: x86_64
> example: [examples/todo_app/app/routes.py#L34](https://github.com/yezz123/ormdantic/blob/178d6fa2c811fd2218288ce2d680545a4a2bfd3f/examples/todo_app/app/routes.py#L34)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

