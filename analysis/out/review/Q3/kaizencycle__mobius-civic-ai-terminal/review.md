# kaizencycle/mobius-civic-ai-terminal

- GitHub: https://github.com/kaizencycle/mobius-civic-ai-terminal
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 5 · commit: `ee8710c784b2`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | api/app/main.py#L396 | The code does not use FastAPI's `Depends` or any annotated dependencies. The `settings` object and `now_utc()` are used directly without explicit injection. |
| 2 | `No Dependency Injection` | api/redis_bridge.py#L276 | The `get_redis()` function is called directly without being injected via `Depends` or other DI mechanisms. |
| 3 | `No Dependency Injection` | api/routes/stream.py#L86 | The `_event_generator` function receives a `Queue` as an argument, but it is not injected through FastAPI's dependency system. |
| 4 | `No Dependency Injection` | gateway.py#L178 | The `httpx.AsyncClient` is created inline within the function, not injected via DI. |

## Pass 2 — reconcile with inventory of kaizencycle/mobius-civic-ai-terminal

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code does not use FastAPI's `Depends` or any DI mechanisms; `settings`, `now_utc()`, and `get_redis()` are used directly without injection. | api/app/main.py#L396 |
| `C4|DEF` | false_pos | yes | No DI is present in the code; dependencies are resolved inline rather than through FastAPI's dependency system. | api/redis_bridge.py#L276 |
| `C4|DEF` | false_pos | yes | The code does not use FastAPI's `Depends` or other DI mechanisms; dependencies are hardcoded or resolved directly. | api/app/main.py#L395 |

### Missed by inventory (2)
- `No DI usage` @ api/app/main.py#L396 — The entire codebase lacks DI patterns (e.g., `Depends`, injected services), but the inventory may have misclassified this as DI-adjacent.
- `No DI usage` @ api/redis_bridge.py#L276 — The codebase has no DI mechanisms; the inventory may have flagged this as DI-related erroneously.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 5 | **false_pos** | [api/app/main.py#L396](https://github.com/kaizencycle/mobius-civic-ai-terminal/blob/ee8710c784b272084023194d1a350200fd6819f8/api/app/main.py#L396) |

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [api/app/main.py#L396](https://github.com/kaizencycle/mobius-civic-ai-terminal/blob/ee8710c784b272084023194d1a350200fd6819f8/api/app/main.py#L396)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

