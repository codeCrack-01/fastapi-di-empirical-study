# aiuda-io/aiuda

- GitHub: https://github.com/aiuda-io/aiuda
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 439 · commit: `86e5a680813f`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection via Depends()` | server/aiuda_server/api/banco.py#L123 | The function `importar_estado` uses `Depends(get_tenant)`, `Depends(get_db)`, and `Depends(get_principal)` to inject dependencies, aligning with FastAPI's DI pattern for managing tenant, database, ... |
| 2 | `Dependency Injection via Depends()` | server/aiuda_server/api/cobro.py#L28 | The function `crear_link_cobro` injects dependencies using `Depends(get_tenant)`, `Depends(get_db)`, and `Depends(require_role("admin"))`, demonstrating DI for tenant, database, and role-based acce... |
| 3 | `Dependency Injection via Depends()` | server/aiuda_server/api/cua.py#L80 | The `estado` function uses `Depends(get_db)` and `Depends(get_tenant)` to inject database and tenant dependencies, a hallmark of FastAPI's DI pattern for service-wide context management. |

## Pass 2 — reconcile with inventory of aiuda-io/aiuda

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `DI_banco_importar_estado` | Dependency Injection via Depends() | yes | The function uses Depends(get_tenant), Depends(get_db), and Depends(get_principal) correctly for tenant, database, and authentication context injection. | server/aiuda_server/api/banco.py#L123 |
| `DI_cobro_crear_link_cobro` | Dependency Injection via Depends() | yes | The function uses Depends(get_tenant), Depends(get_db), and Depends(require_role("admin")) for tenant, database, and role-based access control. | server/aiuda_server/api/cobro.py#L28 |
| `DI_cua_estado` | Dependency Injection via Depends() | yes | The function uses Depends(get_db) and Depends(get_tenant) for database and tenant context injection. | server/aiuda_server/api/cua.py#L80 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 334 | **false_pos** | [server/aiuda_server/api/audit.py#L14](https://github.com/aiuda-io/aiuda/blob/86e5a680813f8af5989d9a4fce7e4c32b9335395/server/aiuda_server/api/audit.py#L14) |
| `C4|DEF` | C4 | 104 | **false_pos** | [core/aiuda_core/connectors/mercadolibre.py#L66](https://github.com/aiuda-io/aiuda/blob/86e5a680813f8af5989d9a4fce7e4c32b9335395/core/aiuda_core/connectors/mercadolibre.py#L66) |
| `C4|USED` | C4 | 1 | **false_pos** | [server/aiuda_server/api/deps.py#L26](https://github.com/aiuda-io/aiuda/blob/86e5a680813f8af5989d9a4fce7e4c32b9335395/server/aiuda_server/api/deps.py#L26) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 334 · corpus total: 83548 · executor: x86_64
> example: [server/aiuda_server/api/audit.py#L14](https://github.com/aiuda-io/aiuda/blob/86e5a680813f8af5989d9a4fce7e4c32b9335395/server/aiuda_server/api/audit.py#L14)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 104 · corpus total: 56644 · executor: x86_64
> example: [core/aiuda_core/connectors/mercadolibre.py#L66](https://github.com/aiuda-io/aiuda/blob/86e5a680813f8af5989d9a4fce7e4c32b9335395/core/aiuda_core/connectors/mercadolibre.py#L66)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [server/aiuda_server/api/deps.py#L26](https://github.com/aiuda-io/aiuda/blob/86e5a680813f8af5989d9a4fce7e4c32b9335395/server/aiuda_server/api/deps.py#L26)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

