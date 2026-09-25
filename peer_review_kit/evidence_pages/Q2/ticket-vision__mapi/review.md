# ticket-vision/mapi

- GitHub: https://github.com/ticket-vision/mapi
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 19 · commit: `b161d0654ec1`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L48 | The `service` parameter uses `Depends(get_ticketmaster_discovery_service)` to inject a dependency, which is FastAPI's standard DI pattern. |
| 2 | `FastAPI Depends injection` | src/mapi/api/v1/endpoints/ticketmaster_enrichment.py#L38 | The `service` parameter in `get_event_map_summary` uses `Depends(get_ticketmaster_enrichment_service)` for dependency injection. |
| 3 | `FastAPI Depends injection` | src/mapi/api/v1/endpoints/ticketmaster_maps.py#L24 | The `service` parameter in `get_place_detail` uses `Depends(get_ticketmaster_maps_service)` to inject a dependency. |

## Pass 2 — reconcile with inventory of ticket-vision/mapi

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends()` for dependency injection (e.g., `service: Annotated[...] = Depends(...)` in `get_events`, `get_legacy_event_ids`, and `get_metadata` endpoints). These... | src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L48 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses FastAPI's parameter injection (e.g., `country_code: Annotated[...] = Query(...)`, `format: Literal[...]`, and `limit: Annotated[...] = Query(...)` in multiple endpoints). Th... | src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L48 |
| `C4|DEF` | true_pos | **no (overturn)** | The `lifespan` context manager in `src/mapi/core/state.py` uses FastAPI's ASGI lifespan management, which is a form of dependency injection for application state. This contradicts the 'false_pos' l... | src/mapi/core/state.py#L10 |

### Missed by inventory (2)
- `FastAPI Depends injection in `ticketmaster_enrichment.py`` @ src/mapi/api/v1/endpoints/ticketmaster_enrichment.py#L38 — The `get_event_map_summary` and `get_sample_map_summaries` endpoints use `Depends(get_ticketmaster_enrichment_service)` for dependency injection, which was not captured in the initial fingerprint i...
- `FastAPI Depends injection in `ticketmaster_maps.py`` @ src/mapi/api/v1/endpoints/ticketmaster_maps.py#L24 — The `get_place_detail` endpoint uses `Depends(get_ticketmaster_maps_service)` for dependency injection, which was not captured in the initial fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 12 | **false_pos** | [src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L46](https://github.com/ticket-vision/mapi/blob/b161d0654ec1f82fef72496690c553079291bb4e/src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L46) |
| `C1|BARE|PARAM` | C1 | 6 | **known** | [src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L48](https://github.com/ticket-vision/mapi/blob/b161d0654ec1f82fef72496690c553079291bb4e/src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L48) |
| `C4|DEF` | C4 | 1 | **false_pos** | [src/mapi/core/state.py#L10](https://github.com/ticket-vision/mapi/blob/b161d0654ec1f82fef72496690c553079291bb4e/src/mapi/core/state.py#L10) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 12 · corpus total: 20139 · executor: x86_64
> example: [src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L46](https://github.com/ticket-vision/mapi/blob/b161d0654ec1f82fef72496690c553079291bb4e/src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L46)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 6 · corpus total: 18195 · executor: x86_64
> example: [src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L48](https://github.com/ticket-vision/mapi/blob/b161d0654ec1f82fef72496690c553079291bb4e/src/mapi/api/v1/endpoints/ticketmaster_discovery.py#L48)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [src/mapi/core/state.py#L10](https://github.com/ticket-vision/mapi/blob/b161d0654ec1f82fef72496690c553079291bb4e/src/mapi/core/state.py#L10)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

