# Uranus313/loan-system

- GitHub: https://github.com/Uranus313/loan-system
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 131 · commit: `b713588f4e73`
- Fingerprints touching this repo: 8
- Label mix: novel=0 variant=4 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Repeated Database Error Handling` | Backend/main.py#L288 | Multiple endpoints (get_notifications, delete_customBanks, update_notification, etc.) contain identical SQLAlchemy error handling patterns with db.rollback() and HTTPException 500. This violates DR... |

## Pass 2 — reconcile with inventory of Uranus313/loan-system

_Presented fingerprints:_ `C3|DOTTED|DOTTED`, `C1|BARE|SIG`, `C1|DOTTED|PARAM`, `C3|BARE|BARE`, `C3|CLASS|EMPTY`, `C4|USED`, `C1|BARE|PARAM`, `C1|EMPTY|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `Repeated Database Error Handling` | Repeated Database Error Handling | yes | Multiple endpoints (get_notifications, delete_customBanks, update_notification, etc.) contain identical SQLAlchemy error handling patterns with db.rollback() and HTTPException 500, violating DRY pr... | Backend/main.py#L288 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|DOTTED|DOTTED` | C3 | 60 | **variant** | [Backend/main.py#L96](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L96) |
| `C1|BARE|SIG` | C1 | 33 | **false_pos** | [Backend/main.py#L39](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L39) |
| `C1|DOTTED|PARAM` | C1 | 30 | **variant** | [Backend/main.py#L96](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L96) |
| `C3|BARE|BARE` | C3 | 2 | **variant** | [Backend/tokens.py#L46](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/tokens.py#L46) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [Backend/main.py#L38](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L38) |
| `C4|USED` | C4 | 2 | **false_pos** | [Backend/main.py#L26](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L26) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [Backend/tokens.py#L46](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/tokens.py#L46) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [Backend/main.py#L38](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L38) |

## `C3|DOTTED|DOTTED` — **variant**
> occurrences here: 60 · corpus total: 216 · executor: x86_64
> example: [Backend/main.py#L96](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L96)
> **rule:** C3

> **evidence (model):** Annotated dependencies with type metadata using dotted module paths (e.g., sqlite3.Connection)

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 33 · corpus total: 83548 · executor: x86_64
> example: [Backend/main.py#L39](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L39)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|DOTTED|PARAM` — **variant**
> occurrences here: 30 · corpus total: 422 · executor: x86_64
> example: [Backend/main.py#L96](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L96)
> **rule:** C1

> **evidence (model):** Dotted paths (e.g., 'deps.db') used as dependencies in parameters, which is a structural variation of C1 (Depends call arguments) but not the standard bare function reference.

## `C3|BARE|BARE` — **variant**
> occurrences here: 2 · corpus total: 1316 · executor: x86_64
> example: [Backend/tokens.py#L46](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/tokens.py#L46)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [Backend/main.py#L38](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L38)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [Backend/main.py#L26](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L26)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [Backend/tokens.py#L46](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/tokens.py#L46)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [Backend/main.py#L38](https://github.com/Uranus313/loan-system/blob/b713588f4e73ed5d307d8d708bdc867ab950fe49/Backend/main.py#L38)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

