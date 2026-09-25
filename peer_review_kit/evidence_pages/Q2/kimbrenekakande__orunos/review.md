# kimbrenekakande/orunos

- GitHub: https://github.com/kimbrenekakande/orunos
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 1 · commit: `43adeeed2f4b`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | apps/agents/app/main.py#L10 | The code defines an async context manager `spinup_actions` for FastAPI's lifespan, but it does not use FastAPI's dependency injection mechanisms (e.g., `Depends`, `Security`, or annotated dependenc... |

## Pass 2 — reconcile with inventory of kimbrenekakande/orunos

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code defines an async context manager for FastAPI's lifespan but does not implement any dependency injection mechanisms (e.g., no use of `Depends`, `Security`, or annotated dependencies). The `... | apps/agents/app/main.py#L10 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [apps/agents/app/main.py#L10](https://github.com/kimbrenekakande/orunos/blob/43adeeed2f4b9cef1839d0c2e8ca685e8384c3e8/apps/agents/app/main.py#L10) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [apps/agents/app/main.py#L10](https://github.com/kimbrenekakande/orunos/blob/43adeeed2f4b9cef1839d0c2e8ca685e8384c3e8/apps/agents/app/main.py#L10)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

