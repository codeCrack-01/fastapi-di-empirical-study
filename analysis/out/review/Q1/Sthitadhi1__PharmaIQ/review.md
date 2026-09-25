# Sthitadhi1/PharmaIQ

- GitHub: https://github.com/Sthitadhi1/PharmaIQ
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 4 · commit: `a6a6747db849`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | backend/app/routes/auth_routes.py#L37 | The get_current_user function uses Depends(oauth2_scheme) to inject an OAuth2 authentication dependency. This is a standard FastAPI pattern where dependencies are explicitly declared with Depends() |
| 2 | `Nested dependency injection` | backend/app/routes/auth_routes.py#L79 | The read_users_me endpoint uses Depends(get_current_user), which itself depends on oauth2_scheme. This shows a layered dependency chain where get_current_user is a reusable dependency that wraps th... |
| 3 | `Generator-based dependency` | backend/app/database.py#L12 | The get_db function uses a generator with yield to provide a database session. This is a common FastAPI pattern for dependencies that need to manage resources (like DB connections) with proper cleanup |
| 4 | `Duplicate dependency implementation` | backend/app/database/connection.py#L14 | A second get_db function is implemented in a separate file with identical logic, suggesting potential code duplication in the dependency management layer |

## Pass 2 — reconcile with inventory of Sthitadhi1/PharmaIQ

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() for dependency injection in both instances (get_current_user and read_users_me). This matches the structural fingerprint of BARE DI usage. | backend/app/routes/auth_routes.py#L37 |
| `C4|DEF` | true_pos | **no (overturn)** | The get_db functions in both files are valid DI dependencies implementing the generator pattern. The panel's false_pos label incorrectly dismisses valid DI implementations. | backend/app/database.py#L12 |

### Missed by inventory (1)
- `Code duplication in DI providers` @ backend/app/database/connection.py#L14 — The inventory missed the code smell of duplicate get_db implementations in database.py and connection.py, which implement identical dependency provider logic.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 2 | **false_pos** | [backend/app/routes/auth_routes.py#L37](https://github.com/Sthitadhi1/PharmaIQ/blob/a6a6747db8496da5ad148a0baa40da317ae07702/backend/app/routes/auth_routes.py#L37) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/app/database.py#L12](https://github.com/Sthitadhi1/PharmaIQ/blob/a6a6747db8496da5ad148a0baa40da317ae07702/backend/app/database.py#L12) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 2 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routes/auth_routes.py#L37](https://github.com/Sthitadhi1/PharmaIQ/blob/a6a6747db8496da5ad148a0baa40da317ae07702/backend/app/routes/auth_routes.py#L37)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/app/database.py#L12](https://github.com/Sthitadhi1/PharmaIQ/blob/a6a6747db8496da5ad148a0baa40da317ae07702/backend/app/database.py#L12)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

