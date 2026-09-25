# paperworkmg-arch/VOLT

- GitHub: https://github.com/paperworkmg-arch/VOLT
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 20 · commit: `5a41df77fe3b`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection` | app/dashboard/app.py#L49 | The code defines an async lifespan context manager for FastAPI, but there is no use of FastAPI's @depends decorator or any explicit dependency injection pattern. The lifespan function handles start... |
| 2 | `No Dependency Injection` | app/omni-source/stemdeck/app/main.py#L158 | Another lifespan context manager is defined, but again, there is no use of FastAPI's dependency injection system. The code focuses on background tasks and process monitoring, not on injecting depen... |
| 3 | `No Dependency Injection` | app/omni-source/stemdeck/tests/conftest.py#L9 | Test fixtures use pytest's fixture system for setup/teardown, but this is test infrastructure, not application-level dependency injection. The code does not show any use of FastAPI's Depends or sim... |

## Pass 2 — reconcile with inventory of paperworkmg-arch/VOLT

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts show lifespan context managers for FastAPI lifecycle management, but no explicit dependency injection patterns (e.g., @depends, explicit DI containers, or service injection). The ... | app/dashboard/app.py#L49 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 20 | **false_pos** | [app/dashboard/app.py#L49](https://github.com/paperworkmg-arch/VOLT/blob/5a41df77fe3ba5e05ebbd8800e2a5e0f85f83569/app/dashboard/app.py#L49) |

## `C4|DEF` — **false_pos**
> occurrences here: 20 · corpus total: 56644 · executor: x86_64
> example: [app/dashboard/app.py#L49](https://github.com/paperworkmg-arch/VOLT/blob/5a41df77fe3ba5e05ebbd8800e2a5e0f85f83569/app/dashboard/app.py#L49)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

