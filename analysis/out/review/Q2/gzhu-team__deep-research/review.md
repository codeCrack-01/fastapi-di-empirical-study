# gzhu-team/deep-research

- GitHub: https://github.com/gzhu-team/deep-research
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 47 · commit: `8c1a538102ac`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Session Management` | app/backend/router/auth_router.py#L103 | The code handles user authentication by creating a session token upon login (_set_session_cookie) and validating it via get_current_user dependency, which is a core aspect of session management. Th... |
| 2 | `Access Control` | app/backend/router/research_router.py#L27 | The _validate_thread_owner function enforces ownership checks on conversations by verifying that the thread ID is prefixed with the user's ID, ensuring users can only access their own data. |

## Pass 2 — reconcile with inventory of gzhu-team/deep-research

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `session_management` | session_management | yes | Session tokens are created, validated, and destroyed via cookies in auth_router.py (lines 103-142). | app/backend/router/auth_router.py#L103 |
| `access_control` | access_control | yes | Thread ownership is enforced via _validate_thread_owner in research_router.py (line 27) and user_id checks in conversation_router.py. | app/backend/router/research_router.py#L27 |
| `password_policy` | password_policy | yes | Password change endpoint enforces non-equality of new/current passwords in auth_router.py (line 130). | app/backend/router/auth_router.py#L130 |
| `input_validation` | input_validation | yes | Tenant ID validation in conversation_router.py (line 24) and research_router.py (line 35) ensures only allowed tenants are used. | app/backend/router/conversation_router.py#L24 |
| `audit_logging` | audit_logging | yes | Admin logout triggers audit logging in auth_router.py (line 142). | app/backend/router/auth_router.py#L142 |

### Missed by inventory (2)
- `missing_password_strength_check` @ app/backend/router/auth_router.py#L130 — Password change lacks strength validation.
- `missing_conversation_ownership_check` @ app/backend/router/conversation_router.py#L35 — get_conversation does not explicitly verify user ownership of thread.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 44 | **false_pos** | [app/backend/router/admin_router.py#L41](https://github.com/gzhu-team/deep-research/blob/8c1a538102ac01457da290e4af001b7c0623a168/app/backend/router/admin_router.py#L41) |
| `C4|DEF` | C4 | 3 | **false_pos** | [app/backend/router/research_router.py#L66](https://github.com/gzhu-team/deep-research/blob/8c1a538102ac01457da290e4af001b7c0623a168/app/backend/router/research_router.py#L66) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 44 · corpus total: 83548 · executor: x86_64
> example: [app/backend/router/admin_router.py#L41](https://github.com/gzhu-team/deep-research/blob/8c1a538102ac01457da290e4af001b7c0623a168/app/backend/router/admin_router.py#L41)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [app/backend/router/research_router.py#L66](https://github.com/gzhu-team/deep-research/blob/8c1a538102ac01457da290e4af001b7c0623a168/app/backend/router/research_router.py#L66)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

