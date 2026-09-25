# EarthSpark/thundercloud

- GitHub: https://github.com/EarthSpark/thundercloud
- Stars: 4 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 96 · commit: `b9ec2def88f7`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of EarthSpark/thundercloud

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly raises APIError with status_code when no meters are found, which is explicitly tested in test_customerviews0.py (line 325). The error handling is intentional and valid DI. | sparkmeter/api/customerviews0.py#L550 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 96 | **false_pos** | [sparkmeter/api/customerviews0.py#L550](https://github.com/EarthSpark/thundercloud/blob/b9ec2def88f7a6da51a76a7b812a956dd8daa090/sparkmeter/api/customerviews0.py#L550) |

## `C4|DEF` — **false_pos**
> occurrences here: 96 · corpus total: 56644 · executor: x86_64
> example: [sparkmeter/api/customerviews0.py#L550](https://github.com/EarthSpark/thundercloud/blob/b9ec2def88f7a6da51a76a7b812a956dd8daa090/sparkmeter/api/customerviews0.py#L550)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

