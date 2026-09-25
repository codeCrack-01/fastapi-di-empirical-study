# Tanishpd/linkedin-insights-microservice

- GitHub: https://github.com/Tanishpd/linkedin-insights-microservice
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 4 · commit: `118f5d4c7cb2`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection with async generator` | app/api/routes.py#L19 | The `get_scraper` function is an async generator that yields a LinkedInScraper instance, which is injected into route handlers via `Depends(get_scraper)` in routes.py:122 and routes.py:412. This fo... |

## Pass 2 — reconcile with inventory of Tanishpd/linkedin-insights-microservice

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly implements FastAPI's dependency injection pattern with an async generator (`get_scraper`), which is properly used in route handlers via `Depends(get_scraper)`. | app/api/routes.py#L122 |
| `C4|DEF` | true_pos | **no (overturn)** | The `lifespan` context manager correctly implements FastAPI's startup/shutdown lifecycle management with async operations. | app/main.py#L12 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_scraper` async generator is correctly defined and used in route handlers via `Depends(get_scraper)` for proper resource management. | app/api/routes.py#L19 |

### Missed by inventory (1)
- `Async generator-based dependency injection with FastAPI's `Depends()`` @ app/api/routes.py#L19 — The inventory missed the structural pattern of using async generators as dependencies via `Depends()` in route handlers.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 2 | **false_pos** | [app/api/routes.py#L122](https://github.com/Tanishpd/linkedin-insights-microservice/blob/118f5d4c7cb2ef4ca367313e50adfab2712fd434/app/api/routes.py#L122) |
| `C4|DEF` | C4 | 1 | **false_pos** | [app/main.py#L12](https://github.com/Tanishpd/linkedin-insights-microservice/blob/118f5d4c7cb2ef4ca367313e50adfab2712fd434/app/main.py#L12) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/api/routes.py#L19](https://github.com/Tanishpd/linkedin-insights-microservice/blob/118f5d4c7cb2ef4ca367313e50adfab2712fd434/app/api/routes.py#L19) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 2 · corpus total: 83548 · executor: x86_64
> example: [app/api/routes.py#L122](https://github.com/Tanishpd/linkedin-insights-microservice/blob/118f5d4c7cb2ef4ca367313e50adfab2712fd434/app/api/routes.py#L122)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [app/main.py#L12](https://github.com/Tanishpd/linkedin-insights-microservice/blob/118f5d4c7cb2ef4ca367313e50adfab2712fd434/app/main.py#L12)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/api/routes.py#L19](https://github.com/Tanishpd/linkedin-insights-microservice/blob/118f5d4c7cb2ef4ca367313e50adfab2712fd434/app/api/routes.py#L19)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

