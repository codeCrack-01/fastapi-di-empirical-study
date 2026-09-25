# googleworkspace/devicetrustportal

- GitHub: https://github.com/googleworkspace/devicetrustportal
- Stars: 6 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 10 · commit: `ffbd2abdfe22`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends for authentication` | backend/routes/admin.py#L57 | The function check_admin_status uses Depends(get_current_user_email) to inject user authentication, a common FastAPI pattern for dependency injection. |
| 2 | `FastAPI Depends for authentication` | backend/routes/chaining.py#L110 | The generate_pairing_code function uses Depends(get_current_user_email) to inject user authentication, consistent with the same DI pattern observed in admin.py. |
| 3 | `FastAPI Depends for authentication` | backend/routes/devices.py#L233 | The get_my_approved_devices function uses Depends(get_current_user_email) to inject user authentication, showing this DI pattern is widely applied across routes. |
| 4 | `FastAPI Depends for authentication` | backend/routes/devices.py#L442 | The approve_device function uses Depends(get_current_user_email) to inject user authentication, reinforcing the consistent use of this DI approach. |
| 5 | `FastAPI Depends for authentication` | backend/routes/network_auth.py#L71 | The network_gated_approval function uses Depends(get_current_user_email) to inject user authentication, indicating this is a standardized DI practice across the codebase. |

## Pass 2 — reconcile with inventory of googleworkspace/devicetrustportal

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code correctly uses FastAPI's Depends for authentication injection, which is a standard DI pattern. The static tool's label contradicts the actual implementation. | backend/routes/admin.py#L57 |
| `C4|DEF` | false_pos | yes | The test code correctly uses pytest fixtures to mock services, which is standard practice. No contradiction found. | backend/tests/test_routes.py#L29 |

### Missed by inventory (2)
- `FastAPI Depends for authentication injection across multiple routes` @ backend/routes/admin.py#L57 — The inventory missed the widespread use of Depends(get_current_user_email) in admin.py, chaining.py, devices.py, and network_auth.py.
- `Consistent DI pattern in route functions` @ backend/routes/chaining.py#L110 — The inventory did not capture the standardized use of Depends for authentication across the codebase.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 9 | **false_pos** | [backend/routes/admin.py#L57](https://github.com/googleworkspace/devicetrustportal/blob/ffbd2abdfe22955347f3929e98e0b4e22cfbd693/backend/routes/admin.py#L57) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/tests/test_routes.py#L29](https://github.com/googleworkspace/devicetrustportal/blob/ffbd2abdfe22955347f3929e98e0b4e22cfbd693/backend/tests/test_routes.py#L29) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 9 · corpus total: 83548 · executor: x86_64
> example: [backend/routes/admin.py#L57](https://github.com/googleworkspace/devicetrustportal/blob/ffbd2abdfe22955347f3929e98e0b4e22cfbd693/backend/routes/admin.py#L57)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/tests/test_routes.py#L29](https://github.com/googleworkspace/devicetrustportal/blob/ffbd2abdfe22955347f3929e98e0b4e22cfbd693/backend/tests/test_routes.py#L29)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

