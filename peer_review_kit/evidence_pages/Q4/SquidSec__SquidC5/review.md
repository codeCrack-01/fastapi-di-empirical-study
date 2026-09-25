# SquidSec/SquidC5

- GitHub: https://github.com/SquidSec/SquidC5
- Stars: 31 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 148 · commit: `2b8959512ecf`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Policy Enforcement with Audit Logging` | src/squidc5/api/routes.py#L1332 | Every critical operation (create_listener, start_listener, generate_payload, etc.) includes a call to state.policy.check_and_audit(), ensuring permissions are verified and actions are logged with r... |
| 2 | `Feature Flag Checks` | src/squidc5/api/routes.py#L1332 | Operations like listener creation are guarded by feature flags (e.g., 'http_listeners', 'dns_listeners'). This allows dynamic control over functionality without code changes, enabling phased rollou... |
| 3 | `Centralized State Management` | src/squidc5/api/routes.py#L1361 | The state object (retrieved via get_state(request)) serves as a single source of truth for listeners, policies, databases, and metrics. This promotes consistency and simplifies testing by decouplin... |

## Pass 2 — reconcile with inventory of SquidSec/SquidC5

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `policy_enforcement` | Policy Enforcement with Audit Logging | yes | All critical operations (create_listener, start_listener, generate_payload, etc.) include state.policy.check_and_audit() calls as observed. | src/squidc5/api/routes.py#L1332 |
| `feature_flags` | Feature Flag Checks | yes | Operations like listener creation are guarded by feature flags (e.g., 'http_listeners', 'dns_listeners') as observed. | src/squidc5/api/routes.py#L1332 |
| `centralized_state` | Centralized State Management | yes | The state object (retrieved via get_state(request)) is used consistently across all operations as observed. | src/squidc5/api/routes.py#L1361 |

### Missed by inventory (2)
- `Missing policy enforcement in delete_listener` @ src/squidc5/api/routes.py#L1390 — delete_listener lacks a state.policy.check_and_audit() call despite being a critical operation.
- `Missing policy enforcement in stop_listener` @ src/squidc5/api/routes.py#L1378 — stop_listener lacks a state.policy.check_and_audit() call despite being a critical operation.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 133 | **false_pos** | [src/squidc5/api/routes.py#L473](https://github.com/SquidSec/SquidC5/blob/2b8959512ecf99914e9ae8bc43b0f68de6c5040d/src/squidc5/api/routes.py#L473) |
| `C4|DEF` | C4 | 15 | **false_pos** | [src/squidc5/api/routes.py#L2150](https://github.com/SquidSec/SquidC5/blob/2b8959512ecf99914e9ae8bc43b0f68de6c5040d/src/squidc5/api/routes.py#L2150) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 133 · corpus total: 83548 · executor: x86_64
> example: [src/squidc5/api/routes.py#L473](https://github.com/SquidSec/SquidC5/blob/2b8959512ecf99914e9ae8bc43b0f68de6c5040d/src/squidc5/api/routes.py#L473)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 15 · corpus total: 56644 · executor: x86_64
> example: [src/squidc5/api/routes.py#L2150](https://github.com/SquidSec/SquidC5/blob/2b8959512ecf99914e9ae8bc43b0f68de6c5040d/src/squidc5/api/routes.py#L2150)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

