# DenisKimskku/DenisKimskku.github.io

- GitHub: https://github.com/DenisKimskku/DenisKimskku.github.io
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 11 · commit: `7aee5537ff9d`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No explicit FastAPI dependency injection` | ctf_backend/app/api/routes.py#L416 | The code uses route decorators like @limiter.limit but does not employ FastAPI's Depends() for injecting dependencies. The limiter is applied as a decorator rather than via a dependency injection m... |
| 2 | `No explicit FastAPI dependency injection` | ctf_backend/app/services/db_session.py#L22 | The _connect() context manager handles database connections manually without using FastAPI's Depends() or other DI mechanisms. |
| 3 | `No explicit FastAPI dependency injection` | ctf_backend/app/services/judge.py#L53 | The inference_slot() context manager uses an asyncio.Semaphore directly without injecting it via FastAPI's dependency system. |

## Pass 2 — reconcile with inventory of DenisKimskku/DenisKimskku.github.io

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code does not use FastAPI's dependency injection (Depends()) in the flagged locations. Instead, it uses route decorators (e.g., @limiter.limit) and manual context managers (e.g., asyncio.Semaph... | ctf_backend/app/api/routes.py#L416 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 11 | **false_pos** | [ctf_backend/app/api/routes.py#L438](https://github.com/DenisKimskku/DenisKimskku.github.io/blob/7aee5537ff9d937b46a5df9481d111494d852b2c/ctf_backend/app/api/routes.py#L438) |

## `C4|DEF` — **false_pos**
> occurrences here: 11 · corpus total: 56644 · executor: x86_64
> example: [ctf_backend/app/api/routes.py#L438](https://github.com/DenisKimskku/DenisKimskku.github.io/blob/7aee5537ff9d937b46a5df9481d111494d852b2c/ctf_backend/app/api/routes.py#L438)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

