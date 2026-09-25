# thulasidharan96/API-Gateway

- GitHub: https://github.com/thulasidharan96/API-Gateway
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 19 · commit: `eee120aea1e6`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection` | src/app/api/v1/auth/routes.py#L27 | register_user uses Depends(get_db_session) and Depends(get_settings) to inject database session and configuration settings |
| 2 | `Nested dependency injection` | src/app/dependencies/auth.py#L19 | get_current_user depends on get_db_session and get_settings, creating a layered dependency chain |
| 3 | `Manual service instantiation` | src/app/api/v1/auth/routes.py#L27 | AuthService is manually instantiated with injected dependencies rather than being injected via Depends() |
| 4 | `Unused dependency parameter` | src/app/api/v1/clients/routes.py#L35 | list_clients uses '_' as a parameter name for get_current_user dependency, indicating the value is intentionally ignored |

## Pass 2 — reconcile with inventory of thulasidharan96/API-Gateway

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI Depends() for dependency injection (e.g., Depends(get_db_session), Depends(get_settings)) which matches the fingerprint's structural pattern of explicit dependency s... | src/app/api/v1/auth/routes.py#L27 |
| `C4|USED` | true_pos | **no (overturn)** | The get_db_session function is properly implemented as a dependency provider (async generator yielding AsyncSession) and is used throughout the codebase (e.g., in auth/routes.py:27). The initial la... | src/app/db/session.py#L19 |

### Missed by inventory (2)
- `Manual service instantiation instead of dependency injection` @ src/app/api/v1/auth/routes.py#L27 — AuthService is manually instantiated (service = AuthService(...)) rather than being injected via Depends(), representing a missed DI pattern
- `Unused dependency parameter with explicit underscore` @ src/app/api/v1/clients/routes.py#L35 — The parameter '_' in list_clients() explicitly ignores the get_current_user dependency, a pattern that was not captured in the fingerprint inventory

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 18 | **false_pos** | [src/app/api/v1/auth/routes.py#L27](https://github.com/thulasidharan96/API-Gateway/blob/eee120aea1e605790a98077b37d7c9e22b8ce199/src/app/api/v1/auth/routes.py#L27) |
| `C4|USED` | C4 | 1 | **false_pos** | [src/app/db/session.py#L19](https://github.com/thulasidharan96/API-Gateway/blob/eee120aea1e605790a98077b37d7c9e22b8ce199/src/app/db/session.py#L19) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 18 · corpus total: 83548 · executor: x86_64
> example: [src/app/api/v1/auth/routes.py#L27](https://github.com/thulasidharan96/API-Gateway/blob/eee120aea1e605790a98077b37d7c9e22b8ce199/src/app/api/v1/auth/routes.py#L27)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [src/app/db/session.py#L19](https://github.com/thulasidharan96/API-Gateway/blob/eee120aea1e605790a98077b37d7c9e22b8ce199/src/app/db/session.py#L19)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

