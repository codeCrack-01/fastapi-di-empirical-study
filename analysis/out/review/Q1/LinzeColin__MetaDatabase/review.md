# LinzeColin/MetaDatabase

- GitHub: https://github.com/LinzeColin/MetaDatabase
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 204 · commit: `dd273b496e17`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=0 known=2 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Depends(get_db)` | JobHuntBotOnline/app/main.py#L890 | The `db` parameter is injected via `Depends(get_db)`, which is a FastAPI dependency injection mechanism to provide a database session to the route handler. |
| 2 | `Depends(get_db)` | JobHuntBotOnline/app/main.py#L940 | The `db` parameter is injected via `Depends(get_db)` in the `recommendation_ai_page` route, demonstrating dependency injection for database access. |
| 3 | `Depends(get_db)` | JobHuntBotOnline/app/main.py#L965 | The `db` parameter is injected via `Depends(get_db)` in the `recommendation_ai_post` route, showing DI for database operations. |

## Pass 2 — reconcile with inventory of LinzeColin/MetaDatabase

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C1|CLASS|PARAM`, `C3|CLASS|CLASS`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `db_dependency_injection` | db_dependency_injection | yes | All routes using database operations correctly inject 'db' via Depends(get_db) as shown in multiple examples (e.g., recommendation_ai_page, recommendation_ai_post, pack_edit_post). | JobHuntBotOnline/app/main.py#L940 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 112 | **false_pos** | [ABD/abd_acceptance/metrics_economics.py#L468](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/ABD/abd_acceptance/metrics_economics.py#L468) |
| `C1|BARE|SIG` | C1 | 46 | **false_pos** | [Alpha/backend/app/control_page/app.py#L127](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/Alpha/backend/app/control_page/app.py#L127) |
| `C1|BARE|PARAM` | C1 | 42 | **known** | [EEI/apps/api/app/domain.py#L215](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/EEI/apps/api/app/domain.py#L215) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [EEI/apps/api/app/domain.py#L215](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/EEI/apps/api/app/domain.py#L215) |
| `C1|CLASS|PARAM` | C1 | 1 | **known** | [EEI/apps/api/app/domain.py#L216](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/EEI/apps/api/app/domain.py#L216) |
| `C3|CLASS|CLASS` | C3 | 1 | **false_pos** | [EEI/apps/api/app/domain.py#L216](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/EEI/apps/api/app/domain.py#L216) |

## `C4|DEF` — **false_pos**
> occurrences here: 112 · corpus total: 56644 · executor: x86_64
> example: [ABD/abd_acceptance/metrics_economics.py#L468](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/ABD/abd_acceptance/metrics_economics.py#L468)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 46 · corpus total: 83548 · executor: x86_64
> example: [Alpha/backend/app/control_page/app.py#L127](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/Alpha/backend/app/control_page/app.py#L127)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 42 · corpus total: 18195 · executor: x86_64
> example: [EEI/apps/api/app/domain.py#L215](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/EEI/apps/api/app/domain.py#L215)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [EEI/apps/api/app/domain.py#L215](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/EEI/apps/api/app/domain.py#L215)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|CLASS|PARAM` — **known**
> occurrences here: 1 · corpus total: 72 · executor: x86_64
> example: [EEI/apps/api/app/domain.py#L216](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/EEI/apps/api/app/domain.py#L216)
> **rule:** C1

> **evidence (model):** The examples show a class (COOKIE_SCHEME) being used as a dependency parameter in function signatures, consistent with C1 (Depends): function/object passed to Depends(...)

## `C3|CLASS|CLASS` — **false_pos**
> occurrences here: 1 · corpus total: 42 · executor: x86_64
> example: [EEI/apps/api/app/domain.py#L216](https://github.com/LinzeColin/MetaDatabase/blob/dd273b496e172c80d1782a0c2767398d1ca99f9f/EEI/apps/api/app/domain.py#L216)

> **evidence (model):** Annotated types are classes but no Depends/Security in metadata; extractor misclassified non-DI Annotated usage as C3

