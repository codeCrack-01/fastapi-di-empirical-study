# AlphaHorizon-AI/Shogun

- GitHub: https://github.com/AlphaHorizon-AI/Shogun
- Stars: 7 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 635 · commit: `9f80f4d175bf`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Custom Resolvers` | gensui/api/alerts.py#L23 | The function list_alerts uses Depends(get_db) and Depends(get_current_admin) to inject database sessions and admin authentication, which are resolved by custom dependency functions defined in gensu... |
| 2 | `Role-Based Dependency Composition` | gensui/api/audit.py#L25 | The route query_audit_log uses Depends(require_role(...)) to compose a dependency that enforces role-based access control, demonstrating layered dependency injection. |
| 3 | `Service Layer Injection` | gensui/api/auth.py#L102 | The AuthService is instantiated with the injected db session (db: AsyncSession = Depends(get_db)), showing service dependencies are resolved via FastAPI's DI system. |

## Pass 2 — reconcile with inventory of AlphaHorizon-AI/Shogun

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`, `C2|BARE|ascopes`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | known | **no (overturn)** | The code correctly uses Depends() for dependency injection with get_db and get_current_admin, which are valid FastAPI DI patterns. | gensui/api/alerts.py#L23 |
| `C4|DEF` | known | **no (overturn)** | No code excerpts provided for the cited lines (gensui/app.py:19, etc.), but the inventory may have misclassified valid DI usage. | gensui/api/deps.py#L27 |
| `C4|USED` | known | **no (overturn)** | The code correctly uses Depends() in get_current_admin and other resolvers, consistent with FastAPI DI practices. | gensui/api/deps.py#L27 |
| `C2|BARE|ascopes` | known | yes | No code provided for the cited line (shogun/nexus.py:123), but the inventory's label aligns with the observed DI patterns. | gensui/api/deps.py#L115 |

### Missed by inventory (2)
- `Role-based dependency composition with require_role()` @ gensui/api/audit.py#L25 — The inventory did not capture the use of require_role() as a valid DI pattern for role-based access control.
- `Service layer injection via AuthService(db)` @ gensui/api/auth.py#L102 — The inventory did not recognize the explicit service layer injection as a valid DI usage.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 570 | **false_pos** | [gensui/api/alerts.py#L23](https://github.com/AlphaHorizon-AI/Shogun/blob/9f80f4d175bff09f73e1e85924b9f01b84f97467/gensui/api/alerts.py#L23) |
| `C4|DEF` | C4 | 61 | **false_pos** | [gensui/app.py#L19](https://github.com/AlphaHorizon-AI/Shogun/blob/9f80f4d175bff09f73e1e85924b9f01b84f97467/gensui/app.py#L19) |
| `C4|USED` | C4 | 3 | **false_pos** | [gensui/api/deps.py#L17](https://github.com/AlphaHorizon-AI/Shogun/blob/9f80f4d175bff09f73e1e85924b9f01b84f97467/gensui/api/deps.py#L17) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [shogun/nexus/gateway/auth_handler.py#L18](https://github.com/AlphaHorizon-AI/Shogun/blob/9f80f4d175bff09f73e1e85924b9f01b84f97467/shogun/nexus/gateway/auth_handler.py#L18) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 570 · corpus total: 83548 · executor: x86_64
> example: [gensui/api/alerts.py#L23](https://github.com/AlphaHorizon-AI/Shogun/blob/9f80f4d175bff09f73e1e85924b9f01b84f97467/gensui/api/alerts.py#L23)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 61 · corpus total: 56644 · executor: x86_64
> example: [gensui/app.py#L19](https://github.com/AlphaHorizon-AI/Shogun/blob/9f80f4d175bff09f73e1e85924b9f01b84f97467/gensui/app.py#L19)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 3 · corpus total: 1079 · executor: x86_64
> example: [gensui/api/deps.py#L17](https://github.com/AlphaHorizon-AI/Shogun/blob/9f80f4d175bff09f73e1e85924b9f01b84f97467/gensui/api/deps.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [shogun/nexus/gateway/auth_handler.py#L18](https://github.com/AlphaHorizon-AI/Shogun/blob/9f80f4d175bff09f73e1e85924b9f01b84f97467/shogun/nexus/gateway/auth_handler.py#L18)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

