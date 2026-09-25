# 514-labs/moosestack

- GitHub: https://github.com/514-labs/moosestack
- Stars: 588 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 7 · commit: `99bcb9f9fff7`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with custom dependencies` | templates/python-fastapi/app/apis/bar.py#L161 | The code uses `Depends(require_auth)` to inject a custom authentication dependency into the `/protected` endpoint, demonstrating FastAPI's DI system where `require_auth` is a resolvable dependency. |
| 2 | `Incomplete dependency injection usage` | templates/python-fastapi-client-only/app/fastapi.py#L57 | The code shows `Depends()` without specifying a concrete dependency, which may indicate an incomplete or placeholder usage of FastAPI's DI system. |

## Pass 2 — reconcile with inventory of 514-labs/moosestack

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|EMPTY|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses `Depends(require_auth)` in a FastAPI endpoint, which is a valid and intentional use of FastAPI's dependency injection system. | templates/python-fastapi/app/apis/bar.py#L161 |
| `C4|DEF` | true_pos | **no (overturn)** | The test fixtures (`clear_registries`, `clear_registry`) are valid uses of pytest's dependency injection system for test setup/teardown, not false positives. | packages/py-moose-lib/tests/conftest.py#L10 |
| `C1|EMPTY|SIG` | variant | yes | The code uses `Depends()` without a concrete argument, which matches the 'variant' label as an incomplete or placeholder DI usage. | templates/python-fastapi-client-only/app/fastapi.py#L57 |

### Missed by inventory (2)
- `Incomplete DI usage with `Depends()` without arguments` @ templates/python-fastapi-client-only/app/fastapi.py#L57 — The inventory did not capture this as a distinct DI pattern (e.g., 'incomplete' or 'placeholder') despite its clear presence in the code.
- `Test-specific DI fixtures (pytest fixtures)` @ packages/py-moose-lib/tests/conftest.py#L10 — The inventory did not recognize pytest fixtures like `clear_registries` as valid DI usages in the test context.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 3 | **false_pos** | [templates/python-fastapi/app/apis/bar.py#L161](https://github.com/514-labs/moosestack/blob/99bcb9f9fff7230e23db49fd5b70af62af511bf9/templates/python-fastapi/app/apis/bar.py#L161) |
| `C4|DEF` | C4 | 3 | **false_pos** | [packages/py-moose-lib/tests/conftest.py#L10](https://github.com/514-labs/moosestack/blob/99bcb9f9fff7230e23db49fd5b70af62af511bf9/packages/py-moose-lib/tests/conftest.py#L10) |
| `C1|EMPTY|SIG` | C1 | 1 | **variant** | [templates/python-fastapi-client-only/app/fastapi.py#L57](https://github.com/514-labs/moosestack/blob/99bcb9f9fff7230e23db49fd5b70af62af511bf9/templates/python-fastapi-client-only/app/fastapi.py#L57) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 3 · corpus total: 83548 · executor: x86_64
> example: [templates/python-fastapi/app/apis/bar.py#L161](https://github.com/514-labs/moosestack/blob/99bcb9f9fff7230e23db49fd5b70af62af511bf9/templates/python-fastapi/app/apis/bar.py#L161)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [packages/py-moose-lib/tests/conftest.py#L10](https://github.com/514-labs/moosestack/blob/99bcb9f9fff7230e23db49fd5b70af62af511bf9/packages/py-moose-lib/tests/conftest.py#L10)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|EMPTY|SIG` — **variant**
> occurrences here: 1 · corpus total: 254 · executor: x86_64
> example: [templates/python-fastapi-client-only/app/fastapi.py#L57](https://github.com/514-labs/moosestack/blob/99bcb9f9fff7230e23db49fd5b70af62af511bf9/templates/python-fastapi-client-only/app/fastapi.py#L57)
> **rule:** C1

> **evidence (model):** Empty Depends() calls in function signatures (C1 rule covers Depends(...) usage but this is a structural variant with empty argument list)

