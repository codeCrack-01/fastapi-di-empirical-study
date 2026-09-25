# google-gemini/robotics-samples

- GitHub: https://github.com/google-gemini/robotics-samples
- Stars: 93 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 8 · commit: `c51cbab6e6ef`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `State-based dependency retrieval` | live-api/agent/server.py#L157 | The code retrieves 'poller' from request.app.state.active_poller_ref, indicating dependencies are accessed via application state rather than being created locally. |
| 2 | `State-based dependency retrieval` | live-api/agent/server.py#L151 | The code accesses 'ui_dir' via request.app.state.ui_dir, showing dependencies are injected through FastAPI's application state. |

## Pass 2 — reconcile with inventory of google-gemini/robotics-samples

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts for C4|DEF (camera_poller.py:165, robot_client.py:153, tts_client.py:93) do not show dependency injection (DI) patterns. They contain async/await and generator logic, but no expli... | live-api/agent/camera_poller.py#L165 |

### Missed by inventory (1)
- `State-based dependency retrieval via FastAPI application state` @ live-api/agent/server.py#L157 — The code retrieves 'poller' from request.app.state.active_poller_ref and 'ui_dir' from request.app.state.ui_dir, which are valid DI patterns (state injection) but were not captured by the initial i...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 8 | **false_pos** | [live-api/agent/camera_poller.py#L165](https://github.com/google-gemini/robotics-samples/blob/c51cbab6e6efffff8738ecf9ce41ba85034d9654/live-api/agent/camera_poller.py#L165) |

## `C4|DEF` — **false_pos**
> occurrences here: 8 · corpus total: 56644 · executor: x86_64
> example: [live-api/agent/camera_poller.py#L165](https://github.com/google-gemini/robotics-samples/blob/c51cbab6e6efffff8738ecf9ce41ba85034d9654/live-api/agent/camera_poller.py#L165)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

