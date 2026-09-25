# joeynyc/hermes-hudui

- GitHub: https://github.com/joeynyc/hermes-hudui
- Stars: 1801 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 4 · commit: `6e7e610fb969`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | backend/api/chat.py#L160 | No use of FastAPI Depends or similar DI mechanisms; chat_engine is used directly without injection |
| 2 | `No Dependency Injection` | backend/api/chat.py#L122 | send_and_stream function uses chat_engine directly without dependency injection |
| 3 | `No Dependency Injection` | backend/chat/streamer.py#L105 | iter_events method uses self._queue and self._stopped without injected dependencies |
| 4 | `No Dependency Injection` | backend/main.py#L253 | lifespan context manager does not use FastAPI dependency injection patterns |

## Pass 2 — reconcile with inventory of joeynyc/hermes-hudui

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No DI mechanisms (e.g., FastAPI Depends) are used in the code excerpts; chat_engine is directly instantiated/used without injection. | backend/api/chat.py#L160 |
| `C4|DEF` | false_pos | yes | No DI patterns detected in send_and_stream function; chat_engine is used directly without injection. | backend/api/chat.py#L122 |
| `C4|DEF` | false_pos | yes | iter_events method uses self._queue and self._stopped without any dependency injection mechanisms. | backend/chat/streamer.py#L105 |
| `C4|DEF` | false_pos | yes | lifespan context manager does not use FastAPI DI patterns. | backend/main.py#L253 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [backend/api/chat.py#L160](https://github.com/joeynyc/hermes-hudui/blob/6e7e610fb969172f5be02a62034675bad34b4866/backend/api/chat.py#L160) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [backend/api/chat.py#L160](https://github.com/joeynyc/hermes-hudui/blob/6e7e610fb969172f5be02a62034675bad34b4866/backend/api/chat.py#L160)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

