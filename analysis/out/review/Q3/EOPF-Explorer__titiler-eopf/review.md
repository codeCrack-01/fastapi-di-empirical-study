# EOPF-Explorer/titiler-eopf

- GitHub: https://github.com/EOPF-Explorer/titiler-eopf
- Stars: 17 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 60 · commit: `f8a07ef0bde8`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=1 known=2 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Depends` | titiler/eopf/cache_deps.py#L46 | Defines CacheBackendDep and CacheKeyGeneratorDep using Annotated[Type, Depends(...)] to create injectable dependencies for cache components. |
| 2 | `Route parameter injection via Depends` | titiler/eopf/extensions.py#L64 | Uses src_path=Depends(factory.path_dependency) to inject path resolution logic into endpoint functions. |
| 3 | `Centralized dependency management` | titiler/eopf/factory.py#L75 | Registers multiple endpoints with dependencies like self.path_dependency and self.reader_dependency, showing centralized dependency configuration. |

## Pass 2 — reconcile with inventory of EOPF-Explorer/titiler-eopf

_Presented fingerprints:_ `C1|DOTTED|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C1|CLASS|SIG`, `C3|ELLIPSIS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|DOTTED|SIG` | known | **no (overturn)** | Valid FastAPI dependency injection via Depends() in route parameters | titiler/eopf/extensions.py#L64 |
| `C4|DEF` | known | **no (overturn)** | Actual dependency definitions in cache_deps.py used in testing | titiler/eopf/cache_deps.py#L46 |
| `C1|BARE|PARAM` | known | yes | Explicit parameterized dependencies in cache setup | titiler/eopf/cache_deps.py#L46 |
| `C1|CLASS|SIG` | known | yes | Class-level dependency injection in endpoint registration | titiler/eopf/factory.py#L75 |
| `C3|ELLIPSIS|BARE` | known | **no (overturn)** | No ellipsis found in code - standard parameter definitions | titiler/eopf/cache_deps.py#L46 |

### Missed by inventory (2)
- `Dependency injection in tilejson endpoint parameters` @ titiler/eopf/factory.py#L424 — Multiple Depends() usages in tilejson route parameters not captured by inventory
- `Dependency injection in tileset_list endpoint` @ titiler/eopf/factory.py#L157 — Async endpoint with multiple Depends() parameters not detected

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|DOTTED|SIG` | C1 | 40 | **false_pos** | [titiler/eopf/extensions.py#L64](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/titiler/eopf/extensions.py#L64) |
| `C4|DEF` | C4 | 14 | **false_pos** | [tests/benchmarks/benchmarks.py#L16](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/tests/benchmarks/benchmarks.py#L16) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [titiler/eopf/cache_deps.py#L46](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/titiler/eopf/cache_deps.py#L46) |
| `C1|CLASS|SIG` | C1 | 2 | **known** | [titiler/eopf/factory.py#L104](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/titiler/eopf/factory.py#L104) |
| `C3|ELLIPSIS|BARE` | C3 | 2 | **variant** | [titiler/eopf/cache_deps.py#L46](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/titiler/eopf/cache_deps.py#L46) |

## `C1|DOTTED|SIG` — **false_pos**
> occurrences here: 40 · corpus total: 2178 · executor: x86_64
> example: [titiler/eopf/extensions.py#L64](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/titiler/eopf/extensions.py#L64)
> **rule:** C1

> **evidence (model):** Parameters use dotted names (core.current_principal) but are not wrapped in Depends/Security calls, indicating standard function parameters rather than FastAPI DI dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [tests/benchmarks/benchmarks.py#L16](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/tests/benchmarks/benchmarks.py#L16)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [titiler/eopf/cache_deps.py#L46](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/titiler/eopf/cache_deps.py#L46)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|CLASS|SIG` — **known**
> occurrences here: 2 · corpus total: 149 · executor: x86_64
> example: [titiler/eopf/factory.py#L104](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/titiler/eopf/factory.py#L104)
> **rule:** C1

> **evidence (model):** Examples show classes (HTTPBearer, CRSParams, RoleChecker) passed to Depends, which fits C1 (function/object passed to Depends) since classes are objects in Python.

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 2 · corpus total: 1113 · executor: x86_64
> example: [titiler/eopf/cache_deps.py#L46](https://github.com/EOPF-Explorer/titiler-eopf/blob/f8a07ef0bde8e7d7475df92197048aa37ecbd953/titiler/eopf/cache_deps.py#L46)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

