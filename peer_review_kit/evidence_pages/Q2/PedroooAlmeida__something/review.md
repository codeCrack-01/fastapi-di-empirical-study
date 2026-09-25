# PedroooAlmeida/something

- GitHub: https://github.com/PedroooAlmeida/something
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 20 · commit: `86f7f4185bba`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI Dependency Injection` | backend/app/db.py#L72 | The code defines a context manager `conn()` for database connections but does not use FastAPI's `Depends` or similar DI mechanisms. It is a utility function, not a dependency injected via FastAPI. |
| 2 | `Test Mocking of Dependencies` | tests/test_classifier.py#L19 | The test uses `monkeypatch.setattr(classifier.llm, 'stream_llm', forbidden)` to mock a dependency during testing. This is test infrastructure, not production DI. |

## Pass 2 — reconcile with inventory of PedroooAlmeida/something

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code in db.py:72 defines a context manager but does not use FastAPI DI mechanisms. The test mocking in tests/test_classifier.py:19 is test infrastructure, not production DI. The llm.py:52 code ... | backend/app/db.py#L72 |

### Missed by inventory (2)
- `Test mocking of dependencies` @ tests/test_classifier.py#L19 — The test infrastructure mocks dependencies (e.g., stream_llm) but this is not production DI and was not captured by the inventory.
- `Test fixtures with dependency mocking` @ tests/test_engine.py#L45 — Test fixtures like _mock_stream and synth_calls mock LLM behavior but are not production DI occurrences.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 20 | **false_pos** | [backend/app/db.py#L72](https://github.com/PedroooAlmeida/something/blob/86f7f4185bbac49396d4cc7a76a59260eae53203/backend/app/db.py#L72) |

## `C4|DEF` — **false_pos**
> occurrences here: 20 · corpus total: 56644 · executor: x86_64
> example: [backend/app/db.py#L72](https://github.com/PedroooAlmeida/something/blob/86f7f4185bbac49396d4cc7a76a59260eae53203/backend/app/db.py#L72)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

