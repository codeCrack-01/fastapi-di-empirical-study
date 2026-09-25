# beenycool/yotuubef

- GitHub: https://github.com/beenycool/yotuubef
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 6 · commit: `9930b9bb9683`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | src/database/db_manager.py#L129 | The code defines an async context manager `get_connection` for managing database connections, but there is no use of FastAPI's `Depends` or other dependency injection patterns. The method yields a ... |
| 2 | `No Dependency Injection` | tests/test_gpu_memory_manager.py#L14 | Test fixtures like `no_torch` and `with_cuda` mock dependencies for testing purposes, but these are part of test infrastructure, not application-level dependency injection. The application code its... |
| 3 | `No Dependency Injection` | tests/test_settings.py#L68 | The `clean_config` fixture resets environment variables and config states for testing, but again, this is test infrastructure. There is no evidence of FastAPI's dependency injection being used in t... |

## Pass 2 — reconcile with inventory of beenycool/yotuubef

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code does not implement FastAPI-style dependency injection (e.g., no `Depends` usage). The `get_connection` method is an async context manager, not a DI dependency. | src/database/db_manager.py#L129 |
| `C4|DEF` | false_pos | yes | Test fixtures like `no_torch` and `with_cuda` are test infrastructure, not application-level DI. No FastAPI `Depends` or DI framework usage is present. | tests/test_gpu_memory_manager.py#L14 |
| `C4|DEF` | false_pos | yes | The test code uses mocking for testing, not application-level dependency injection. No DI framework patterns are implemented. | tests/test_gpu_memory_manager.py#L21 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 6 | **false_pos** | [src/database/db_manager.py#L129](https://github.com/beenycool/yotuubef/blob/9930b9bb9683371c88c3f81c2fc4564c49e609d7/src/database/db_manager.py#L129) |

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [src/database/db_manager.py#L129](https://github.com/beenycool/yotuubef/blob/9930b9bb9683371c88c3f81c2fc4564c49e609d7/src/database/db_manager.py#L129)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

