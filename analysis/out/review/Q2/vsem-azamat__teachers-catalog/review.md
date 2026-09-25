# vsem-azamat/teachers-catalog

- GitHub: https://github.com/vsem-azamat/teachers-catalog
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 29 · commit: `4dd1561450eb`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI native dependency injection with Annotated and Depends` | apps/api/src/students_cz/api/deps.py#L15 | The code defines SettingsDep = Annotated[Settings, Depends(get_settings)] and SessionDep = Annotated[AsyncSession, Depends(session_scope, scope="function")], showing explicit use of FastAPI's depen... |
| 2 | `Chained dependency resolution` | apps/api/src/students_cz/api/deps.py#L45 | current_identity depends on SettingsDep and authorization header, then IdentityDep is built from current_identity. current_user depends on IdentityDep, SessionDep, and SettingsDep, creating a layer... |
| 3 | `Test-specific dependency overriding` | apps/api/tests/conftest.py#L114 | The app_for() function overrides session_scope with a test-specific implementation using app.dependency_overrides[session_scope] = scope, demonstrating how test fixtures can replace real dependenci... |

## Pass 2 — reconcile with inventory of vsem-azamat/teachers-catalog

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | known | **no (overturn)** | The code explicitly uses Annotated[Settings, Depends(...)] and Annotated[AsyncSession, Depends(...)] as FastAPI dependencies, confirming their use in the DI system. | apps/api/src/students_cz/api/deps.py#L15 |
| `C1|BARE|PARAM` | known | **no (overturn)** | Parameters like authorization: Annotated[str | None, Header()] = None use explicit dependencies (Header()), contradicting the 'BARE' label. | apps/api/src/students_cz/api/deps.py#L45 |
| `C3|CLASS|BARE` | known | **no (overturn)** | Classes like TelegramIdentity are wrapped in Annotated[... , Depends(...)], showing they are not 'BARE' in the DI context. | apps/api/src/students_cz/api/deps.py#L45 |
| `C4|USED` | known | **no (overturn)** | session_scope is explicitly used as a dependency (Depends(session_scope, scope='function')), contradicting the 'false_pos' label. | apps/api/src/students_cz/api/deps.py#L15 |

### Missed by inventory (2)
- `Test-specific dependency overriding with app.dependency_overrides` @ apps/api/tests/conftest.py#L114 — The inventory did not capture test fixtures that replace real dependencies (e.g., overriding session_scope with a test-specific implementation).
- `Chained dependency resolution (SettingsDep → IdentityDep → UserDep)` @ apps/api/src/students_cz/api/deps.py#L45 — The inventory missed the layered dependency chain explicitly defined in the code.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 14 | **false_pos** | [apps/api/src/students_cz/db/session.py#L56](https://github.com/vsem-azamat/teachers-catalog/blob/4dd1561450ebed2b1d52b7932a7f3a8b537eec2e/apps/api/src/students_cz/db/session.py#L56) |
| `C1|BARE|PARAM` | C1 | 7 | **known** | [apps/api/src/students_cz/api/deps.py#L15](https://github.com/vsem-azamat/teachers-catalog/blob/4dd1561450ebed2b1d52b7932a7f3a8b537eec2e/apps/api/src/students_cz/api/deps.py#L15) |
| `C3|CLASS|BARE` | C3 | 7 | **false_pos** | [apps/api/src/students_cz/api/deps.py#L15](https://github.com/vsem-azamat/teachers-catalog/blob/4dd1561450ebed2b1d52b7932a7f3a8b537eec2e/apps/api/src/students_cz/api/deps.py#L15) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/api/src/students_cz/db/session.py#L72](https://github.com/vsem-azamat/teachers-catalog/blob/4dd1561450ebed2b1d52b7932a7f3a8b537eec2e/apps/api/src/students_cz/db/session.py#L72) |

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [apps/api/src/students_cz/db/session.py#L56](https://github.com/vsem-azamat/teachers-catalog/blob/4dd1561450ebed2b1d52b7932a7f3a8b537eec2e/apps/api/src/students_cz/db/session.py#L56)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 7 · corpus total: 18195 · executor: x86_64
> example: [apps/api/src/students_cz/api/deps.py#L15](https://github.com/vsem-azamat/teachers-catalog/blob/4dd1561450ebed2b1d52b7932a7f3a8b537eec2e/apps/api/src/students_cz/api/deps.py#L15)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 7 · corpus total: 20139 · executor: x86_64
> example: [apps/api/src/students_cz/api/deps.py#L15](https://github.com/vsem-azamat/teachers-catalog/blob/4dd1561450ebed2b1d52b7932a7f3a8b537eec2e/apps/api/src/students_cz/api/deps.py#L15)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/api/src/students_cz/db/session.py#L72](https://github.com/vsem-azamat/teachers-catalog/blob/4dd1561450ebed2b1d52b7932a7f3a8b537eec2e/apps/api/src/students_cz/db/session.py#L72)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

