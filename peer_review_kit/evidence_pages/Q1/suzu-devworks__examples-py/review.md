# suzu-devworks/examples-py

- GitHub: https://github.com/suzu-devworks/examples-py
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 36 · commit: `d3773959f350`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=2 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection using Depends()` | packages/web/examples-fastapi/scripts/tutorials/app/main.py#L8 | The FastAPI instance is initialized with a dependency using Depends(get_query_token), demonstrating DI at the application level. |
| 2 | `Router-level dependency injection` | packages/web/examples-fastapi/scripts/tutorials/app/routers/items.py#L10 | The APIRouter is configured with dependencies=[Depends(get_token_header)], showing DI applied to a router. |
| 3 | `Nested dependency injection` | packages/web/examples-fastapi/scripts/tutorials/security/main.py#L116 | get_current_active_user depends on get_current_user, creating a layered DI structure where one dependency relies on another. |
| 4 | `Parameter-level dependency injection` | packages/web/examples-fastapi/scripts/tutorials/security/main.py#L141 | The read_users_me endpoint uses Annotated[User, Depends(get_current_active_user)] to inject the current user directly into the function parameter. |

## Pass 2 — reconcile with inventory of suzu-devworks/examples-py

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|BARE|BARE`, `C3|CLASS|EMPTY`, `C1|EMPTY|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | known | **no (overturn)** | The test fixtures in numpy and context manager tests use DI via pytest fixtures (e.g., @pytest.fixture), which are valid DI patterns. | packages/fundamentals/examples-lib/tests/libraries/numpy/basics/test_numpy_basics_creation.py#L214 |
| `C3|CLASS|BARE` | known | **no (overturn)** | The code uses nested DI (get_current_active_user depends on get_current_user), which is a valid class-level dependency pattern. | packages/web/examples-fastapi/scripts/tutorials/security/main.py#L116 |
| `C3|CLASS|EMPTY` | known | **no (overturn)** | The login_for_access_token endpoint uses parameter-level DI with Depends(), which is a valid pattern. | packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125 |
| `C1|EMPTY|PARAM` | known | **no (overturn)** | The parameter form_data uses Depends() correctly, which is a valid DI pattern. | packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125 |

### Missed by inventory (3)
- `pytest fixture-based DI` @ packages/fundamentals/examples-lib/tests/libraries/numpy/basics/test_numpy_basics_creation.py#L214 — The inventory missed fixtures like @pytest.fixture which implement DI in tests.
- `nested DI in security layer` @ packages/web/examples-fastapi/scripts/tutorials/security/main.py#L116 — The inventory missed the nested dependency structure (get_current_active_user → get_current_user).
- `router-level DI configuration` @ packages/web/examples-fastapi/scripts/tutorials/app/routers/items.py#L10 — The inventory missed the APIRouter's dependencies=[Depends(...)] pattern.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 18 | **false_pos** | [packages/fundamentals/examples-lib/tests/libraries/numpy/basics/test_numpy_basics_creation.py#L214](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/fundamentals/examples-lib/tests/libraries/numpy/basics/test_numpy_basics_creation.py#L214) |
| `C1|BARE|PARAM` | C1 | 7 | **known** | [packages/web/examples-fastapi/scripts/tutorials/app/main.py#L8](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/app/main.py#L8) |
| `C3|CLASS|BARE` | C3 | 6 | **false_pos** | [packages/web/examples-fastapi/scripts/tutorials/security/main.py#L116](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L116) |
| `C3|BARE|BARE` | C3 | 2 | **variant** | [packages/web/examples-fastapi/scripts/tutorials/security/main.py#L95](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L95) |
| `C3|CLASS|EMPTY` | C3 | 2 | **false_pos** | [packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125) |
| `C1|EMPTY|PARAM` | C1 | 1 | **variant** | [packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125) |

## `C4|DEF` — **false_pos**
> occurrences here: 18 · corpus total: 56644 · executor: x86_64
> example: [packages/fundamentals/examples-lib/tests/libraries/numpy/basics/test_numpy_basics_creation.py#L214](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/fundamentals/examples-lib/tests/libraries/numpy/basics/test_numpy_basics_creation.py#L214)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 7 · corpus total: 18195 · executor: x86_64
> example: [packages/web/examples-fastapi/scripts/tutorials/app/main.py#L8](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/app/main.py#L8)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 6 · corpus total: 20139 · executor: x86_64
> example: [packages/web/examples-fastapi/scripts/tutorials/security/main.py#L116](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L116)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|BARE|BARE` — **variant**
> occurrences here: 2 · corpus total: 1316 · executor: x86_64
> example: [packages/web/examples-fastapi/scripts/tutorials/security/main.py#L95](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L95)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 2 · corpus total: 89 · executor: x86_64
> example: [packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 1 · corpus total: 45 · executor: x86_64
> example: [packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L125)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

