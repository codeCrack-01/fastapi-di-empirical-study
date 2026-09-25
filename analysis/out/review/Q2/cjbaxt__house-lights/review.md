# cjbaxt/house-lights

- GitHub: https://github.com/cjbaxt/house-lights
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 13 · commit: `2a2aa1e2e8fb`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with get_session` | backend/app/api/calendar.py#L14 | The function export_watchlist_ical uses session: Session = Depends(get_session) to inject a database session. This is a standard FastAPI pattern where get_session is a dependency provider. |
| 2 | `FastAPI Dependency Injection with get_session` | backend/app/api/recommendations.py#L60 | The function recommended_shows uses session: Session = Depends(get_session) to inject a database session, following the same pattern as in calendar.py. |
| 3 | `FastAPI Dependency Injection with get_session` | backend/app/api/shows.py#L15 | The function list_shows uses session: Session = Depends(get_session) to inject a database session, demonstrating consistent use of this pattern across multiple API routes. |
| 4 | `FastAPI Dependency Injection with get_session` | backend/app/api/venues.py#L21 | The function list_venues uses session: Session = Depends(get_session) to inject a database session, further illustrating the widespread use of this DI approach. |
| 5 | `Dependency Provider Function` | backend/app/db.py#L17 | The get_session function is defined as a generator that yields a Session object. It is used as a dependency in multiple routes, providing a centralized way to manage database sessions. |

## Pass 2 — reconcile with inventory of cjbaxt/house-lights

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() with get_session, which is a canonical DI pattern. The panel incorrectly labeled these as false positives. | backend/app/api/calendar.py#L14 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() with get_session, which is a canonical DI pattern. The panel incorrectly labeled these as false positives. | backend/app/api/recommendations.py#L60 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() with get_session, which is a canonical DI pattern. The panel incorrectly labeled these as false positives. | backend/app/api/shows.py#L15 |
| `C4|DEF` | false_pos | yes | No DI usage is present in the cited lines (import statements and router definition). The panel's label is correct. | backend/app/api/publish.py#L13 |
| `C4|USED` | true_pos | **no (overturn)** | The get_session function is a dependency provider used throughout the app. The panel incorrectly labeled this as a false positive. | backend/app/db.py#L17 |

### Missed by inventory (4)
- `FastAPI Dependency Injection with get_session` @ backend/app/api/venues.py#L21 — The list_venues function uses session: Session = Depends(get_session), which was not counted in the initial inventory.
- `FastAPI Dependency Injection with get_session` @ backend/app/api/watchlist.py#L18 — The get_watchlist function uses session: Session = Depends(get_session), which was not counted in the initial inventory.
- `FastAPI Dependency Injection with get_session` @ backend/app/api/watchlist.py#L25 — The upsert_watchlist function uses session: Session = Depends(get_session), which was not counted in the initial inventory.
- `FastAPI Dependency Injection with get_session` @ backend/app/api/watchlist.py#L41 — The remove_watchlist function uses session: Session = Depends(get_session), which was not counted in the initial inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 10 | **false_pos** | [backend/app/api/calendar.py#L14](https://github.com/cjbaxt/house-lights/blob/2a2aa1e2e8fbfdbc25c2ace965f9cb25171fdd03/backend/app/api/calendar.py#L14) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/app/api/publish.py#L13](https://github.com/cjbaxt/house-lights/blob/2a2aa1e2e8fbfdbc25c2ace965f9cb25171fdd03/backend/app/api/publish.py#L13) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db.py#L17](https://github.com/cjbaxt/house-lights/blob/2a2aa1e2e8fbfdbc25c2ace965f9cb25171fdd03/backend/app/db.py#L17) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 10 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/calendar.py#L14](https://github.com/cjbaxt/house-lights/blob/2a2aa1e2e8fbfdbc25c2ace965f9cb25171fdd03/backend/app/api/calendar.py#L14)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/publish.py#L13](https://github.com/cjbaxt/house-lights/blob/2a2aa1e2e8fbfdbc25c2ace965f9cb25171fdd03/backend/app/api/publish.py#L13)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db.py#L17](https://github.com/cjbaxt/house-lights/blob/2a2aa1e2e8fbfdbc25c2ace965f9cb25171fdd03/backend/app/db.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

