# WiredMind2/AnimeManager

- GitHub: https://github.com/WiredMind2/AnimeManager
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 165 · commit: `9e606eb85b14`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection` | clients/torrent_daemon/app.py#L99 | The code uses FastAPI's `Depends()` to inject `_require_token` into endpoints, e.g., `dependencies=[Depends(_require_token)]`. This is FastAPI's framework-level DI, though not using type-annotated ... |

## Pass 2 — reconcile with inventory of WiredMind2/AnimeManager

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No code contradicts the label; the searchAnime methods in AnilistCo.py and AnidbNet.py use standard parameters (search, limit) consistent with false positives for DI detection. | adapters/api/AnilistCo.py#L298 |
| `C1|BARE|PARAM` | known | yes | The FastAPI endpoints in clients/torrent_daemon/app.py correctly use Depends() for DI, aligning with the 'known' label for bare parameter dependencies. | clients/torrent_daemon/app.py#L99 |

### Missed by inventory (1)
- `FastAPI dependency injection via Depends() without type annotations` @ clients/torrent_daemon/app.py#L99 — The inventory may have missed DI occurrences using Depends() without explicit type annotations, though the panel already labeled these instances.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 157 | **false_pos** | [adapters/api/AnidbNet.py#L223](https://github.com/WiredMind2/AnimeManager/blob/9e606eb85b140035bec92b70e0fca67fccf77d74/adapters/api/AnidbNet.py#L223) |
| `C1|BARE|PARAM` | C1 | 8 | **known** | [clients/torrent_daemon/app.py#L99](https://github.com/WiredMind2/AnimeManager/blob/9e606eb85b140035bec92b70e0fca67fccf77d74/clients/torrent_daemon/app.py#L99) |

## `C4|DEF` — **false_pos**
> occurrences here: 157 · corpus total: 56644 · executor: x86_64
> example: [adapters/api/AnidbNet.py#L223](https://github.com/WiredMind2/AnimeManager/blob/9e606eb85b140035bec92b70e0fca67fccf77d74/adapters/api/AnidbNet.py#L223)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 8 · corpus total: 18195 · executor: x86_64
> example: [clients/torrent_daemon/app.py#L99](https://github.com/WiredMind2/AnimeManager/blob/9e606eb85b140035bec92b70e0fca67fccf77d74/clients/torrent_daemon/app.py#L99)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

