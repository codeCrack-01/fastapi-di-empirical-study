# GlacierEQ/ECHO

- GitHub: https://github.com/GlacierEQ/ECHO
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 13 · commit: `b90f72e71d82`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based authentication dependencies` | echo/main.py#L31 | AuthRead, AuthWrite, AuthVerify, and AuthExecute are defined using Annotated[AuthContext, Depends(...)] with auth_dependency() from echo.security, indicating FastAPI dependency injection for authen... |
| 2 | `Lifespan context manager for DB initialization` | echo/main.py#L38 | The @asynccontextmanager lifespan() function initializes ENGINE via init_db(), demonstrating FastAPI's lifespan management as a form of dependency injection for startup/shutdown logic |
| 3 | `Database session context manager` | echo/db.py#L148 | The @contextmanager get_session() function provides database sessions, a common DI pattern for resource management |
| 4 | `Test fixture dependency injection` | tests/test_behavioral.py#L14 | The pytest fixture 'svc' injects a ContinuityService with a database session, showing DI in testing |

## Pass 2 — reconcile with inventory of GlacierEQ/ECHO

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() for authentication dependencies (e.g., AuthRead = Annotated[AuthContext, Depends(...)]), which is a canonical DI pattern. The panel's 'false_pos' label ... | echo/main.py#L31 |
| `C1|BARE|PARAM` | known | yes | The annotated parameters (AuthRead, AuthWrite, etc.) with Depends() are correctly identified as DI occurrences in the panel's 'known' label. | echo/main.py#L31 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code defines top-level annotated variables (e.g., AuthRead) with Depends(), which are DI parameters. The panel's 'false_pos' label incorrectly dismisses these as non-DI. | echo/main.py#L31 |

### Missed by inventory (2)
- `Test fixture DI injection` @ tests/test_behavioral.py#L14 — The pytest fixture 'svc' injects a ContinuityService with a database session, representing DI in testing, but this pattern was not captured by the inventory.
- `Lifespan context manager for DB initialization` @ echo/main.py#L38 — The @asynccontextmanager lifespan() function for DB startup/shutdown is a DI pattern for lifecycle management, but it was not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 5 | **false_pos** | [echo/db.py#L148](https://github.com/GlacierEQ/ECHO/blob/b90f72e71d823dfc107658b3ff2eec5a22f01417/echo/db.py#L148) |
| `C1|BARE|PARAM` | C1 | 4 | **known** | [echo/main.py#L31](https://github.com/GlacierEQ/ECHO/blob/b90f72e71d823dfc107658b3ff2eec5a22f01417/echo/main.py#L31) |
| `C3|CLASS|BARE` | C3 | 4 | **false_pos** | [echo/main.py#L31](https://github.com/GlacierEQ/ECHO/blob/b90f72e71d823dfc107658b3ff2eec5a22f01417/echo/main.py#L31) |

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [echo/db.py#L148](https://github.com/GlacierEQ/ECHO/blob/b90f72e71d823dfc107658b3ff2eec5a22f01417/echo/db.py#L148)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 4 · corpus total: 18195 · executor: x86_64
> example: [echo/main.py#L31](https://github.com/GlacierEQ/ECHO/blob/b90f72e71d823dfc107658b3ff2eec5a22f01417/echo/main.py#L31)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 4 · corpus total: 20139 · executor: x86_64
> example: [echo/main.py#L31](https://github.com/GlacierEQ/ECHO/blob/b90f72e71d823dfc107658b3ff2eec5a22f01417/echo/main.py#L31)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

