# ActiveInferenceInstitute/ActiveInferAnts

- GitHub: https://github.com/ActiveInferenceInstitute/ActiveInferAnts
- Stars: 29 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 17 · commit: `1dea3cd6a65a`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | 6_API/Knowledge_API.py#L123 | The `get_db` function is defined as a dependency provider using `yield db`, and is injected into endpoints via `Depends(get_db)` (e.g., line 239). This is a standard FastAPI pattern for database se... |
| 2 | `API key authentication dependency` | 6_API/Knowledge_API.py#L123 | The `get_api_key` function is defined as a dependency using `Depends(api_key_header)`, and is injected into endpoints via `Depends(get_api_key)` (e.g., line 239). This handles authentication via AP... |
| 3 | `Reused dependency injection pattern` | 6_API/MetaInformAnt_API.py#L54 | The `get_current_api_key` function mirrors `get_api_key` in structure, using `Depends(api_key_header)` and being injected via `Depends(get_current_api_key)` in endpoints like `perform_advanced_infe... |

## Pass 2 — reconcile with inventory of ActiveInferenceInstitute/ActiveInferAnts

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends()` for dependency injection (e.g., `Depends(get_db)` in endpoints and `Depends(api_key_header)` in authentication). This matches standard DI patterns, co... | 6_API/Knowledge_API.py#L239 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db` function is a valid DI provider using `yield db` (line 109), which is a core FastAPI pattern for managing database sessions. The 'false_pos' label incorrectly dismisses this as non-DI. | 6_API/Knowledge_API.py#L109 |

### Missed by inventory (2)
- `FastAPI dependency injection via `Depends()` in MetaInformAnt_API.py` @ 6_API/MetaInformAnt_API.py#L179 — The inventory missed the `Depends(get_current_api_key)` usage in `/api/v1/advanced_infer/` and similar endpoints, which are clear DI occurrences.
- `Repeated DI usage in Knowledge_API.py endpoints` @ 6_API/Knowledge_API.py#L265 — The inventory only linked 3 lines for C1|BARE|SIG but missed other DI instances like `Depends(get_api_key)` in `read_knowledge` (line 265) and `update_knowledge` (line 284).

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 16 | **false_pos** | [6_API/Knowledge_API.py#L123](https://github.com/ActiveInferenceInstitute/ActiveInferAnts/blob/1dea3cd6a65a999b14b2ca3fd52542e395a33624/6_API/Knowledge_API.py#L123) |
| `C4|USED` | C4 | 1 | **false_pos** | [6_API/Knowledge_API.py#L109](https://github.com/ActiveInferenceInstitute/ActiveInferAnts/blob/1dea3cd6a65a999b14b2ca3fd52542e395a33624/6_API/Knowledge_API.py#L109) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 16 · corpus total: 83548 · executor: x86_64
> example: [6_API/Knowledge_API.py#L123](https://github.com/ActiveInferenceInstitute/ActiveInferAnts/blob/1dea3cd6a65a999b14b2ca3fd52542e395a33624/6_API/Knowledge_API.py#L123)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [6_API/Knowledge_API.py#L109](https://github.com/ActiveInferenceInstitute/ActiveInferAnts/blob/1dea3cd6a65a999b14b2ca3fd52542e395a33624/6_API/Knowledge_API.py#L109)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

