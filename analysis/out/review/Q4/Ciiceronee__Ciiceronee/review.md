# Ciiceronee/Ciiceronee

- GitHub: https://github.com/Ciiceronee/Ciiceronee
- Stars: 544 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 38 · commit: `acc7fec929be`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection with global instances` | ciicerone/api/main.py#L225 | The route handler uses `sim: Simulator = Depends(get_simulator)` to inject a dependency. The `get_simulator` function likely returns the global `simulator` instance initialized in the lifespan mana... |
| 2 | `Same DI pattern for LLMManager` | ciicerone/api/main.py#L305 | The `generate_content` endpoint uses `llm: LLMManager = Depends(get_llm_manager)`, mirroring the Simulator injection pattern. The `get_llm_manager` function probably returns the global `llm_manager... |
| 3 | `Lifespan manager for global dependency initialization` | ciicerone/api/main.py#L34 | The `lifespan` async context manager initializes `simulator` and `llm_manager` as global variables. These are later injected into route handlers via Depends(), showing a clear DI pattern where depe... |

## Pass 2 — reconcile with inventory of Ciiceronee/Ciiceronee

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code demonstrates valid FastAPI dependency injection using global instances initialized in the lifespan manager (line 34). The Simulator and LLMManager are properly injected via Depends() in ro... | ciicerone/api/main.py#L34 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code shows correct use of FastAPI's Depends() for injecting global dependencies (lines 225, 305). Error handling and proper DI patterns are implemented in the route handlers. | ciicerone/api/main.py#L225 |

### Missed by inventory (2)
- `Async context manager DI initialization` @ ciicerone/core/postgres_event_store.py#L194 — The _acquire() method uses async context managers for dependency injection, which was not captured in the fingerprint inventory.
- `Thread-local DI in security module` @ ciicerone/security/template_validator.py#L151 — The regex_timeout() context manager implements thread-local dependency injection patterns not identified in the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 33 | **false_pos** | [ciicerone/api/main.py#L34](https://github.com/Ciiceronee/Ciiceronee/blob/acc7fec929be129b8b6d0e3240ad5b48b4a04f20/ciicerone/api/main.py#L34) |
| `C1|BARE|SIG` | C1 | 5 | **false_pos** | [ciicerone/api/main.py#L225](https://github.com/Ciiceronee/Ciiceronee/blob/acc7fec929be129b8b6d0e3240ad5b48b4a04f20/ciicerone/api/main.py#L225) |

## `C4|DEF` — **false_pos**
> occurrences here: 33 · corpus total: 56644 · executor: x86_64
> example: [ciicerone/api/main.py#L34](https://github.com/Ciiceronee/Ciiceronee/blob/acc7fec929be129b8b6d0e3240ad5b48b4a04f20/ciicerone/api/main.py#L34)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 5 · corpus total: 83548 · executor: x86_64
> example: [ciicerone/api/main.py#L225](https://github.com/Ciiceronee/Ciiceronee/blob/acc7fec929be129b8b6d0e3240ad5b48b4a04f20/ciicerone/api/main.py#L225)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

