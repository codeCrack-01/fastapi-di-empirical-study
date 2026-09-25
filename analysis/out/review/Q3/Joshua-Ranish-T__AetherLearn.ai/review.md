# Joshua-Ranish-T/AetherLearn.ai

- GitHub: https://github.com/Joshua-Ranish-T/AetherLearn.ai
- Stars: 16 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 21 · commit: `37802ed399db`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends usage for authentication` | backend/app/api/v1/generation.py#L39 | The route handler uses Depends(get_current_user) to inject authenticated user data, a common DI pattern in FastAPI for authentication. |
| 2 | `Dependency composition` | backend/app/core/auth.py#L64 | get_current_user depends on get_optional_user, showing layered dependency injection where dependencies can themselves depend on other dependencies. |
| 3 | `Shared dependency injection` | backend/app/api/v1/projects.py#L43 | The explain_topic endpoint uses Depends(get_current_user), demonstrating reuse of the same authentication dependency across multiple routes. |

## Pass 2 — reconcile with inventory of Joshua-Ranish-T/AetherLearn.ai

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() for authentication injection, a canonical DI pattern. The labeled 'false_pos' contradicts this. | backend/app/api/v1/generation.py#L39 |
| `C4|DEF` | false_pos | yes | The code does not use explicit DI mechanisms like Depends() or injection patterns. The labeled 'false_pos' aligns with the code's lack of DI. | backend/app/api/v1/generation.py#L194 |

### Missed by inventory (2)
- `FastAPI Depends-based authentication DI` @ backend/app/api/v1/generation.py#L39 — The inventory missed the explicit use of Depends(get_current_user) for authentication, a clear DI occurrence.
- `Shared DI dependency across routes` @ backend/app/api/v1/projects.py#L43 — The inventory missed the reuse of get_current_user dependency across multiple endpoints, a structural DI fingerprint.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 16 | **false_pos** | [backend/app/api/v1/generation.py#L39](https://github.com/Joshua-Ranish-T/AetherLearn.ai/blob/37802ed399db5f549508d1166c04be0e6795d60e/backend/app/api/v1/generation.py#L39) |
| `C4|DEF` | C4 | 5 | **false_pos** | [backend/app/api/v1/generation.py#L194](https://github.com/Joshua-Ranish-T/AetherLearn.ai/blob/37802ed399db5f549508d1166c04be0e6795d60e/backend/app/api/v1/generation.py#L194) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 16 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/v1/generation.py#L39](https://github.com/Joshua-Ranish-T/AetherLearn.ai/blob/37802ed399db5f549508d1166c04be0e6795d60e/backend/app/api/v1/generation.py#L39)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/v1/generation.py#L194](https://github.com/Joshua-Ranish-T/AetherLearn.ai/blob/37802ed399db5f549508d1166c04be0e6795d60e/backend/app/api/v1/generation.py#L194)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

