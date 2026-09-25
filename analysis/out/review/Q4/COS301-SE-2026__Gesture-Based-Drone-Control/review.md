# COS301-SE-2026/Gesture-Based-Drone-Control

- GitHub: https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control
- Stars: 23 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 104 · commit: `f81f666bd8a9`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection with Annotated` | apps/backend/app/api/analytics.py#L37 | The 'db' parameter uses Depends(get_db) to inject a database session, a common FastAPI DI pattern. |
| 2 | `State dependency injection` | apps/backend/app/api/drone.py#L116 | The 'state' parameter uses Depends(get_state) to inject application state, demonstrating DI for state management. |
| 3 | `Annotated dependency with metadata` | apps/backend/app/api/auth.py#L39 | The 'db' parameter uses Annotated[AsyncSession, Depends(get_db)] to combine type hints with DI. |
| 4 | `Nested dependency chain` | apps/backend/app/dependencies.py#L38 | get_adapter depends on get_state, showing a layered DI approach where dependencies are composed. |

## Pass 2 — reconcile with inventory of COS301-SE-2026/Gesture-Based-Drone-Control

_Presented fingerprints:_ `C3|CLASS|BARE`, `C1|BARE|PARAM`, `C4|DEF`, `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | Valid FastAPI DI pattern with Annotated[AsyncSession, Depends(get_db)] in auth.py:39 | apps/backend/app/api/auth.py#L39 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | Valid DI usage with Annotated[AsyncSession, Depends(get_db)] in auth.py:61 | apps/backend/app/api/auth.py#L61 |
| `C3|CLASS|BARE` | false_pos | **no (overturn)** | Valid DI pattern with Annotated[AsyncSession, Depends(get_db)] in auth.py:90 | apps/backend/app/api/auth.py#L90 |
| `C1|PARAM|BARE` | true | yes | Valid state dependency injection with Depends(get_state) in drone.py:116 | apps/backend/app/api/drone.py#L116 |
| `C1|PARAM|BARE` | true | yes | Valid state dependency injection with Depends(get_state) in drone.py:169 | apps/backend/app/api/drone.py#L169 |
| `C2|FUNC|BARE` | true | yes | Valid nested dependency chain (get_adapter depends on get_state) in dependencies.py:38 | apps/backend/app/dependencies.py#L38 |

### Missed by inventory (2)
- `Annotated dependency with metadata` @ apps/backend/app/api/auth.py#L39 — Annotated[AsyncSession, Depends(get_db)] pattern not captured in inventory
- `Nested dependency chain` @ apps/backend/app/dependencies.py#L38 — get_adapter depends on get_state relationship not captured in inventory

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 50 | **false_pos** | [apps/backend/app/api/auth.py#L39](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/apps/backend/app/api/auth.py#L39) |
| `C1|BARE|PARAM` | C1 | 26 | **known** | [apps/backend/app/api/auth.py#L39](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/apps/backend/app/api/auth.py#L39) |
| `C4|DEF` | C4 | 24 | **false_pos** | [adapter_demo.py#L290](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/adapter_demo.py#L290) |
| `C1|BARE|SIG` | C1 | 3 | **false_pos** | [apps/backend/app/api/analytics.py#L37](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/apps/backend/app/api/analytics.py#L37) |
| `C4|USED` | C4 | 1 | **false_pos** | [services/database_manager/database.py#L52](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/services/database_manager/database.py#L52) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 50 · corpus total: 20139 · executor: x86_64
> example: [apps/backend/app/api/auth.py#L39](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/apps/backend/app/api/auth.py#L39)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C1|BARE|PARAM` — **known**
> occurrences here: 26 · corpus total: 18195 · executor: x86_64
> example: [apps/backend/app/api/auth.py#L39](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/apps/backend/app/api/auth.py#L39)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 24 · corpus total: 56644 · executor: x86_64
> example: [adapter_demo.py#L290](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/adapter_demo.py#L290)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 83548 · executor: x86_64
> example: [apps/backend/app/api/analytics.py#L37](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/apps/backend/app/api/analytics.py#L37)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [services/database_manager/database.py#L52](https://github.com/COS301-SE-2026/Gesture-Based-Drone-Control/blob/f81f666bd8a99b5e986d58ff455c3f2b5e065769/services/database_manager/database.py#L52)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

