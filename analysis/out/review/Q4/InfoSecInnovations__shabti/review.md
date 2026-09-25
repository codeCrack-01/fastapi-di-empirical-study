# InfoSecInnovations/shabti

- GitHub: https://github.com/InfoSecInnovations/shabti
- Stars: 197 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 81 · commit: `c1c65aef1f5e`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection with router-level and parameter-level dependencies` | docker_containers/shabti_api/src/app/secure_routes.py#L51 | The 'valid_access_token' function is defined as a dependency using 'Depends(oauth_2_scheme)' and is later used as a router-level dependency via 'APIRouter(dependencies=[Depends(valid_access_token)]... |
| 2 | `Reused dependency across multiple routes` | docker_containers/shabti_api/src/app/secure_routes.py#L61 | The 'valid_access_token' dependency is applied to multiple routes (e.g., get_collections_route, create_collection_route, delete_collection_route) both via router-level dependencies and as explicit ... |

## Pass 2 — reconcile with inventory of InfoSecInnovations/shabti

_Presented fingerprints:_ `C4|DEF`, `C3|BARE|BARE`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_positive | **no (overturn)** | The 'token' parameter in insert_document is part of an actual authentication workflow (e.g., passed to get_collection_info and used in logging_enabled()), contradicting the false_pos label. | docker_containers/shabti_api/src/app/ingesting.py#L11 |
| `C3|BARE|BARE` | standard_usage | **no (overturn)** | The code uses FastAPI's standard DI pattern with router-level and parameter-level dependencies, not a variant. | docker_containers/shabti_api/src/app/secure_routes.py#L51 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses Annotated[...] with Depends(...) as a parameter, aligning with the known label. | docker_containers/shabti_api/src/app/secure_routes.py#L61 |

### Missed by inventory (2)
- `Router-level and parameter-level dependency reuse` @ docker_containers/shabti_api/src/app/secure_routes.py#L51 — The inventory did not capture the combination of router-level and parameter-level dependency injection for 'valid_access_token'.
- `Token parameter in authentication workflow` @ docker_containers/shabti_api/src/app/ingesting.py#L11 — The inventory missed the token parameter's role in authentication, which is critical for DI validation.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 38 | **false_pos** | [docker_containers/shabti_api/src/app/ingesting.py#L11](https://github.com/InfoSecInnovations/shabti/blob/c1c65aef1f5ea0e4be4379a3a2b225e97f20f5cb/docker_containers/shabti_api/src/app/ingesting.py#L11) |
| `C3|BARE|BARE` | C3 | 28 | **variant** | [docker_containers/shabti_api/src/app/secure_routes.py#L51](https://github.com/InfoSecInnovations/shabti/blob/c1c65aef1f5ea0e4be4379a3a2b225e97f20f5cb/docker_containers/shabti_api/src/app/secure_routes.py#L51) |
| `C1|BARE|PARAM` | C1 | 15 | **known** | [docker_containers/shabti_api/src/app/secure_routes.py#L51](https://github.com/InfoSecInnovations/shabti/blob/c1c65aef1f5ea0e4be4379a3a2b225e97f20f5cb/docker_containers/shabti_api/src/app/secure_routes.py#L51) |

## `C4|DEF` — **false_pos**
> occurrences here: 38 · corpus total: 56644 · executor: x86_64
> example: [docker_containers/shabti_api/src/app/ingesting.py#L11](https://github.com/InfoSecInnovations/shabti/blob/c1c65aef1f5ea0e4be4379a3a2b225e97f20f5cb/docker_containers/shabti_api/src/app/ingesting.py#L11)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|BARE|BARE` — **variant**
> occurrences here: 28 · corpus total: 1316 · executor: x86_64
> example: [docker_containers/shabti_api/src/app/secure_routes.py#L51](https://github.com/InfoSecInnovations/shabti/blob/c1c65aef1f5ea0e4be4379a3a2b225e97f20f5cb/docker_containers/shabti_api/src/app/secure_routes.py#L51)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C1|BARE|PARAM` — **known**
> occurrences here: 15 · corpus total: 18195 · executor: x86_64
> example: [docker_containers/shabti_api/src/app/secure_routes.py#L51](https://github.com/InfoSecInnovations/shabti/blob/c1c65aef1f5ea0e4be4379a3a2b225e97f20f5cb/docker_containers/shabti_api/src/app/secure_routes.py#L51)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

