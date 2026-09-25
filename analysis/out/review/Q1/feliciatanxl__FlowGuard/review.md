# feliciatanxl/FlowGuard

- GitHub: https://github.com/feliciatanxl/FlowGuard
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 12 · commit: `fa313fa9c1c8`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends for service key validation` | ai-service/main.py#L212 | The endpoint /api/encode-faces uses dependencies=[Depends(require_service_key)] to enforce service key authentication. |
| 2 | `FastAPI Depends for service key validation` | ai-service/main.py#L285 | The endpoint /user/recognize uses dependencies=[Depends(require_service_key)] for service key authentication. |
| 3 | `FastAPI Depends for service key validation` | ai-service/main.py#L384 | The endpoint /user/track uses dependencies=[Depends(require_service_key)] to require a service key. |
| 4 | `FastAPI Depends for service key validation` | ai-service/main.py#L431 | The endpoint /refresh uses dependencies=[Depends(require_service_key)] for service key authentication. |
| 5 | `FastAPI Depends for service key validation` | ai-service/main.py#L520 | The endpoint /api/qr/decode uses dependencies=[Depends(require_service_key)] to enforce service key access. |
| 6 | `FastAPI Depends for service key validation` | ai-service/main.py#L1513 | The endpoint /api/yolo/stream uses dependencies=[Depends(require_service_key)] for service key authentication. |
| 7 | `FastAPI Depends for service key validation` | ai-service/main.py#L1535 | The endpoint /api/yolo/analyze-frame uses dependencies=[Depends(require_service_key)] to require a service key. |
| 8 | `FastAPI Depends for service key validation` | ai-service/main.py#L1578 | The endpoint /api/yolo/people-count uses dependencies=[Depends(require_service_key)] for service key authentication. |

## Pass 2 — reconcile with inventory of feliciatanxl/FlowGuard

_Presented fingerprints:_ `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | The endpoints /api/encode-faces, /user/recognize, and /user/track all correctly use Depends(require_service_key) for authentication, matching the canonical fingerprint. | ai-service/main.py#L212 |
| `C4|DEF` | false_pos | **no (overturn)** | The code at ai-service/main.py:1489 is part of a YOLO stream endpoint (/api/yolo/stream) that does use Depends(require_service_key) in its route definition, contradicting the false_pos label. | ai-service/main.py#L1513 |

### Missed by inventory (1)
- `FastAPI endpoint with service key dependency` @ ai-service/main.py#L431 — The /refresh endpoint uses Depends(require_service_key) but was not included in the initial C1|BARE|PARAM count (n=8).

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 8 | **known** | [ai-service/main.py#L212](https://github.com/feliciatanxl/FlowGuard/blob/fa313fa9c1c8521b5e5cf5589bcb68cd6b191292/ai-service/main.py#L212) |
| `C4|DEF` | C4 | 4 | **false_pos** | [ai-service/main.py#L1489](https://github.com/feliciatanxl/FlowGuard/blob/fa313fa9c1c8521b5e5cf5589bcb68cd6b191292/ai-service/main.py#L1489) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 8 · corpus total: 18195 · executor: x86_64
> example: [ai-service/main.py#L212](https://github.com/feliciatanxl/FlowGuard/blob/fa313fa9c1c8521b5e5cf5589bcb68cd6b191292/ai-service/main.py#L212)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [ai-service/main.py#L1489](https://github.com/feliciatanxl/FlowGuard/blob/fa313fa9c1c8521b5e5cf5589bcb68cd6b191292/ai-service/main.py#L1489)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

