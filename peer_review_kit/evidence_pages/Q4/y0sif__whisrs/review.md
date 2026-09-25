# y0sif/whisrs

- GitHub: https://github.com/y0sif/whisrs
- Stars: 81 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 6 · commit: `901483516edd`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Manual app.state-based dependency injection` | contrib/asr-sidecars/moonshine/server.py#L82 | The lifespan context manager injects the sidecar into app.state.sidecar, which is later accessed in /health endpoint via app.state.sidecar.model_id |
| 2 | `Manual app.state-based dependency injection` | contrib/asr-sidecars/parakeet/server.py#L83 | Same pattern as moonshine: lifespan sets app.state.sidecar, which is accessed in /health endpoint |
| 3 | `Manual app.state-based dependency injection` | contrib/asr-sidecars/vibevoice/server.py#L98 | Lifespan context manager injects sidecar into app.state, which is accessed in /health endpoint via app.state.sidecar.model_id |

## Pass 2 — reconcile with inventory of y0sif/whisrs

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses app.state.sidecar for dependency injection, which is a valid DI pattern. The lifespan context manager injects the sidecar into app.state, and it is accessed in the /health ... | contrib/asr-sidecars/moonshine/server.py#L82 |
| `C4|DEF` | true_pos | **no (overturn)** | Same pattern as moonshine: lifespan sets app.state.sidecar, which is accessed in /health endpoint. | contrib/asr-sidecars/parakeet/server.py#L83 |
| `C4|DEF` | true_pos | **no (overturn)** | Lifespan context manager injects sidecar into app.state, which is accessed in /health endpoint. | contrib/asr-sidecars/vibevoice/server.py#L98 |

### Missed by inventory (3)
- `app.state-based manual DI` @ contrib/asr-sidecars/moonshine/server.py#L82 — The inventory did not recognize app.state as a valid DI vector, despite explicit usage in lifespan and endpoint access.
- `app.state-based manual DI` @ contrib/asr-sidecars/parakeet/server.py#L83 — Same as moonshine: inventory missed app.state DI pattern.
- `app.state-based manual DI` @ contrib/asr-sidecars/vibevoice/server.py#L98 — Inventory failed to detect app.state DI usage in vibevoice.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 6 | **false_pos** | [contrib/asr-sidecars/moonshine/server.py#L82](https://github.com/y0sif/whisrs/blob/901483516edd60e10f64380480ef1cac07534a08/contrib/asr-sidecars/moonshine/server.py#L82) |

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [contrib/asr-sidecars/moonshine/server.py#L82](https://github.com/y0sif/whisrs/blob/901483516edd60e10f64380480ef1cac07534a08/contrib/asr-sidecars/moonshine/server.py#L82)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

