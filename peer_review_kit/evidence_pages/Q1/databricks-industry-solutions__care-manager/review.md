# databricks-industry-solutions/care-manager

- GitHub: https://github.com/databricks-industry-solutions/care-manager
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `68c7ff572950`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | app.py#L13 | The code defines a lifespan context manager for FastAPI but does not use any dependency injection patterns. The 'db' and 'store' modules are imported directly and used without being injected via Fa... |

## Pass 2 — reconcile with inventory of databricks-industry-solutions/care-manager

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code defines a lifespan context manager but does not implement dependency injection patterns. The 'db' and 'store' modules are used directly without injection via FastAPI's dependency system. | app.py#L13 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [app.py#L13](https://github.com/databricks-industry-solutions/care-manager/blob/68c7ff572950402a4f9f67ef666bd42bc5fb7df6/app.py#L13) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [app.py#L13](https://github.com/databricks-industry-solutions/care-manager/blob/68c7ff572950402a4f9f67ef666bd42bc5fb7df6/app.py#L13)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

