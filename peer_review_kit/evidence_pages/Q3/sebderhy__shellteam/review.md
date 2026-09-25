# sebderhy/shellteam

- GitHub: https://github.com/sebderhy/shellteam
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 116 · commit: `122138f8a312`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Inconsistent use of origin trust checks` | api/routers/computers.py#L116 | The /apps endpoint (set_app_route) requires require_trusted_origin, but /apps (list_app_routes) does not. This creates a security gap where listing app routes (sensitive data) is not origin-restric... |
| 2 | `Missing origin trust for report visibility` | api/routers/computers.py#L151 | The /reports endpoint (set_report_visibility) requires require_trusted_origin, but the /reports (get_report_visibility) endpoint does not. This allows visibility checks of published reports without... |
| 3 | `Unvalidated file uploads` | api/routers/feedback.py#L59 | The submit_feedback endpoint allows screenshot uploads with only count/size limits, but no file type validation or sanitization. This could allow malicious file types (e.g., executables) to be uplo... |

## Pass 2 — reconcile with inventory of sebderhy/shellteam

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `inconsistent_origin_trust_apps` | Inconsistent origin trust checks for /apps endpoints | yes | GET /apps lacks require_trusted_origin while POST /apps has it, exposing app route listings to cross-origin requests. | api/routers/computers.py#L125 |
| `inconsistent_origin_trust_reports` | Inconsistent origin trust checks for /reports endpoints | yes | GET /reports lacks require_trusted_origin while POST /reports has it, allowing visibility checks of published reports without origin restriction. | api/routers/computers.py#L173 |
| `unvalidated_file_uploads` | Unvalidated file uploads in submit_feedback | yes | Screenshot and voice_recording uploads lack file type validation, enabling malicious file types to be uploaded. | api/routers/feedback.py#L59 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 64 | **false_pos** | [api/routers/ai_tools.py#L31](https://github.com/sebderhy/shellteam/blob/122138f8a312b95099a84ae1ff8457b98624c8c7/api/routers/ai_tools.py#L31) |
| `C4|DEF` | C4 | 40 | **false_pos** | [api/main.py#L37](https://github.com/sebderhy/shellteam/blob/122138f8a312b95099a84ae1ff8457b98624c8c7/api/main.py#L37) |
| `C1|BARE|PARAM` | C1 | 12 | **known** | [api/routers/ai_tools.py#L71](https://github.com/sebderhy/shellteam/blob/122138f8a312b95099a84ae1ff8457b98624c8c7/api/routers/ai_tools.py#L71) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 64 · corpus total: 83548 · executor: x86_64
> example: [api/routers/ai_tools.py#L31](https://github.com/sebderhy/shellteam/blob/122138f8a312b95099a84ae1ff8457b98624c8c7/api/routers/ai_tools.py#L31)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 40 · corpus total: 56644 · executor: x86_64
> example: [api/main.py#L37](https://github.com/sebderhy/shellteam/blob/122138f8a312b95099a84ae1ff8457b98624c8c7/api/main.py#L37)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 12 · corpus total: 18195 · executor: x86_64
> example: [api/routers/ai_tools.py#L71](https://github.com/sebderhy/shellteam/blob/122138f8a312b95099a84ae1ff8457b98624c8c7/api/routers/ai_tools.py#L71)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

