# tramontano/fiap-ml-stock-price-prediction

- GitHub: https://github.com/tramontano/fiap-ml-stock-price-prediction
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 18 · commit: `2b545209e2a3`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | src/api/routes.py#L93 | The `get_model` endpoint uses `Depends(verify_api_key)` to inject authentication validation, a common FastAPI DI pattern. This is also seen in `promote_model` (line 145) and `delete_model` (line 191). |
| 2 | `Reusable dependency functions` | src/api/routes.py#L29 | The `verify_api_key` function is defined once and reused across multiple endpoints via `Depends(verify_api_key)`, demonstrating DI through reusable dependency functions. |
| 3 | `State injection via app.state` | src/api/main.py#L18 | The `lifespan` context manager injects `client`, `pipeline`, and `model` into `app.state`, making them available to routes via `request.app.state.client` (seen in `get_model` at line 93). |
| 4 | `Security dependency injection` | src/api/routes.py#L34 | The `security = HTTPBasic()` object is injected into `verify_api_key` (line 29) via `Depends(security)`, showing DI for authentication. |

## Pass 2 — reconcile with inventory of tramontano/fiap-ml-stock-price-prediction

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code correctly uses FastAPI's `Depends(verify_api_key)` for dependency injection in multiple endpoints (get_model, promote_model, delete_model), which aligns with the C1|BARE|SIG fingerprint. | src/api/routes.py#L93 |
| `C4|DEF` | false_pos | **no (overturn)** | The code in `lifespan` correctly injects `client`, `pipeline`, and `model` into `app.state`, which is a valid form of dependency injection (C4|DEF) through stateful middleware. | src/api/main.py#L18 |

### Missed by inventory (2)
- `Security dependency injection via HTTPBasic()` @ src/api/routes.py#L34 — The use of `security = HTTPBasic()` injected via `Depends(security)` was not captured in the fingerprint inventory.
- `State injection via app.state.client` @ src/api/main.py#L18 — The injection of `client` into `app.state` for cross-route availability was not captured in the fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 13 | **false_pos** | [src/api/routes.py#L29](https://github.com/tramontano/fiap-ml-stock-price-prediction/blob/2b545209e2a359a81733cff331063d0f0c673e67/src/api/routes.py#L29) |
| `C4|DEF` | C4 | 5 | **false_pos** | [src/api/main.py#L18](https://github.com/tramontano/fiap-ml-stock-price-prediction/blob/2b545209e2a359a81733cff331063d0f0c673e67/src/api/main.py#L18) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 13 · corpus total: 83548 · executor: x86_64
> example: [src/api/routes.py#L29](https://github.com/tramontano/fiap-ml-stock-price-prediction/blob/2b545209e2a359a81733cff331063d0f0c673e67/src/api/routes.py#L29)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [src/api/main.py#L18](https://github.com/tramontano/fiap-ml-stock-price-prediction/blob/2b545209e2a359a81733cff331063d0f0c673e67/src/api/main.py#L18)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

