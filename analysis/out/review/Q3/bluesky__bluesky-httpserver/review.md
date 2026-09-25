# bluesky/bluesky-httpserver

- GitHub: https://github.com/bluesky/bluesky-httpserver
- Stars: 19 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 137 · commit: `a8093be87a8d`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=1 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based DI` | src/bluesky_httpserver/authentication.py#L231 | The function get_decoded_access_token uses Depends(oauth2_scheme) and Depends(get_settings) to inject authentication schemes and configuration settings. |
| 2 | `FastAPI Depends-based DI` | src/bluesky_httpserver/authentication.py#L262 | The function get_current_principal uses multiple Depends() calls (e.g., Depends(get_decoded_access_token), Depends(get_api_key), Depends(get_settings)) to inject authentication-related dependencies. |
| 3 | `FastAPI Depends-based DI` | src/bluesky_httpserver/routers/core_api.py#L193 | The function queue_item_add_handler uses Depends(get_current_principal) for authentication and Depends(get_api_access_manager) for resource access control. |

## Pass 2 — reconcile with inventory of bluesky/bluesky-httpserver

_Presented fingerprints:_ `C2|BARE|ascopes`, `C1|BARE|SIG`, `C4|DEF`, `C1|EMPTY|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `FastAPI_Depends_based_DI_authentication_py_231` | FastAPI Depends-based DI @ src/bluesky_httpserver/authentication.py:231 | yes | The function get_decoded_access_token uses Depends(oauth2_scheme) and Depends(get_settings) as observed. | src/bluesky_httpserver/authentication.py#L231 |
| `FastAPI_Depends_based_DI_authentication_py_262` | FastAPI Depends-based DI @ src/bluesky_httpserver/authentication.py:262 | yes | The function get_current_principal uses Depends(get_decoded_access_token), Depends(get_api_key), and Depends(get_settings) as observed. | src/bluesky_httpserver/authentication.py#L262 |
| `FastAPI_Depends_based_DI_core_api_py_193` | FastAPI Depends-based DI @ src/bluesky_httpserver/routers/core_api.py:193 | yes | The function queue_item_add_handler uses Depends(get_current_principal), Depends(get_api_access_manager), and Depends(get_resource_access_manager) as observed. | src/bluesky_httpserver/routers/core_api.py#L193 |

### Missed by inventory (3)
- `Other instances of Depends in core_api.py endpoints` @ src/bluesky_httpserver/routers/core_api.py#L223 — The queue_item_execute_handler also uses Depends(get_current_principal) and other managers but was not mentioned in initial observations.
- `Other instances of Depends in core_api.py endpoints` @ src/bluesky_httpserver/routers/core_api.py#L252 — The queue_item_add_batch_handler uses Depends(get_current_principal) and other managers but was not mentioned in initial observations.
- `Other instances of Depends in core_api.py endpoints` @ src/bluesky_httpserver/routers/core_api.py#L394 — The queue_item_update_handler uses Depends(get_current_principal) and other managers but was not mentioned in initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C2|BARE|ascopes` | C2 | 69 | **known** | [src/bluesky_httpserver/authentication.py#L204](https://github.com/bluesky/bluesky-httpserver/blob/a8093be87a8dddca6175b12c64b59581cf5a97fb/src/bluesky_httpserver/authentication.py#L204) |
| `C1|BARE|SIG` | C1 | 59 | **false_pos** | [src/bluesky_httpserver/authentication.py#L231](https://github.com/bluesky/bluesky-httpserver/blob/a8093be87a8dddca6175b12c64b59581cf5a97fb/src/bluesky_httpserver/authentication.py#L231) |
| `C4|DEF` | C4 | 8 | **false_pos** | [src/bluesky_httpserver/console_output.py#L175](https://github.com/bluesky/bluesky-httpserver/blob/a8093be87a8dddca6175b12c64b59581cf5a97fb/src/bluesky_httpserver/console_output.py#L175) |
| `C1|EMPTY|SIG` | C1 | 1 | **variant** | [src/bluesky_httpserver/authentication.py#L669](https://github.com/bluesky/bluesky-httpserver/blob/a8093be87a8dddca6175b12c64b59581cf5a97fb/src/bluesky_httpserver/authentication.py#L669) |

## `C2|BARE|ascopes` — **known**
> occurrences here: 69 · corpus total: 504 · executor: x86_64
> example: [src/bluesky_httpserver/authentication.py#L204](https://github.com/bluesky/bluesky-httpserver/blob/a8093be87a8dddca6175b12c64b59581cf5a97fb/src/bluesky_httpserver/authentication.py#L204)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 59 · corpus total: 83548 · executor: x86_64
> example: [src/bluesky_httpserver/authentication.py#L231](https://github.com/bluesky/bluesky-httpserver/blob/a8093be87a8dddca6175b12c64b59581cf5a97fb/src/bluesky_httpserver/authentication.py#L231)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 8 · corpus total: 56644 · executor: x86_64
> example: [src/bluesky_httpserver/console_output.py#L175](https://github.com/bluesky/bluesky-httpserver/blob/a8093be87a8dddca6175b12c64b59581cf5a97fb/src/bluesky_httpserver/console_output.py#L175)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 1 · corpus total: 254 · executor: x86_64
> example: [src/bluesky_httpserver/authentication.py#L669](https://github.com/bluesky/bluesky-httpserver/blob/a8093be87a8dddca6175b12c64b59581cf5a97fb/src/bluesky_httpserver/authentication.py#L669)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

