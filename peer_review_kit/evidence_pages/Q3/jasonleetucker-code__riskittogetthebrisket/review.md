# jasonleetucker-code/riskittogetthebrisket

- GitHub: https://github.com/jasonleetucker-code/riskittogetthebrisket
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 79 · commit: `adf84271fed5`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of jasonleetucker-code/riskittogetthebrisket

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code at the cited lines contains valid function definitions (DEFs) that contradict the false_pos label. | scripts/validate_va_v2.py#L174 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 79 | **false_pos** | [scripts/backfill_rank_history.py#L95](https://github.com/jasonleetucker-code/riskittogetthebrisket/blob/adf84271fed53b96906b7e25382b3f94fc091532/scripts/backfill_rank_history.py#L95) |

## `C4|DEF` — **false_pos**
> occurrences here: 79 · corpus total: 56644 · executor: x86_64
> example: [scripts/backfill_rank_history.py#L95](https://github.com/jasonleetucker-code/riskittogetthebrisket/blob/adf84271fed53b96906b7e25382b3f94fc091532/scripts/backfill_rank_history.py#L95)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

