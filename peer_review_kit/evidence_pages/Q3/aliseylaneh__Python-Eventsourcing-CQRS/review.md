# aliseylaneh/Python-Eventsourcing-CQRS

- GitHub: https://github.com/aliseylaneh/Python-Eventsourcing-CQRS
- Stars: 12 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 12 · commit: `801aa436edbc`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Custom Providers` | internal/modules/invenotry/delivery/v1/apis.py#L20 | The 'reserve' endpoint uses FastAPI's 'Depends' to inject 'ReserveStockCommand' via 'get_reserve_stock_command', demonstrating dependency injection through custom provider functions. |
| 2 | `Chained Dependency Providers` | internal/modules/invenotry/dependencies/inventory.py#L17 | 'inventory_repository' depends on 'get_inventory_collection', which is itself a provider, creating a chain of dependencies. |
| 3 | `Aggregate-Backed Command Providers` | internal/modules/invenotry/dependencies/inventory.py#L25 | 'get_reserve_stock_command' depends on 'inventory_aggregate', which is built from 'inventory_repository', showing aggregate-backed command creation. |
| 4 | `Query Dependency Injection` | internal/modules/invenotry/dependencies/inventory.py#L41 | 'get_inventory_query' is a provider function injected into the 'get' endpoint via 'Depends', demonstrating query object injection. |

## Pass 2 — reconcile with inventory of aliseylaneh/Python-Eventsourcing-CQRS

_Presented fingerprints:_ `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | FASTAPI_DEPENDS_COMMAND_INJECTION | **no (overturn)** | The code explicitly uses FastAPI's 'Depends' to inject commands (e.g., ReserveStockCommand) via provider functions like get_reserve_stock_command, which is canonical DI. | internal/modules/invenotry/delivery/v1/apis.py#L20 |
| `C1|BARE|SIG` | FASTAPI_DEPENDS_COMMAND_INJECTION | **no (overturn)** | The 'complete' endpoint uses Depends(get_complete_reserved_command), demonstrating DI through provider functions. | internal/modules/invenotry/delivery/v1/apis.py#L37 |
| `C1|BARE|SIG` | FASTAPI_DEPENDS_COMMAND_INJECTION | **no (overturn)** | The 'create' endpoint uses Depends(get_create_inventory_command), confirming DI via provider functions. | internal/modules/invenotry/delivery/v1/apis.py#L55 |

### Missed by inventory (3)
- `Chained Dependency Providers` @ internal/modules/invenotry/dependencies/inventory.py#L17 — The 'inventory_repository' function depends on 'get_inventory_collection', forming a chain of dependencies not captured by the fingerprint inventory.
- `Aggregate-Backed Command Providers` @ internal/modules/invenotry/dependencies/inventory.py#L25 — The 'get_reserve_stock_command' depends on 'inventory_aggregate', which is built from 'inventory_repository', a pattern not captured by the fingerprint inventory.
- `Query Dependency Injection` @ internal/modules/invenotry/dependencies/inventory.py#L41 — The 'get_inventory_query' provider is injected into the 'get' endpoint via 'Depends', a DI pattern not captured by the fingerprint inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 12 | **false_pos** | [internal/modules/invenotry/delivery/v1/apis.py#L20](https://github.com/aliseylaneh/Python-Eventsourcing-CQRS/blob/801aa436edbc3c5749c3eff5ab47aa17d0a43f2c/internal/modules/invenotry/delivery/v1/apis.py#L20) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 12 · corpus total: 83548 · executor: x86_64
> example: [internal/modules/invenotry/delivery/v1/apis.py#L20](https://github.com/aliseylaneh/Python-Eventsourcing-CQRS/blob/801aa436edbc3c5749c3eff5ab47aa17d0a43f2c/internal/modules/invenotry/delivery/v1/apis.py#L20)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

