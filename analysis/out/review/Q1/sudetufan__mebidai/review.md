# sudetufan/mebidai

- GitHub: https://github.com/sudetufan/mebidai
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 117 · commit: `0ac72952b733`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Custom Dependency Injection with Depends()` | backend/app/api/dependencies.py#L25 | The get_db function is a dependency that yields a database session, demonstrating FastAPI's DI pattern where dependencies are created via functions and injected using Depends(). This is used in rou... |
| 2 | `Dependency Chaining` | backend/app/api/dependencies.py#L90 | get_admin_user depends on get_current_user (via Depends(get_current_user)), showing a layered DI approach where higher-level dependencies build on lower ones. This is seen in admin.py:36 where admi... |
| 3 | `Optional Dependencies` | backend/app/api/v1/routes/pages.py#L163 | current_user is declared as optional via User | None = Depends(get_optional_user), illustrating DI support for optional dependencies in routes like pages.py:163. |
| 4 | `Generator-based Dependencies` | backend/app/api/dependencies.py#L25 | get_db uses yield to manage the database session lifecycle, a common pattern in FastAPI DI for resource management. This is referenced in routes like admin.py:36 (db: Session = Depends(get_db)). |

## Pass 2 — reconcile with inventory of sudetufan/mebidai

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly implements FastAPI-style DI with Depends() in get_db(), get_current_user(), and get_admin_user(), which are valid dependencies used throughout the repo (e.g., admin.py:36, pages... | backend/app/api/dependencies.py#L25 |
| `C4|USED` | false_pos | yes | The cited lines (dependencies.py:L15, session.py:L18) are import statements, not DI dependencies. The panel correctly labeled these as false positives since they don't represent actual dependency i... | backend/app/db/session.py#L18 |

### Missed by inventory (2)
- `Optional dependencies with User | None = Depends(...)` @ backend/app/api/v1/routes/pages.py#L163 — The inventory missed optional DI patterns like current_user: User | None = Depends(get_optional_user) used in pages.py:163 for authentication flows.
- `Dependency chaining (get_admin_user depends on get_current_user)` @ backend/app/api/dependencies.py#L90 — The inventory did not capture the layered DI pattern where get_admin_user (L90) depends on get_current_user (L25), seen in admin.py:36.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 115 | **false_pos** | [backend/app/api/dependencies.py#L25](https://github.com/sudetufan/mebidai/blob/0ac72952b733bec57e86a4c1105d6bd1792f0130/backend/app/api/dependencies.py#L25) |
| `C4|USED` | C4 | 2 | **false_pos** | [backend/app/api/dependencies.py#L15](https://github.com/sudetufan/mebidai/blob/0ac72952b733bec57e86a4c1105d6bd1792f0130/backend/app/api/dependencies.py#L15) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 115 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/dependencies.py#L25](https://github.com/sudetufan/mebidai/blob/0ac72952b733bec57e86a4c1105d6bd1792f0130/backend/app/api/dependencies.py#L25)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [backend/app/api/dependencies.py#L15](https://github.com/sudetufan/mebidai/blob/0ac72952b733bec57e86a4c1105d6bd1792f0130/backend/app/api/dependencies.py#L15)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

