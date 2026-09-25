# GolubchikovKirill/InfraScope

- GitHub: https://github.com/GolubchikovKirill/InfraScope
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 114 · commit: `1f8e7b04572a`
- Fingerprints touching this repo: 7
- Label mix: novel=0 variant=2 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection` | app/api/routes/onec_exchange.py#L77 | The function uses `session: SessionDep` as a parameter, indicating a dependency injection pattern where the database session is injected rather than created internally. This aligns with FastAPI's D... |
| 2 | `FastAPI Dependency Injection` | app/api/routes/printers.py#L151 | The `sync_cartridge_stock` function uses `session: SessionDep` as a parameter, demonstrating dependency injection of the database session. This allows for testability and separation of concerns. |
| 3 | `FastAPI Dependency Injection` | app/api/routes/scanner.py#L171 | The `add_discovered_printer` function injects `session: SessionDep` and uses `Depends(get_current_active_superuser)` to enforce authentication, showcasing FastAPI's DI for both database and auth de... |

## Pass 2 — reconcile with inventory of GolubchikovKirill/InfraScope

_Presented fingerprints:_ `C1|BARE|PARAM`, `C4|DEF`, `C3|CLASS|BARE`, `C3|CLASS|EMPTY`, `C1|EMPTY|PARAM`, `C3|BARE|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_dependency_injection` | FastAPI Dependency Injection | yes | Multiple routes use session: SessionDep and Depends() for auth, consistent with FastAPI DI patterns. | app/api/routes/printers.py#L151 |
| `fastapi_dependency_injection` | FastAPI Dependency Injection | yes | Printer route uses session injection and authentication dependency as expected. | app/api/routes/scanner.py#L171 |
| `fastapi_dependency_injection` | FastAPI Dependency Injection | yes | Switch routes consistently use SessionDep and authentication dependencies. | app/api/routes/switches/crud.py#L99 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 90 | **known** | [app/api/deps.py#L34](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L34) |
| `C4|DEF` | C4 | 17 | **false_pos** | [app/discovery_service/main.py#L31](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/discovery_service/main.py#L31) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [app/api/deps.py#L34](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L34) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [app/api/routes/auth.py#L73](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/routes/auth.py#L73) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [app/api/routes/auth.py#L73](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/routes/auth.py#L73) |
| `C3|BARE|BARE` | C3 | 1 | **variant** | [app/api/deps.py#L35](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L35) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/api/deps.py#L29](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L29) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 90 · corpus total: 18195 · executor: x86_64
> example: [app/api/deps.py#L34](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L34)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 17 · corpus total: 56644 · executor: x86_64
> example: [app/discovery_service/main.py#L31](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/discovery_service/main.py#L31)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [app/api/deps.py#L34](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L34)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [app/api/routes/auth.py#L73](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/routes/auth.py#L73)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [app/api/routes/auth.py#L73](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/routes/auth.py#L73)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C3|BARE|BARE` — **variant**
> occurrences here: 1 · corpus total: 1316 · executor: x86_64
> example: [app/api/deps.py#L35](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L35)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/api/deps.py#L29](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L29)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

