# stevezau/shortlist

- GitHub: https://github.com/stevezau/shortlist
- Stars: 14 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 56 · commit: `a13f187cf263`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Fixture-based Dependency Injection` | tests/e2e/conftest.py#L327 | The `fresh_app` fixture uses `monkeypatch.setattr` to inject mock dependencies (PLEXTV, TMDB) into the application, replacing real implementations with fakes for testing. This allows tests to contr... |
| 2 | `Isolation Fixtures` | tests/unit/test_jobs.py#L54 | The `_isolate_handlers` fixture resets job handlers between tests to prevent cross-test contamination. This ensures each test runs in isolation by replacing global state with test-specific configur... |
| 3 | `Session-based DI` | tests/unit/test_notifications.py#L17 | The `session` fixture provides a database session with pre-configured migrations and cleanup. Tests depend on this session to interact with the database, ensuring consistent state without relying o... |

## Pass 2 — reconcile with inventory of stevezau/shortlist

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `tests/e2e/conftest.py:327` | Fixture-based Dependency Injection | yes | The `fresh_app` fixture uses `monkeypatch.setattr` to inject mock PLEXTV/TMDB URLs, replacing real implementations for test isolation. | tests/e2e/conftest.py#L327 |
| `tests/unit/test_jobs.py:54` | Isolation Fixtures | yes | The `_isolate_handlers` fixture resets job handlers between tests by clearing and restoring global state, ensuring test isolation. | tests/unit/test_jobs.py#L54 |
| `tests/unit/test_notifications.py:17` | Session-based DI | yes | The `session` fixture provides a database session with pre-configured migrations and cleanup, enabling consistent test state. | tests/unit/test_notifications.py#L17 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 41 | **false_pos** | [shortlist/server/api/collections.py#L866](https://github.com/stevezau/shortlist/blob/a13f187cf2639d2c24b061a2251fb15d4e445b06/shortlist/server/api/collections.py#L866) |
| `C1|BARE|PARAM` | C1 | 15 | **known** | [shortlist/server/api/collections.py#L40](https://github.com/stevezau/shortlist/blob/a13f187cf2639d2c24b061a2251fb15d4e445b06/shortlist/server/api/collections.py#L40) |

## `C4|DEF` — **false_pos**
> occurrences here: 41 · corpus total: 56644 · executor: x86_64
> example: [shortlist/server/api/collections.py#L866](https://github.com/stevezau/shortlist/blob/a13f187cf2639d2c24b061a2251fb15d4e445b06/shortlist/server/api/collections.py#L866)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 15 · corpus total: 18195 · executor: x86_64
> example: [shortlist/server/api/collections.py#L40](https://github.com/stevezau/shortlist/blob/a13f187cf2639d2c24b061a2251fb15d4e445b06/shortlist/server/api/collections.py#L40)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

