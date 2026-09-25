# AydinTHR/aimentum

- GitHub: https://github.com/AydinTHR/aimentum
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 23 · commit: `39add614f85c`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Annotated and Depends` | backend/app/db.py#L46 | DbSession is defined as Annotated[Session, Depends(get_db)], showing explicit dependency injection using FastAPI's Depends() and Annotated type hints. |
| 2 | `Memoized dependency providers` | backend/app/db.py#L46 | get_sessionmaker and get_db use @lru_cache(maxsize=1) for memoization, ensuring singletons for database connections. |
| 3 | `Test-specific dependency overriding` | backend/tests/conftest.py#L115 | Test fixtures override dependencies like get_db, get_calendar, and get_llm with mocks using app.dependency_overrides, demonstrating DI usage in testing. |
| 4 | `Service abstraction with DI` | backend/app/services/calendar.py#L252 | CalendarDep is defined as Annotated[CalendarService, Depends(get_calendar)], abstracting the GoogleCalendarService behind a dependency-injected interface. |

## Pass 2 — reconcile with inventory of AydinTHR/aimentum

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | known | **no (overturn)** | DbSession is explicitly defined with Annotated[Session, Depends(get_db)], which is a valid FastAPI DI occurrence. | backend/app/db.py#L46 |
| `C1|BARE|PARAM` | known | yes | DbSession uses Depends(get_db) as a parameterized dependency, aligning with the 'known' label. | backend/app/db.py#L46 |
| `C3|CLASS|BARE` | known | **no (overturn)** | CalendarDep is defined with Annotated[CalendarService, Depends(get_calendar)], a valid class-based DI occurrence. | backend/app/services/calendar.py#L252 |
| `C4|USED` | known | **no (overturn)** | get_db is explicitly used in DbSession via Depends(get_db), a valid DI occurrence. | backend/app/db.py#L41 |

### Missed by inventory (2)
- `Test-specific dependency overriding with app.dependency_overrides` @ backend/tests/conftest.py#L115 — Overrides like app.dependency_overrides[get_llm] = lambda: fake_llm are DI usages in testing but not captured by the inventory.
- `Fake service fixtures overriding dependencies` @ backend/tests/conftest.py#L131 — Fixtures like fake_push and fake_stt use app.dependency_overrides to mock services, representing DI patterns missed by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 10 | **false_pos** | [backend/app/db.py#L52](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L52) |
| `C1|BARE|PARAM` | C1 | 6 | **known** | [backend/app/db.py#L46](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L46) |
| `C3|CLASS|BARE` | C3 | 6 | **false_pos** | [backend/app/db.py#L46](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L46) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db.py#L41](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L41) |

## `C4|DEF` — **false_pos**
> occurrences here: 10 · corpus total: 56644 · executor: x86_64
> example: [backend/app/db.py#L52](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L52)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 6 · corpus total: 18195 · executor: x86_64
> example: [backend/app/db.py#L46](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L46)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 6 · corpus total: 20139 · executor: x86_64
> example: [backend/app/db.py#L46](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L46)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db.py#L41](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L41)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

