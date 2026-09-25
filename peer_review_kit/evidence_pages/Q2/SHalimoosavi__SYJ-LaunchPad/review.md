# SHalimoosavi/SYJ-LaunchPad

- GitHub: https://github.com/SHalimoosavi/SYJ-LaunchPad
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 4 · commit: `105268c48788`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection with async generator` | backend/app/db/session.py#L32 | The get_db() function is an async generator that yields AsyncSession instances, typical for FastAPI dependency injection. It uses asynccontextmanager and yields sessions for dependency injection in... |
| 2 | `Dependency injection via Depends()` | backend/app/features/health/routes.py#L14 | The health() endpoint uses Depends(get_db) and Depends(get_settings) to inject dependencies, demonstrating FastAPI's standard DI pattern with explicit dependency functions. |

## Pass 2 — reconcile with inventory of SHalimoosavi/SYJ-LaunchPad

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code at lines 14-15 shows FastAPI's DI pattern via Depends() in the health() function's parameters, not the imports. The panel incorrectly labeled the import lines as false positives. | backend/app/features/health/routes.py#L14 |
| `C4|DEF` | true_pos | **no (overturn)** | The lifespan() function in main.py line 29 is a valid FastAPI DI lifespan manager, which is part of the framework's dependency injection system for startup/shutdown hooks. The panel's false_pos lab... | backend/app/main.py#L29 |
| `C4|USED` | true_pos | **no (overturn)** | The get_db() function in session.py line 32 is a standard FastAPI async generator dependency, correctly used for DI in routes. The panel's false_pos label is incorrect. | backend/app/db/session.py#L32 |

### Missed by inventory (2)
- `FastAPI lifespan manager as DI pattern` @ backend/app/main.py#L29 — The lifespan() function with @asynccontextmanager is a valid DI usage pattern for startup/shutdown, but the inventory did not capture this.
- `Async generator dependency injection` @ backend/app/db/session.py#L32 — The get_db() async generator is a core DI pattern, but the inventory missed this specific implementation.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 2 | **false_pos** | [backend/app/features/health/routes.py#L14](https://github.com/SHalimoosavi/SYJ-LaunchPad/blob/105268c4878842476f8e734f699abe4565fb883a/backend/app/features/health/routes.py#L14) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/main.py#L29](https://github.com/SHalimoosavi/SYJ-LaunchPad/blob/105268c4878842476f8e734f699abe4565fb883a/backend/app/main.py#L29) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/session.py#L32](https://github.com/SHalimoosavi/SYJ-LaunchPad/blob/105268c4878842476f8e734f699abe4565fb883a/backend/app/db/session.py#L32) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 2 · corpus total: 83548 · executor: x86_64
> example: [backend/app/features/health/routes.py#L14](https://github.com/SHalimoosavi/SYJ-LaunchPad/blob/105268c4878842476f8e734f699abe4565fb883a/backend/app/features/health/routes.py#L14)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L29](https://github.com/SHalimoosavi/SYJ-LaunchPad/blob/105268c4878842476f8e734f699abe4565fb883a/backend/app/main.py#L29)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/session.py#L32](https://github.com/SHalimoosavi/SYJ-LaunchPad/blob/105268c4878842476f8e734f699abe4565fb883a/backend/app/db/session.py#L32)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

