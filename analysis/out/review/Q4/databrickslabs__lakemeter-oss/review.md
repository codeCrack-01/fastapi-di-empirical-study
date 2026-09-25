# databrickslabs/lakemeter-oss

- GitHub: https://github.com/databrickslabs/lakemeter-oss
- Stars: 58 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 164 · commit: `ab0dfcbfdc16`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | backend/app/auth/databricks_auth.py#L155 | The `get_current_user` function uses `Depends(_get_db)` to inject a database session. This is a clear example of FastAPI's dependency injection pattern where the `_get_db` generator provides a data... |
| 2 | `FastAPI Depends injection` | backend/app/main.py#L93 | The `system_health` function uses `db=Depends(get_db)` to inject a database session. This demonstrates the use of FastAPI's `Depends` to manage database dependencies in route handlers. |
| 3 | `FastAPI Depends injection` | backend/app/routes/calculate/ai_parse_calc.py#L38 | The `calculate_ai_parse_cost` function uses `db: Session = Depends(get_db)` to inject a database session. This is another instance of FastAPI's dependency injection pattern for database access. |
| 4 | `FastAPI Depends injection` | backend/app/routes/chat.py#L90 | The `chat` function uses `db: Session = Depends(get_db)` to inject a database session. This shows the consistent use of FastAPI's `Depends` across different route handlers for database access. |
| 5 | `FastAPI Depends injection` | backend/app/routes/estimates.py#L47 | The `list_estimates` function uses `current_user: User = Depends(get_current_user)` and `db: Session = Depends(get_db)` to inject both the authenticated user and a database session. This illustrate... |

## Pass 2 — reconcile with inventory of databrickslabs/lakemeter-oss

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_depends_injection_1` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends to inject dependencies like database sessions and authenticated users. | backend/app/auth/databricks_auth.py#L155 |
| `fastapi_depends_injection_2` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends to inject a database session into the system_health route. | backend/app/main.py#L93 |
| `fastapi_depends_injection_3` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends to inject a database session into the calculate_ai_parse_cost function. | backend/app/routes/calculate/ai_parse_calc.py#L38 |
| `fastapi_depends_injection_4` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends to inject a database session into the chat route. | backend/app/routes/chat.py#L90 |
| `fastapi_depends_injection_5` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends to inject both the authenticated user and a database session into the list_estimates route. | backend/app/routes/estimates.py#L47 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 96 | **false_pos** | [backend/app/auth/databricks_auth.py#L155](https://github.com/databrickslabs/lakemeter-oss/blob/ab0dfcbfdc1627ea77d052d44b97be7860e34a48/backend/app/auth/databricks_auth.py#L155) |
| `C4|DEF` | C4 | 66 | **false_pos** | [backend/app/routes/chat.py#L160](https://github.com/databrickslabs/lakemeter-oss/blob/ab0dfcbfdc1627ea77d052d44b97be7860e34a48/backend/app/routes/chat.py#L160) |
| `C4|USED` | C4 | 2 | **false_pos** | [backend/app/auth/databricks_auth.py#L147](https://github.com/databrickslabs/lakemeter-oss/blob/ab0dfcbfdc1627ea77d052d44b97be7860e34a48/backend/app/auth/databricks_auth.py#L147) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 96 · corpus total: 83548 · executor: x86_64
> example: [backend/app/auth/databricks_auth.py#L155](https://github.com/databrickslabs/lakemeter-oss/blob/ab0dfcbfdc1627ea77d052d44b97be7860e34a48/backend/app/auth/databricks_auth.py#L155)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 66 · corpus total: 56644 · executor: x86_64
> example: [backend/app/routes/chat.py#L160](https://github.com/databrickslabs/lakemeter-oss/blob/ab0dfcbfdc1627ea77d052d44b97be7860e34a48/backend/app/routes/chat.py#L160)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [backend/app/auth/databricks_auth.py#L147](https://github.com/databrickslabs/lakemeter-oss/blob/ab0dfcbfdc1627ea77d052d44b97be7860e34a48/backend/app/auth/databricks_auth.py#L147)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

