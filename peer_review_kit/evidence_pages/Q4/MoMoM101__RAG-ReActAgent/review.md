# MoMoM101/RAG-ReActAgent

- GitHub: https://github.com/MoMoM101/RAG-ReActAgent
- Stars: 75 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 77 · commit: `3c57e634feaf`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | backend/api/audit.py#L18 | Depends(get_current_user) and require_role("system_admin") are used as dependencies in the list_audit_logs endpoint. |
| 2 | `FastAPI Depends injection` | backend/api/auth.py#L140 | Depends(jwt_auth) is injected into the /me endpoint for authentication. |
| 3 | `FastAPI Depends injection` | backend/api/conversations.py#L21 | db: AsyncSession = Depends(get_db) injects a database session into list_conversations. |
| 4 | `FastAPI Depends injection` | backend/api/users.py#L37 | Depends(get_current_user) and require_role("system_admin") are used in list_users for authentication and authorization. |
| 5 | `Router-level dependency injection` | backend/main.py#L386 | app.include_router(..., dependencies=[Depends(jwt_auth)]) applies JWT auth to multiple routers at the router level. |

## Pass 2 — reconcile with inventory of MoMoM101/RAG-ReActAgent

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | known | **no (overturn)** | The code at backend/api/chat.py#289 uses Depends(jwt_auth) explicitly, which is a valid DI occurrence. | backend/api/chat.py#L289 |
| `C1|BARE|SIG` | known | **no (overturn)** | The code at backend/api/audit.py#18 uses Depends(get_current_user) and require_role("system_admin"), which are valid DI dependencies. | backend/api/audit.py#L18 |
| `C4|USED` | known | **no (overturn)** | The code at backend/models/database.py#239 defines get_db() as a dependency injector, which is a valid DI occurrence. | backend/models/database.py#L239 |

### Missed by inventory (2)
- `Router-level dependency injection` @ backend/main.py#L386 — The code applies dependencies=[Depends(jwt_auth)] to multiple routers, which is a valid DI pattern but may have been missed by the inventory.
- `Dependency factory definition` @ backend/security.py#L72 — The require_role function is a dependency factory, which is a valid DI pattern but may not have been captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 41 | **false_pos** | [backend/agent/loop.py#L258](https://github.com/MoMoM101/RAG-ReActAgent/blob/3c57e634feafc6ecb402b13723d9a5a07ec6dc4c/backend/agent/loop.py#L258) |
| `C1|BARE|SIG` | C1 | 26 | **false_pos** | [backend/api/audit.py#L18](https://github.com/MoMoM101/RAG-ReActAgent/blob/3c57e634feafc6ecb402b13723d9a5a07ec6dc4c/backend/api/audit.py#L18) |
| `C1|BARE|PARAM` | C1 | 9 | **known** | [backend/main.py#L382](https://github.com/MoMoM101/RAG-ReActAgent/blob/3c57e634feafc6ecb402b13723d9a5a07ec6dc4c/backend/main.py#L382) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/models/database.py#L239](https://github.com/MoMoM101/RAG-ReActAgent/blob/3c57e634feafc6ecb402b13723d9a5a07ec6dc4c/backend/models/database.py#L239) |

## `C4|DEF` — **false_pos**
> occurrences here: 41 · corpus total: 56644 · executor: x86_64
> example: [backend/agent/loop.py#L258](https://github.com/MoMoM101/RAG-ReActAgent/blob/3c57e634feafc6ecb402b13723d9a5a07ec6dc4c/backend/agent/loop.py#L258)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 26 · corpus total: 83548 · executor: x86_64
> example: [backend/api/audit.py#L18](https://github.com/MoMoM101/RAG-ReActAgent/blob/3c57e634feafc6ecb402b13723d9a5a07ec6dc4c/backend/api/audit.py#L18)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 9 · corpus total: 18195 · executor: x86_64
> example: [backend/main.py#L382](https://github.com/MoMoM101/RAG-ReActAgent/blob/3c57e634feafc6ecb402b13723d9a5a07ec6dc4c/backend/main.py#L382)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/models/database.py#L239](https://github.com/MoMoM101/RAG-ReActAgent/blob/3c57e634feafc6ecb402b13723d9a5a07ec6dc4c/backend/models/database.py#L239)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

