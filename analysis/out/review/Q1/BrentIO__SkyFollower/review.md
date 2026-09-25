# BrentIO/SkyFollower

- GitHub: https://github.com/BrentIO/SkyFollower
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 25 · commit: `9bcbf11eda22`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `pytest fixtures for dependency injection` | management-ui/backend/tests/test_archive_search.py#L287 | The `client` fixture uses pytest fixtures to inject a TestClient with mocked dependencies (fake_redis, fake_athena, fake_s3), demonstrating dependency injection through pytest's fixture system. |
| 2 | `context managers for resource setup` | management-ui/backend/tests/test_archive_search.py#L217 | The `_synchronous_thread` context manager patches threading behavior, showing resource setup/teardown patterns that could be considered a form of dependency injection for test environments. |

## Pass 2 — reconcile with inventory of BrentIO/SkyFollower

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code in management-ui/backend/main.py:827 demonstrates a valid pattern of ensuring a Redis search index exists, which is a legitimate use case and not a false positive. | management-ui/backend/main.py#L827 |

### Missed by inventory (2)
- `pytest fixtures for dependency injection` @ management-ui/backend/tests/test_archive_search.py#L287 — The inventory did not account for pytest fixtures used for dependency injection in test code, which is a valid and common practice.
- `context managers for resource setup` @ management-ui/backend/tests/test_archive_search.py#L217 — The inventory missed context managers used for resource setup in test environments, which are essential for test reliability.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 25 | **false_pos** | [archive-compaction/tests/test_archive_compaction.py#L158](https://github.com/BrentIO/SkyFollower/blob/9bcbf11eda227a30cafdb36eda93a88ace4ecab5/archive-compaction/tests/test_archive_compaction.py#L158) |

## `C4|DEF` — **false_pos**
> occurrences here: 25 · corpus total: 56644 · executor: x86_64
> example: [archive-compaction/tests/test_archive_compaction.py#L158](https://github.com/BrentIO/SkyFollower/blob/9bcbf11eda227a30cafdb36eda93a88ace4ecab5/archive-compaction/tests/test_archive_compaction.py#L158)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

