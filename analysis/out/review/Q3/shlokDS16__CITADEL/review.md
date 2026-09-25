# shlokDS16/CITADEL

- GitHub: https://github.com/shlokDS16/CITADEL
- Stars: 3 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 74 · commit: `6f2ef5beb6ca`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Role-based dependency injection with factory pattern` | backend/app/core/deps.py#L15 | The require_roles function creates a dependency factory that returns a guard function using Depends(get_current_user), demonstrating a pattern where role-specific dependencies are generated dynamic... |
| 2 | `Custom dependency injection for user claims` | backend/app/modules/expenses/router.py#L123 | The _citizen function is injected as a dependency (citizen: str = Depends(_citizen)) to extract user identity, showing a custom dependency that's reused across multiple endpoints. |
| 3 | `Rate limit dependency injection` | backend/app/modules/fake_news/router.py#L45 | The _RL_HEAVY and _RL_STD dependencies use rate_limit with specific buckets, illustrating how rate limiting is implemented as a reusable dependency across routes. |
| 4 | `Composition of multiple dependencies` | backend/app/modules/tickets/router.py#L50 | The _claims and _actor functions are composed into dependencies that extract user information, showing how multiple dependencies can be combined for complex authorization logic. |

## Pass 2 — reconcile with inventory of shlokDS16/CITADEL

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `require_roles_factory` | Role-based dependency injection with factory pattern | yes | The require_roles function in deps.py:15 creates a dependency factory that returns a guard function using Depends(get_current_user), matching the observation. | backend/app/core/deps.py#L15 |
| `citizen_dependency` | Custom dependency injection for user claims | yes | The _citizen function in expenses/router.py:123 is injected as a dependency (citizen: str = Depends(_citizen)), matching the observation. | backend/app/modules/expenses/router.py#L123 |
| `rate_limit_dependency` | Rate limit dependency injection | yes | The _RL_HEAVY and _RL_STD dependencies in fake_news/router.py:45 use rate_limit with specific buckets, matching the observation. | backend/app/modules/fake_news/router.py#L45 |
| `dependency_composition` | Composition of multiple dependencies | yes | The _claims and _actor functions in tickets/router.py:50 are composed into dependencies that extract user information, matching the observation. | backend/app/modules/tickets/router.py#L50 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 39 | **false_pos** | [backend/app/core/deps.py#L44](https://github.com/shlokDS16/CITADEL/blob/6f2ef5beb6ca13eee01a2dd1348a2768b38bb52b/backend/app/core/deps.py#L44) |
| `C1|BARE|PARAM` | C1 | 18 | **known** | [backend/app/modules/auth/router.py#L23](https://github.com/shlokDS16/CITADEL/blob/6f2ef5beb6ca13eee01a2dd1348a2768b38bb52b/backend/app/modules/auth/router.py#L23) |
| `C4|DEF` | C4 | 17 | **false_pos** | [backend/app/main.py#L47](https://github.com/shlokDS16/CITADEL/blob/6f2ef5beb6ca13eee01a2dd1348a2768b38bb52b/backend/app/main.py#L47) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 39 · corpus total: 83548 · executor: x86_64
> example: [backend/app/core/deps.py#L44](https://github.com/shlokDS16/CITADEL/blob/6f2ef5beb6ca13eee01a2dd1348a2768b38bb52b/backend/app/core/deps.py#L44)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 18 · corpus total: 18195 · executor: x86_64
> example: [backend/app/modules/auth/router.py#L23](https://github.com/shlokDS16/CITADEL/blob/6f2ef5beb6ca13eee01a2dd1348a2768b38bb52b/backend/app/modules/auth/router.py#L23)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 17 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L47](https://github.com/shlokDS16/CITADEL/blob/6f2ef5beb6ca13eee01a2dd1348a2768b38bb52b/backend/app/main.py#L47)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

