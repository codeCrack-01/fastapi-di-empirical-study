# habinrahman/MyCareer-AI

- GitHub: https://github.com/habinrahman/MyCareer-AI
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 67 · commit: `494759a09631`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=1 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | backend/app/api/routes/careers.py#L38 | user_id and db parameters use Depends() for authentication and database access |
| 2 | `FastAPI Depends-based injection` | backend/app/api/routes/chat.py#L44 | Multiple dependencies injected via Depends() including auth, DB, settings, and feature flags |
| 3 | `Custom dependency checks` | backend/app/api/routes/careers.py#L38 | require_career_profile_enabled and require_job_matching_enabled dependencies indicate feature toggle checks |
| 4 | `Service layer injection` | backend/app/api/routes/careers.py#L66 | benchmarking_service is injected and used for business logic |
| 5 | `Configuration injection` | backend/app/api/routes/chat.py#L44 | Settings object injected via get_settings_dep for configuration access |

## Pass 2 — reconcile with inventory of habinrahman/MyCareer-AI

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C3|ELLIPSIS|BARE`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | known | **no (overturn)** | The code correctly uses FastAPI Depends() for authentication (user_id) and database access (db) in routes/careers.py lines 38-40, which are valid dependency injections. | backend/app/api/routes/careers.py#L38 |

### Missed by inventory (2)
- `Service layer injection via Depends()` @ backend/app/api/routes/careers.py#L66 — The inventory did not account for service layer dependencies like benchmarking_service injected via Depends(), which is a valid pattern in FastAPI.
- `Configuration injection via get_settings_dep` @ backend/app/api/routes/chat.py#L44 — The inventory missed dependencies injected via get_settings_dep for configuration access, which is a common practice.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 58 | **false_pos** | [backend/app/api/routes/careers.py#L38](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/api/routes/careers.py#L38) |
| `C4|DEF` | C4 | 5 | **false_pos** | [backend/app/main.py#L32](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/main.py#L32) |
| `C3|ELLIPSIS|BARE` | C3 | 2 | **variant** | [backend/app/core/security.py#L37](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/core/security.py#L37) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [backend/app/core/security.py#L39](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/core/security.py#L39) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/core/database.py#L79](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/core/database.py#L79) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 58 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/routes/careers.py#L38](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/api/routes/careers.py#L38)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L32](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/main.py#L32)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 2 · corpus total: 1113 · executor: x86_64
> example: [backend/app/core/security.py#L37](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/core/security.py#L37)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [backend/app/core/security.py#L39](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/core/security.py#L39)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/core/database.py#L79](https://github.com/habinrahman/MyCareer-AI/blob/494759a096310e6408b0646d91d8fa50f454c71e/backend/app/core/database.py#L79)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

