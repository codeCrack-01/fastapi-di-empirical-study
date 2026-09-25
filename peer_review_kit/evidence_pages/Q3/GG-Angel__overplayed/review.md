# GG-Angel/overplayed

- GitHub: https://github.com/GG-Angel/overplayed
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 54 · commit: `0ae33e785f61`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection with Depends()` | apps/api/src/core/database.py#L26 | The async function get_db uses Depends(get_state) to inject the State object, which is part of FastAPI's dependency injection system. |
| 2 | `Layered dependencies` | apps/api/src/services/previews/dependencies.py#L13 | The get_deezer_service function depends on multiple other dependencies (get_session, get_redis_client, get_settings), showing a layered approach to dependency injection. |
| 3 | `Async generator dependencies` | apps/api/src/core/redis.py#L16 | The get_redis function is an async generator that yields a Redis connection, demonstrating how FastAPI handles async dependencies. |
| 4 | `Service composition via dependencies` | apps/api/src/services/spotify/dependencies.py#L22 | The get_spotify_service function composes multiple dependencies (get_spotify_cache, get_oauth, get_database_service) to create a SpotifyService instance. |
| 5 | `Route handler dependencies` | apps/api/src/routes/auth.py#L27 | The handle_login route uses Depends(get_oauth) to inject the SpotifyOAuth object directly into the route handler. |

## Pass 2 — reconcile with inventory of GG-Angel/overplayed

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses RedisClient and Redis via Depends() in route handlers and service dependencies, confirming real DI usage. | apps/api/src/core/redis.py#L16 |
| `C4|DEF` | true_pos | **no (overturn)** | The code uses Depends(get_spotify_service) in route handlers and composes dependencies in service layers, confirming real DI usage. | apps/api/src/routes/playlists.py#L47 |
| `C4|USED` | true_pos | **no (overturn)** | The code uses Depends(get_state) and Depends(get_redis_client) in async generators and service dependencies, confirming real DI usage. | apps/api/src/core/database.py#L26 |

### Missed by inventory (2)
- `Dependency composition in service layers` @ apps/api/src/services/spotify/dependencies.py#L22 — The inventory missed the layered composition of SpotifyService via multiple Depends() dependencies (get_oauth, get_redis_client, etc.).
- `Async generator DI in route handlers` @ apps/api/src/core/redis.py#L16 — The inventory missed the async generator pattern used in get_redis, which yields a Redis connection via Depends().

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 40 | **false_pos** | [apps/api/src/cache/client.py#L91](https://github.com/GG-Angel/overplayed/blob/0ae33e785f611238c276f8b65586d9cce945a76f/apps/api/src/cache/client.py#L91) |
| `C4|DEF` | C4 | 12 | **false_pos** | [apps/api/src/routes/playlists.py#L47](https://github.com/GG-Angel/overplayed/blob/0ae33e785f611238c276f8b65586d9cce945a76f/apps/api/src/routes/playlists.py#L47) |
| `C4|USED` | C4 | 2 | **false_pos** | [apps/api/src/core/database.py#L26](https://github.com/GG-Angel/overplayed/blob/0ae33e785f611238c276f8b65586d9cce945a76f/apps/api/src/core/database.py#L26) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 40 · corpus total: 83548 · executor: x86_64
> example: [apps/api/src/cache/client.py#L91](https://github.com/GG-Angel/overplayed/blob/0ae33e785f611238c276f8b65586d9cce945a76f/apps/api/src/cache/client.py#L91)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 12 · corpus total: 56644 · executor: x86_64
> example: [apps/api/src/routes/playlists.py#L47](https://github.com/GG-Angel/overplayed/blob/0ae33e785f611238c276f8b65586d9cce945a76f/apps/api/src/routes/playlists.py#L47)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [apps/api/src/core/database.py#L26](https://github.com/GG-Angel/overplayed/blob/0ae33e785f611238c276f8b65586d9cce945a76f/apps/api/src/core/database.py#L26)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

