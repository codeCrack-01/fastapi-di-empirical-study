# EndofTimeWorks/pluris-haven

- GitHub: https://github.com/EndofTimeWorks/pluris-haven
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 26 · commit: `e6fe1d7dd34b`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=1 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Depends() and Annotated types` | server/pluris_server/dependencies.py#L30 | The get_auth_context function uses Depends() for injecting dependencies like HTTPBearer, get_db, and settings_from_request. Parameters are annotated with Annotated[type, Depends(...)] to explicitly... |
| 2 | `Router-level dependency injection` | server/pluris_server/routers/friends.py#L40 | The router is configured with dependencies=[Depends(require_friends_enabled)], applying a global dependency to all endpoints under this router. |
| 3 | `Custom dependency factories with Annotated` | server/pluris_server/dependencies.py#L69 | Db, CurrentAuth, and AppSettings are defined as Annotated types with Depends(...) to create reusable dependency injection shortcuts for AsyncSession, AuthContext, and Settings. |
| 4 | `Database session dependency` | server/pluris_server/database.py#L44 | The get_db function is an async generator that yields AsyncSession instances, serving as a dependency provider for database operations. |

## Pass 2 — reconcile with inventory of EndofTimeWorks/pluris-haven

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`, `C3|ELLIPSIS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | false_pos | yes | The class definition is not a dependency injection point but a data class. The static label correctly identifies this as a false positive. | server/pluris_server/dependencies.py#L31 |
| `C1|BARE|PARAM` | known | yes | Parameters use Annotated[type, Depends(...)] correctly for dependency injection. The static label is accurate. | server/pluris_server/dependencies.py#L31 |
| `C4|DEF` | false_pos | **no (overturn)** | The lifespan context manager in main.py is a valid dependency for the FastAPI app. The static label incorrectly marks this as a false positive. | server/pluris_server/main.py#L60 |
| `C3|ELLIPSIS|BARE` | variant | **no (overturn)** | The code at line 30 does not contain an ellipsis. The static label is incorrect. | server/pluris_server/dependencies.py#L30 |
| `C4|USED` | false_pos | **no (overturn)** | The get_db function is a valid dependency provider for database sessions. The static label incorrectly marks this as a false positive. | server/pluris_server/database.py#L44 |

### Missed by inventory (2)
- `Custom dependency factories with Annotated[type, Depends(...)]` @ server/pluris_server/dependencies.py#L69 — Db, CurrentAuth, and AppSettings are defined as Annotated dependencies but were not captured by the inventory.
- `Router-level dependencies=[Depends(...)]` @ server/pluris_server/routers/friends.py#L40 — The router's global dependency on require_friends_enabled was not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 9 | **false_pos** | [server/pluris_server/dependencies.py#L31](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L31) |
| `C1|BARE|PARAM` | C1 | 8 | **known** | [server/pluris_server/dependencies.py#L30](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L30) |
| `C4|DEF` | C4 | 6 | **false_pos** | [server/pluris_server/main.py#L60](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/main.py#L60) |
| `C3|ELLIPSIS|BARE` | C3 | 2 | **variant** | [server/pluris_server/dependencies.py#L30](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L30) |
| `C4|USED` | C4 | 1 | **false_pos** | [server/pluris_server/database.py#L44](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/database.py#L44) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 9 · corpus total: 20139 · executor: x86_64
> example: [server/pluris_server/dependencies.py#L31](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L31)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 8 · corpus total: 18195 · executor: x86_64
> example: [server/pluris_server/dependencies.py#L30](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L30)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [server/pluris_server/main.py#L60](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/main.py#L60)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 2 · corpus total: 1113 · executor: x86_64
> example: [server/pluris_server/dependencies.py#L30](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L30)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [server/pluris_server/database.py#L44](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/database.py#L44)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

