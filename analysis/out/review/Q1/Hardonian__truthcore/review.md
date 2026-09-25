# Hardonian/truthcore

- GitHub: https://github.com/Hardonian/truthcore
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 19 · commit: `2da9c0e76eff`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends for authentication/rate-limiting injection` | src/truthcore/server.py#L502 | The status endpoint uses Depends(verify_api_key) and Depends(functools.partial(...)) to inject authentication and rate-limiting checks as parameters. This is repeated in judge (L532), intel (L688),... |
| 2 | `Parameterized dependency injection` | src/truthcore/server.py#L502 | The rate-limiting dependency uses functools.partial to bind max_requests and window_seconds parameters to check_rate_limit, demonstrating parameterized DI. |
| 3 | `Unused dependency declaration` | src/truthcore/server.py#L64 | SECURITY_BEARER_DEPENDENCY = Depends(SECURITY_BEARER) is declared but never used in the code excerpts. |

## Pass 2 — reconcile with inventory of Hardonian/truthcore

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|DOTTED|SIG`, `C4|DEF`, `C1|CLASS|PARAM`

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 8 | **false_pos** | [src/truthcore/server.py#L502](https://github.com/Hardonian/truthcore/blob/2da9c0e76eff4a9aacaf3aebe4aeabe1d790cc72/src/truthcore/server.py#L502) |
| `C1|DOTTED|SIG` | C1 | 8 | **false_pos** | [src/truthcore/server.py#L503](https://github.com/Hardonian/truthcore/blob/2da9c0e76eff4a9aacaf3aebe4aeabe1d790cc72/src/truthcore/server.py#L503) |
| `C4|DEF` | C4 | 2 | **false_pos** | [src/truthcore/determinism.py#L54](https://github.com/Hardonian/truthcore/blob/2da9c0e76eff4a9aacaf3aebe4aeabe1d790cc72/src/truthcore/determinism.py#L54) |
| `C1|CLASS|PARAM` | C1 | 1 | **known** | [src/truthcore/server.py#L64](https://github.com/Hardonian/truthcore/blob/2da9c0e76eff4a9aacaf3aebe4aeabe1d790cc72/src/truthcore/server.py#L64) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 8 · corpus total: 83548 · executor: x86_64
> example: [src/truthcore/server.py#L502](https://github.com/Hardonian/truthcore/blob/2da9c0e76eff4a9aacaf3aebe4aeabe1d790cc72/src/truthcore/server.py#L502)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|DOTTED|SIG` — **false_pos**
> occurrences here: 8 · corpus total: 2178 · executor: x86_64
> example: [src/truthcore/server.py#L503](https://github.com/Hardonian/truthcore/blob/2da9c0e76eff4a9aacaf3aebe4aeabe1d790cc72/src/truthcore/server.py#L503)
> **rule:** C1

> **evidence (model):** Parameters use dotted names (core.current_principal) but are not wrapped in Depends/Security calls, indicating standard function parameters rather than FastAPI DI dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [src/truthcore/determinism.py#L54](https://github.com/Hardonian/truthcore/blob/2da9c0e76eff4a9aacaf3aebe4aeabe1d790cc72/src/truthcore/determinism.py#L54)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|CLASS|PARAM` — **known**
> occurrences here: 1 · corpus total: 72 · executor: x86_64
> example: [src/truthcore/server.py#L64](https://github.com/Hardonian/truthcore/blob/2da9c0e76eff4a9aacaf3aebe4aeabe1d790cc72/src/truthcore/server.py#L64)
> **rule:** C1

> **evidence (model):** The examples show a class (COOKIE_SCHEME) being used as a dependency parameter in function signatures, consistent with C1 (Depends): function/object passed to Depends(...)

