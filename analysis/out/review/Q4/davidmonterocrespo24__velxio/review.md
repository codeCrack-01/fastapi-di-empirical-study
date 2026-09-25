# davidmonterocrespo24/velxio

- GitHub: https://github.com/davidmonterocrespo24/velxio
- Stars: 2541 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 10 · commit: `e2615584b65b`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends() for user authentication` | backend/app/api/routes/compile.py#L1174 | The `compile_sketch` function uses `Depends(get_current_user_id)` to inject user authentication, as seen in the parameter `user_id: str | None = Depends(get_current_user_id)`. |
| 2 | `FastAPI Depends() for user authentication` | backend/app/api/routes/compile.py#L1322 | The `compile_start` function uses `Depends(get_current_user_id)` for the `requester_id` parameter, indicating dependency injection for user authentication. |
| 3 | `FastAPI Depends() for user authentication` | backend/app/api/routes/libraries.py#L43 | The `install_library` function uses `Depends(get_current_user_id)` for the `requester_id` parameter, showing dependency injection for user authentication. |
| 4 | `FastAPI Depends() for user authentication` | backend/app/api/routes/libraries.py#L105 | The `uninstall_library` function uses `Depends(get_current_user_id)` for the `requester_id` parameter, another instance of dependency injection for user authentication. |

## Pass 2 — reconcile with inventory of davidmonterocrespo24/velxio

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses `Depends(get_current_user_id)` for authentication in multiple routes, confirming the presence of dependency injection. | backend/app/api/routes/compile.py#L1174 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses `Depends(get_current_user_id)` for authentication in multiple routes, confirming the presence of dependency injection. | backend/app/api/routes/compile.py#L1322 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses `Depends(get_current_user_id)` for authentication in multiple routes, confirming the presence of dependency injection. | backend/app/api/routes/libraries.py#L43 |

### Missed by inventory (1)
- `FastAPI `Depends()` usage for user authentication` @ backend/app/api/routes/libraries.py#L105 — The `uninstall_library` route also uses `Depends(get_current_user_id)` for authentication, but this instance was not captured by the fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 6 | **false_pos** | [backend/app/api/routes/flash.py#L195](https://github.com/davidmonterocrespo24/velxio/blob/e2615584b65bf5b19d0269480da02fd5e51f34a9/backend/app/api/routes/flash.py#L195) |
| `C1|BARE|SIG` | C1 | 4 | **false_pos** | [backend/app/api/routes/compile.py#L1174](https://github.com/davidmonterocrespo24/velxio/blob/e2615584b65bf5b19d0269480da02fd5e51f34a9/backend/app/api/routes/compile.py#L1174) |

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/routes/flash.py#L195](https://github.com/davidmonterocrespo24/velxio/blob/e2615584b65bf5b19d0269480da02fd5e51f34a9/backend/app/api/routes/flash.py#L195)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 4 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/routes/compile.py#L1174](https://github.com/davidmonterocrespo24/velxio/blob/e2615584b65bf5b19d0269480da02fd5e51f34a9/backend/app/api/routes/compile.py#L1174)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

