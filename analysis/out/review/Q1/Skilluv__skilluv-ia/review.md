# Skilluv/skilluv-ia

- GitHub: https://github.com/Skilluv/skilluv-ia
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 9 · commit: `a85162fddd49`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `pytest fixtures for test dependency injection` | tests/integration/conftest.py#L65 | The redis_client fixture provides a Redis connection to tests, demonstrating dependency injection via pytest fixtures. It yields a client and handles cleanup. |
| 2 | `monkeypatching for dependency override` | tests/integration/test_redis_services_integration.py#L36 | The _override_redis fixture uses monkeypatch to replace the get_redis function with a test-specific implementation, overriding dependencies. |
| 3 | `fixture-based configuration injection` | tests/integration/test_services_llm_live.py#L75 | The _use_real_ollama fixture injects Ollama model configuration into tests, ensuring dependencies use production-like settings. |
| 4 | `mocking with fake services` | tests/test_workers_envelope.py#L76 | The fake_redis fixture replaces the real Redis client with a FakeRedis instance, demonstrating dependency injection of mock services. |

## Pass 2 — reconcile with inventory of Skilluv/skilluv-ia

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly implements dependency injection patterns via pytest fixtures and monkeypatching, which aligns with the fingerprint's structural definition. | tests/integration/conftest.py#L65 |

### Missed by inventory (3)
- `monkeypatch-based dependency override` @ tests/integration/test_redis_services_integration.py#L36 — The _override_redis fixture uses monkeypatch to replace Redis client implementations, a clear DI pattern not captured in the initial inventory
- `mock service injection via fake implementations` @ tests/test_workers_envelope.py#L76 — The fake_redis fixture replaces real Redis with a mock implementation, demonstrating DI through service substitution
- `environment-specific configuration injection` @ tests/test_grpc_reflection.py#L19 — The test uses patch to modify settings.environment, demonstrating DI of configuration parameters

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 9 | **false_pos** | [tests/integration/conftest.py#L65](https://github.com/Skilluv/skilluv-ia/blob/a85162fddd498d786dc11ef6f0b0f924ebf7bb6a/tests/integration/conftest.py#L65) |

## `C4|DEF` — **false_pos**
> occurrences here: 9 · corpus total: 56644 · executor: x86_64
> example: [tests/integration/conftest.py#L65](https://github.com/Skilluv/skilluv-ia/blob/a85162fddd498d786dc11ef6f0b0f924ebf7bb6a/tests/integration/conftest.py#L65)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

