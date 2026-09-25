# Quantrail-Data/CH-AdNova

- GitHub: https://github.com/Quantrail-Data/CH-AdNova
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 29 · commit: `cb4a12a186c0`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | backend/app/routers/analytics.py#L34 | Route uses Depends(get_repo) and Depends(get_settings) to inject dependencies explicitly |
| 2 | `FastAPI Depends-based injection` | backend/app/routers/analytics.py#L53 | Anomaly route adds store: AnomalyStore = Depends(get_anomaly_store) to its dependencies |
| 3 | `FastAPI Depends-based injection` | backend/app/routers/chat.py#L14 | Chat route injects repo, llm, and settings via Depends() with explicit dependency functions |
| 4 | `FastAPI Depends-based injection` | backend/app/routers/health.py#L8 | Health endpoint uses repo: ClickHouseRepository = Depends(get_repo) for dependency injection |
| 5 | `FastAPI Depends-based injection` | backend/app/routers/investigate.py#L17 | Investigate route uses service: InvestigationService = Depends(get_investigation_service) |

## Pass 2 — reconcile with inventory of Quantrail-Data/CH-AdNova

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI Depends() for dependency injection (repo, settings, store) in analytics.py routes. The static instrument incorrectly labeled this as false_pos. | backend/app/routers/analytics.py#L34 |
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly implements context managers with dependency injection (deps.tracer.agent_span in common.py, lifespan contextmanager in main.py, and langfuse_tracer.py's agent_span). The static i... | backend/app/agents/common.py#L23 |

### Missed by inventory (3)
- `FastAPI Depends-based injection` @ backend/app/routers/investigate.py#L17 — The investigate route uses service: InvestigationService = Depends(get_investigation_service) which was not captured in the initial inventory
- `FastAPI Depends-based injection` @ backend/app/routers/metrics.py#L30 — The kpis endpoint uses repo: ClickHouseRepository = Depends(get_repo) which was not captured in the initial inventory
- `Context manager with dependency injection` @ backend/app/observability/langfuse_tracer.py#L44 — The agent_span contextmanager in langfuse_tracer.py was not captured in the initial inventory

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 24 | **false_pos** | [backend/app/routers/analytics.py#L34](https://github.com/Quantrail-Data/CH-AdNova/blob/cb4a12a186c0ec20ac2ba7b874ea311ed303d3ae/backend/app/routers/analytics.py#L34) |
| `C4|DEF` | C4 | 5 | **false_pos** | [backend/app/agents/common.py#L23](https://github.com/Quantrail-Data/CH-AdNova/blob/cb4a12a186c0ec20ac2ba7b874ea311ed303d3ae/backend/app/agents/common.py#L23) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 24 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routers/analytics.py#L34](https://github.com/Quantrail-Data/CH-AdNova/blob/cb4a12a186c0ec20ac2ba7b874ea311ed303d3ae/backend/app/routers/analytics.py#L34)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [backend/app/agents/common.py#L23](https://github.com/Quantrail-Data/CH-AdNova/blob/cb4a12a186c0ec20ac2ba7b874ea311ed303d3ae/backend/app/agents/common.py#L23)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

