# doronz88/pymobiledevice3

- GitHub: https://github.com/doronz88/pymobiledevice3
- Stars: 2611 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 108 · commit: `fc0d053411fa`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends usage` | pymobiledevice3/cli/restore.py#L12 | The code defines 'DeviceDep' using 'Depends(device_dependency)', which is FastAPI's dependency injection pattern. This indicates explicit DI setup via framework-specific decorators. |

## Pass 2 — reconcile with inventory of doronz88/pymobiledevice3

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `async_generator_usage_in_services` | AsyncGenerator usage in multiple services | yes | Multiple services (e.g., tunnel_service, accessibilityaudit, afc) use AsyncGenerator with yield and async for loops | pymobiledevice3/remote/tunnel_service.py#L1443 |
| `fastapi_dependency_injection` | FastAPI Depends usage in CLI | yes | cli/restore.py uses Depends(device_dependency) for dependency injection | pymobiledevice3/cli/restore.py#L12 |
| `asynccontextmanager_usage` | Async context managers with @asynccontextmanager | yes | Multiple files use @asynccontextmanager and async with blocks (e.g., tunnel_service.py) | pymobiledevice3/remote/tunnel_service.py#L1443 |

### Missed by inventory (1)
- `specific_error_handling_patterns` @ pymobiledevice3/remote/utils.py#L94 — Error handling with AccessDeniedError not captured in initial inventory

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 108 | **false_pos** | [pymobiledevice3/cli/developer/dvt/sysmon/process.py#L277](https://github.com/doronz88/pymobiledevice3/blob/fc0d053411fa1d3c9e80efc17962dc6b4e50526d/pymobiledevice3/cli/developer/dvt/sysmon/process.py#L277) |

## `C4|DEF` — **false_pos**
> occurrences here: 108 · corpus total: 56644 · executor: x86_64
> example: [pymobiledevice3/cli/developer/dvt/sysmon/process.py#L277](https://github.com/doronz88/pymobiledevice3/blob/fc0d053411fa1d3c9e80efc17962dc6b4e50526d/pymobiledevice3/cli/developer/dvt/sysmon/process.py#L277)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

