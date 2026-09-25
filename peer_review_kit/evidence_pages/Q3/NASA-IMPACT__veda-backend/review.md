# NASA-IMPACT/veda-backend

- GitHub: https://github.com/NASA-IMPACT/veda-backend
- Stars: 21 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 41 · commit: `32273eb09e60`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=3 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection` | ingest_api/runtime/src/dependencies.py#L18 | The function `get_db` uses `Depends(get_table)` to inject a dependency, demonstrating FastAPI's DI mechanism where dependencies are resolved at runtime. |
| 2 | `Nested Dependency Injection` | ingest_api/runtime/src/dependencies.py#L24 | The `fetch_ingestion` function injects multiple dependencies via `Depends(get_db)` and `Depends(get_username)`, showing nested DI where one dependency (e.g., `get_db`) itself depends on another (`g... |
| 3 | `Security-Scoped Dependencies` | ingest_api/runtime/src/main.py#L68 | The route decorator uses `Security(oidc_auth.valid_token_dependency, scopes=...)`, injecting a security-scoped dependency for authentication/authorization. |
| 4 | `Annotated Dependency Injection` | ingest_api/runtime/src/auth.py#L16 | The parameter `token` is annotated with `Annotated[Dict[Any, Any], Depends(...)]`, using FastAPI's newer syntax for explicit DI with type hints. |

## Pass 2 — reconcile with inventory of NASA-IMPACT/veda-backend

_Presented fingerprints:_ `C4|DEF`, `C1|DOTTED|SIG`, `C2|ELLIPSIS|ascopes`, `C1|BARE|SIG`, `C3|ELLIPSIS|DOTTED`, `C1|DOTTED|PARAM`, `C1|EMPTY|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No DI occurrence found in the cited code; the function `get_queued_ingestions` does not use FastAPI DI mechanisms. | ingest_api/runtime/src/ingestor.py#L20 |
| `C1|DOTTED|SIG` | false_pos | **no (overturn)** | The code correctly uses `Security(..., scopes=...)` for scoped authentication, which is a valid DI occurrence. | ingest_api/runtime/src/main.py#L68 |
| `C2|ELLIPSIS|ascopes` | variant | yes | The code uses `required_scopes: security.SecurityScopes` (dotted notation), aligning with the 'variant' label. | common/auth/veda_auth/main.py#L36 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code uses `Depends(get_table)` in `get_db`, a valid DI occurrence. | ingest_api/runtime/src/dependencies.py#L18 |
| `C3|ELLIPSIS|DOTTED` | known | yes | The code uses `Annotated[Dict[Any, Any], Depends(...)]`, a known DI pattern. | common/auth/veda_auth/main.py#L70 |
| `C1|DOTTED|PARAM` | variant | yes | The code uses `Annotated[...]` with `Depends(...)`, consistent with the 'variant' label. | ingest_api/runtime/src/auth.py#L16 |
| `C1|EMPTY|SIG` | variant | **no (overturn)** | The cited line (44) does not contain DI; the actual DI occurs in line 68 with `Security(..., scopes=...)`. | ingest_api/runtime/src/main.py#L68 |

### Missed by inventory (2)
- `Annotated[...] with Depends(...) in auth.py:16` @ ingest_api/runtime/src/auth.py#L16 — The static inventory may have missed this explicit DI usage with `Annotated`.
- `Security-scoped dependencies in main.py:68` @ ingest_api/runtime/src/main.py#L68 — The static inventory may have misclassified this as false_pos instead of recognizing it as a valid DI occurrence.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 14 | **false_pos** | [ingest_api/runtime/src/ingestor.py#L20](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/ingest_api/runtime/src/ingestor.py#L20) |
| `C1|DOTTED|SIG` | C1 | 10 | **false_pos** | [ingest_api/runtime/src/main.py#L45](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/ingest_api/runtime/src/main.py#L45) |
| `C2|ELLIPSIS|ascopes` | C2 | 6 | **variant** | [common/auth/veda_auth/main.py#L36](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/common/auth/veda_auth/main.py#L36) |
| `C1|BARE|SIG` | C1 | 4 | **false_pos** | [ingest_api/runtime/src/dependencies.py#L18](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/ingest_api/runtime/src/dependencies.py#L18) |
| `C3|ELLIPSIS|DOTTED` | C3 | 4 | **known** | [common/auth/veda_auth/main.py#L70](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/common/auth/veda_auth/main.py#L70) |
| `C1|DOTTED|PARAM` | C1 | 2 | **variant** | [common/auth/veda_auth/main.py#L70](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/common/auth/veda_auth/main.py#L70) |
| `C1|EMPTY|SIG` | C1 | 1 | **variant** | [ingest_api/runtime/src/main.py#L44](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/ingest_api/runtime/src/main.py#L44) |

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [ingest_api/runtime/src/ingestor.py#L20](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/ingest_api/runtime/src/ingestor.py#L20)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|DOTTED|SIG` — **false_pos**
> occurrences here: 10 · corpus total: 2178 · executor: x86_64
> example: [ingest_api/runtime/src/main.py#L45](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/ingest_api/runtime/src/main.py#L45)
> **rule:** C1

> **evidence (model):** Parameters use dotted names (core.current_principal) but are not wrapped in Depends/Security calls, indicating standard function parameters rather than FastAPI DI dependencies

## `C2|ELLIPSIS|ascopes` — **variant**
> occurrences here: 6 · corpus total: 116 · executor: x86_64
> example: [common/auth/veda_auth/main.py#L36](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/common/auth/veda_auth/main.py#L36)
> **rule:** C2

> **evidence (model):** The use of ellipsis (...) in Security dependencies (e.g., Security(...)) is a structural variation of the standard C2 pattern (Security(...) with scopes).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 4 · corpus total: 83548 · executor: x86_64
> example: [ingest_api/runtime/src/dependencies.py#L18](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/ingest_api/runtime/src/dependencies.py#L18)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C3|ELLIPSIS|DOTTED` — **known**
> occurrences here: 4 · corpus total: 8 · executor: x86_64
> example: [common/auth/veda_auth/main.py#L70](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/common/auth/veda_auth/main.py#L70)
> **rule:** C3

> **evidence (model):** Annotated[Type, ...] metadata with ellipsis placeholder matches C3's pattern of Annotated[Type, Depends(...)] type metadata

## `C1|DOTTED|PARAM` — **variant**
> occurrences here: 2 · corpus total: 422 · executor: x86_64
> example: [common/auth/veda_auth/main.py#L70](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/common/auth/veda_auth/main.py#L70)
> **rule:** C1

> **evidence (model):** Dotted paths (e.g., 'deps.db') used as dependencies in parameters, which is a structural variation of C1 (Depends call arguments) but not the standard bare function reference.

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 1 · corpus total: 254 · executor: x86_64
> example: [ingest_api/runtime/src/main.py#L44](https://github.com/NASA-IMPACT/veda-backend/blob/32273eb09e60e5af7f68c779d60c06a9372f7270/ingest_api/runtime/src/main.py#L44)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

