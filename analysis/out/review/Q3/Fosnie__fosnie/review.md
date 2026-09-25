# Fosnie/fosnie

- GitHub: https://github.com/Fosnie/fosnie
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 16 · commit: `0f857ac47e0c`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of Fosnie/fosnie

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No DEF keywords or patterns matching C4|DEF found in the provided code excerpts. The code uses standard Python function definitions (def/async def) without any uppercase DEF or structural anomalies. | backend/deploy/voice/softphone.py#L68 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 16 | **false_pos** | [backend/deploy/voice/softphone.py#L68](https://github.com/Fosnie/fosnie/blob/0f857ac47e0ce6c1855d08602a4b2a2db168faf5/backend/deploy/voice/softphone.py#L68) |

## `C4|DEF` — **false_pos**
> occurrences here: 16 · corpus total: 56644 · executor: x86_64
> example: [backend/deploy/voice/softphone.py#L68](https://github.com/Fosnie/fosnie/blob/0f857ac47e0ce6c1855d08602a4b2a2db168faf5/backend/deploy/voice/softphone.py#L68)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

