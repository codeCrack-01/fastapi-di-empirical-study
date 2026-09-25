# tuannguyen8531/novel-ai-trans

- GitHub: https://github.com/tuannguyen8531/novel-ai-trans
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 26 · commit: `98d939977185`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Annotated Depends` | src/api/dependencies.py#L36 | Defines AuthenticatedPrincipal = Annotated[Principal, Depends(authenticate)] which uses FastAPI's Depends() to inject authentication into route parameters. Similar patterns for HealthPrincipal and ... |
| 2 | `Dependency Injection in Route Parameters` | src/api/routes/jobs.py#L131 | Uses JobManagerDependency (defined as Annotated[JobManager, Depends(get_job_manager)]) as a parameter in the stream_events route, demonstrating injection of a JobManager instance via FastAPI's depe... |

## Pass 2 — reconcile with inventory of tuannguyen8531/novel-ai-trans

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends()` in `Annotated` type definitions (e.g., `AuthenticatedPrincipal = Annotated[Principal, Depends(authenticate)]`), which are valid DI occurrences. | src/api/dependencies.py#L36 |
| `C1|BARE|PARAM` | known | yes | The code defines parameter-level DI via `Annotated[JobManager, Depends(...)]` and `Annotated[Principal, Depends(...)]`, which aligns with the 'known' label for parameter-based DI. | src/api/dependencies.py#L36 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code uses `Annotated` with `Depends()` for parameter injection, not class-level DI. The static inventory incorrectly labeled this as a class-based false positive. | src/api/dependencies.py#L36 |

### Missed by inventory (2)
- `Annotated[... , Depends(...)] in route parameters` @ src/api/routes/jobs.py#L131 — The inventory missed DI occurrences in route parameters like `jobs: JobManagerDependency` (defined via `Annotated[JobManager, Depends(...)]`)
- `Context managers with dependency injection` @ src/api/factory.py#L29 — The inventory did not capture DI in `_lifespan` context manager, which uses `AppState` and `JobManager` via dependency injection

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 20 | **false_pos** | [src/api/factory.py#L29](https://github.com/tuannguyen8531/novel-ai-trans/blob/98d9399771858b43fe9126c470ead0c9390d75c2/src/api/factory.py#L29) |
| `C1|BARE|PARAM` | C1 | 3 | **known** | [src/api/dependencies.py#L36](https://github.com/tuannguyen8531/novel-ai-trans/blob/98d9399771858b43fe9126c470ead0c9390d75c2/src/api/dependencies.py#L36) |
| `C3|CLASS|BARE` | C3 | 3 | **false_pos** | [src/api/dependencies.py#L36](https://github.com/tuannguyen8531/novel-ai-trans/blob/98d9399771858b43fe9126c470ead0c9390d75c2/src/api/dependencies.py#L36) |

## `C4|DEF` — **false_pos**
> occurrences here: 20 · corpus total: 56644 · executor: x86_64
> example: [src/api/factory.py#L29](https://github.com/tuannguyen8531/novel-ai-trans/blob/98d9399771858b43fe9126c470ead0c9390d75c2/src/api/factory.py#L29)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 3 · corpus total: 18195 · executor: x86_64
> example: [src/api/dependencies.py#L36](https://github.com/tuannguyen8531/novel-ai-trans/blob/98d9399771858b43fe9126c470ead0c9390d75c2/src/api/dependencies.py#L36)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 3 · corpus total: 20139 · executor: x86_64
> example: [src/api/dependencies.py#L36](https://github.com/tuannguyen8531/novel-ai-trans/blob/98d9399771858b43fe9126c470ead0c9390d75c2/src/api/dependencies.py#L36)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

