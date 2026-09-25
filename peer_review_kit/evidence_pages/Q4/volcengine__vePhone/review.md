# volcengine/vePhone

- GitHub: https://github.com/volcengine/vePhone
- Stars: 23 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 41 · commit: `dc3f489dfbd7`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with custom dependency chaining` | Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20 | The code defines a dependency injection chain using FastAPI's Depends. get_db provides a database session, which is then used by require_session to validate authentication sessions. These dependenc... |
| 2 | `Same DI pattern in parallel module` | Quick Start/MobileUse/ui_test_demo/src/mua_platform/api/deps.py#L20 | Identical dependency injection pattern is replicated in the mobile use module, with get_db, require_session, and annotated dependencies like Database and CurrentSession. This shows a consistent DI ... |

## Pass 2 — reconcile with inventory of volcengine/vePhone

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code defines real dependency functions (e.g., `get_db`, `require_session`) in `deps.py` which are used as dependencies. The panel's links to lines like L367 (which is unrelated to dependency de... | Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L15 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses `Annotated[Type, Depends(...)]` for parameterized dependencies (e.g., `Database = Annotated[Session, Depends(get_db)]`), matching the panel's label. | Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code uses `Annotated[Session, ...]` with a class (`Session`) and dependency, which is valid. The panel's false_pos label is incorrect. | Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20 |
| `C4|USED` | true_pos | **no (overturn)** | The code explicitly uses `Depends(...)` in annotated dependencies (e.g., `Database = Annotated[Session, Depends(get_db)]`), contradicting the panel's false_pos label. | Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20 |

### Missed by inventory (1)
- `DI pattern in MobileUse module` @ Quick Start/MobileUse/ui_test_demo/src/mua_platform/api/deps.py#L20 — The inventory did not account for the identical DI pattern in the MobileUse module, which mirrors the ComputerUseAgent's implementation.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 15 | **false_pos** | [Quick Start/ComputerUseAgent/src/cua_platform/main.py#L367](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/main.py#L367) |
| `C1|BARE|PARAM` | C1 | 12 | **known** | [Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20) |
| `C3|CLASS|BARE` | C3 | 12 | **false_pos** | [Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20) |
| `C4|USED` | C4 | 2 | **false_pos** | [Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L15](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L15) |

## `C4|DEF` — **false_pos**
> occurrences here: 15 · corpus total: 56644 · executor: x86_64
> example: [Quick Start/ComputerUseAgent/src/cua_platform/main.py#L367](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/main.py#L367)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 12 · corpus total: 18195 · executor: x86_64
> example: [Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 12 · corpus total: 20139 · executor: x86_64
> example: [Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L20)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L15](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L15)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

