# pmgraham/datagrunt-studio

- GitHub: https://github.com/pmgraham/datagrunt-studio
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `da9e690590af`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection Detected` | backend/app/pdf_service.py#L142 | The code excerpt shows utility functions (_image_elements, _rewrite_image_locations) and a save_upload method, but none use FastAPI's dependency injection mechanisms like Depends, Security, or othe... |

## Pass 2 — reconcile with inventory of pmgraham/datagrunt-studio

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No FastAPI dependency injection constructs (Depends, Security, etc.) are present in the code excerpt. The functions shown are utility methods without DI usage. | backend/app/pdf_service.py#L142 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/pdf_service.py#L142](https://github.com/pmgraham/datagrunt-studio/blob/da9e690590af11e8d1ded3e3ba18dadcede8a529/backend/app/pdf_service.py#L142) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/pdf_service.py#L142](https://github.com/pmgraham/datagrunt-studio/blob/da9e690590af11e8d1ded3e3ba18dadcede8a529/backend/app/pdf_service.py#L142)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

