# martinge17/codex-exporter

- GitHub: https://github.com/martinge17/codex-exporter
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `d21e382f8ea4`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `lifespan hook for resource management` | app/main.py#L21 | The lifespan async context manager handles exporter_state.shutdown() in finally block, suggesting dependency lifecycle management but no explicit FastAPI Depends() usage. exporter_state is referenc... |

## Pass 2 — reconcile with inventory of martinge17/codex-exporter

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code uses a lifespan async context manager for resource management but does not employ FastAPI Depends() or explicit parameter injection for dependency management, aligning with the 'false_pos'... | app/main.py#L21 |

### Missed by inventory (1)
- `lifespan hook for resource management without explicit DI` @ app/main.py#L21 — The inventory may have missed that the lifespan hook handles exporter_state.shutdown() as lifecycle management, even though it doesn't use Depends() or explicit DI parameters.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [app/main.py#L21](https://github.com/martinge17/codex-exporter/blob/d21e382f8ea4060c32ba566e97949a7a42bf0c61/app/main.py#L21) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [app/main.py#L21](https://github.com/martinge17/codex-exporter/blob/d21e382f8ea4060c32ba566e97949a7a42bf0c61/app/main.py#L21)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

