# MKRWW/wortlaut

- GitHub: https://github.com/MKRWW/wortlaut
- Stars: 13 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 16 · commit: `ff66a3ccec64`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Annotated[AsyncSession, Depends(...)]` | src/wortlaut/serving/app.py#L150 | The code defines SessionDep = Annotated[AsyncSession, Depends(get_session)], which is a FastAPI dependency injection pattern. This creates a reusable dependency that injects an AsyncSession into ro... |
| 2 | `Async dependency provider with yield` | src/wortlaut/serving/app.py#L146 | The async def get_session() -> AsyncIterator[AsyncSession] function uses async with sessionmaker() as session: yield session, which is a FastAPI pattern for creating async dependencies that manage ... |
| 3 | `Test fixture dependency injection` | tests/integration/conftest.py#L43 | The db_engine fixture depends on pg_dsn (another fixture), creating a dependency chain where db_engine provides an AsyncEngine to tests that need it, following pytest's fixture-based DI pattern. |
| 4 | `Composition root dependency wiring` | src/wortlaut/serving/app.py#L126 | The create_app() function takes sessionmaker, worm, and allowed_origins as parameters, indicating explicit wiring of dependencies at the composition root (as noted in the code comment about allowed... |

## Pass 2 — reconcile with inventory of MKRWW/wortlaut

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code at src/wortlaut/serving/app.py:126 explicitly wires dependencies in the composition root (create_app function), which matches C4|DEF (dependency injection via explicit wiring). The label '... | src/wortlaut/serving/app.py#L126 |
| `C1|BARE|PARAM` | known | yes | The code at src/wortlaut/serving/app.py:150 uses FastAPI's Annotated[AsyncSession, Depends(...)] pattern for parameterized dependency injection, matching C1|BARE|PARAM. | src/wortlaut/serving/app.py#L150 |
| `C3|CLASS|BARE` | false_pos | yes | The code at src/wortlaut/serving/app.py:150 does not use class-based DI (C3|CLASS|BARE). Instead, it uses FastAPI's Annotated parameterized DI, so the label 'false_pos' is correct. | src/wortlaut/serving/app.py#L150 |
| `C4|USED` | false_pos | yes | The code at src/wortlaut/serving/app.py:146 defines an async dependency provider (get_session), not a usage of a dependency. The label 'false_pos' correctly identifies this as not a 'used' DI occur... | src/wortlaut/serving/app.py#L146 |

### Missed by inventory (2)
- `pytest fixture-based DI chains (e.g., db_engine depends on pg_dsn)` @ tests/integration/conftest.py#L43 — The inventory did not capture the DI chain between fixtures (e.g., db_engine depends on pg_dsn).
- `Async dependency provider with yield (get_session)` @ src/wortlaut/serving/app.py#L146 — The inventory missed this specific FastAPI async dependency provider pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 13 | **false_pos** | [src/wortlaut/serving/app.py#L126](https://github.com/MKRWW/wortlaut/blob/ff66a3ccec642d8c71a1afb0ca8b5780e642ec5b/src/wortlaut/serving/app.py#L126) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [src/wortlaut/serving/app.py#L150](https://github.com/MKRWW/wortlaut/blob/ff66a3ccec642d8c71a1afb0ca8b5780e642ec5b/src/wortlaut/serving/app.py#L150) |
| `C3|CLASS|BARE` | C3 | 1 | **false_pos** | [src/wortlaut/serving/app.py#L150](https://github.com/MKRWW/wortlaut/blob/ff66a3ccec642d8c71a1afb0ca8b5780e642ec5b/src/wortlaut/serving/app.py#L150) |
| `C4|USED` | C4 | 1 | **false_pos** | [src/wortlaut/serving/app.py#L146](https://github.com/MKRWW/wortlaut/blob/ff66a3ccec642d8c71a1afb0ca8b5780e642ec5b/src/wortlaut/serving/app.py#L146) |

## `C4|DEF` — **false_pos**
> occurrences here: 13 · corpus total: 56644 · executor: x86_64
> example: [src/wortlaut/serving/app.py#L126](https://github.com/MKRWW/wortlaut/blob/ff66a3ccec642d8c71a1afb0ca8b5780e642ec5b/src/wortlaut/serving/app.py#L126)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [src/wortlaut/serving/app.py#L150](https://github.com/MKRWW/wortlaut/blob/ff66a3ccec642d8c71a1afb0ca8b5780e642ec5b/src/wortlaut/serving/app.py#L150)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 1 · corpus total: 20139 · executor: x86_64
> example: [src/wortlaut/serving/app.py#L150](https://github.com/MKRWW/wortlaut/blob/ff66a3ccec642d8c71a1afb0ca8b5780e642ec5b/src/wortlaut/serving/app.py#L150)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [src/wortlaut/serving/app.py#L146](https://github.com/MKRWW/wortlaut/blob/ff66a3ccec642d8c71a1afb0ca8b5780e642ec5b/src/wortlaut/serving/app.py#L146)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

