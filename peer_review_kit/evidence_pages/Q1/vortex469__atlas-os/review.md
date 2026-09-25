# vortex469/atlas-os

- GitHub: https://github.com/vortex469/atlas-os
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 74 · commit: `1371cd369c2d`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based Dependency Injection` | services/atlas-core/app/routes/delivery_enablement.py#L46 | The code uses FastAPI's `Depends` to inject dependencies (e.g., `_read` and `_create` functions) into route handlers. This follows the DI pattern by decoupling permission-checking logic from route ... |
| 2 | `FastAPI Depends-based Dependency Injection` | services/atlas-core/app/routes/installation.py#L51 | Similar to the first observation, `Depends(_read)` and `Depends(_mutate)` inject operator permission dependencies, demonstrating the same DI pattern for authentication/authorization logic. |
| 3 | `FastAPI Depends-based Dependency Injection` | services/atlas-core/app/routes/execution_candidates.py#L62 | The code uses `Depends(_require_intent_creation)` and `Depends(_require_intent_read)` to inject dependencies, again showing the DI pattern through FastAPI's dependency injection system. |

## Pass 2 — reconcile with inventory of vortex469/atlas-os

_Presented fingerprints:_ `C4|DEF`, `C3|CLASS|BARE`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_depends_di_1` | FastAPI Depends-based Dependency Injection | yes | The code explicitly uses FastAPI's `Depends` to inject permission-checking dependencies into route handlers, aligning with the observation. | services/atlas-core/app/routes/delivery_enablement.py#L46 |
| `fastapi_depends_di_2` | FastAPI Depends-based Dependency Injection | yes | The code uses `Depends(_read)` and `Depends(_mutate)` to inject operator permission dependencies, consistent with the observation. | services/atlas-core/app/routes/installation.py#L51 |
| `fastapi_depends_di_3` | FastAPI Depends-based Dependency Injection | yes | The code uses `Depends(_require_intent_creation)` and `Depends(_require_intent_read)` to inject dependencies, matching the observed pattern. | services/atlas-core/app/routes/execution_candidates.py#L62 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 28 | **false_pos** | [services/atlas-agent/app/main.py#L82](https://github.com/vortex469/atlas-os/blob/1371cd369c2dc416eae7b9d4bdac504700888935/services/atlas-agent/app/main.py#L82) |
| `C3|CLASS|BARE` | C3 | 24 | **false_pos** | [services/atlas-core/app/routes/delivery_activation_preflight.py#L45](https://github.com/vortex469/atlas-os/blob/1371cd369c2dc416eae7b9d4bdac504700888935/services/atlas-core/app/routes/delivery_activation_preflight.py#L45) |
| `C1|BARE|PARAM` | C1 | 22 | **known** | [services/atlas-core/app/routes/delivery_activation_preflight.py#L45](https://github.com/vortex469/atlas-os/blob/1371cd369c2dc416eae7b9d4bdac504700888935/services/atlas-core/app/routes/delivery_activation_preflight.py#L45) |

## `C4|DEF` — **false_pos**
> occurrences here: 28 · corpus total: 56644 · executor: x86_64
> example: [services/atlas-agent/app/main.py#L82](https://github.com/vortex469/atlas-os/blob/1371cd369c2dc416eae7b9d4bdac504700888935/services/atlas-agent/app/main.py#L82)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 24 · corpus total: 20139 · executor: x86_64
> example: [services/atlas-core/app/routes/delivery_activation_preflight.py#L45](https://github.com/vortex469/atlas-os/blob/1371cd369c2dc416eae7b9d4bdac504700888935/services/atlas-core/app/routes/delivery_activation_preflight.py#L45)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 22 · corpus total: 18195 · executor: x86_64
> example: [services/atlas-core/app/routes/delivery_activation_preflight.py#L45](https://github.com/vortex469/atlas-os/blob/1371cd369c2dc416eae7b9d4bdac504700888935/services/atlas-core/app/routes/delivery_activation_preflight.py#L45)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

