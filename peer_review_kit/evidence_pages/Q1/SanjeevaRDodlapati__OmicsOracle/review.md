# SanjeevaRDodlapati/OmicsOracle

- GitHub: https://github.com/SanjeevaRDodlapati/OmicsOracle
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 101 · commit: `ebe268638d0c`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=2 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection` | extras/auth_quotas/routes_quotas.py#L91 | The route uses Depends(get_current_active_user) to inject authenticated user information, a standard FastAPI pattern. |
| 2 | `Database dependency injection` | extras/auth_quotas/routes_quotas.py#L133 | The route uses Depends(get_db) to inject an async database session, demonstrating dependency injection for database access. |
| 3 | `Authentication dependency injection` | omics_oracle_v2/api/routes/users.py#L126 | The route uses Depends(get_current_active_user) to enforce authentication, showing DI for security checks. |
| 4 | `Settings injection` | omics_oracle_v2/api/routes/health.py#L44 | The health check endpoint uses Depends(get_api_settings) to inject application settings, a common DI pattern for configuration. |

## Pass 2 — reconcile with inventory of SanjeevaRDodlapati/OmicsOracle

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C2|BARE|ascopes`, `C1|CLASS|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code demonstrates standard FastAPI dependency injection for authentication, not a false positive. | extras/auth_quotas/routes_quotas.py#L91 |
| `C4|USED` | false_pos | **no (overturn)** | The code correctly uses Depends(get_db) for database dependency injection, not a false positive. | omics_oracle_v2/database/session.py#L41 |

### Missed by inventory (2)
- `Test file DI usages` @ archive/streamlit-dashboard-20251012/dashboard-tests/test_preferences.py#L20 — Test files contain DI patterns (e.g., Depends) that were not captured by the initial inventory.
- `Multiple DI instances in auth routes` @ omics_oracle_v2/api/routes/auth.py#L80 — Multiple DI usages (e.g., Depends(get_current_active_user)) in auth routes were not fully accounted for in the initial inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 62 | **false_pos** | [extras/auth_quotas/routes_quotas.py#L91](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/extras/auth_quotas/routes_quotas.py#L91) |
| `C4|DEF` | C4 | 34 | **false_pos** | [archive/streamlit-dashboard-20251012/dashboard-tests/test_preferences.py#L20](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/archive/streamlit-dashboard-20251012/dashboard-tests/test_preferences.py#L20) |
| `C2|BARE|ascopes` | C2 | 3 | **known** | [archive/auth-duplicate-api-keys-oct15/auth/api_keys.py#L33](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/archive/auth-duplicate-api-keys-oct15/auth/api_keys.py#L33) |
| `C1|CLASS|SIG` | C1 | 1 | **known** | [archive/auth-duplicate-api-keys-oct15/auth/api_keys.py#L123](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/archive/auth-duplicate-api-keys-oct15/auth/api_keys.py#L123) |
| `C4|USED` | C4 | 1 | **false_pos** | [omics_oracle_v2/database/session.py#L41](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/omics_oracle_v2/database/session.py#L41) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 62 · corpus total: 83548 · executor: x86_64
> example: [extras/auth_quotas/routes_quotas.py#L91](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/extras/auth_quotas/routes_quotas.py#L91)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 34 · corpus total: 56644 · executor: x86_64
> example: [archive/streamlit-dashboard-20251012/dashboard-tests/test_preferences.py#L20](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/archive/streamlit-dashboard-20251012/dashboard-tests/test_preferences.py#L20)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C2|BARE|ascopes` — **known**
> occurrences here: 3 · corpus total: 504 · executor: x86_64
> example: [archive/auth-duplicate-api-keys-oct15/auth/api_keys.py#L33](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/archive/auth-duplicate-api-keys-oct15/auth/api_keys.py#L33)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C1|CLASS|SIG` — **known**
> occurrences here: 1 · corpus total: 149 · executor: x86_64
> example: [archive/auth-duplicate-api-keys-oct15/auth/api_keys.py#L123](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/archive/auth-duplicate-api-keys-oct15/auth/api_keys.py#L123)
> **rule:** C1

> **evidence (model):** Examples show classes (HTTPBearer, CRSParams, RoleChecker) passed to Depends, which fits C1 (function/object passed to Depends) since classes are objects in Python.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [omics_oracle_v2/database/session.py#L41](https://github.com/SanjeevaRDodlapati/OmicsOracle/blob/ebe268638d0ccf12232da2b5a06bd60cded43792/omics_oracle_v2/database/session.py#L41)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

