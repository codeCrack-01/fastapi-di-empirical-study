# verticalpartnersai-sketch/haz-que-vuelva-lw-dr

- GitHub: https://github.com/verticalpartnersai-sketch/haz-que-vuelva-lw-dr
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 19 · commit: `62037c42f5cf`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI standard dependency injection` | apps/agent/app/api/routes.py#L28 | Uses Depends(generation_service) and Depends(get_settings) for injecting GenerationService and Settings into the stream_generation endpoint, which is the standard FastAPI pattern for dependency inj... |
| 2 | `Nested dependency injection` | apps/agent/app/core/security.py#L10 | The require_internal_request function itself uses Depends(get_settings) to inject Settings, showing that dependencies can be injected into other dependency functions. |
| 3 | `Route-level dependency injection` | apps/agent/app/api/routes.py#L28 | The /v1/generations/stream route explicitly declares Depends(require_internal_request) in its dependencies list, demonstrating route-level security checks via dependency injection. |

## Pass 2 — reconcile with inventory of verticalpartnersai-sketch/haz-que-vuelva-lw-dr

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code uses standard FastAPI dependency injection with Depends(), not bare classes. The parameters in stream_generation() and create_diagnostic() correctly use Annotated[...] with Depends(...). | apps/agent/app/api/routes.py#L28 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses Annotated[...] with Depends(...) for parameters, matching the 'known' label for this fingerprint. | apps/agent/app/api/routes.py#L28 |
| `C4|DEF` | true_pos | **no (overturn)** | The code defines valid async methods (e.g., stream() in service.py) and context managers (lifespan in main.py), which are legitimate definitions, contradicting the 'false_pos' label. | apps/agent/app/generation/service.py#L47 |

### Missed by inventory (1)
- `Route-level security checks via Depends(require_internal_request)` @ apps/agent/app/api/routes.py#L28 — The inventory did not explicitly capture the use of route-level security checks with Depends(...) in the route definition, which is a distinct pattern from parameter-level DI.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 10 | **false_pos** | [apps/agent/app/api/routes.py#L28](https://github.com/verticalpartnersai-sketch/haz-que-vuelva-lw-dr/blob/62037c42f5cf5b4a3286231786dbafe28ce66354/apps/agent/app/api/routes.py#L28) |
| `C1|BARE|PARAM` | C1 | 7 | **known** | [apps/agent/app/api/routes.py#L28](https://github.com/verticalpartnersai-sketch/haz-que-vuelva-lw-dr/blob/62037c42f5cf5b4a3286231786dbafe28ce66354/apps/agent/app/api/routes.py#L28) |
| `C4|DEF` | C4 | 2 | **false_pos** | [apps/agent/app/generation/service.py#L47](https://github.com/verticalpartnersai-sketch/haz-que-vuelva-lw-dr/blob/62037c42f5cf5b4a3286231786dbafe28ce66354/apps/agent/app/generation/service.py#L47) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 10 · corpus total: 20139 · executor: x86_64
> example: [apps/agent/app/api/routes.py#L28](https://github.com/verticalpartnersai-sketch/haz-que-vuelva-lw-dr/blob/62037c42f5cf5b4a3286231786dbafe28ce66354/apps/agent/app/api/routes.py#L28)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 7 · corpus total: 18195 · executor: x86_64
> example: [apps/agent/app/api/routes.py#L28](https://github.com/verticalpartnersai-sketch/haz-que-vuelva-lw-dr/blob/62037c42f5cf5b4a3286231786dbafe28ce66354/apps/agent/app/api/routes.py#L28)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [apps/agent/app/generation/service.py#L47](https://github.com/verticalpartnersai-sketch/haz-que-vuelva-lw-dr/blob/62037c42f5cf5b4a3286231786dbafe28ce66354/apps/agent/app/generation/service.py#L47)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

