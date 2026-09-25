# b1rdmania/legalise

- GitHub: https://github.com/b1rdmania/legalise
- Stars: 21 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 221 · commit: `0a5126920882`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=1 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI standard dependency injection` | backend/app/api/account.py#L32 | The delete_account function uses Depends(get_session) and Depends(current_user) to inject AsyncSession and User objects, which is FastAPI's standard DI pattern. |
| 2 | `FastAPI standard dependency injection` | backend/app/api/admin_launch_funnel.py#L63 | The launch_funnel_endpoint function uses Depends(get_session) and Depends(current_user) to inject dependencies, following FastAPI's standard DI approach. |
| 3 | `FastAPI standard dependency injection` | backend/app/api/admin_users.py#L113 | The change_user_role_endpoint function uses Depends(get_session) and Depends(current_user) to inject dependencies, consistent with FastAPI's DI pattern. |

## Pass 2 — reconcile with inventory of b1rdmania/legalise

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`, `C3|ELLIPSIS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses Depends(get_session) and Depends(current_user) as standard FastAPI dependencies in multiple endpoints (e.g., account.py:32, admin_launch_funnel.py:63). These are valid DI u... | backend/app/api/account.py#L32 |
| `C4|DEF` | true_pos | **no (overturn)** | The code in jobs.py and main.py uses Depends(get_session) as valid dependency definitions. The static instrument incorrectly labeled these as false positives. | backend/app/api/jobs.py#L106 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | Imports like 'from app.core.auth import current_user' in core/auth.py are valid class-level dependencies, not false positives. | backend/app/api/core/auth.py#L41 |
| `C4|USED` | true_pos | **no (overturn)** | The code in core/auth.py uses 'Depends(get_session)' as valid parameter dependencies, contradicting the false_pos label. | backend/app/api/core/auth.py#L41 |
| `C3|ELLIPSIS|BARE` | variant | yes | The ellipsis (...) in core/auth.py is a valid variant pattern for parameter omission. | backend/app/api/core/auth.py#L41 |

### Missed by inventory (1)
- `FastAPI standard DI in auth.py` @ backend/app/api/auth.py#L72 — The inventory missed the standard DI pattern in auth.py:72 where Depends is used in router.include_router.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 167 | **false_pos** | [backend/app/api/account.py#L32](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/api/account.py#L32) |
| `C4|DEF` | C4 | 35 | **false_pos** | [backend/app/api/jobs.py#L130](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/api/jobs.py#L130) |
| `C1|BARE|PARAM` | C1 | 9 | **known** | [backend/app/api/auth.py#L72](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/api/auth.py#L72) |
| `C3|CLASS|BARE` | C3 | 5 | **false_pos** | [backend/app/core/auth.py#L390](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/core/auth.py#L390) |
| `C4|USED` | C4 | 4 | **false_pos** | [backend/app/core/auth.py#L43](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/core/auth.py#L43) |
| `C3|ELLIPSIS|BARE` | C3 | 1 | **variant** | [backend/app/core/auth.py#L391](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/core/auth.py#L391) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 167 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/account.py#L32](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/api/account.py#L32)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 35 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/jobs.py#L130](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/api/jobs.py#L130)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 9 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/auth.py#L72](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/api/auth.py#L72)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 5 · corpus total: 20139 · executor: x86_64
> example: [backend/app/core/auth.py#L390](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/core/auth.py#L390)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 4 · corpus total: 1079 · executor: x86_64
> example: [backend/app/core/auth.py#L43](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/core/auth.py#L43)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 1 · corpus total: 1113 · executor: x86_64
> example: [backend/app/core/auth.py#L391](https://github.com/b1rdmania/legalise/blob/0a5126920882510dc122f1952ab7221652673650/backend/app/core/auth.py#L391)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

