# acebmxer/beacon_pxe

- GitHub: https://github.com/acebmxer/beacon_pxe
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 101 · commit: `b1ec93e8d72e`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection` | web/app/routers/drivers.py#L76 | The code uses FastAPI's `Depends()` to inject dependencies like `require_admin` and `get_db` into route handlers. This is evident in the `upload` function where `user: User = Depends(require_admin)... |
| 2 | `FastAPI Dependency Injection` | web/app/routers/images.py#L38 | The `images_page` function uses `db: Session = Depends(get_db)` to inject a database session. This demonstrates FastAPI's DI pattern, where dependencies are resolved and injected at runtime rather ... |

## Pass 2 — reconcile with inventory of acebmxer/beacon_pxe

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `FastAPI Dependency Injection` | FastAPI Dependency Injection | yes | Code explicitly uses Depends() for dependency injection in route handlers (e.g., drivers.py:76, images.py:38). | web/app/routers/drivers.py#L76 |
| `FastAPI Dependency Injection` | FastAPI Dependency Injection | yes | Code uses Depends() for injecting database sessions and authentication checks (e.g., images.py:38). | web/app/routers/images.py#L38 |

### Missed by inventory (4)
- `Async Route Handlers` @ web/app/routers/images.py#L93 — Async def used in route handlers (e.g., images.py:93) with await operations.
- `Background Tasks` @ web/app/routers/images.py#L93 — BackgroundTasks used in upload route (images.py:93) with background.add_task().
- `SQLAlchemy ORM` @ web/app/routers/images.py#L127 — Database interactions use SQLAlchemy ORM (e.g., db.execute(), db.get()).
- `Templating System` @ web/app/routers/drivers.py#L76 — render() function used to render HTML templates (drivers.py:76).

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 93 | **false_pos** | [web/app/deps.py#L52](https://github.com/acebmxer/beacon_pxe/blob/b1ec93e8d72e9670e653ebd86535b2c94551f66d/web/app/deps.py#L52) |
| `C4|DEF` | C4 | 7 | **false_pos** | [web/app/main.py#L51](https://github.com/acebmxer/beacon_pxe/blob/b1ec93e8d72e9670e653ebd86535b2c94551f66d/web/app/main.py#L51) |
| `C4|USED` | C4 | 1 | **false_pos** | [web/app/db.py#L20](https://github.com/acebmxer/beacon_pxe/blob/b1ec93e8d72e9670e653ebd86535b2c94551f66d/web/app/db.py#L20) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 93 · corpus total: 83548 · executor: x86_64
> example: [web/app/deps.py#L52](https://github.com/acebmxer/beacon_pxe/blob/b1ec93e8d72e9670e653ebd86535b2c94551f66d/web/app/deps.py#L52)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [web/app/main.py#L51](https://github.com/acebmxer/beacon_pxe/blob/b1ec93e8d72e9670e653ebd86535b2c94551f66d/web/app/main.py#L51)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [web/app/db.py#L20](https://github.com/acebmxer/beacon_pxe/blob/b1ec93e8d72e9670e653ebd86535b2c94551f66d/web/app/db.py#L20)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

