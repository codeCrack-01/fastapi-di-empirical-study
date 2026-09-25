# crygup/fish

- GitHub: https://github.com/crygup/fish
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 11 · commit: `24692d128247`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI Dependency Injection` | src/core/deletions.py#L25 | The code uses asyncpg and async context managers but contains no FastAPI-specific dependency injection patterns like Depends or DI-related decorators. The static summary confirms depends_total=0. |
| 2 | `No FastAPI Dependency Injection` | src/extensions/voicemaster/__init__.py#L1381 | The async context manager _player_typing handles Discord operations but lacks FastAPI DI constructs. The static analysis confirms no annotated_depends_total or yield_dep_total. |
| 3 | `No FastAPI Dependency Injection` | tests/test_network.py#L140 | Test code mocks HTTP responses but does not use FastAPI's dependency injection system. The static summary confirms depends_total=0 across the repo. |

## Pass 2 — reconcile with inventory of crygup/fish

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No FastAPI dependency injection patterns (e.g., Depends, DI decorators) are present in the cited code. The code uses async context managers and database operations but lacks FastAPI-specific DI con... | src/core/deletions.py#L25 |
| `C4|DEF` | false_pos | yes | The code in src/extensions/events/boards.py:257 defines async functions but does not use FastAPI dependency injection patterns. The static analysis confirmed depends_total=0 for the repo. | src/extensions/events/boards.py#L257 |
| `C4|DEF` | false_pos | yes | The code in src/extensions/mudae/series_scraper.py:408 uses async operations but contains no FastAPI DI elements. The static analysis confirmed no annotated_depends_total or yield_dep_total in the ... | src/extensions/mudae/series_scraper.py#L408 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 11 | **false_pos** | [src/core/deletions.py#L25](https://github.com/crygup/fish/blob/24692d128247b4d0f864f657585c70a268ff9c2e/src/core/deletions.py#L25) |

## `C4|DEF` — **false_pos**
> occurrences here: 11 · corpus total: 56644 · executor: x86_64
> example: [src/core/deletions.py#L25](https://github.com/crygup/fish/blob/24692d128247b4d0f864f657585c70a268ff9c2e/src/core/deletions.py#L25)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

