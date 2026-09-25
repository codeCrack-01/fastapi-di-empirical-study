# auth0/auth0-fastapi-api

- GitHub: https://github.com/auth0/auth0-fastapi-api
- Stars: 10 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 37 · commit: `6cfd1044527a`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based DI` | tests/test_bearer_token_validation.py#L26 | The route uses `claims=Depends(auth0.require_auth())` to inject authentication dependencies. This is a standard FastAPI pattern where dependencies are resolved via the `Depends` function. |
| 2 | `FastAPI Depends-based DI` | tests/test_dpop_authentication.py#L38 | Similar usage of `Depends(auth0.require_auth())` in a route, demonstrating dependency injection for DPoP authentication. |
| 3 | `FastAPI Depends-based DI` | tests/test_on_behalf_of.py#L92 | The route uses `claims=Depends(auth0.require_auth())` again, showing consistent use of FastAPI's DI system across test cases. |

## Pass 2 — reconcile with inventory of auth0/auth0-fastapi-api

_Presented fingerprints:_ `C1|DOTTED|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|DOTTED|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends(auth0.require_auth())` pattern for dependency injection in routes, which is a legitimate DI usage. The panel's 'false_pos' label incorrectly dismisses va... | tests/test_bearer_token_validation.py#L26 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|DOTTED|SIG` | C1 | 37 | **false_pos** | [tests/test_bearer_token_validation.py#L26](https://github.com/auth0/auth0-fastapi-api/blob/6cfd1044527aff6b18dc2be6ba45f49feffc3295/tests/test_bearer_token_validation.py#L26) |

## `C1|DOTTED|SIG` — **false_pos**
> occurrences here: 37 · corpus total: 2178 · executor: x86_64
> example: [tests/test_bearer_token_validation.py#L26](https://github.com/auth0/auth0-fastapi-api/blob/6cfd1044527aff6b18dc2be6ba45f49feffc3295/tests/test_bearer_token_validation.py#L26)
> **rule:** C1

> **evidence (model):** Parameters use dotted names (core.current_principal) but are not wrapped in Depends/Security calls, indicating standard function parameters rather than FastAPI DI dependencies

