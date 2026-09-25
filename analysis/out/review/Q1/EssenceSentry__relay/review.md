# EssenceSentry/relay

- GitHub: https://github.com/EssenceSentry/relay
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 5 · commit: `6717ff7c6f1e`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends with Annotated` | services/api/app/auth.py#L162 | The `current_principal` function uses `Depends(_bearer)` within an `Annotated` type hint, indicating FastAPI dependency injection where `_bearer` is a resolved dependency. |
| 2 | `Container-based Dependency Injection` | services/api/app/routes.py#L132 | The `build_api_router` function accepts a `container: ServiceContainer` and uses `Depends(principal_dependency)` to inject dependencies, suggesting a custom container manages service resolution. |

## Pass 2 — reconcile with inventory of EssenceSentry/relay

_Presented fingerprints:_ `C1|BARE|PARAM`, `C3|ELLIPSIS|BARE`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | The `current_principal` function in auth.py:162 and routes.py:132 correctly uses FastAPI `Depends` within `Annotated` for dependency injection, aligning with the 'known' label. | services/api/app/auth.py#L162 |
| `C3|ELLIPSIS|BARE` | variant | **no (overturn)** | The code at auth.py:160 does not contain an ellipsis (`...`), but rather a union type (`HTTPAuthorizationCredentials | None`). The label 'variant' is incorrect as no ellipsis is present. | services/api/app/auth.py#L160 |
| `C4|DEF` | false_pos | **no (overturn)** | The `lifespan` function in main.py:44 is a valid FastAPI lifespan handler using `@asynccontextmanager`, not a false positive. The label 'false_pos' is incorrect. | services/api/app/main.py#L44 |

### Missed by inventory (1)
- `Container-based DI with `Depends(principal_dependency)`` @ services/api/app/routes.py#L132 — The use of a custom `ServiceContainer` and `Depends(principal_dependency)` in `build_api_router` was not captured by the initial inventory as a distinct DI pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 2 | **known** | [services/api/app/auth.py#L162](https://github.com/EssenceSentry/relay/blob/6717ff7c6f1e7bf80d0b8f891e0eea73cca83659/services/api/app/auth.py#L162) |
| `C3|ELLIPSIS|BARE` | C3 | 2 | **variant** | [services/api/app/auth.py#L160](https://github.com/EssenceSentry/relay/blob/6717ff7c6f1e7bf80d0b8f891e0eea73cca83659/services/api/app/auth.py#L160) |
| `C4|DEF` | C4 | 1 | **false_pos** | [services/api/app/main.py#L44](https://github.com/EssenceSentry/relay/blob/6717ff7c6f1e7bf80d0b8f891e0eea73cca83659/services/api/app/main.py#L44) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [services/api/app/auth.py#L162](https://github.com/EssenceSentry/relay/blob/6717ff7c6f1e7bf80d0b8f891e0eea73cca83659/services/api/app/auth.py#L162)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 2 · corpus total: 1113 · executor: x86_64
> example: [services/api/app/auth.py#L160](https://github.com/EssenceSentry/relay/blob/6717ff7c6f1e7bf80d0b8f891e0eea73cca83659/services/api/app/auth.py#L160)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [services/api/app/main.py#L44](https://github.com/EssenceSentry/relay/blob/6717ff7c6f1e7bf80d0b8f891e0eea73cca83659/services/api/app/main.py#L44)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

