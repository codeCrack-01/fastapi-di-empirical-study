# auracarehq/auradefi

- GitHub: https://github.com/auracarehq/auradefi
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 1 · commit: `194719195044`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | src/auradefi/sources/evm/logs.py#L97 | The code snippet shows a function `_chunks` with parameter validation and range calculation logic, but there are no FastAPI dependency injection patterns (e.g., `Depends()`, dependency classes, or ... |

## Pass 2 — reconcile with inventory of auracarehq/auradefi

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code at logs.py:97 contains no FastAPI dependency injection patterns (e.g., Depends(), dependency classes, or DI decorators). The static analysis correctly identified this as a false positive. | src/auradefi/sources/evm/logs.py#L97 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [src/auradefi/sources/evm/logs.py#L97](https://github.com/auracarehq/auradefi/blob/194719195044a9146d78566da44adf1fe428c819/src/auradefi/sources/evm/logs.py#L97) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [src/auradefi/sources/evm/logs.py#L97](https://github.com/auracarehq/auradefi/blob/194719195044a9146d78566da44adf1fe428c819/src/auradefi/sources/evm/logs.py#L97)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

