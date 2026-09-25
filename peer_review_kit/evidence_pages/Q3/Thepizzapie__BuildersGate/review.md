# Thepizzapie/BuildersGate

- GitHub: https://github.com/Thepizzapie/BuildersGate
- Stars: 17 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 77 · commit: `a909968c50a5`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=1 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Fixture Pattern` | tests/conftest.py#L22 | The `_no_dashboard_auth` fixture uses `monkeypatch.setenv` to modify environment variables, a common pattern in pytest for setting up test preconditions. This ensures tests run in isolation without... |
| 2 | `Stream Processing` | bgate_ui/redact.py#L232 | The `_scrub_whole` function processes response bodies in chunks using iterators, avoiding memory overload for large responses. This aligns with the Stream Processing pattern, crucial for handling l... |
| 3 | `Error Handling` | bgate_ui/redact.py#L261 | The `try-except` block around `body.decode("utf-8")` demonstrates robust error handling for non-UTF-8 content, preventing crashes and ensuring graceful fallback to raw bytes. |
| 4 | `State Reset` | tests/test_cinematic.py#L625 | The `_no_leak` fixture resets module-level state (`kie.MODELS`) after each test, preventing test contamination. This is essential for isolation in unit tests. |
| 5 | `Mocking` | tests/test_dispatch_env.py#L44 | The `spawned` fixture mocks `subprocess.Popen` to capture CLI arguments without executing real processes, a classic Mocking pattern for isolating tests from external systems. |

## Pass 2 — reconcile with inventory of Thepizzapie/BuildersGate

_Presented fingerprints:_ `C4|DEF`, `C1|EMPTY|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `Fixture Pattern @ tests/conftest.py:22` | Fixture Pattern @ tests/conftest.py:22 | yes | The `_no_dashboard_auth` fixture correctly uses `monkeypatch.setenv` to modify environment variables for test isolation. | tests/conftest.py#L22 |
| `Stream Processing @ bgate_ui/redact.py:232` | Stream Processing @ bgate_ui/redact.py:232 | yes | The `_scrub_whole` function processes response bodies in chunks using iterators, avoiding memory overload for large responses. | bgate_ui/redact.py#L232 |
| `Error Handling @ bgate_ui/redact.py:261` | Error Handling @ bgate_ui/redact.py:261 | yes | The `try-except` block around `body.decode("utf-8")` correctly handles non-UTF-8 content with graceful fallback. | bgate_ui/redact.py#L261 |
| `State Reset @ tests/test_cinematic.py:625` | State Reset @ tests/test_cinematic.py:625 | yes | The `_no_leak` fixture resets module-level state (`kie.MODELS`) after each test to prevent contamination. | tests/test_cinematic.py#L625 |
| `Mocking @ tests/test_dispatch_env.py:44` | Mocking @ tests/test_dispatch_env.py:44 | yes | The `spawned` fixture mocks `subprocess.Popen` to capture CLI arguments without executing real processes. | tests/test_dispatch_env.py#L44 |

### Missed by inventory (3)
- `ASGI Error Avoidance @ bgate_ui/redact.py:278` @ bgate_ui/redact.py#L278 — The code avoids re-constructing StreamingResponse to prevent ASGI errors from double-consumption of response bodies.
- `State Management in dispatch_ops @ tests/test_dispatch_ops.py:28` @ tests/test_dispatch_ops.py#L28 — The `client` fixture uses `dispatch._live.clear()` to ensure no leftover processes from previous tests.
- `Test Isolation via Copytree @ tests/conftest.py:95` @ tests/conftest.py#L95 — The `root` fixture uses `shutil.copytree` to create a fresh project for each test, ensuring isolation.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 64 | **false_pos** | [bgate_core/adopt.py#L59](https://github.com/Thepizzapie/BuildersGate/blob/a909968c50a571bd0c981b846a2718361af957a2/bgate_core/adopt.py#L59) |
| `C1|EMPTY|SIG` | C1 | 13 | **variant** | [bgate_ui/app.py#L791](https://github.com/Thepizzapie/BuildersGate/blob/a909968c50a571bd0c981b846a2718361af957a2/bgate_ui/app.py#L791) |

## `C4|DEF` — **false_pos**
> occurrences here: 64 · corpus total: 56644 · executor: x86_64
> example: [bgate_core/adopt.py#L59](https://github.com/Thepizzapie/BuildersGate/blob/a909968c50a571bd0c981b846a2718361af957a2/bgate_core/adopt.py#L59)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 13 · corpus total: 254 · executor: x86_64
> example: [bgate_ui/app.py#L791](https://github.com/Thepizzapie/BuildersGate/blob/a909968c50a571bd0c981b846a2718361af957a2/bgate_ui/app.py#L791)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

