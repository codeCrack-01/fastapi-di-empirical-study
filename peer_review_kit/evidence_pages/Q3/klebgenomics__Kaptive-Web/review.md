# klebgenomics/Kaptive-Web

- GitHub: https://github.com/klebgenomics/Kaptive-Web
- Stars: 11 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 36 · commit: `9ac5686cd9d9`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI function-based dependency injection` | src/kaptive_web/api/routes/auth.py#L22 | The `get_current_user` function uses `Depends(api_key_header)` and `Depends(get_repository)` to inject dependencies, demonstrating FastAPI's pattern of using functions with `Depends()` to resolve d... |
| 2 | `Reused dependency providers` | src/kaptive_web/api/routes/serotype.py#L214 | Multiple endpoints use `Depends(get_current_user)` and `Depends(get_repository)`, showing that these functions are reused as dependency providers across different routes. This centralizes dependenc... |
| 3 | `Asynchronous dependency resolution` | src/kaptive_web/api/routes/serotype.py#L278 | The `list_runs` endpoint uses `Depends(get_current_user)` and `Depends(get_repository)` in an async function, indicating that FastAPI's DI system handles asynchronous dependencies seamlessly. |

## Pass 2 — reconcile with inventory of klebgenomics/Kaptive-Web

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code correctly implements FastAPI's dependency injection pattern using `Depends()` for authentication and repository access. This is a valid and intended usage, not a false positive. | src/kaptive_web/api/routes/auth.py#L22 |
| `C4|DEF` | false_pos | **no (overturn)** | The code correctly uses `Depends(get_current_user)` and `Depends(get_repository)` across multiple async endpoints in `serotype.py`, which is standard practice in FastAPI for secure, reusable depend... | src/kaptive_web/api/routes/serotype.py#L214 |

### Missed by inventory (1)
- `Centralized dependency providers with async support` @ src/kaptive_web/api/routes/serotype.py#L278 — The inventory did not capture the reuse of `get_current_user` and `get_repository` across multiple async endpoints, which demonstrates a sophisticated DI pattern with user authentication and databa...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 29 | **false_pos** | [src/kaptive_web/api/routes/auth.py#L22](https://github.com/klebgenomics/Kaptive-Web/blob/9ac5686cd9d94109cd5bdd3caa53ea434fd2360d/src/kaptive_web/api/routes/auth.py#L22) |
| `C4|DEF` | C4 | 7 | **false_pos** | [src/kaptive_web/api/routes/serotype.py#L537](https://github.com/klebgenomics/Kaptive-Web/blob/9ac5686cd9d94109cd5bdd3caa53ea434fd2360d/src/kaptive_web/api/routes/serotype.py#L537) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 29 · corpus total: 83548 · executor: x86_64
> example: [src/kaptive_web/api/routes/auth.py#L22](https://github.com/klebgenomics/Kaptive-Web/blob/9ac5686cd9d94109cd5bdd3caa53ea434fd2360d/src/kaptive_web/api/routes/auth.py#L22)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [src/kaptive_web/api/routes/serotype.py#L537](https://github.com/klebgenomics/Kaptive-Web/blob/9ac5686cd9d94109cd5bdd3caa53ea434fd2360d/src/kaptive_web/api/routes/serotype.py#L537)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

