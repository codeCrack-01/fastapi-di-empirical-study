# center-for-threat-informed-defense/attack-flow

- GitHub: https://github.com/center-for-threat-informed-defense/attack-flow
- Stars: 761 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 4 · commit: `0bd4a2d45dce`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of center-for-threat-informed-defense/attack-flow

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly uses context managers (e.g., lifespan, temporary_json_file, local_server) in appropriate contexts (application setup, testing, mock servers). No DI issues are present in these im... | src/attack_flow_api/main.py#L46 |
| `C4|DEF` | true_pos | **no (overturn)** | The temporary_json_file context manager correctly creates temporary files for testing, which is a valid use case and not a DI issue. | tests/test_schema.py#L85 |
| `C4|DEF` | true_pos | **no (overturn)** | The temporary_flow_file context manager properly constructs Attack Flow bundles for testing, which is a legitimate use of context managers and not a DI issue. | tests/test_schema.py#L96 |
| `C4|DEF` | true_pos | **no (overturn)** | The local_server fixture correctly sets up a mock HTTP server for testing, which is a valid use of context managers and not a DI issue. | tests/test_url_fetch.py#L50 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [src/attack_flow_api/main.py#L46](https://github.com/center-for-threat-informed-defense/attack-flow/blob/0bd4a2d45dceacce499d7e94b85f7966e70f5399/src/attack_flow_api/main.py#L46) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [src/attack_flow_api/main.py#L46](https://github.com/center-for-threat-informed-defense/attack-flow/blob/0bd4a2d45dceacce499d7e94b85f7966e70f5399/src/attack_flow_api/main.py#L46)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

