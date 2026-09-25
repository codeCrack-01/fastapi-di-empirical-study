# Tanush-Jain/kelan

- GitHub: https://github.com/Tanush-Jain/kelan
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 20 · commit: `ea16df2796e2`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | kelan/api/server.py#L236 | The get_current_org function uses Depends(security) to inject an HTTPBearer authentication dependency. This is FastAPI's standard DI pattern where dependencies are explicitly declared with Depends() |
| 2 | `Chained dependency injection` | kelan/api/server.py#L868 | The auth_me endpoint uses Depends(get_current_org), creating a dependency chain where get_current_org (which itself uses Depends) is injected into auth_me |
| 3 | `Reusable dependency injection` | kelan/api/server.py#L888 | The list_entities endpoint also uses Depends(get_current_org), showing that the same authentication dependency is reused across multiple endpoints |
| 4 | `Async context manager injection` | kelan-python/kelan/database.py#L129 | The get_db() async context manager is defined for database sessions - though not shown being used with Depends(), this is a common DI pattern in FastAPI for managing database connections |

## Pass 2 — reconcile with inventory of Tanush-Jain/kelan

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() for authentication and dependency injection, which matches the C1|BARE|SIG fingerprint (bare DI usage). The original label of 'false_pos' is incorrect. | kelan/api/server.py#L236 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The auth_me endpoint uses Depends(get_current_org), demonstrating chained DI, which aligns with the C1|BARE|SIG fingerprint. The original 'false_pos' label is incorrect. | kelan/api/server.py#L868 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The list_entities endpoint reuses Depends(get_current_org), confirming standard DI practice. The original 'false_pos' label is incorrect. | kelan/api/server.py#L888 |
| `C4|DEF` | true_pos | **no (overturn)** | The get_db() async context manager in database.py:129 is a canonical DI pattern for database sessions. The original 'false_pos' label is incorrect. | kelan-python/kelan/database.py#L129 |
| `C4|DEF` | true_pos | **no (overturn)** | The lifespan context manager in server/main.py:64 is a standard DI pattern for application lifecycle management. The original 'false_pos' label is incorrect. | kelan-python/kelan/server/main.py#L64 |
| `C4|DEF` | true_pos | **no (overturn)** | The lifespan context manager in server.py:82 is another instance of DI via context managers. The original 'false_pos' label is incorrect. | kelan/api/server.py#L82 |

### Missed by inventory (3)
- `Async context manager DI (get_db())` @ kelan-python/kelan/database.py#L129 — The inventory did not capture the async context manager pattern for database sessions, which is a clear DI occurrence.
- `Lifespan context manager DI` @ kelan-python/kelan/server/main.py#L64 — The inventory missed the lifespan context manager pattern used for application startup/shutdown, a standard DI practice.
- `Lifespan context manager DI` @ kelan/api/server.py#L82 — Another instance of lifespan context manager DI was not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 11 | **false_pos** | [kelan/api/server.py#L236](https://github.com/Tanush-Jain/kelan/blob/ea16df2796e2cf07a2a52e0187eb93160485e186/kelan/api/server.py#L236) |
| `C4|DEF` | C4 | 9 | **false_pos** | [kelan-python/kelan/database.py#L129](https://github.com/Tanush-Jain/kelan/blob/ea16df2796e2cf07a2a52e0187eb93160485e186/kelan-python/kelan/database.py#L129) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 11 · corpus total: 83548 · executor: x86_64
> example: [kelan/api/server.py#L236](https://github.com/Tanush-Jain/kelan/blob/ea16df2796e2cf07a2a52e0187eb93160485e186/kelan/api/server.py#L236)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 9 · corpus total: 56644 · executor: x86_64
> example: [kelan-python/kelan/database.py#L129](https://github.com/Tanush-Jain/kelan/blob/ea16df2796e2cf07a2a52e0187eb93160485e186/kelan-python/kelan/database.py#L129)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

