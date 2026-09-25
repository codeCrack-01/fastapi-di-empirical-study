# georgejieh/REED

- GitHub: https://github.com/georgejieh/REED
- Stars: 6 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 40 · commit: `1991e94aad74`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=1 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection with explicit provider functions` | backend/app/api/admin.py#L61 | The run_manually function uses Depends(get_pipeline), Depends(get_repository), and Depends(get_settings_store) to inject dependencies. This is the core FastAPI pattern where dependencies are resolv... |
| 2 | `Annotated dependency wrappers` | backend/app/api/admin.py#L25 | MutationAuth is defined as Annotated[None, Depends(require_mutation_auth)], showing use of Annotated to wrap dependencies for type hinting while maintaining injection |
| 3 | `Multiple dependency injection in single endpoint` | backend/app/api/wizard.py#L185 | configure_provider injects 6 dependencies via Depends() including get_settings_store, get_secret_store, get_source_catalog, get_url_policy, and get_runtime_settings, demonstrating complex dependenc... |

## Pass 2 — reconcile with inventory of georgejieh/REED

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C3|ELLIPSIS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses Depends() with provider functions (get_pipeline, get_repository, get_settings_store) which matches the canonical C1|BARE|SIG pattern | backend/app/api/admin.py#L61 |
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly implements context managers for database connections and transactions, which matches the C4|DEF pattern | backend/app/db/connection.py#L15 |
| `C1|BARE|PARAM` | known | yes | Annotated[None, Depends(...)] is correctly used for parameterized dependencies | backend/app/api/admin.py#L25 |
| `C3|ELLIPSIS|BARE` | variant | yes | The use of Annotated with Depends(...) represents a valid variant of the BARE pattern | backend/app/api/wizard.py#L35 |

### Missed by inventory (1)
- `Multiple nested Depends() in single endpoint` @ backend/app/api/wizard.py#L185 — The configure_provider endpoint uses 6 nested Depends() calls which represents a complex DI pattern not captured in the inventory

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 30 | **false_pos** | [backend/app/api/admin.py#L61](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/api/admin.py#L61) |
| `C4|DEF` | C4 | 4 | **false_pos** | [backend/app/db/connection.py#L15](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/db/connection.py#L15) |
| `C1|BARE|PARAM` | C1 | 3 | **known** | [backend/app/api/admin.py#L25](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/api/admin.py#L25) |
| `C3|ELLIPSIS|BARE` | C3 | 3 | **variant** | [backend/app/api/admin.py#L25](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/api/admin.py#L25) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 30 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/admin.py#L61](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/api/admin.py#L61)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [backend/app/db/connection.py#L15](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/db/connection.py#L15)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 3 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/admin.py#L25](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/api/admin.py#L25)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 3 · corpus total: 1113 · executor: x86_64
> example: [backend/app/api/admin.py#L25](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/api/admin.py#L25)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

