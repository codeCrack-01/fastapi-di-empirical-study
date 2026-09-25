# ArtigenZ-IT-Solutions/artigenznewsite

- GitHub: https://github.com/ArtigenZ-IT-Solutions/artigenznewsite
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 9 · commit: `ccb4c0cdc141`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of ArtigenZ-IT-Solutions/artigenznewsite

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_positive | **no (overturn)** | The code correctly implements async streaming patterns without blocking the event loop, using proper async generators and thread-pool bridging. The static instrument's 'false_pos' label is incorrect. | Backend/llm_client.py#L85 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 9 | **false_pos** | [Backend/Main.py#L58](https://github.com/ArtigenZ-IT-Solutions/artigenznewsite/blob/ccb4c0cdc14190a8e8c900f85dc16ef174f1f7ad/Backend/Main.py#L58) |

## `C4|DEF` — **false_pos**
> occurrences here: 9 · corpus total: 56644 · executor: x86_64
> example: [Backend/Main.py#L58](https://github.com/ArtigenZ-IT-Solutions/artigenznewsite/blob/ccb4c0cdc14190a8e8c900f85dc16ef174f1f7ad/Backend/Main.py#L58)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

