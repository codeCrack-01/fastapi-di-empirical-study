# asfrosche/VillageGameBot

- GitHub: https://github.com/asfrosche/VillageGameBot
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 21 · commit: `bd762b6a877d`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI route-level dependency injection` | analytics_dashboard/api/cogs.py#L11 | The `cog_stats` endpoint uses `db=Depends(get_db)` to inject a database dependency, demonstrating FastAPI's route-level DI pattern. |
| 2 | `Router-level dependency injection` | analytics_dashboard/main.py#L40 | The `create_app` function applies `dependencies=[Depends(auth)]` to multiple routers, showing DI at the router level for authentication. |
| 3 | `Custom dependency creation` | analytics_dashboard/auth.py#L13 | The `create_auth_dependency` function generates a `verify_auth` dependency for HTTP Basic Auth, illustrating custom DI providers. |
| 4 | `Context manager as dependency` | cogs/game_manager_en.py#L56 | The `get_db` context manager provides database connections, which are injected via `Depends(get_db)` in API routes. |

## Pass 2 — reconcile with inventory of asfrosche/VillageGameBot

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses `Depends(get_db)` in route definitions (e.g., `cog_stats` in `analytics_dashboard/api/cogs.py#L11`), which is a valid FastAPI DI pattern. | analytics_dashboard/api/cogs.py#L11 |
| `C1|BARE|PARAM` | known | yes | Router-level DI via `dependencies=[Depends(auth)]` in `analytics_dashboard/main.py#L40` matches the known pattern of parameterized dependencies. | analytics_dashboard/main.py#L40 |
| `C4|DEF` | false_pos | yes | The `_connect` context manager in `cogs/library_cog.py#L81` is not used as a DI dependency (no `Depends(...)` invocation exists for it in the repo). | cogs/library_cog.py#L81 |
| `C4|USED` | true_pos | **no (overturn)** | The `get_db` context manager in `cogs/game_manager_en.py#L56` is explicitly used as a DI dependency via `Depends(get_db)` in API routes (e.g., `analytics_dashboard/api/cogs.py#L11`). | cogs/game_manager_en.py#L56 |

### Missed by inventory (2)
- `Custom dependency creation with `Depends(...)`` @ analytics_dashboard/auth.py#L13 — The `create_auth_dependency` function generates a `verify_auth` dependency, but the inventory did not capture this as a DI pattern.
- `Context manager as DI provider` @ cogs/game_manager_en.py#L56 — The `get_db` context manager is used as a DI provider via `Depends(get_db)`, but the inventory missed this occurrence.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 11 | **false_pos** | [analytics_dashboard/api/cogs.py#L11](https://github.com/asfrosche/VillageGameBot/blob/bd762b6a877da8000762ac705de544cd26619266/analytics_dashboard/api/cogs.py#L11) |
| `C1|BARE|PARAM` | C1 | 6 | **known** | [analytics_dashboard/main.py#L39](https://github.com/asfrosche/VillageGameBot/blob/bd762b6a877da8000762ac705de544cd26619266/analytics_dashboard/main.py#L39) |
| `C4|DEF` | C4 | 2 | **false_pos** | [cogs/library_cog.py#L81](https://github.com/asfrosche/VillageGameBot/blob/bd762b6a877da8000762ac705de544cd26619266/cogs/library_cog.py#L81) |
| `C4|USED` | C4 | 2 | **false_pos** | [cogs/game_manager_en.py#L56](https://github.com/asfrosche/VillageGameBot/blob/bd762b6a877da8000762ac705de544cd26619266/cogs/game_manager_en.py#L56) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 11 · corpus total: 83548 · executor: x86_64
> example: [analytics_dashboard/api/cogs.py#L11](https://github.com/asfrosche/VillageGameBot/blob/bd762b6a877da8000762ac705de544cd26619266/analytics_dashboard/api/cogs.py#L11)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 6 · corpus total: 18195 · executor: x86_64
> example: [analytics_dashboard/main.py#L39](https://github.com/asfrosche/VillageGameBot/blob/bd762b6a877da8000762ac705de544cd26619266/analytics_dashboard/main.py#L39)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [cogs/library_cog.py#L81](https://github.com/asfrosche/VillageGameBot/blob/bd762b6a877da8000762ac705de544cd26619266/cogs/library_cog.py#L81)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [cogs/game_manager_en.py#L56](https://github.com/asfrosche/VillageGameBot/blob/bd762b6a877da8000762ac705de544cd26619266/cogs/game_manager_en.py#L56)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

