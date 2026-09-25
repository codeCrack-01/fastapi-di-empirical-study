# muju0629/KB_Tune

- GitHub: https://github.com/muju0629/KB_Tune
- Stars: 16 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 8 · commit: `3c2432217517`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency lists` | backend/app/main.py#L39 | Code defines _auth = [Depends(require_api_key)] and combines dependencies into _llm/_cheap lists for reuse across endpoints. These lists are later used in @app.post('/api/chat', dependencies=_llm) ... |
| 2 | `Endpoint-specific dependency injection` | backend/app/main.py#L56 | The /api/health endpoint explicitly uses dependencies=[Depends(rate_limit('cheap'))] to apply a rate-limiting dependency directly to a specific route. |

## Pass 2 — reconcile with inventory of muju0629/KB_Tune

_Presented fingerprints:_ `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | The code explicitly uses Depends() for API key authentication and rate-limiting parameters in _auth, _llm, and _cheap lists, which aligns with the BARE|PARAM fingerprint. | backend/app/main.py#L39 |
| `C4|DEF` | false_pos | yes | The code in chat.py does not use dependency injection (Depends()) in the flagged lines; these are stream processing functions without parameter dependencies. | backend/app/llm/chat.py#L136 |

### Missed by inventory (1)
- `Endpoint-specific dependency injection` @ backend/app/main.py#L56 — The /api/health endpoint uses dependencies=[Depends(rate_limit('cheap'))] explicitly, but this pattern was not captured in the inventory's fingerprint counts.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 4 | **known** | [backend/app/main.py#L39](https://github.com/muju0629/KB_Tune/blob/3c2432217517ddbc5a7e46f1262f94236ef39d05/backend/app/main.py#L39) |
| `C4|DEF` | C4 | 4 | **false_pos** | [backend/app/llm/chat.py#L136](https://github.com/muju0629/KB_Tune/blob/3c2432217517ddbc5a7e46f1262f94236ef39d05/backend/app/llm/chat.py#L136) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 4 · corpus total: 18195 · executor: x86_64
> example: [backend/app/main.py#L39](https://github.com/muju0629/KB_Tune/blob/3c2432217517ddbc5a7e46f1262f94236ef39d05/backend/app/main.py#L39)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [backend/app/llm/chat.py#L136](https://github.com/muju0629/KB_Tune/blob/3c2432217517ddbc5a7e46f1262f94236ef39d05/backend/app/llm/chat.py#L136)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

