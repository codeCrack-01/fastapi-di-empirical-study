# quoeamaster/python_for_ai_prep

- GitHub: https://github.com/quoeamaster/python_for_ai_prep
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 3 · commit: `ab4cbabd6189`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends usage` | fastapi-demo/backend/api/router.py#L23 | The code uses `Depends(get_validator)` to inject a validation dependency into the `/api/chat` endpoint. This is FastAPI's built-in dependency injection system, where `get_validator` is a function t... |

## Pass 2 — reconcile with inventory of quoeamaster/python_for_ai_prep

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code in the fixtures does not use dependency injection (DI) patterns; it merely spawns subprocesses for test servers. The static instrument's label is correct. | mcp_educational/tests/conftest.py#L15 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends(get_validator)` for dependency injection, which is a canonical DI pattern. The static instrument's label of 'false_pos' is incorrect. | fastapi-demo/backend/api/router.py#L23 |

### Missed by inventory (1)
- `FastAPI Depends usage` @ fastapi-demo/backend/api/router.py#L23 — The inventory did not capture this instance of FastAPI's built-in DI system, which was explicitly noted in pass-1 observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 2 | **false_pos** | [mcp_educational/tests/conftest.py#L15](https://github.com/quoeamaster/python_for_ai_prep/blob/ab4cbabd61896e4d660ec24123583b86739d33d7/mcp_educational/tests/conftest.py#L15) |
| `C1|BARE|SIG` | C1 | 1 | **false_pos** | [fastapi-demo/backend/api/router.py#L19](https://github.com/quoeamaster/python_for_ai_prep/blob/ab4cbabd61896e4d660ec24123583b86739d33d7/fastapi-demo/backend/api/router.py#L19) |

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [mcp_educational/tests/conftest.py#L15](https://github.com/quoeamaster/python_for_ai_prep/blob/ab4cbabd61896e4d660ec24123583b86739d33d7/mcp_educational/tests/conftest.py#L15)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 1 · corpus total: 83548 · executor: x86_64
> example: [fastapi-demo/backend/api/router.py#L19](https://github.com/quoeamaster/python_for_ai_prep/blob/ab4cbabd61896e4d660ec24123583b86739d33d7/fastapi-demo/backend/api/router.py#L19)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

