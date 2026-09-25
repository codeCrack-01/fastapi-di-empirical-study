# orca-gamedev/orca-engine

- GitHub: https://github.com/orca-gamedev/orca-engine
- Stars: 85 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 14 · commit: `207cab8e3459`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of orca-gamedev/orca-engine

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code contains valid streaming NDJSON generators (e.g., generate_exploration_stream, quota_exceeded_stream) that match the C4|DEF pattern, contradicting the false_pos label. | backend/app.py#L7618 |

### Missed by inventory (1)
- `NDJSON streaming generators` @ backend/app.py#L8066 — The inventory missed the quota_exceeded_stream generator which uses NDJSON streaming, a pattern consistent with C4|DEF.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 14 | **false_pos** | [backend/app.py#L7618](https://github.com/orca-gamedev/orca-engine/blob/207cab8e3459882e8ffeaec95b3c9062dbf924fe/backend/app.py#L7618) |

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [backend/app.py#L7618](https://github.com/orca-gamedev/orca-engine/blob/207cab8e3459882e8ffeaec95b3c9062dbf924fe/backend/app.py#L7618)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

