# CognitiveCodeAI/rag-main-2

- GitHub: https://github.com/CognitiveCodeAI/rag-main-2
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 49 · commit: `d032c103455a`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection for database and entitlements` | backend/app/routes/acl.py#L54 | The function update_document_policy uses Depends(get_session) to inject a database session and Depends(require_entitlements) to inject entitlement checks, which are standard FastAPI dependency inje... |
| 2 | `FastAPI Depends injection for database and entitlements` | backend/app/routes/documents.py#L250 | The function list_documents uses Depends(get_session) for database injection and Depends(get_entitlements) for entitlement checks, following the same FastAPI dependency injection pattern seen in ot... |
| 3 | `FastAPI Depends injection for database and entitlements` | backend/app/db/session.py#L36 | The get_session function provides a database session generator used throughout the app via Depends(), which is the core mechanism for database dependency injection in FastAPI. |

## Pass 2 — reconcile with inventory of CognitiveCodeAI/rag-main-2

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | yes | Code correctly uses FastAPI Depends injection for database and entitlements as standard patterns | backend/app/routes/acl.py#L54 |
| `C4|DEF` | false_pos | yes | Code correctly defines database session generator via Depends() as standard FastAPI pattern | backend/app/db/session.py#L36 |
| `C4|USED` | false_pos | yes | Code correctly uses FastAPI Depends injection for database and entitlements in routes | backend/app/routes/documents.py#L250 |

### Missed by inventory (1)
- `FastAPI Depends injection in list_documents route` @ backend/app/routes/documents.py#L250 — Dependency injection pattern not captured in inventory

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 45 | **false_pos** | [backend/app/routes/acl.py#L54](https://github.com/CognitiveCodeAI/rag-main-2/blob/d032c103455a76153523523b063c658a8f78d973/backend/app/routes/acl.py#L54) |
| `C4|DEF` | C4 | 3 | **false_pos** | [backend/app/db/session.py#L46](https://github.com/CognitiveCodeAI/rag-main-2/blob/d032c103455a76153523523b063c658a8f78d973/backend/app/db/session.py#L46) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/session.py#L36](https://github.com/CognitiveCodeAI/rag-main-2/blob/d032c103455a76153523523b063c658a8f78d973/backend/app/db/session.py#L36) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 45 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routes/acl.py#L54](https://github.com/CognitiveCodeAI/rag-main-2/blob/d032c103455a76153523523b063c658a8f78d973/backend/app/routes/acl.py#L54)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [backend/app/db/session.py#L46](https://github.com/CognitiveCodeAI/rag-main-2/blob/d032c103455a76153523523b063c658a8f78d973/backend/app/db/session.py#L46)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/session.py#L36](https://github.com/CognitiveCodeAI/rag-main-2/blob/d032c103455a76153523523b063c658a8f78d973/backend/app/db/session.py#L36)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

