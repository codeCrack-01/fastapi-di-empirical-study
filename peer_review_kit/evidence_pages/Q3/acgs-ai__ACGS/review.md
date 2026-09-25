# acgs-ai/ACGS

- GitHub: https://github.com/acgs-ai/ACGS
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 119 · commit: `81de59eabacd`
- Fingerprints touching this repo: 6
- Label mix: novel=0 variant=1 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | acgs_governance_eval_mvp/governance/service/api.py#L66 | verify_caller uses Depends(_http_bearer) to inject HTTP bearer authentication |
| 2 | `Chained dependencies` | acgs_governance_eval_mvp/governance/service/api.py#L93 | validate endpoint uses Depends(verify_caller) which itself depends on _http_bearer |
| 3 | `Annotated dependencies` | apps/second-brain/service/src/second_brain/app.py#L98 | PrincipalDependency uses Annotated[Principal, Depends(get_principal)] for type hinting |
| 4 | `Custom dependency factories` | packages/acgs-control-plane/src/acgs_control_plane/app.py#L229 | _session_dep creates a session factory with Depends() and exports as SessionDep |
| 5 | `Role-based dependencies` | packages/agent-bus-analyzer/src/agent_bus_analyzer/auth.py#L203 | require_reviewer_role dependency enforces RBAC through Depends() |

## Pass 2 — reconcile with inventory of acgs-ai/ACGS

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C1|BARE|SIG`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_depends_pattern` | Consistent use of FastAPI Depends for dependency injection | yes | All endpoints use Depends() for authentication, authorization, and session management | acgs-control-plane/src/acgs_control_plane/app.py#L377 |
| `rbac_enforcement` | Role-based access control via dependencies | yes | require() and require_reviewer_role() both use Depends() to enforce permissions/roles | agent-bus-analyzer/src/agent_bus_analyzer/auth.py#L201 |
| `audit_logging` | Audit event iteration pattern | yes | Both in_memory.py and jsonl_chain.py implement iter_events() for audit records | acgs_governance_eval_mvp/governance/audit/in_memory.py#L41 |
| `session_management` | Scoped database sessions with context managers | yes | scoped_session() uses context manager pattern for transactional integrity | second-brain/service/src/second_brain/db.py#L82 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 88 | **false_pos** | [acgs_governance_eval_mvp/governance/audit/in_memory.py#L41](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/acgs_governance_eval_mvp/governance/audit/in_memory.py#L41) |
| `C1|BARE|PARAM` | C1 | 13 | **known** | [apps/second-brain/service/src/second_brain/app.py#L98](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/apps/second-brain/service/src/second_brain/app.py#L98) |
| `C1|BARE|SIG` | C1 | 7 | **false_pos** | [acgs_governance_eval_mvp/governance/service/api.py#L66](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/acgs_governance_eval_mvp/governance/service/api.py#L66) |
| `C3|CLASS|BARE` | C3 | 5 | **false_pos** | [apps/second-brain/service/src/second_brain/app.py#L98](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/apps/second-brain/service/src/second_brain/app.py#L98) |
| `C3|ELLIPSIS|BARE` | C3 | 5 | **variant** | [packages/agent-bus-analyzer/src/agent_bus_analyzer/auth.py#L201](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/packages/agent-bus-analyzer/src/agent_bus_analyzer/auth.py#L201) |
| `C4|USED` | C4 | 1 | **false_pos** | [packages/acgs-control-plane/src/acgs_control_plane/app.py#L221](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/packages/acgs-control-plane/src/acgs_control_plane/app.py#L221) |

## `C4|DEF` — **false_pos**
> occurrences here: 88 · corpus total: 56644 · executor: x86_64
> example: [acgs_governance_eval_mvp/governance/audit/in_memory.py#L41](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/acgs_governance_eval_mvp/governance/audit/in_memory.py#L41)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 13 · corpus total: 18195 · executor: x86_64
> example: [apps/second-brain/service/src/second_brain/app.py#L98](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/apps/second-brain/service/src/second_brain/app.py#L98)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 7 · corpus total: 83548 · executor: x86_64
> example: [acgs_governance_eval_mvp/governance/service/api.py#L66](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/acgs_governance_eval_mvp/governance/service/api.py#L66)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 5 · corpus total: 20139 · executor: x86_64
> example: [apps/second-brain/service/src/second_brain/app.py#L98](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/apps/second-brain/service/src/second_brain/app.py#L98)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 5 · corpus total: 1113 · executor: x86_64
> example: [packages/agent-bus-analyzer/src/agent_bus_analyzer/auth.py#L201](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/packages/agent-bus-analyzer/src/agent_bus_analyzer/auth.py#L201)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [packages/acgs-control-plane/src/acgs_control_plane/app.py#L221](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/packages/acgs-control-plane/src/acgs_control_plane/app.py#L221)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

