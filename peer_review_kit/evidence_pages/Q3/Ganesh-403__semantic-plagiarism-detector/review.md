# Ganesh-403/semantic-plagiarism-detector

- GitHub: https://github.com/Ganesh-403/semantic-plagiarism-detector
- Stars: 15 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 66 · commit: `081737c868c4`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=2 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends usage` | src/api/app.py#L49 | Dependencies=[Depends(verify_bearer_token)] shows explicit use of FastAPI's Depends() for dependency injection in the API setup. |
| 2 | `FastAPI Depends usage` | src/api/middleware.py#L123 | async def verify_bearer_token(..., credentials: Optional[...] = Depends(security), ...) uses Depends() to inject the 'security' dependency. |
| 3 | `FastAPI Depends usage` | src/api/middleware.py#L172 | async def get_current_user(..., token: Optional[str] = Depends(verify_bearer_token), ...) shows a dependency chain using Depends(). |
| 4 | `FastAPI Depends usage` | src/api/routers/analysis.py#L194 | def get_incidents(..., _token: str = Depends(verify_bearer_token), ...) directly uses Depends() for token injection. |
| 5 | `FastAPI Security usage` | src/api/routers/analysis.py#L257 | _user: dict = Security(get_current_user, scopes=["write"])) uses FastAPI's Security() for scoped authentication. |

## Pass 2 — reconcile with inventory of Ganesh-403/semantic-plagiarism-detector

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C2|BARE|ascopes`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No explicit contradictions found in the code; the panel's label remains valid. | src/api/app.py#L49 |
| `C1|BARE|SIG` | known | **no (overturn)** | The code correctly uses FastAPI's Depends() and Security() for dependency injection and authentication, contradicting the 'false_pos' label. | src/api/middleware.py#L172 |
| `C2|BARE|ascopes` | known | yes | The code explicitly uses Security() with scopes, aligning with the 'known' label. | src/api/routers/analysis.py#L256 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses Depends(verify_bearer_token) in the API setup, aligning with the 'known' label. | src/api/app.py#L49 |

### Missed by inventory (1)
- `FastAPI Security usage with scopes` @ src/api/routers/analysis.py#L434 — The inventory may have missed this instance of Security() with scopes in the async endpoint.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 55 | **false_pos** | [app/components/advanced_analytics.py#L572](https://github.com/Ganesh-403/semantic-plagiarism-detector/blob/081737c868c4eb953c56c08ed72f11d934c7ebdf/app/components/advanced_analytics.py#L572) |
| `C1|BARE|SIG` | C1 | 5 | **false_pos** | [src/api/middleware.py#L123](https://github.com/Ganesh-403/semantic-plagiarism-detector/blob/081737c868c4eb953c56c08ed72f11d934c7ebdf/src/api/middleware.py#L123) |
| `C2|BARE|ascopes` | C2 | 5 | **known** | [src/api/routers/admin.py#L153](https://github.com/Ganesh-403/semantic-plagiarism-detector/blob/081737c868c4eb953c56c08ed72f11d934c7ebdf/src/api/routers/admin.py#L153) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [src/api/app.py#L49](https://github.com/Ganesh-403/semantic-plagiarism-detector/blob/081737c868c4eb953c56c08ed72f11d934c7ebdf/src/api/app.py#L49) |

## `C4|DEF` — **false_pos**
> occurrences here: 55 · corpus total: 56644 · executor: x86_64
> example: [app/components/advanced_analytics.py#L572](https://github.com/Ganesh-403/semantic-plagiarism-detector/blob/081737c868c4eb953c56c08ed72f11d934c7ebdf/app/components/advanced_analytics.py#L572)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 5 · corpus total: 83548 · executor: x86_64
> example: [src/api/middleware.py#L123](https://github.com/Ganesh-403/semantic-plagiarism-detector/blob/081737c868c4eb953c56c08ed72f11d934c7ebdf/src/api/middleware.py#L123)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C2|BARE|ascopes` — **known**
> occurrences here: 5 · corpus total: 504 · executor: x86_64
> example: [src/api/routers/admin.py#L153](https://github.com/Ganesh-403/semantic-plagiarism-detector/blob/081737c868c4eb953c56c08ed72f11d934c7ebdf/src/api/routers/admin.py#L153)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [src/api/app.py#L49](https://github.com/Ganesh-403/semantic-plagiarism-detector/blob/081737c868c4eb953c56c08ed72f11d934c7ebdf/src/api/app.py#L49)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

