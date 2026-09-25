# d4551/pekka

- GitHub: https://github.com/d4551/pekka
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 10 · commit: `3be2afa207e4`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends usage` | packages/hermes-gateway/src/hermes_gateway/integration_routes.py#L35 | The line CONTROL_PLANE_SESSION_DEPENDENCY = Depends(control_plane_session) explicitly uses FastAPI's Depends constructor to create a dependency injection token. This is a classic FastAPI pattern fo... |

## Pass 2 — reconcile with inventory of d4551/pekka

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code in the cited lines does not use FastAPI's Depends constructor, confirming the label as false positives. | packages/hermes-gateway/src/hermes_gateway/pipes/base.py#L41 |
| `C1|BARE|PARAM` | known | yes | The line explicitly uses FastAPI's Depends constructor, confirming the label as a known occurrence. | packages/hermes-gateway/src/hermes_gateway/integration_routes.py#L35 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 9 | **false_pos** | [packages/hermes-gateway/src/hermes_gateway/pipes/base.py#L41](https://github.com/d4551/pekka/blob/3be2afa207e4ab7b5125cca6470bca92f4bf39d2/packages/hermes-gateway/src/hermes_gateway/pipes/base.py#L41) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [packages/hermes-gateway/src/hermes_gateway/integration_routes.py#L35](https://github.com/d4551/pekka/blob/3be2afa207e4ab7b5125cca6470bca92f4bf39d2/packages/hermes-gateway/src/hermes_gateway/integration_routes.py#L35) |

## `C4|DEF` — **false_pos**
> occurrences here: 9 · corpus total: 56644 · executor: x86_64
> example: [packages/hermes-gateway/src/hermes_gateway/pipes/base.py#L41](https://github.com/d4551/pekka/blob/3be2afa207e4ab7b5125cca6470bca92f4bf39d2/packages/hermes-gateway/src/hermes_gateway/pipes/base.py#L41)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [packages/hermes-gateway/src/hermes_gateway/integration_routes.py#L35](https://github.com/d4551/pekka/blob/3be2afa207e4ab7b5125cca6470bca92f4bf39d2/packages/hermes-gateway/src/hermes_gateway/integration_routes.py#L35)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

