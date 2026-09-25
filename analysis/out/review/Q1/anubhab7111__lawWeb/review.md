# anubhab7111/lawWeb

- GitHub: https://github.com/anubhab7111/lawWeb
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 83 · commit: `945b2819c93a`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends for authentication and database sessions` | server/app/deps/auth.py#L22 | The get_current_user function uses Depends to inject a database session (via get_session) and handles JWT authentication, demonstrating FastAPI's dependency injection for authentication. This is re... |
| 2 | `Reused dependencies across routers` | server/app/routers/bookings.py#L64 | The checkout endpoint uses Depends(get_current_user) and Depends(get_session), showing how dependencies defined in deps/auth.py are reused across different routers for authentication and database a... |
| 3 | `Optional dependencies for flexible routing` | server/app/routers/chat.py#L256 | The chat endpoint uses get_current_user_optional (which returns Optional[User]) to handle both authenticated and unauthenticated users, demonstrating optional dependency injection for flexible rout... |

## Pass 2 — reconcile with inventory of anubhab7111/lawWeb

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | actual_auth_dependency | **no (overturn)** | The code explicitly uses get_current_user and get_current_user_optional for JWT authentication in multiple routers (e.g., /me, /checkout), contradicting the false_pos label. | server/app/deps/auth.py#L22 |
| `C4|DEF` | actual_db_dependency | **no (overturn)** | The code shows get_session is reused across routers (e.g., /checkout, /chat) for database access, contradicting the false_pos label. | server/app/routers/bookings.py#L64 |
| `C4|USED` | actual_optional_dependency | **no (overturn)** | The chat endpoint uses get_current_user_optional to handle both authenticated/unauthenticated users, contradicting the false_pos label. | server/app/routers/chat.py#L256 |

### Missed by inventory (2)
- `cross-router_dependency_reuse` @ server/app/routers/bookings.py#L64 — The inventory did not capture the reuse of auth.py dependencies (get_current_user, get_session) across multiple routers.
- `optional_dependency_for_flexible_routing` @ server/app/routers/chat.py#L256 — The inventory did not capture the use of get_current_user_optional for handling both authenticated/unauthenticated users in the chat endpoint.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 78 | **false_pos** | [server/app/deps/auth.py#L22](https://github.com/anubhab7111/lawWeb/blob/945b2819c93aed68367a9cd5cf4fabd96d074f26/server/app/deps/auth.py#L22) |
| `C4|DEF` | C4 | 4 | **false_pos** | [server/app/chatbot.py#L1594](https://github.com/anubhab7111/lawWeb/blob/945b2819c93aed68367a9cd5cf4fabd96d074f26/server/app/chatbot.py#L1594) |
| `C4|USED` | C4 | 1 | **false_pos** | [server/app/db/engine.py#L28](https://github.com/anubhab7111/lawWeb/blob/945b2819c93aed68367a9cd5cf4fabd96d074f26/server/app/db/engine.py#L28) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 78 · corpus total: 83548 · executor: x86_64
> example: [server/app/deps/auth.py#L22](https://github.com/anubhab7111/lawWeb/blob/945b2819c93aed68367a9cd5cf4fabd96d074f26/server/app/deps/auth.py#L22)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [server/app/chatbot.py#L1594](https://github.com/anubhab7111/lawWeb/blob/945b2819c93aed68367a9cd5cf4fabd96d074f26/server/app/chatbot.py#L1594)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [server/app/db/engine.py#L28](https://github.com/anubhab7111/lawWeb/blob/945b2819c93aed68367a9cd5cf4fabd96d074f26/server/app/db/engine.py#L28)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

