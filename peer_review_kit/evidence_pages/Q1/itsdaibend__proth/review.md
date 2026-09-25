# itsdaibend/proth

- GitHub: https://github.com/itsdaibend/proth
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 40 · commit: `79cfa346fff1`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection via get_db` | apps/api/app/database.py#L17 | The get_db function is a dependency injection pattern that provides a database session to routes via Depends(get_db). This decouples route logic from database session management, allowing centraliz... |
| 2 | `Dependency Injection for User Authentication` | apps/api/app/security.py#L52 | The current_user function uses Depends(get_db) to inject a database session, demonstrating DI for authentication. It retrieves the user from the token and database without hardcoding dependencies i... |

## Pass 2 — reconcile with inventory of itsdaibend/proth

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `dependency_injection_get_db` | Dependency Injection via get_db | yes | The get_db function in apps/api/app/database.py:17 correctly implements dependency injection by providing a database session to routes via Depends(get_db). | apps/api/app/database.py#L17 |
| `dependency_injection_current_user` | Dependency Injection for User Authentication | yes | The current_user function in apps/api/app/security.py:52 uses Depends(get_db) to inject a database session, demonstrating DI for authentication as observed. | apps/api/app/security.py#L52 |

### Missed by inventory (2)
- `Dependency Injection in Route Handlers` @ apps/api/app/main.py#L123 — The log_habit route in main.py:123 uses Depends(get_db) but was not mentioned in initial observations.
- `Dependency Injection in Lifespan` @ apps/api/app/main.py#L98 — The lifespan function in main.py:98 uses get_db for seeding data but was not noted in initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 38 | **false_pos** | [apps/api/app/main.py#L120](https://github.com/itsdaibend/proth/blob/79cfa346fff1d736266f5a64daffa07cb9bd3f20/apps/api/app/main.py#L120) |
| `C4|DEF` | C4 | 1 | **false_pos** | [apps/api/app/main.py#L98](https://github.com/itsdaibend/proth/blob/79cfa346fff1d736266f5a64daffa07cb9bd3f20/apps/api/app/main.py#L98) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/api/app/database.py#L17](https://github.com/itsdaibend/proth/blob/79cfa346fff1d736266f5a64daffa07cb9bd3f20/apps/api/app/database.py#L17) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 38 · corpus total: 83548 · executor: x86_64
> example: [apps/api/app/main.py#L120](https://github.com/itsdaibend/proth/blob/79cfa346fff1d736266f5a64daffa07cb9bd3f20/apps/api/app/main.py#L120)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [apps/api/app/main.py#L98](https://github.com/itsdaibend/proth/blob/79cfa346fff1d736266f5a64daffa07cb9bd3f20/apps/api/app/main.py#L98)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/api/app/database.py#L17](https://github.com/itsdaibend/proth/blob/79cfa346fff1d736266f5a64daffa07cb9bd3f20/apps/api/app/database.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

