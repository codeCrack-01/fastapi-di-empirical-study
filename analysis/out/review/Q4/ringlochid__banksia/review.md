# ringlochid/banksia

- GitHub: https://github.com/ringlochid/banksia
- Stars: 67 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 103 · commit: `3cddeeaceadf`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=1 known=2 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Annotated and Depends` | src/banksia/interfaces/http/routers/command_runs.py#L28 | Defines type aliases using Annotated[Type, Depends(...)] for DBSession, ActorRef, and RuntimeEffectPublisherDep, which FastAPI resolves at runtime. This is the core DI pattern in FastAPI where depe... |
| 2 | `FastAPI dependency injection with Annotated and Depends` | src/banksia/interfaces/http/routers/human_requests.py#L27 | Repeats the same DI pattern as command_runs.py, defining DBSession, ActorRef, and RuntimeEffectPublisherDep with Depends() for dependency resolution in route handlers. |
| 3 | `Security dependency injection` | src/banksia/interfaces/http/support.py#L64 | Uses Depends(_require_support_admission) in FastAPI app dependencies to enforce bearer token authentication, demonstrating DI for security checks. |

## Pass 2 — reconcile with inventory of ringlochid/banksia

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`, `C2|BARE|ascopes`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | real_usage | **no (overturn)** | The code shows actual async context managers for lifespan management in integrations, contradicting the 'false_pos' label. | src/banksia/integrations/claude/adapter.py#L249 |
| `C3|CLASS|BARE` | real_di_usage | **no (overturn)** | The code defines valid FastAPI DI patterns with Annotated[Type, Depends(...)] in multiple routers, contradicting the 'false_pos' label. | src/banksia/interfaces/http/routers/command_runs.py#L28 |
| `C4|USED` | real_di_usage | **no (overturn)** | The code implements a valid FastAPI dependency injection pattern for database sessions, contradicting the 'false_pos' label. | src/banksia/persistence/session.py#L91 |

### Missed by inventory (2)
- `FastAPI DI with Annotated[Type, Depends(...)] in task_activities.py` @ src/banksia/interfaces/http/routers/task_activities.py#L25 — The inventory did not capture this valid DI pattern in task_activities router
- `Security DI with Depends(...) in MCP node server` @ src/banksia/interfaces/mcp/node/server.py#L292 — The inventory missed this security-related DI usage in MCP projection apps

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 70 | **false_pos** | [src/banksia/integrations/claude/adapter.py#L249](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/integrations/claude/adapter.py#L249) |
| `C1|BARE|PARAM` | C1 | 16 | **known** | [src/banksia/interfaces/http/routers/command_runs.py#L28](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/interfaces/http/routers/command_runs.py#L28) |
| `C3|CLASS|BARE` | C3 | 9 | **false_pos** | [src/banksia/interfaces/http/routers/command_runs.py#L28](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/interfaces/http/routers/command_runs.py#L28) |
| `C3|ELLIPSIS|BARE` | C3 | 6 | **variant** | [src/banksia/interfaces/http/routers/command_runs.py#L29](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/interfaces/http/routers/command_runs.py#L29) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [src/banksia/interfaces/http/support.py#L77](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/interfaces/http/support.py#L77) |
| `C4|USED` | C4 | 1 | **false_pos** | [src/banksia/persistence/session.py#L91](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/persistence/session.py#L91) |

## `C4|DEF` — **false_pos**
> occurrences here: 70 · corpus total: 56644 · executor: x86_64
> example: [src/banksia/integrations/claude/adapter.py#L249](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/integrations/claude/adapter.py#L249)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 16 · corpus total: 18195 · executor: x86_64
> example: [src/banksia/interfaces/http/routers/command_runs.py#L28](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/interfaces/http/routers/command_runs.py#L28)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 9 · corpus total: 20139 · executor: x86_64
> example: [src/banksia/interfaces/http/routers/command_runs.py#L28](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/interfaces/http/routers/command_runs.py#L28)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 6 · corpus total: 1113 · executor: x86_64
> example: [src/banksia/interfaces/http/routers/command_runs.py#L29](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/interfaces/http/routers/command_runs.py#L29)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [src/banksia/interfaces/http/support.py#L77](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/interfaces/http/support.py#L77)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [src/banksia/persistence/session.py#L91](https://github.com/ringlochid/banksia/blob/3cddeeaceadf4375f7451b1023c74c476eda2bb2/src/banksia/persistence/session.py#L91)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

