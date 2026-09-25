# exeaman/Atlanta-Banking

- GitHub: https://github.com/exeaman/Atlanta-Banking
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 1 · commit: `a19d5f405f4f`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Manual Dependency Injection` | services/notification-service/app/main.py#L23 | The code directly instantiates dependencies (e.g., `get_notification_service(db)`) and manually passes them to consumers like `EmployeeCreatedConsumer`, rather than using FastAPI's `Depends()` mech... |

## Pass 2 — reconcile with inventory of exeaman/Atlanta-Banking

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly performs manual dependency injection by instantiating `get_notification_service(db)` and passing it to `EmployeeCreatedConsumer`, which matches the structural fingerprint of man... | services/notification-service/app/main.py#L23 |

### Missed by inventory (1)
- `Manual DI via direct instantiation and parameter passing` @ services/notification-service/app/main.py#L23 — The inventory failed to capture this explicit manual DI pattern, which is clearly present in the code.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [services/notification-service/app/main.py#L18](https://github.com/exeaman/Atlanta-Banking/blob/a19d5f405f4ff7c385b45a3f5183fb4e2d864d64/services/notification-service/app/main.py#L18) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [services/notification-service/app/main.py#L18](https://github.com/exeaman/Atlanta-Banking/blob/a19d5f405f4ff7c385b45a3f5183fb4e2d864d64/services/notification-service/app/main.py#L18)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

