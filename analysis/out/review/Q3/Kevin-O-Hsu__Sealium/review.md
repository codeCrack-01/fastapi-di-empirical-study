# Kevin-O-Hsu/Sealium

- GitHub: https://github.com/Kevin-O-Hsu/Sealium
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 12 · commit: `0f42a8111aac`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | src/sealium/server/deps.py#L35 | The get_activation_dependencies function uses Depends() to inject RSAEncryptor, ActivationService, and RateLimiter dependencies. These are resolved via get_server_encryptor, get_activation_service,... |
| 2 | `Route-level dependency injection` | src/sealium/server/routes/activation.py#L40 | The activate endpoint directly uses Depends(get_server_encryptor), Depends(get_activation_service), and Depends(get_rate_limiter) to inject dependencies into the route handler. |
| 3 | `Configurable app creation` | src/sealium/server/app.py#L67 | The create_app function accepts optional parameters like encryptor, storage, rate_limiter that can be injected, allowing dependency substitution during application initialization. |

## Pass 2 — reconcile with inventory of Kevin-O-Hsu/Sealium

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() for dependency injection in get_activation_dependencies() and activate() route handler. These are valid DI occurrences. | src/sealium/server/deps.py#L35 |
| `C4|DEF` | true_pos | **no (overturn)** | The create_app() function in src/sealium/server/app.py:67 demonstrates explicit dependency injection through optional parameters (encryptor, storage, rate_limiter). This is a valid DI pattern even ... | src/sealium/server/app.py#L67 |

### Missed by inventory (1)
- `Configurable app creation with injectable parameters` @ src/sealium/server/app.py#L67 — The create_app() function's parameterized dependency injection (encryptor, storage, rate_limiter) was not captured by the fingerprint inventory despite being a clear DI occurrence.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 6 | **false_pos** | [src/sealium/server/deps.py#L35](https://github.com/Kevin-O-Hsu/Sealium/blob/0f42a8111aac0c5fbb10463eedeb2b221fcb6d63/src/sealium/server/deps.py#L35) |
| `C4|DEF` | C4 | 6 | **false_pos** | [src/sealium/common/hardware/native_surfaces.py#L81](https://github.com/Kevin-O-Hsu/Sealium/blob/0f42a8111aac0c5fbb10463eedeb2b221fcb6d63/src/sealium/common/hardware/native_surfaces.py#L81) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 6 · corpus total: 83548 · executor: x86_64
> example: [src/sealium/server/deps.py#L35](https://github.com/Kevin-O-Hsu/Sealium/blob/0f42a8111aac0c5fbb10463eedeb2b221fcb6d63/src/sealium/server/deps.py#L35)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [src/sealium/common/hardware/native_surfaces.py#L81](https://github.com/Kevin-O-Hsu/Sealium/blob/0f42a8111aac0c5fbb10463eedeb2b221fcb6d63/src/sealium/common/hardware/native_surfaces.py#L81)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

