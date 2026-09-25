# ivangor246/live_stream

- GitHub: https://github.com/ivangor246/live_stream
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 11 · commit: `ecbf88543775`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Instance method used as dependency` | server/src/app/api/auth.py#L44 | Dependencies use auth_service.require_admin (an instance method) directly via Depends(auth_service.require_admin). This is not standard FastAPI DI, which typically uses classes or functions as depe... |
| 2 | `Service injection via function parameters` | server/src/app/api/auth.py#L44 | auth_service is injected as a parameter to route functions (e.g., setup_auth(auth_service)), but also used within dependencies as methods (auth_service.require_admin). This mixes parameter injectio... |
| 3 | `Non-standard dependency structure` | server/src/app/api/routes.py#L245 | Dependencies use auth_service.require_operator (another instance method) in the same pattern as auth.py, indicating this is a recurring non-standard DI approach across the codebase. |

## Pass 2 — reconcile with inventory of ivangor246/live_stream

_Presented fingerprints:_ `C1|DOTTED|PARAM`, `C1|DOTTED|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|DOTTED|PARAM` | variant | yes | The code uses instance methods (e.g., auth_service.require_admin) directly as dependencies via Depends(), which is non-standard FastAPI DI but consistent with the 'variant' label. | server/src/app/api/auth.py#L44 |
| `C1|DOTTED|SIG` | false_pos | **no (overturn)** | The code explicitly uses instance methods (e.g., auth_service.require_user) as dependencies, which are valid DI occurrences and not false positives. | server/src/app/api/auth.py#L99 |
| `C4|DEF` | false_pos | yes | The cited lines (e.g., lifespan in main.py) are not DI occurrences but FastAPI app setup code, confirming the 'false_pos' label. | server/src/app/main.py#L102 |

### Missed by inventory (2)
- `Instance method used as dependency (e.g., Depends(auth_service.require_admin))` @ server/src/app/api/auth.py#L44 — The inventory did not capture the recurring pattern of using instance methods directly as dependencies, which is a significant DI structural feature.
- `Service injection via function parameters (e.g., setup_auth(auth_service))` @ server/src/app/api/auth.py#L44 — The inventory missed the hybrid injection pattern where services are both passed as parameters and used within dependencies.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|DOTTED|PARAM` | C1 | 4 | **variant** | [server/src/app/api/auth.py#L44](https://github.com/ivangor246/live_stream/blob/ecbf885437758a41fdbd1d60bf0aef6aa08e634f/server/src/app/api/auth.py#L44) |
| `C1|DOTTED|SIG` | C1 | 4 | **false_pos** | [server/src/app/api/auth.py#L99](https://github.com/ivangor246/live_stream/blob/ecbf885437758a41fdbd1d60bf0aef6aa08e634f/server/src/app/api/auth.py#L99) |
| `C4|DEF` | C4 | 3 | **false_pos** | [server/src/app/main.py#L102](https://github.com/ivangor246/live_stream/blob/ecbf885437758a41fdbd1d60bf0aef6aa08e634f/server/src/app/main.py#L102) |

## `C1|DOTTED|PARAM` — **variant**
> occurrences here: 4 · corpus total: 422 · executor: x86_64
> example: [server/src/app/api/auth.py#L44](https://github.com/ivangor246/live_stream/blob/ecbf885437758a41fdbd1d60bf0aef6aa08e634f/server/src/app/api/auth.py#L44)
> **rule:** C1

> **evidence (model):** Dotted paths (e.g., 'deps.db') used as dependencies in parameters, which is a structural variation of C1 (Depends call arguments) but not the standard bare function reference.

## `C1|DOTTED|SIG` — **false_pos**
> occurrences here: 4 · corpus total: 2178 · executor: x86_64
> example: [server/src/app/api/auth.py#L99](https://github.com/ivangor246/live_stream/blob/ecbf885437758a41fdbd1d60bf0aef6aa08e634f/server/src/app/api/auth.py#L99)
> **rule:** C1

> **evidence (model):** Parameters use dotted names (core.current_principal) but are not wrapped in Depends/Security calls, indicating standard function parameters rather than FastAPI DI dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [server/src/app/main.py#L102](https://github.com/ivangor246/live_stream/blob/ecbf885437758a41fdbd1d60bf0aef6aa08e634f/server/src/app/main.py#L102)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

