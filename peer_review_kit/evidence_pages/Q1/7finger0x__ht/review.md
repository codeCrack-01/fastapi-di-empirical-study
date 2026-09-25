# 7finger0x/ht

- GitHub: https://github.com/7finger0x/ht
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 28 · commit: `f063670ecee5`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Annotated and Depends` | services/api/app/main.py#L83 | The code defines multiple annotated dependencies using Annotated[AuthContext, Depends(...)], such as AuthenticatedPrincipal and DecisionWriter. These use FastAPI's Depends() to inject authenticatio... |
| 2 | `Custom Dependency Functions` | services/api/app/auth.py#L32 | The require_authenticated_principal function uses Depends(bearer_scheme) to inject an authentication scheme, and require_scopes defines a higher-order function that returns a dependency checking re... |

## Pass 2 — reconcile with inventory of 7finger0x/ht

_Presented fingerprints:_ `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | The code uses FastAPI's Annotated[AuthContext, Depends(...)] pattern for parameter injection, matching the fingerprint's structural definition. | services/api/app/main.py#L83 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | The code defines annotated dependencies (e.g., AuthenticatedPrincipal = Annotated[AuthContext, Depends(...)]) which are class-like parameter definitions, not false positives. | services/api/app/main.py#L83 |
| `C4|DEF` | false_pos | **no (overturn)** | The code in main.py:98 uses Depends(...) in Annotated[...], which is a valid dependency definition, not a false positive. | services/api/app/main.py#L98 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The require_scopes function in auth.py:40 uses Depends(bearer_scheme) in its signature, which is a valid DI occurrence. | services/api/app/auth.py#L40 |

### Missed by inventory (1)
- `Higher-order dependency functions (e.g., require_scopes)` @ services/api/app/auth.py#L32 — The inventory did not capture the require_scopes function, which dynamically generates dependencies via closure.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 11 | **known** | [services/api/app/main.py#L83](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/services/api/app/main.py#L83) |
| `C3|CLASS|BARE` | C3 | 11 | **false_pos** | [services/api/app/main.py#L83](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/services/api/app/main.py#L83) |
| `C4|DEF` | C4 | 4 | **false_pos** | [scripts/validate_package.py#L124](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/scripts/validate_package.py#L124) |
| `C1|BARE|SIG` | C1 | 2 | **false_pos** | [services/api/app/auth.py#L32](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/services/api/app/auth.py#L32) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 11 · corpus total: 18195 · executor: x86_64
> example: [services/api/app/main.py#L83](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/services/api/app/main.py#L83)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 11 · corpus total: 20139 · executor: x86_64
> example: [services/api/app/main.py#L83](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/services/api/app/main.py#L83)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [scripts/validate_package.py#L124](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/scripts/validate_package.py#L124)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 2 · corpus total: 83548 · executor: x86_64
> example: [services/api/app/auth.py#L32](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/services/api/app/auth.py#L32)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

