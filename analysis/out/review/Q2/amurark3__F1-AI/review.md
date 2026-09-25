# amurark3/F1-AI

- GitHub: https://github.com/amurark3/F1-AI
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 8 · commit: `0970a012d33d`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of amurark3/F1-AI

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No explicit code contradiction found; the labeled instances appear to be standard async/await patterns in API routers and test fixtures, which align with the 'false_pos' classification for this fin... | backend/app/api/routers/chat.py#L182 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 8 | **false_pos** | [backend/app/api/routers/chat.py#L182](https://github.com/amurark3/F1-AI/blob/0970a012d33d53b9f8bd90375d2a4768684711f4/backend/app/api/routers/chat.py#L182) |

## `C4|DEF` — **false_pos**
> occurrences here: 8 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/routers/chat.py#L182](https://github.com/amurark3/F1-AI/blob/0970a012d33d53b9f8bd90375d2a4768684711f4/backend/app/api/routers/chat.py#L182)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

