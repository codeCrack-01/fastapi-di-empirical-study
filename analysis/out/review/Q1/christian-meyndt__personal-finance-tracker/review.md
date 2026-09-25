# christian-meyndt/personal-finance-tracker

- GitHub: https://github.com/christian-meyndt/personal-finance-tracker
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 113 · commit: `3bd54c739e7d`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=2 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection with Depends()` | backend/app/api/accounts.py#L18 | The code uses FastAPI's Depends() to inject dependencies like get_current_user and get_db into route handlers. For example, current_user is annotated with Depends(get_current_user) to enforce authe... |
| 2 | `Consistent use of Annotated for dependency typing` | backend/app/api/accounts.py#L18 | Annotated is used to explicitly type dependencies (e.g., Annotated[User, Depends(get_current_user)]) which improves readability and type safety. |
| 3 | `Shared dependencies across multiple routes` | backend/app/api/analytics.py#L18 | The db: Session = Depends(get_db) dependency is reused in multiple endpoints (e.g., get_summary, get_by_category) across different API modules. |

## Pass 2 — reconcile with inventory of christian-meyndt/personal-finance-tracker

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|SIG`, `C1|BARE|PARAM`, `C3|CLASS|EMPTY`, `C3|ELLIPSIS|BARE`, `C1|EMPTY|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | The code correctly uses Annotated[User, Depends(...)] for dependency injection, which is standard in FastAPI. The static tool's 'false_pos' label is incorrect. | backend/app/api/accounts.py#L18 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | Parameters like current_user and db are properly annotated with Annotated[User, Depends(...)], which is correct usage. The 'false_pos' label is invalid. | backend/app/api/accounts.py#L18 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses db: Session = Depends(get_db) as a standard parameter pattern. The 'known' label is accurate. | backend/app/api/accounts.py#L17 |
| `C3|CLASS|EMPTY` | false_pos | **no (overturn)** | The parameter current_user is properly annotated with Annotated[User, Depends(...)], not empty. The 'false_pos' label is incorrect. | backend/app/api/auth.py#L18 |
| `C3|ELLIPSIS|BARE` | variant | **no (overturn)** | No ellipsis (...) is present in the code. The 'variant' label appears to be a misclassification. | backend/app/api/auth.py#L18 |

### Missed by inventory (1)
- `Consistent use of Annotated[Type, Depends(...)] for dependency injection` @ backend/app/api/transactions.py#L87 — The inventory did not capture the widespread use of Annotated with Depends() across multiple modules, which is a key pattern in the codebase.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 52 | **false_pos** | [backend/app/api/accounts.py#L17](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/accounts.py#L17) |
| `C1|BARE|SIG` | C1 | 28 | **false_pos** | [backend/app/api/accounts.py#L18](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/accounts.py#L18) |
| `C1|BARE|PARAM` | C1 | 27 | **known** | [backend/app/api/accounts.py#L17](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/accounts.py#L17) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [backend/app/api/auth.py#L18](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/auth.py#L18) |
| `C3|ELLIPSIS|BARE` | C3 | 2 | **variant** | [backend/app/auth.py#L46](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/auth.py#L46) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [backend/app/api/auth.py#L18](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/auth.py#L18) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db.py#L17](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/db.py#L17) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 52 · corpus total: 20139 · executor: x86_64
> example: [backend/app/api/accounts.py#L17](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/accounts.py#L17)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 28 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/accounts.py#L18](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/accounts.py#L18)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 27 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/accounts.py#L17](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/accounts.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [backend/app/api/auth.py#L18](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/auth.py#L18)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 2 · corpus total: 1113 · executor: x86_64
> example: [backend/app/auth.py#L46](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/auth.py#L46)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [backend/app/api/auth.py#L18](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/api/auth.py#L18)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db.py#L17](https://github.com/christian-meyndt/personal-finance-tracker/blob/3bd54c739e7dc20c03705c16c662b63dfd60f995/backend/app/db.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

