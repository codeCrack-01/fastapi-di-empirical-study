# theSamPadilla/montaj

- GitHub: https://github.com/theSamPadilla/montaj
- Stars: 25 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 68 · commit: `ec428a7fea87`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Global State Registry for Async Jobs` | serve/routes/projects.py#L2510 | The code uses module-level dictionaries (_render_jobs, _caption_jobs) and sets (_render_task_refs) to track asynchronous operations. This allows status polling endpoints (e.g., /render/status) to a... |

## Pass 2 — reconcile with inventory of theSamPadilla/montaj

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `global_state_registry_async_jobs` | Global State Registry for Async Jobs | yes | Module-level dictionaries (_render_jobs, _caption_jobs) and sets (_render_task_refs) track async operations, enabling decoupled status polling. This matches the observation in serve/routes/projects... | serve/routes/projects.py#L2510 |

### Missed by inventory (3)
- `SSE streaming for real-time updates` @ serve/routes/projects.py#L1444 — The code uses SSE (Server-Sent Events) via sse_stream and broadcaster.subscribe to stream project state changes in real-time, but this wasn't mentioned in the initial observations.
- `Dependency injection via FastAPI Depends` @ serve/routes/projects.py#L2920 — The generate_captions route uses project_dir: Path = Depends(get_project_dir) for dependency injection, but this wasn't noted in the initial observations.
- `Robust error handling for I/O operations` @ lib/remote_io.py#L241 — The _file_iter function handles exceptions like TimeoutException, TransportError, and OSError with specific error responses, but this wasn't highlighted in the initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 39 | **false_pos** | [cli/commands/clean.py#L148](https://github.com/theSamPadilla/montaj/blob/ec428a7fea874b826c3d8f47958cdb7bd6d20d6c/cli/commands/clean.py#L148) |
| `C1|BARE|SIG` | C1 | 29 | **false_pos** | [serve/routes/projects.py#L1354](https://github.com/theSamPadilla/montaj/blob/ec428a7fea874b826c3d8f47958cdb7bd6d20d6c/serve/routes/projects.py#L1354) |

## `C4|DEF` — **false_pos**
> occurrences here: 39 · corpus total: 56644 · executor: x86_64
> example: [cli/commands/clean.py#L148](https://github.com/theSamPadilla/montaj/blob/ec428a7fea874b826c3d8f47958cdb7bd6d20d6c/cli/commands/clean.py#L148)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 29 · corpus total: 83548 · executor: x86_64
> example: [serve/routes/projects.py#L1354](https://github.com/theSamPadilla/montaj/blob/ec428a7fea874b826c3d8f47958cdb7bd6d20d6c/serve/routes/projects.py#L1354)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

