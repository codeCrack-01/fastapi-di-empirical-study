# IanShaw027/openmail

- GitHub: https://github.com/IanShaw027/openmail
- Stars: 14 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 48 · commit: `96566a710d54`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Annotated Dependencies with FastAPI Depends` | backend/app/deps.py#L13 | DbDep and SettingsDep are defined using Annotated[Type, Depends(...)], a common FastAPI pattern for creating reusable, typed dependencies. These are later used as type hints in route parameters (e.... |
| 2 | `Dependency Injection in Route Parameters` | backend/app/routers/accounts.py#L106 | The list_accounts() function uses db: DbDep and device_id: str = Depends(device_id_strict), demonstrating injection of both the annotated DbDep dependency and a named dependency (device_id_strict). |
| 3 | `Reused Annotated Dependencies` | backend/app/routers/accounts.py#L125 | The create_account() function also uses db: DbDep and settings: SettingsDep, showing these annotated dependencies are reused across multiple route functions. |

## Pass 2 — reconcile with inventory of IanShaw027/openmail

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | known | **no (overturn)** | DbDep and SettingsDep are correctly defined as annotated dependencies in deps.py and reused in route parameters (e.g., accounts.py:106, 125). The static instrument incorrectly labeled them as false... | backend/app/routers/accounts.py#L106 |
| `C4|DEF` | known | **no (overturn)** | get_db() is correctly used in main.py:71 as part of the lifespan context manager for dependency injection. The static instrument's false_pos label is incorrect. | backend/app/main.py#L71 |
| `C3|CLASS|BARE` | known | **no (overturn)** | DbDep and SettingsDep in deps.py:13-14 are annotated dependencies, not classes. The static instrument's false_pos label is incorrect. | backend/app/deps.py#L13 |
| `C4|USED` | known | **no (overturn)** | get_db() in db.py:69 is correctly implemented as a FastAPI dependency generator. The static instrument's false_pos label is incorrect. | backend/app/db.py#L69 |

### Missed by inventory (2)
- `Annotated[Type, Depends(...)] dependency definitions` @ backend/app/deps.py#L13 — The inventory missed detecting the correct use of Annotated dependencies for DbDep and SettingsDep.
- `Reused annotated dependencies in route parameters` @ backend/app/routers/accounts.py#L106 — The inventory missed detecting the reuse of DbDep and SettingsDep across multiple route functions.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 25 | **false_pos** | [backend/app/routers/accounts.py#L106](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/routers/accounts.py#L106) |
| `C4|DEF` | C4 | 18 | **false_pos** | [backend/app/fetch_guard.py#L184](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/fetch_guard.py#L184) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [backend/app/deps.py#L13](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/deps.py#L13) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [backend/app/deps.py#L13](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/deps.py#L13) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db.py#L69](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/db.py#L69) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 25 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routers/accounts.py#L106](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/routers/accounts.py#L106)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 18 · corpus total: 56644 · executor: x86_64
> example: [backend/app/fetch_guard.py#L184](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/fetch_guard.py#L184)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [backend/app/deps.py#L13](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/deps.py#L13)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [backend/app/deps.py#L13](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/deps.py#L13)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db.py#L69](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/db.py#L69)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

