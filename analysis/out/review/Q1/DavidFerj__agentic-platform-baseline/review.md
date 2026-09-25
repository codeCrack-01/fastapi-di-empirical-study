# DavidFerj/agentic-platform-baseline

- GitHub: https://github.com/DavidFerj/agentic-platform-baseline
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 9 · commit: `4c6cba09eb62`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends with Annotated` | gcp/services/control-plane/src/platform_api/api/routes/health.py#L28 | The `database` parameter uses `Depends(get_database)` within an `Annotated` type to inject a dependency. |
| 2 | `FastAPI Depends with Annotated` | gcp/services/control-plane/src/platform_api/api/routes/platform.py#L16 | The `settings` parameter uses `Depends(get_settings)` within an `Annotated` type to inject a dependency. |
| 3 | `Manual DI via function parameters` | gcp/services/control-plane/src/platform_api/api/app.py#L19 | The `create_app` function accepts `settings` and `database` as explicit parameters, allowing replacement of dependencies. |
| 4 | `Test DI with mocks` | gcp/services/control-plane/tests/conftest.py#L43 | The `client` fixture injects a `fake_database` into `create_app`, demonstrating DI in testing. |

## Pass 2 — reconcile with inventory of DavidFerj/agentic-platform-baseline

_Presented fingerprints:_ `C3|CLASS|BARE`, `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | known | **no (overturn)** | The code explicitly uses FastAPI's `Depends` within `Annotated` for dependency injection, which matches the fingerprint's structural pattern. | gcp/services/control-plane/src/platform_api/api/routes/health.py#L28 |
| `C4|DEF` | known | **no (overturn)** | The `create_app` function and test fixture demonstrate explicit parameter-based DI, which aligns with the fingerprint's structural pattern. | gcp/services/control-plane/src/platform_api/api/app.py#L19 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses `Annotated` with `Depends` for parameterized DI, matching the fingerprint's classification. | gcp/services/control-plane/src/platform_api/api/routes/platform.py#L16 |

### Missed by inventory (2)
- `Manual DI via function parameters` @ gcp/services/control-plane/src/platform_api/api/app.py#L19 — The `create_app` function explicitly accepts `settings` and `database` as replaceable dependencies, a DI pattern not captured by existing fingerprints.
- `Test DI with mocks` @ gcp/services/control-plane/tests/conftest.py#L43 — The `client` fixture injects a `fake_database` into `create_app`, demonstrating DI in testing, which was not inventoried.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 4 | **false_pos** | [gcp/services/control-plane/src/platform_api/api/routes/health.py#L28](https://github.com/DavidFerj/agentic-platform-baseline/blob/4c6cba09eb62031d03bb510288726012431d696d/gcp/services/control-plane/src/platform_api/api/routes/health.py#L28) |
| `C4|DEF` | C4 | 3 | **false_pos** | [gcp/services/control-plane/src/platform_api/api/app.py#L37](https://github.com/DavidFerj/agentic-platform-baseline/blob/4c6cba09eb62031d03bb510288726012431d696d/gcp/services/control-plane/src/platform_api/api/app.py#L37) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [gcp/services/control-plane/src/platform_api/api/routes/health.py#L28](https://github.com/DavidFerj/agentic-platform-baseline/blob/4c6cba09eb62031d03bb510288726012431d696d/gcp/services/control-plane/src/platform_api/api/routes/health.py#L28) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 4 · corpus total: 20139 · executor: x86_64
> example: [gcp/services/control-plane/src/platform_api/api/routes/health.py#L28](https://github.com/DavidFerj/agentic-platform-baseline/blob/4c6cba09eb62031d03bb510288726012431d696d/gcp/services/control-plane/src/platform_api/api/routes/health.py#L28)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [gcp/services/control-plane/src/platform_api/api/app.py#L37](https://github.com/DavidFerj/agentic-platform-baseline/blob/4c6cba09eb62031d03bb510288726012431d696d/gcp/services/control-plane/src/platform_api/api/app.py#L37)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [gcp/services/control-plane/src/platform_api/api/routes/health.py#L28](https://github.com/DavidFerj/agentic-platform-baseline/blob/4c6cba09eb62031d03bb510288726012431d696d/gcp/services/control-plane/src/platform_api/api/routes/health.py#L28)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

