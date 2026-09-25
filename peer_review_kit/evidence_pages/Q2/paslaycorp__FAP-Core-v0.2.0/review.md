# paslaycorp/FAP-Core-v0.2.0

- GitHub: https://github.com/paslaycorp/FAP-Core-v0.2.0
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 3 · commit: `ee23ca285aa7`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | api.py#L116 | The verify endpoint uses Depends(verify_key) to inject the verify_key function as a dependency (line 116). This is a standard FastAPI dependency injection pattern where a function is injected into ... |
| 2 | `FastAPI Depends injection` | api.py#L149 | The enroll endpoint similarly uses Depends(verify_key) (line 149), demonstrating reuse of the same dependency across multiple endpoints. |
| 3 | `Unresolved dependency` | api.py#L79 | The verify_key function uses Depends(security) (line 79) but no definition of 'security' is visible in the provided code excerpts, matching the static summary's unresolved_depends=1. |

## Pass 2 — reconcile with inventory of paslaycorp/FAP-Core-v0.2.0

_Presented fingerprints:_ `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code at line 79 uses Depends(security) but 'security' is not defined in the provided code, indicating a real unresolved dependency rather than a false positive. | api.py#L79 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The verify endpoint at line 116 correctly uses Depends(verify_key), which is a valid FastAPI dependency injection pattern. | api.py#L116 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The enroll endpoint at line 149 correctly reuses Depends(verify_key), demonstrating proper dependency injection. | api.py#L149 |

### Missed by inventory (1)
- `Unresolved dependency in Depends()` @ api.py#L79 — The static inventory did not flag the unresolved 'security' parameter in Depends(security) at line 79.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 3 | **false_pos** | [api.py#L79](https://github.com/paslaycorp/FAP-Core-v0.2.0/blob/ee23ca285aa7bc935198554ee2e6435dc701f6fe/api.py#L79) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 83548 · executor: x86_64
> example: [api.py#L79](https://github.com/paslaycorp/FAP-Core-v0.2.0/blob/ee23ca285aa7bc935198554ee2e6435dc701f6fe/api.py#L79)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

