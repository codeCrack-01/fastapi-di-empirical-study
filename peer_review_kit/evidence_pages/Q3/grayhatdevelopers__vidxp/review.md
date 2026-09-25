# grayhatdevelopers/vidxp

- GitHub: https://github.com/grayhatdevelopers/vidxp
- Stars: 20 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 216 · commit: `0a48ed812061`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=2 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection with context and security dependencies` | src/vidxp/api_routes/artifacts.py#L18 | Router defines dependencies=[Depends(read_principal)] for authentication, and endpoint parameters use Annotated[HttpApplicationContext, Depends(context)] to inject application context. |
| 2 | `Context-based service injection` | src/vidxp/api_routes/jobs.py#L71 | submit_index endpoint uses service: Annotated[HttpApplicationContext, Depends(context)] to inject context, and actor: Annotated[Principal, Depends(write_principal)] for authentication. |
| 3 | `Security dependency composition` | src/vidxp/api_routes/media.py#L93 | create_upload_intent uses Depends(write_principal) for authentication and injects context via service: Annotated[HttpApplicationContext, Depends(context)] to access uploads service. |

## Pass 2 — reconcile with inventory of grayhatdevelopers/vidxp

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`, `C2|BARE|ascopes`

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 112 | **false_pos** | [src/vidxp/api.py#L113](https://github.com/grayhatdevelopers/vidxp/blob/0a48ed8120615567e7dc2767a820b87fcfdb26cf/src/vidxp/api.py#L113) |
| `C1|BARE|PARAM` | C1 | 81 | **known** | [src/vidxp/api.py#L113](https://github.com/grayhatdevelopers/vidxp/blob/0a48ed8120615567e7dc2767a820b87fcfdb26cf/src/vidxp/api.py#L113) |
| `C4|DEF` | C4 | 22 | **false_pos** | [src/vidxp/api.py#L67](https://github.com/grayhatdevelopers/vidxp/blob/0a48ed8120615567e7dc2767a820b87fcfdb26cf/src/vidxp/api.py#L67) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [src/vidxp/api.py#L124](https://github.com/grayhatdevelopers/vidxp/blob/0a48ed8120615567e7dc2767a820b87fcfdb26cf/src/vidxp/api.py#L124) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 112 · corpus total: 20139 · executor: x86_64
> example: [src/vidxp/api.py#L113](https://github.com/grayhatdevelopers/vidxp/blob/0a48ed8120615567e7dc2767a820b87fcfdb26cf/src/vidxp/api.py#L113)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 81 · corpus total: 18195 · executor: x86_64
> example: [src/vidxp/api.py#L113](https://github.com/grayhatdevelopers/vidxp/blob/0a48ed8120615567e7dc2767a820b87fcfdb26cf/src/vidxp/api.py#L113)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 22 · corpus total: 56644 · executor: x86_64
> example: [src/vidxp/api.py#L67](https://github.com/grayhatdevelopers/vidxp/blob/0a48ed8120615567e7dc2767a820b87fcfdb26cf/src/vidxp/api.py#L67)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [src/vidxp/api.py#L124](https://github.com/grayhatdevelopers/vidxp/blob/0a48ed8120615567e7dc2767a820b87fcfdb26cf/src/vidxp/api.py#L124)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

