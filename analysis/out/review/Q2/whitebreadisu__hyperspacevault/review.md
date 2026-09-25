# whitebreadisu/hyperspacevault

- GitHub: https://github.com/whitebreadisu/hyperspacevault
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 87 · commit: `b821a69e7c06`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection` | backend/app/routers/inventory.py#L212 | The `import_inventory` endpoint uses `Depends(get_db)` to inject a tenant-scoped database session. This follows FastAPI's DI pattern where dependencies like database sessions are resolved and injec... |
| 2 | `FastAPI Dependency Injection` | backend/app/routers/settings.py#L19 | The `get_limits` endpoint uses `Depends(get_db)` to inject a database session. This is a standard DI pattern in FastAPI, where dependencies are declared with `Depends()` and resolved by the framewo... |
| 3 | `FastAPI Dependency Injection` | backend/app/routers/shares.py#L168 | The `resolve_share` endpoint uses `Depends(get_shared_db)` to inject a token-scoped database session. This demonstrates DI where the session is injected based on the share token, rather than being ... |
| 4 | `FastAPI Dependency Injection` | backend/app/database.py#L185 | The `get_db` function is a FastAPI dependency that yields a tenant-scoped database session. It is used across multiple routes, exemplifying DI by centralizing session management and injecting it in... |

## Pass 2 — reconcile with inventory of whitebreadisu/hyperspacevault

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `pass1_observation_1` | FastAPI Dependency Injection @ backend/app/routers/inventory.py:212 | yes | The code confirms import_inventory uses Depends(get_db) for tenant-scoped sessions as observed | backend/app/routers/inventory.py#L212 |
| `pass1_observation_2` | FastAPI Dependency Injection @ backend/app/routers/settings.py:19 | yes | The code shows get_limits explicitly uses Depends(get_db) as observed | backend/app/routers/settings.py#L19 |
| `pass1_observation_3` | FastAPI Dependency Injection @ backend/app/routers/shares.py:168 | yes | resolve_share's use of Depends(get_shared_db) matches the code implementation | backend/app/routers/shares.py#L168 |
| `pass1_observation_4` | FastAPI Dependency Injection @ backend/app/database.py:185 | yes | get_db's tenant-scoped session implementation matches the observation | backend/app/database.py#L185 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 41 | **false_pos** | [backend/app/main.py#L28](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/main.py#L28) |
| `C1|BARE|SIG` | C1 | 30 | **false_pos** | [backend/app/auth.py#L103](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/auth.py#L103) |
| `C1|BARE|PARAM` | C1 | 12 | **known** | [backend/app/routers/base_cards.py#L34](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/routers/base_cards.py#L34) |
| `C4|USED` | C4 | 4 | **false_pos** | [backend/app/database.py#L156](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/database.py#L156) |

## `C4|DEF` — **false_pos**
> occurrences here: 41 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L28](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/main.py#L28)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 30 · corpus total: 83548 · executor: x86_64
> example: [backend/app/auth.py#L103](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/auth.py#L103)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 12 · corpus total: 18195 · executor: x86_64
> example: [backend/app/routers/base_cards.py#L34](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/routers/base_cards.py#L34)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 4 · corpus total: 1079 · executor: x86_64
> example: [backend/app/database.py#L156](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/database.py#L156)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

