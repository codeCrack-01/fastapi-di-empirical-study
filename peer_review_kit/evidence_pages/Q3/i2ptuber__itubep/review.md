# i2ptuber/itubep

- GitHub: https://github.com/i2ptuber/itubep
- Stars: 11 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 19 · commit: `58352a91c0db`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | site/app/main.py#L174 | The register_channel function uses session: AsyncSession = Depends(get_session) to inject a database session. This is a standard FastAPI pattern where dependencies are resolved using the Depends() ... |
| 2 | `Async generator dependency provider` | site/app/database.py#L63 | The get_session function is defined as an async generator that yields an AsyncSession. This allows FastAPI to manage the lifecycle of the session, ensuring it is properly created and closed for eac... |

## Pass 2 — reconcile with inventory of i2ptuber/itubep

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | yes | The code uses FastAPI's Depends() for dependency injection but does not implement cryptographic signatures or bare sig verification patterns as claimed by the fingerprint. The enforce() calls are r... | site/app/main.py#L174 |
| `C4|USED` | true_pos | **no (overturn)** | The get_session() async generator is explicitly used as a dependency in multiple endpoints (e.g., register_channel at line 174), confirming it is actively used in the codebase. | site/app/main.py#L174 |

### Missed by inventory (1)
- `Rate-limiting enforcement via enforce() with unique identifiers` @ site/app/main.py#L174 — The code uses enforce() with specific identifiers (e.g., 'channel_register_global', 'studio_update_id') for rate-limiting, but this pattern was not captured in the fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 18 | **false_pos** | [site/app/main.py#L174](https://github.com/i2ptuber/itubep/blob/58352a91c0db37ad703c93ebb8834d01f1ce5c82/site/app/main.py#L174) |
| `C4|USED` | C4 | 1 | **false_pos** | [site/app/database.py#L63](https://github.com/i2ptuber/itubep/blob/58352a91c0db37ad703c93ebb8834d01f1ce5c82/site/app/database.py#L63) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 18 · corpus total: 83548 · executor: x86_64
> example: [site/app/main.py#L174](https://github.com/i2ptuber/itubep/blob/58352a91c0db37ad703c93ebb8834d01f1ce5c82/site/app/main.py#L174)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [site/app/database.py#L63](https://github.com/i2ptuber/itubep/blob/58352a91c0db37ad703c93ebb8834d01f1ce5c82/site/app/database.py#L63)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

