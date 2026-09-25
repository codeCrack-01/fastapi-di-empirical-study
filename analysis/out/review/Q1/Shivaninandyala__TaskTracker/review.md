# Shivaninandyala/TaskTracker

- GitHub: https://github.com/Shivaninandyala/TaskTracker
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 27 · commit: `594bbe7b0416`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection` | backend/app/api/auth.py#L31 | The `db: Session = Depends(get_db)` shows FastAPI's dependency injection where `get_db` is a dependency providing a database session. |
| 2 | `Nested dependencies` | backend/app/core/dependencies.py#L15 | The `get_current_user` function uses `Depends(oauth2_scheme)` and `Depends(get_db)`, demonstrating nested dependencies where one dependency (user authentication) relies on another (database access). |
| 3 | `Generator-based dependency` | backend/app/database/database.py#L17 | The `get_db` function uses `yield db` to provide a database session, a common pattern in FastAPI for context managers that handle resource cleanup. |
| 4 | `Repeated dependency usage` | backend/app/api/task.py#L33 | Both `current_user: User = Depends(get_current_user)` and `db: Session = Depends(get_db)` are used in multiple route handlers across the codebase, showing consistent DI application. |

## Pass 2 — reconcile with inventory of Shivaninandyala/TaskTracker

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|EMPTY|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI's dependency injection with `Depends(get_db)` in multiple routes (e.g., auth.py:L31, task.py:L33). The label 'false_pos' incorrectly dismisses valid DI usage. | backend/app/api/auth.py#L31 |
| `C1|EMPTY|SIG` | true_pos | **no (overturn)** | The line in question (auth.py:L48) is not empty but contains a valid return statement. The 'EMPTY' label misclassifies a functional DI usage. | backend/app/api/auth.py#L48 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db` generator (database.py:L17) is a correct FastAPI dependency provider using `yield`. Labeling it as 'false_pos' ignores its proper implementation. | backend/app/database/database.py#L17 |

### Missed by inventory (2)
- `Nested dependencies (Depends within Depends)` @ backend/app/core/dependencies.py#L15 — The `get_current_user` function uses both `Depends(oauth2_scheme)` and `Depends(get_db)` as nested dependencies, a pattern not captured by the inventory.
- `Repeated DI usage across routes` @ backend/app/api/task.py#L33 — Multiple route handlers consistently use `Depends(get_current_user)` and `Depends(get_db)`, indicating a systemic DI pattern missed by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 25 | **false_pos** | [backend/app/api/auth.py#L31](https://github.com/Shivaninandyala/TaskTracker/blob/594bbe7b041665361082d66518a546fe8daa3e85/backend/app/api/auth.py#L31) |
| `C1|EMPTY|SIG` | C1 | 1 | **variant** | [backend/app/api/auth.py#L48](https://github.com/Shivaninandyala/TaskTracker/blob/594bbe7b041665361082d66518a546fe8daa3e85/backend/app/api/auth.py#L48) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/database/database.py#L17](https://github.com/Shivaninandyala/TaskTracker/blob/594bbe7b041665361082d66518a546fe8daa3e85/backend/app/database/database.py#L17) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 25 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/auth.py#L31](https://github.com/Shivaninandyala/TaskTracker/blob/594bbe7b041665361082d66518a546fe8daa3e85/backend/app/api/auth.py#L31)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 1 · corpus total: 254 · executor: x86_64
> example: [backend/app/api/auth.py#L48](https://github.com/Shivaninandyala/TaskTracker/blob/594bbe7b041665361082d66518a546fe8daa3e85/backend/app/api/auth.py#L48)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database/database.py#L17](https://github.com/Shivaninandyala/TaskTracker/blob/594bbe7b041665361082d66518a546fe8daa3e85/backend/app/database/database.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

