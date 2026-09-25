# freemocap/freemocap

- GitHub: https://github.com/freemocap/freemocap
- Stars: 9954 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 5 · commit: `e547707afc4e`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No explicit dependency injection` | freemocap/app/app.py#L329 | The app_lifespan function handles startup/shutdown logic but contains no Depends() or other FastAPI DI constructs. It manually manages resources like directories and logging. |
| 2 | `Test fixture mocking` | freemocap/tests/http/test_calibration_router_recording_state.py#L37 | Test code uses pytest fixtures to mock dependencies (e.g., app.realtime_pipeline_manager) but this is test infrastructure, not production DI. |
| 3 | `Manual dependency setup` | freemocap/tests/http/test_mocap_router_import.py#L36 | Test code creates a _FakeApp class with manually injected SyncJobManager, but this is test-specific and not production DI. |

## Pass 2 — reconcile with inventory of freemocap/freemocap

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts show no explicit FastAPI dependency injection (e.g., Depends(), DI constructs), only manual resource management and test-specific mocking. The app_lifespan function handles startu... | freemocap/app/app.py#L329 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 5 | **false_pos** | [freemocap/app/app.py#L329](https://github.com/freemocap/freemocap/blob/e547707afc4ebd368d3cc54718db2601434585eb/freemocap/app/app.py#L329) |

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [freemocap/app/app.py#L329](https://github.com/freemocap/freemocap/blob/e547707afc4ebd368d3cc54718db2601434585eb/freemocap/app/app.py#L329)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

