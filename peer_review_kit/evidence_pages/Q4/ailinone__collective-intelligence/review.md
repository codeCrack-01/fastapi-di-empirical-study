# ailinone/collective-intelligence

- GitHub: https://github.com/ailinone/collective-intelligence
- Stars: 209 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 16 · commit: `8baa376c8f8f`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI endpoint dependencies` | model-stack/serving/aggregation/coord_serving.py#L639 | The @app.post('/v1/ensemble/decide') endpoint explicitly uses FastAPI's Depends() for dependency injection, with [Depends(_require_rate_limit), Depends(_require_auth)] indicating rate-limiting and ... |

## Pass 2 — reconcile with inventory of ailinone/collective-intelligence

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts show data processing functions (iter_jsonl, _read_jsonl, _read_parquet) that do not involve FastAPI dependency injection or parameterized DI patterns. The static inventory correct... | model-stack/data/ingestion/ingest.py#L55 |
| `C1|BARE|PARAM` | known | yes | The code at coord_serving.py:639 explicitly uses FastAPI's Depends() for rate-limiting and authentication dependencies, confirming the presence of a known DI occurrence with parameterized dependenc... | model-stack/serving/aggregation/coord_serving.py#L639 |

### Missed by inventory (1)
- `FastAPI endpoint dependencies` @ model-stack/serving/aggregation/coord_serving.py#L639 — The inventory correctly captured the C1|BARE|PARAM DI occurrence, but there are additional DI patterns in other endpoints (e.g., /metrics) that were not labeled. However, these may not qualify as '...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 14 | **false_pos** | [model-stack/data/feedback/synthesize_sft.py#L211](https://github.com/ailinone/collective-intelligence/blob/8baa376c8f8f3c3689995e5ae570469ba0fa5d8c/model-stack/data/feedback/synthesize_sft.py#L211) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [model-stack/serving/aggregation/coord_serving.py#L639](https://github.com/ailinone/collective-intelligence/blob/8baa376c8f8f3c3689995e5ae570469ba0fa5d8c/model-stack/serving/aggregation/coord_serving.py#L639) |

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [model-stack/data/feedback/synthesize_sft.py#L211](https://github.com/ailinone/collective-intelligence/blob/8baa376c8f8f3c3689995e5ae570469ba0fa5d8c/model-stack/data/feedback/synthesize_sft.py#L211)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [model-stack/serving/aggregation/coord_serving.py#L639](https://github.com/ailinone/collective-intelligence/blob/8baa376c8f8f3c3689995e5ae570469ba0fa5d8c/model-stack/serving/aggregation/coord_serving.py#L639)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

