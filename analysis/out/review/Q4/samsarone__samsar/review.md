# samsarone/samsar

- GitHub: https://github.com/samsarone/samsar
- Stars: 55 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 7 · commit: `444734948be7`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends usage for authentication` | utils/vast-flux2/scripts/vast-flux2/server.py#L288 | The generate endpoint uses Depends(_require_auth) to inject an authentication dependency, indicating FastAPI's built-in DI system is used for request validation. |
| 2 | `Manual runtime injection via factory` | services/genblaze-gateway/app/main.py#L27 | The create_app function accepts a runtime_factory parameter that constructs GatewayRuntime instances, demonstrating manual DI where the application's runtime is injected through a factory pattern. |

## Pass 2 — reconcile with inventory of samsarone/samsar

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses manual DI via a runtime_factory parameter in create_app(), which constructs GatewayRuntime instances. This matches the C4|DEF fingerprint's structural pattern of factory-ba... | services/genblaze-gateway/app/main.py#L27 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The generate endpoint uses FastAPI's built-in DI system via Depends(_require_auth), which is a canonical example of the C1|BARE|SIG fingerprint pattern (signal-based dependency injection through Fa... | utils/vast-flux2/scripts/vast-flux2/server.py#L288 |

### Missed by inventory (1)
- `Manual DI via context manager lifespan hooks` @ utils/vast-flux2/scripts/vast-flux2/server.py#L239 — The _lifespan context manager demonstrates DI through resource initialization/teardown patterns (pipeline loading, thread management) that were not captured in the fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [services/genblaze-gateway/app/main.py#L27](https://github.com/samsarone/samsar/blob/444734948be7a9063090130a11a4e7fe8aad6ca0/services/genblaze-gateway/app/main.py#L27) |
| `C1|BARE|SIG` | C1 | 3 | **false_pos** | [utils/vast-flux2/scripts/vast-flux2/server.py#L288](https://github.com/samsarone/samsar/blob/444734948be7a9063090130a11a4e7fe8aad6ca0/utils/vast-flux2/scripts/vast-flux2/server.py#L288) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [services/genblaze-gateway/app/main.py#L27](https://github.com/samsarone/samsar/blob/444734948be7a9063090130a11a4e7fe8aad6ca0/services/genblaze-gateway/app/main.py#L27)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 83548 · executor: x86_64
> example: [utils/vast-flux2/scripts/vast-flux2/server.py#L288](https://github.com/samsarone/samsar/blob/444734948be7a9063090130a11a4e7fe8aad6ca0/utils/vast-flux2/scripts/vast-flux2/server.py#L288)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

