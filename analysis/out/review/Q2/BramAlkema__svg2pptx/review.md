# BramAlkema/svg2pptx

- GitHub: https://github.com/BramAlkema/svg2pptx
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 86 · commit: `b582bac1b85b`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=2 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Annotated Type Aliases` | api/dependencies.py#L56 | The code defines AnalyzerDep and ValidatorDep as Annotated type aliases with Depends(get_analyzer) and Depends(get_validator), showing FastAPI's DI pattern where dependencies are injected via the D... |
| 2 | `FastAPI Dependency Injection for Authentication` | api/main.py#L84 | The convert_svg_to_drive endpoint uses current_user: dict = Depends(get_current_user) to inject authentication information, demonstrating FastAPI's DI system for handling user authentication across... |
| 3 | `Reused Dependency Aliases in Route Handlers` | api/routes/analysis.py#L62 | The analyze_svg route uses analyzer: AnalyzerDep = None, referencing the AnalyzerDep type alias defined in dependencies.py. This shows centralized dependency management through type aliases. |

## Pass 2 — reconcile with inventory of BramAlkema/svg2pptx

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C2|BARE|ascopes`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code correctly uses context managers in apply_lazy and apply_stream without DI issues. | archive/legacy-src/converters/filters/core/chain.py#L232 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code correctly uses Depends(get_current_user) for authentication injection. | api/main.py#L84 |
| `C1|BARE|PARAM` | known | yes | AnalyzerDep and ValidatorDep are properly defined as annotated type aliases with Depends. | api/dependencies.py#L56 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | Annotated[SVGAnalyzerAPI, Depends(...)] correctly represents class-based dependency injection. | api/dependencies.py#L56 |
| `C2|BARE|ascopes` | known | yes | Depends(security) is properly used in the authentication scheme. | api/auth.py#L89 |

### Missed by inventory (1)
- `Reused dependency aliases in route handlers` @ api/routes/analysis.py#L62 — The inventory did not explicitly note the usage of AnalyzerDep in route handlers, though it was mentioned in pass1 observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 62 | **false_pos** | [archive/legacy-src/converters/filters/core/chain.py#L232](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/archive/legacy-src/converters/filters/core/chain.py#L232) |
| `C1|BARE|SIG` | C1 | 19 | **false_pos** | [api/main.py#L84](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/api/main.py#L84) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [api/dependencies.py#L56](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/api/dependencies.py#L56) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [api/dependencies.py#L56](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/api/dependencies.py#L56) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [api/auth.py#L89](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/api/auth.py#L89) |

## `C4|DEF` — **false_pos**
> occurrences here: 62 · corpus total: 56644 · executor: x86_64
> example: [archive/legacy-src/converters/filters/core/chain.py#L232](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/archive/legacy-src/converters/filters/core/chain.py#L232)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 19 · corpus total: 83548 · executor: x86_64
> example: [api/main.py#L84](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/api/main.py#L84)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [api/dependencies.py#L56](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/api/dependencies.py#L56)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [api/dependencies.py#L56](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/api/dependencies.py#L56)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [api/auth.py#L89](https://github.com/BramAlkema/svg2pptx/blob/b582bac1b85b2e3ee64353c5affa95446ea15be9/api/auth.py#L89)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

