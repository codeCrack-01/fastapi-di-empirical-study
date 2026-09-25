# STarLighTsMoveMenTs/European-Union-Complince-Portal

- GitHub: https://github.com/STarLighTsMoveMenTs/European-Union-Complince-Portal
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 15 · commit: `6a97b1249797`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based injection for authentication` | backend/routers/admin.py#L21 | The `Depends(require_admin)` pattern injects an authentication dependency into the `/admin/overview` endpoint, decoupling authorization logic from route implementation. |
| 2 | `Repeated authentication dependency injection` | backend/routers/issuer.py#L55 | The `Depends(require_user)` pattern is used in `/issuer/credential` to enforce user authentication, showing consistent use of DI for access control across multiple endpoints. |
| 3 | `Service dependency injection` | backend/routers/pnia_registry.py#L305 | The `Depends(require_user)` pattern in `/consents` demonstrates DI for user-authorized operations, with the dependency likely handling both authentication and consent validation. |

## Pass 2 — reconcile with inventory of STarLighTsMoveMenTs/European-Union-Complince-Portal

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code explicitly uses `Depends(require_admin)` and `Depends(require_user)` for authentication, which are valid DI usages. The static tool incorrectly labeled these as false positives. | backend/routers/admin.py#L21 |
| `C4|DEF` | false_pos | **no (overturn)** | The code in `server.py` uses FastAPI's `@asynccontextmanager` for lifespan management, which is a DI pattern for startup/shutdown hooks. The static tool's label is incorrect. | backend/server.py#L59 |

### Missed by inventory (2)
- `Dependency injection for consent management` @ backend/routers/pnia_registry.py#L305 — The `create_consent` endpoint uses `Depends(require_user)` for user-authorized operations, which was not captured by the static inventory.
- `DI in test fixtures for session setup` @ backend/tests/backend_test.py#L642 — The `seeded_session` fixture uses `_seed_auth_session` with dependency-like logic, but the inventory missed this test-related DI usage.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 13 | **false_pos** | [backend/routers/admin.py#L21](https://github.com/STarLighTsMoveMenTs/European-Union-Complince-Portal/blob/6a97b12497977c58d4c8d8bd519a932f59604d79/backend/routers/admin.py#L21) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/server.py#L59](https://github.com/STarLighTsMoveMenTs/European-Union-Complince-Portal/blob/6a97b12497977c58d4c8d8bd519a932f59604d79/backend/server.py#L59) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 13 · corpus total: 83548 · executor: x86_64
> example: [backend/routers/admin.py#L21](https://github.com/STarLighTsMoveMenTs/European-Union-Complince-Portal/blob/6a97b12497977c58d4c8d8bd519a932f59604d79/backend/routers/admin.py#L21)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/server.py#L59](https://github.com/STarLighTsMoveMenTs/European-Union-Complince-Portal/blob/6a97b12497977c58d4c8d8bd519a932f59604d79/backend/server.py#L59)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

