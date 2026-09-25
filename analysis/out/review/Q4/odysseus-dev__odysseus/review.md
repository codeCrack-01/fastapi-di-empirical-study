# odysseus-dev/odysseus

- GitHub: https://github.com/odysseus-dev/odysseus
- Stars: 84888 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 344 · commit: `b4d12932a953`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection (Constructor/Setter)` | routes/email_routes.py#L3711 | The code uses FastAPI's dependency injection system via 'owner: str = Depends(require_owner)' to inject authentication context into routes, demonstrating IoC. |
| 2 | `Service Layer` | routes/email_routes.py#L3733 | Functions like '_store_email_flag' and '_email_index_update_flags' encapsulate business logic, separating concerns between routing and data operations. |
| 3 | `Resource Management` | routes/email_routes.py#L4232 | Uses 'with _imap(...) as conn:' context manager to ensure proper cleanup of IMAP connections, aligning with RAII principles. |
| 4 | `Singleton` | routes/email_routes.py#L4020 | COMPOSE_UPLOADS_DIR is a singleton directory path used consistently for file staging, ensuring a single point of access. |

## Pass 2 — reconcile with inventory of odysseus-dev/odysseus

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `Dependency Injection (Constructor/Setter)` | Dependency Injection (Constructor/Setter) | yes | FastAPI's 'Depends(require_owner)' injects authentication context into routes, demonstrating IoC. | routes/email_routes.py#L3711 |
| `Service Layer` | Service Layer | yes | '_store_email_flag' and '_email_index_update_flags' encapsulate business logic, separating routing from data operations. | routes/email_routes.py#L3733 |
| `Resource Management` | Resource Management | yes | 'with _imap(...) as conn:' ensures proper IMAP connection cleanup via RAII. | routes/email_routes.py#L4232 |
| `Singleton` | Singleton | yes | COMPOSE_UPLOADS_DIR is a singleton directory path for file staging. | routes/email_routes.py#L4020 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 260 | **false_pos** | [app.py#L1021](https://github.com/odysseus-dev/odysseus/blob/b4d12932a953b3cdfc745b3525c7ecd5dffd8b3c/app.py#L1021) |
| `C1|BARE|SIG` | C1 | 83 | **false_pos** | [routes/contacts/contacts_routes.py#L742](https://github.com/odysseus-dev/odysseus/blob/b4d12932a953b3cdfc745b3525c7ecd5dffd8b3c/routes/contacts/contacts_routes.py#L742) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [routes/embedding_routes.py#L113](https://github.com/odysseus-dev/odysseus/blob/b4d12932a953b3cdfc745b3525c7ecd5dffd8b3c/routes/embedding_routes.py#L113) |

## `C4|DEF` — **false_pos**
> occurrences here: 260 · corpus total: 56644 · executor: x86_64
> example: [app.py#L1021](https://github.com/odysseus-dev/odysseus/blob/b4d12932a953b3cdfc745b3525c7ecd5dffd8b3c/app.py#L1021)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 83 · corpus total: 83548 · executor: x86_64
> example: [routes/contacts/contacts_routes.py#L742](https://github.com/odysseus-dev/odysseus/blob/b4d12932a953b3cdfc745b3525c7ecd5dffd8b3c/routes/contacts/contacts_routes.py#L742)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [routes/embedding_routes.py#L113](https://github.com/odysseus-dev/odysseus/blob/b4d12932a953b3cdfc745b3525c7ecd5dffd8b3c/routes/embedding_routes.py#L113)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

