# abdeljalil-elg/ai-fraud-detection-platform

- GitHub: https://github.com/abdeljalil-elg/ai-fraud-detection-platform
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 14 · commit: `11bbed22902a`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI function-based dependency injection` | src/fraud_detection/api/dependencies.py#L106 | The get_token_service(), get_password_verifier(), and get_current_subject() functions are defined as dependency resolvers. They return instances of services (JWTTokenService, PasswordVerifier) and ... |
| 2 | `Cached dependency resolvers` | src/fraud_detection/api/dependencies.py#L106 | get_password_verifier() uses @lru_cache(maxsize=1) to cache the PasswordVerifier instance, optimizing repeated dependency resolution. |
| 3 | `Cross-route dependency reuse` | src/fraud_detection/api/routes/model.py#L18 | get_current_subject() is reused in multiple routes (model_info, model_versions, predict, predict_batch) for authentication, demonstrating centralized dependency management. |
| 4 | `Service abstraction via dependencies` | src/fraud_detection/api/routes/auth.py#L17 | Dependencies like get_token_service and get_password_verifier abstract service creation, allowing routes to depend on interfaces (JWTTokenService, PasswordVerifier) rather than concrete implementat... |

## Pass 2 — reconcile with inventory of abdeljalil-elg/ai-fraud-detection-platform

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly implements authentication via JWT token decoding and password verification, not a false positive. | src/fraud_detection/api/dependencies.py#L106 |
| `C4|DEF` | true_pos | **no (overturn)** | The session_scope context manager properly handles database transactions with commit/rollback, not a false positive. | src/fraud_detection/infrastructure/database.py#L37 |

### Missed by inventory (2)
- `LRU-cached dependency resolvers` @ src/fraud_detection/api/dependencies.py#L106 — The @lru_cache decorator on get_password_verifier() was not captured in the fingerprint inventory.
- `Context manager transaction handling` @ src/fraud_detection/infrastructure/database.py#L37 — The session_scope() context manager's try/except/finally pattern was not captured in the fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 13 | **false_pos** | [src/fraud_detection/api/dependencies.py#L106](https://github.com/abdeljalil-elg/ai-fraud-detection-platform/blob/11bbed22902ae1cc8beb729c17c5700a475f7eda/src/fraud_detection/api/dependencies.py#L106) |
| `C4|DEF` | C4 | 1 | **false_pos** | [src/fraud_detection/infrastructure/database.py#L37](https://github.com/abdeljalil-elg/ai-fraud-detection-platform/blob/11bbed22902ae1cc8beb729c17c5700a475f7eda/src/fraud_detection/infrastructure/database.py#L37) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 13 · corpus total: 83548 · executor: x86_64
> example: [src/fraud_detection/api/dependencies.py#L106](https://github.com/abdeljalil-elg/ai-fraud-detection-platform/blob/11bbed22902ae1cc8beb729c17c5700a475f7eda/src/fraud_detection/api/dependencies.py#L106)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [src/fraud_detection/infrastructure/database.py#L37](https://github.com/abdeljalil-elg/ai-fraud-detection-platform/blob/11bbed22902ae1cc8beb729c17c5700a475f7eda/src/fraud_detection/infrastructure/database.py#L37)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

