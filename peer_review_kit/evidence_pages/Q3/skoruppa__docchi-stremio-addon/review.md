# skoruppa/docchi-stremio-addon

- GitHub: https://github.com/skoruppa/docchi-stremio-addon
- Stars: 21 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 1 · commit: `5776d866e05f`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | run.py#L49 | The code does not use FastAPI's dependency injection system (e.g., Depends(), Security(), or annotated dependencies). The 'lifespan' function is part of FastAPI's lifecycle management, but no depen... |

## Pass 2 — reconcile with inventory of skoruppa/docchi-stremio-addon

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code at run.py:49 configures logging and a FastAPI lifespan handler, but does not use FastAPI's dependency injection system (no Depends(), Security(), or annotated dependencies). The static sum... | run.py#L49 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [run.py#L49](https://github.com/skoruppa/docchi-stremio-addon/blob/5776d866e05fb2906f80c59b4654e72b624710fd/run.py#L49) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [run.py#L49](https://github.com/skoruppa/docchi-stremio-addon/blob/5776d866e05fb2906f80c59b4654e72b624710fd/run.py#L49)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

