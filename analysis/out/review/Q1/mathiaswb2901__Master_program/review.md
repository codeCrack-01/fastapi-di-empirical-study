# mathiaswb2901/Master_program

- GitHub: https://github.com/mathiaswb2901/Master_program
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 42 · commit: `ded9fb01e393`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `app state storage` | server/src/workbench_server/main.py#L495 | The code stores services like `workspace_service`, `watcher`, and `shortcuts_service` in the app's state, which is accessed later via `app.state` in routes (e.g., `server/src/workbench_server/route... |
| 2 | `app state access` | server/src/workbench_server/routers/agents.py#L173 | The route accesses `ws.app.state.session_manager` to retrieve a session manager, indicating that dependencies are stored in the app state and manually retrieved rather than injected via FastAPI's D... |

## Pass 2 — reconcile with inventory of mathiaswb2901/Master_program

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code uses manual app state storage for services (e.g., `workspace_service`, `watcher`), which is not FastAPI's DI system but a form of manual dependency management. The panel's label of 'false_... | server/src/workbench_server/main.py#L495 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 42 | **false_pos** | [server/src/workbench_server/main.py#L495](https://github.com/mathiaswb2901/Master_program/blob/ded9fb01e3932631eec30463e70009225a8d774c/server/src/workbench_server/main.py#L495) |

## `C4|DEF` — **false_pos**
> occurrences here: 42 · corpus total: 56644 · executor: x86_64
> example: [server/src/workbench_server/main.py#L495](https://github.com/mathiaswb2901/Master_program/blob/ded9fb01e3932631eec30463e70009225a8d774c/server/src/workbench_server/main.py#L495)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

