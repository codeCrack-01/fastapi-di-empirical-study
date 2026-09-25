# Pratzz14/Phys.io

- GitHub: https://github.com/Pratzz14/Phys.io
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 26 · commit: `0811d664304d`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | backend/app/main.py#L78 | The health endpoint uses db: Session = Depends(get_db) to inject a database session. This is a standard FastAPI dependency injection pattern where get_db is a dependency provider function. |
| 2 | `Custom user dependency` | backend/app/main.py#L141 | The me() endpoint uses user: User = Depends(current_user), indicating a custom dependency called current_user defined in security.py that provides authenticated user objects. |
| 3 | `Database session generator` | backend/app/db.py#L125 | The get_db() function is a generator that yields Session objects, which is the standard FastAPI pattern for creating database session dependencies. |

## Pass 2 — reconcile with inventory of Pratzz14/Phys.io

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code correctly uses FastAPI's Depends(get_db) for dependency injection, which is standard practice. The health endpoint at main.py:L78 demonstrates proper usage of database session injection. | backend/app/main.py#L78 |
| `C4|DEF` | false_pos | **no (overturn)** | The code in main.py:L55 correctly initializes the database and uses the get_db dependency generator, which is standard in FastAPI. The test setup in test_api.py:L12 also correctly configures the da... | backend/app/main.py#L55 |
| `C4|USED` | false_pos | **no (overturn)** | The get_db function in db.py:L125 is a standard FastAPI generator that yields Session objects for dependency injection. This is correctly implemented and used throughout the codebase. | backend/app/db.py#L125 |

### Missed by inventory (2)
- `CSRF protection via require_csrf middleware` @ backend/app/security.py#L111 — The code enforces CSRF protection in endpoints like /api/auth/register and /api/profile/image through the require_csrf function, but this pattern was not captured by the fingerprint inventory.
- `User authentication via current_user dependency` @ backend/app/main.py#L141 — The me() endpoint uses a custom current_user dependency for authentication, but this pattern was not captured by the fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 23 | **false_pos** | [backend/app/main.py#L78](https://github.com/Pratzz14/Phys.io/blob/0811d664304d3c573e33368770f25136da10cb1b/backend/app/main.py#L78) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/app/main.py#L55](https://github.com/Pratzz14/Phys.io/blob/0811d664304d3c573e33368770f25136da10cb1b/backend/app/main.py#L55) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db.py#L125](https://github.com/Pratzz14/Phys.io/blob/0811d664304d3c573e33368770f25136da10cb1b/backend/app/db.py#L125) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 23 · corpus total: 83548 · executor: x86_64
> example: [backend/app/main.py#L78](https://github.com/Pratzz14/Phys.io/blob/0811d664304d3c573e33368770f25136da10cb1b/backend/app/main.py#L78)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L55](https://github.com/Pratzz14/Phys.io/blob/0811d664304d3c573e33368770f25136da10cb1b/backend/app/main.py#L55)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db.py#L125](https://github.com/Pratzz14/Phys.io/blob/0811d664304d3c573e33368770f25136da10cb1b/backend/app/db.py#L125)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

