# its-spark-dev/toollayer-ai

- GitHub: https://github.com/its-spark-dev/toollayer-ai
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 23 · commit: `c142a39b57dd`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=2 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends with Annotated` | apps/control-plane/backend/control_plane/dependencies.py#L46 | SettingsDep is defined using Annotated[ControlPlaneSettings, Depends(settings_dependency)], showing explicit dependency injection via FastAPI's Depends mechanism. |
| 2 | `FastAPI Depends with Annotated` | apps/control-plane/backend/control_plane/dependencies.py#L67 | AdminDep and ServiceDep are created with Annotated[str, Depends(require_admin)] and Annotated[str, Depends(require_service)], demonstrating injection of authentication dependencies. |
| 3 | `FastAPI Depends in route handlers` | apps/control-plane/backend/control_plane/routes_admin.py#L46 | list_connectors uses SessionDep and AdminDep as parameters, showing dependency injection in endpoint functions. |
| 4 | `Custom session dependency` | apps/control-plane/backend/control_plane/db.py#L88 | get_session is defined as a FastAPI dependency yielding a request-scoped session using Depends, with explicit context manager handling. |

## Pass 2 — reconcile with inventory of its-spark-dev/toollayer-ai

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|BARE|BARE`, `C3|ELLIPSIS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | known | **no (overturn)** | The code explicitly uses Annotated[ControlPlaneSettings, Depends(...)] in dependencies.py:L46, which is a valid FastAPI dependency injection pattern. | apps/control-plane/backend/control_plane/dependencies.py#L46 |
| `C1|BARE|PARAM` | known | yes | The code uses Header(alias=...) as a parameter annotation in dependencies.py:L46, matching the fingerprint's structural pattern. | apps/control-plane/backend/control_plane/dependencies.py#L46 |
| `C3|CLASS|BARE` | false_pos | yes | The code defines a custom exception class Unauthenticated in dependencies.py:L14, which is unrelated to dependency injection and matches the false positive label. | apps/control-plane/backend/control_plane/dependencies.py#L14 |
| `C3|BARE|BARE` | variant | yes | The code uses Annotated[str, Depends(...)] in dependencies.py:L67, which is a valid but non-standard variant of dependency injection. | apps/control-plane/backend/control_plane/dependencies.py#L67 |
| `C3|ELLIPSIS|BARE` | variant | yes | The code uses Annotated[CallerIdentity | None, Depends(...)] in runtime_service/main.py:L112, which includes a union type and matches the variant label. | apps/runtime/runtime_service/main.py#L112 |
| `C4|USED` | known | **no (overturn)** | The code defines get_session as a FastAPI dependency using Depends in db.py:L88, which is a valid usage. | apps/control-plane/backend/control_plane/db.py#L88 |

### Missed by inventory (2)
- `FastAPI dependency in test fixtures` @ tests/conftest.py#L108 — The control_plane fixture uses Depends implicitly through the FastAPI app creation, but this pattern was not captured in the inventory.
- `Dependency injection in integration tests` @ tests/integration/test_read_your_own_write.py#L194 — The test modifies cp_db.session_scope to track transaction states, involving dependency injection patterns not detected by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 10 | **false_pos** | [apps/control-plane/backend/control_plane/db.py#L75](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/db.py#L75) |
| `C1|BARE|PARAM` | C1 | 6 | **known** | [apps/control-plane/backend/control_plane/dependencies.py#L39](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/dependencies.py#L39) |
| `C3|CLASS|BARE` | C3 | 3 | **false_pos** | [apps/control-plane/backend/control_plane/dependencies.py#L39](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/dependencies.py#L39) |
| `C3|BARE|BARE` | C3 | 2 | **variant** | [apps/control-plane/backend/control_plane/dependencies.py#L62](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/dependencies.py#L62) |
| `C3|ELLIPSIS|BARE` | C3 | 1 | **variant** | [apps/runtime/runtime_service/main.py#L112](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/runtime/runtime_service/main.py#L112) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/control-plane/backend/control_plane/db.py#L88](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/db.py#L88) |

## `C4|DEF` — **false_pos**
> occurrences here: 10 · corpus total: 56644 · executor: x86_64
> example: [apps/control-plane/backend/control_plane/db.py#L75](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/db.py#L75)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 6 · corpus total: 18195 · executor: x86_64
> example: [apps/control-plane/backend/control_plane/dependencies.py#L39](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/dependencies.py#L39)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 3 · corpus total: 20139 · executor: x86_64
> example: [apps/control-plane/backend/control_plane/dependencies.py#L39](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/dependencies.py#L39)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|BARE|BARE` — **variant**
> occurrences here: 2 · corpus total: 1316 · executor: x86_64
> example: [apps/control-plane/backend/control_plane/dependencies.py#L62](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/dependencies.py#L62)
> **rule:** C3

> **evidence (model):** Annotated type uses bare function (e.g. get_current_user) as metadata instead of Depends(...)

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 1 · corpus total: 1113 · executor: x86_64
> example: [apps/runtime/runtime_service/main.py#L112](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/runtime/runtime_service/main.py#L112)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/control-plane/backend/control_plane/db.py#L88](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/db.py#L88)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

