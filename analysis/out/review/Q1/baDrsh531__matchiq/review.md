# baDrsh531/matchiq

- GitHub: https://github.com/baDrsh531/matchiq
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 4 · commit: `f96467908945`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI Dependency Injection` | persistence/database.py#L26 | The code defines a `get_session` function that yields a SQLAlchemy session, but there is no use of FastAPI's `Depends()` or any other dependency injection mechanism. The function appears to be a ma... |
| 2 | `No FastAPI Dependency Injection` | tests/test_api.py#L61 | Test code sets up a test database and mocks dependencies, but this is part of testing infrastructure, not FastAPI's dependency injection system. No `Depends()` or similar constructs are present. |
| 3 | `No FastAPI Dependency Injection` | tests/test_persistence.py#L22 | Test fixture creates a SQLAlchemy session for testing, but this is unrelated to FastAPI's dependency injection. The code uses `sessionmaker` directly, not as a FastAPI dependency. |
| 4 | `No FastAPI Dependency Injection` | tests/test_scouting.py#L13 | Another test fixture creates a SQLAlchemy session, but again, this is test infrastructure. No FastAPI dependency injection patterns are present. |

## Pass 2 — reconcile with inventory of baDrsh531/matchiq

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts show manual SQLAlchemy session management (e.g., `get_session` as a context manager) and test infrastructure, but no FastAPI `Depends()` or DI patterns. The static instrument's la... | persistence/database.py#L26 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [persistence/database.py#L26](https://github.com/baDrsh531/matchiq/blob/f96467908945c40a62fb3f7899a3a4fadf9852e4/persistence/database.py#L26) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [persistence/database.py#L26](https://github.com/baDrsh531/matchiq/blob/f96467908945c40a62fb3f7899a3a4fadf9852e4/persistence/database.py#L26)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

