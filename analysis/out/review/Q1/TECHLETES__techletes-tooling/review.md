# TECHLETES/techletes-tooling

- GitHub: https://github.com/TECHLETES/techletes-tooling
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 27 · commit: `8d56b22502cc`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=2 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Depends and Annotated` | apps/engineering-cockpit/backend/api/deps.py#L31 | Defines SessionDep = Annotated[Session, Depends(get_db)] and TokenDep = Annotated[str | None, Depends(reusable_oauth2)] showing explicit use of FastAPI's dependency system with Annotated types and ... |
| 2 | `Request-scoped database dependency` | apps/engineering-cockpit/backend/api/deps.py#L25 | get_db() is a generator function yielding Session objects, used as the source for SessionDep which is injected into routes |
| 3 | `Authentication dependency chain` | apps/engineering-cockpit/backend/api/deps.py#L66 | CurrentUser = Annotated[User, Depends(get_current_user)] creates a dependency that validates JWT tokens and fetches users, which is then used in SuperUserDep |
| 4 | `Permission-based dependency factory` | apps/engineering-cockpit/backend/api/deps.py#L78 | require_role() returns a Callable[..., User] that can be used as a dependency factory for RBAC checks |
| 5 | `Test-specific dependency override` | apps/engineering-cockpit/backend/tests/conftest.py#L39 | Overrides app.dependency_overrides[get_db] with a test-specific _get_test_db() function showing DI system usage in testing |

## Pass 2 — reconcile with inventory of TECHLETES/techletes-tooling

_Presented fingerprints:_ `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|DEF`, `C3|CLASS|EMPTY`, `C1|EMPTY|PARAM`, `C3|ELLIPSIS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | Annotated parameters with Depends() are explicitly used in deps.py for SessionDep and TokenDep | apps/engineering-cockpit/backend/api/deps.py#L31 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | The code uses Annotated[Session, Depends(...)] which is a parameter definition, not a class | apps/engineering-cockpit/backend/api/deps.py#L31 |
| `C4|DEF` | false_pos | yes | The code defines functions (get_db, get_current_user) not classes | apps/engineering-cockpit/backend/api/deps.py#L25 |
| `C3|CLASS|EMPTY` | false_pos | yes | No empty classes found in the code at the cited location | apps/engineering-cockpit/backend/api/routes/login.py#L30 |
| `C1|EMPTY|PARAM` | variant | yes | The parameter form_data uses Annotated with Depends() as shown in the code | apps/engineering-cockpit/backend/api/routes/login.py#L30 |
| `C3|ELLIPSIS|BARE` | variant | yes | The OAuth2PasswordBearer constructor uses ellipsis in parameter definitions | apps/engineering-cockpit/backend/api/deps.py#L32 |
| `C4|USED` | false_pos | yes | The get_db function is used as a dependency but is not a class | apps/engineering-cockpit/backend/api/deps.py#L25 |

### Missed by inventory (1)
- `Annotated[Type, Depends(...)] parameter patterns` @ apps/engineering-cockpit/backend/api/deps.py#L31 — The inventory missed multiple instances of Annotated parameters with Depends() in deps.py

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 9 | **known** | [apps/engineering-cockpit/backend/api/deps.py#L31](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L31) |
| `C3|CLASS|BARE` | C3 | 7 | **false_pos** | [apps/engineering-cockpit/backend/api/deps.py#L31](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L31) |
| `C4|DEF` | C4 | 6 | **false_pos** | [apps/engineering-cockpit/backend/main.py#L36](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/main.py#L36) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [apps/engineering-cockpit/backend/api/routes/login.py#L30](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/routes/login.py#L30) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [apps/engineering-cockpit/backend/api/routes/login.py#L30](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/routes/login.py#L30) |
| `C3|ELLIPSIS|BARE` | C3 | 1 | **variant** | [apps/engineering-cockpit/backend/api/deps.py#L32](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L32) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/engineering-cockpit/backend/api/deps.py#L25](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L25) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 9 · corpus total: 18195 · executor: x86_64
> example: [apps/engineering-cockpit/backend/api/deps.py#L31](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L31)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 7 · corpus total: 20139 · executor: x86_64
> example: [apps/engineering-cockpit/backend/api/deps.py#L31](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L31)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [apps/engineering-cockpit/backend/main.py#L36](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/main.py#L36)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [apps/engineering-cockpit/backend/api/routes/login.py#L30](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/routes/login.py#L30)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [apps/engineering-cockpit/backend/api/routes/login.py#L30](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/routes/login.py#L30)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 1 · corpus total: 1113 · executor: x86_64
> example: [apps/engineering-cockpit/backend/api/deps.py#L32](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L32)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/engineering-cockpit/backend/api/deps.py#L25](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L25)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

