# wq147/bookmark-navigation

- GitHub: https://github.com/wq147/bookmark-navigation
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 133 · commit: `1044131db839`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Annotated Types` | navigation/backend/app/dependencies.py#L15 | Defines DatabaseSession as Annotated[Session, Depends(get_session)], establishing a reusable dependency for database sessions. |
| 2 | `Chained Dependency Injection` | navigation/backend/app/dependencies.py#L51 | require_ready_user depends on require_user, which depends on require_session, creating a chain of authentication dependencies. |
| 3 | `Router-Level Dependency Injection` | navigation/backend/app/routers/admin.py#L27 | Router is configured with dependencies=[Depends(require_admin)], applying authentication to all routes under /admin. |
| 4 | `Explicit Dependency Annotation` | navigation/backend/app/routers/admin.py#L81 | Actor parameter annotated with Annotated[User, Depends(require_admin)], explicitly declaring admin privilege requirement. |
| 5 | `CSRF Protection Dependency` | navigation/backend/app/routers/auth.py#L72 | Logout endpoint uses Depends(require_csrf) to enforce CSRF token validation for security. |

## Pass 2 — reconcile with inventory of wq147/bookmark-navigation

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | false_pos | yes | No bare class definitions found; all dependencies use Annotated[...] with explicit Depends() | navigation/backend/app/dependencies.py#L15 |
| `C1|BARE|PARAM` | known | yes | Parameters correctly annotated with Annotated[Type, Depends(...)] as seen in require_ready_user() | navigation/backend/app/dependencies.py#L51 |
| `C4|DEF` | false_pos | **no (overturn)** | No definitions in provided code match the inventory's cited lines (bookmark_audit.py:222, etc.) | navigation/backend/app/dependencies.py#L15 |
| `C4|USED` | false_pos | **no (overturn)** | No usage in provided code matches the inventory's cited line (navigation/backend/app/db.py:48) | navigation/backend/app/dependencies.py#L15 |

### Missed by inventory (1)
- `Annotated[...]` @ navigation/backend/app/routers/bookmarks.py#L110 — Dependency injection pattern in post_bookmark() with Annotated[User, Depends(require_ready_user)] not captured in inventory

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 61 | **false_pos** | [navigation/backend/app/dependencies.py#L15](https://github.com/wq147/bookmark-navigation/blob/1044131db839293f68aae69372501df26b83c254/navigation/backend/app/dependencies.py#L15) |
| `C1|BARE|PARAM` | C1 | 52 | **known** | [navigation/backend/app/dependencies.py#L15](https://github.com/wq147/bookmark-navigation/blob/1044131db839293f68aae69372501df26b83c254/navigation/backend/app/dependencies.py#L15) |
| `C4|DEF` | C4 | 19 | **false_pos** | [bookmark_audit.py#L222](https://github.com/wq147/bookmark-navigation/blob/1044131db839293f68aae69372501df26b83c254/bookmark_audit.py#L222) |
| `C4|USED` | C4 | 1 | **false_pos** | [navigation/backend/app/db.py#L48](https://github.com/wq147/bookmark-navigation/blob/1044131db839293f68aae69372501df26b83c254/navigation/backend/app/db.py#L48) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 61 · corpus total: 20139 · executor: x86_64
> example: [navigation/backend/app/dependencies.py#L15](https://github.com/wq147/bookmark-navigation/blob/1044131db839293f68aae69372501df26b83c254/navigation/backend/app/dependencies.py#L15)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 52 · corpus total: 18195 · executor: x86_64
> example: [navigation/backend/app/dependencies.py#L15](https://github.com/wq147/bookmark-navigation/blob/1044131db839293f68aae69372501df26b83c254/navigation/backend/app/dependencies.py#L15)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 19 · corpus total: 56644 · executor: x86_64
> example: [bookmark_audit.py#L222](https://github.com/wq147/bookmark-navigation/blob/1044131db839293f68aae69372501df26b83c254/bookmark_audit.py#L222)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [navigation/backend/app/db.py#L48](https://github.com/wq147/bookmark-navigation/blob/1044131db839293f68aae69372501df26b83c254/navigation/backend/app/db.py#L48)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

