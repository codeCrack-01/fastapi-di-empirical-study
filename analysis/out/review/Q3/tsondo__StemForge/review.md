# tsondo/StemForge

- GitHub: https://github.com/tsondo/StemForge
- Stars: 21 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 72 · commit: `4b753372a04d`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | backend/api/audio.py#L14 | The `session` parameter uses `Depends(get_user_session)` to inject a user session, a common FastAPI DI pattern. |
| 2 | `FastAPI Depends injection` | backend/api/enhance.py#L15 | The `session` parameter uses `Depends(get_user_session)` to inject a user session, consistent with the DI pattern observed in audio.py. |
| 3 | `Direct dependency resolution` | backend/api/compose.py#L28 | The `backend` variable is resolved directly via `get_compose_backend()` without using `Depends()`, indicating a mix of DI approaches. |

## Pass 2 — reconcile with inventory of tsondo/StemForge

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | yes | The code explicitly resolves dependencies via direct function calls (e.g., `get_compose_backend()`) without using FastAPI's `Depends()` injection, which aligns with the inventory's label of false_pos. | backend/api/compose.py#L28 |
| `C4|DEF` | false_pos | yes | The code uses direct dependency resolution (e.g., `get_compose_backend()`) in `pipeline_manager.py` and `inference.py`, consistent with the inventory's false_pos label. | backend/api/compose.py#L28 |

### Missed by inventory (1)
- `Mix of DI approaches (Depends vs direct resolution)` @ backend/api/compose.py#L28 — The inventory may have overlooked that some parts of the codebase use `Depends()` (e.g., `audio.py`, `enhance.py`) while others use direct resolution (e.g., `compose.py`), indicating inconsistent D...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 68 | **false_pos** | [backend/api/audio.py#L47](https://github.com/tsondo/StemForge/blob/4b753372a04d4e72ffe330e3ec6f510dcd93c29b/backend/api/audio.py#L47) |
| `C4|DEF` | C4 | 4 | **false_pos** | [backend/services/pipeline_manager.py#L102](https://github.com/tsondo/StemForge/blob/4b753372a04d4e72ffe330e3ec6f510dcd93c29b/backend/services/pipeline_manager.py#L102) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 68 · corpus total: 83548 · executor: x86_64
> example: [backend/api/audio.py#L47](https://github.com/tsondo/StemForge/blob/4b753372a04d4e72ffe330e3ec6f510dcd93c29b/backend/api/audio.py#L47)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [backend/services/pipeline_manager.py#L102](https://github.com/tsondo/StemForge/blob/4b753372a04d4e72ffe330e3ec6f510dcd93c29b/backend/services/pipeline_manager.py#L102)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

