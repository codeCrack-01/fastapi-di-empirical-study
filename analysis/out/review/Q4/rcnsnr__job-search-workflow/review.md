# rcnsnr/job-search-workflow

- GitHub: https://github.com/rcnsnr/job-search-workflow
- Stars: 60 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 3 · commit: `84bbbe0eb0e0`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI Dependency Injection` | scripts/scan_pii.py#L104 | The code shows standard file iteration logic with Path objects but contains no FastAPI-specific dependency injection constructs like Depends(), Security(), or annotated dependencies. |
| 2 | `No FastAPI Dependency Injection` | scripts/workflow_guard.py#L74 | The iter_job_records function uses Path objects and yields data but lacks any FastAPI dependency injection patterns or annotations. |
| 3 | `No FastAPI Dependency Injection` | tests/test_linkedin_capture_server.py#L16 | The TestClient setup uses FastAPI but does not demonstrate any dependency injection patterns in the test code. |

## Pass 2 — reconcile with inventory of rcnsnr/job-search-workflow

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No FastAPI DI constructs (e.g., Depends(), Security()) are present in the code excerpts. The functions shown are standard file iteration, metadata parsing, and test setup without dependency injection. | scripts/scan_pii.py#L104 |
| `C4|DEF` | false_pos | yes | The iter_job_records function uses Path objects and yields data but lacks any FastAPI DI patterns or annotations. | scripts/workflow_guard.py#L74 |
| `C4|DEF` | false_pos | yes | The test code uses FastAPI's TestClient but does not demonstrate any dependency injection patterns in the test logic. | tests/test_linkedin_capture_server.py#L16 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 3 | **false_pos** | [scripts/scan_pii.py#L104](https://github.com/rcnsnr/job-search-workflow/blob/84bbbe0eb0e0274dee3d15283e6307b53c3dff87/scripts/scan_pii.py#L104) |

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [scripts/scan_pii.py#L104](https://github.com/rcnsnr/job-search-workflow/blob/84bbbe0eb0e0274dee3d15283e6307b53c3dff87/scripts/scan_pii.py#L104)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

