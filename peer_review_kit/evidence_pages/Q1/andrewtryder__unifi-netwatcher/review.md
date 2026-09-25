# andrewtryder/unifi-netwatcher

- GitHub: https://github.com/andrewtryder/unifi-netwatcher
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 57 · commit: `8ab259aacb37`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends()` | app/api/routes_devices.py#L42 | The route handlers use 'db: Session = Depends(get_db)' to inject a database session. This is FastAPI's standard DI pattern where dependencies are resolved via functions decorated with @Depends. |
| 2 | `Service class instantiation with injected dependencies` | app/api/routes_devices.py#L42 | The '_service' function creates a DeviceService instance with 'db' and 'request_context_from_request(request)', showing explicit injection of dependencies into a service class. |
| 3 | `Consistent use of Depends() across routes` | app/web/routes.py#L100 | Multiple route handlers in 'app/web/routes.py' use 'db: Session = Depends(get_db)', demonstrating a consistent DI pattern throughout the application. |

## Pass 2 — reconcile with inventory of andrewtryder/unifi-netwatcher

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 39 | **false_pos** | [app/api/routes_devices.py#L42](https://github.com/andrewtryder/unifi-netwatcher/blob/8ab259aacb37da7c2dbff03dc9ed151d1110d0d2/app/api/routes_devices.py#L42) |
| `C4|DEF` | C4 | 17 | **false_pos** | [app/main.py#L93](https://github.com/andrewtryder/unifi-netwatcher/blob/8ab259aacb37da7c2dbff03dc9ed151d1110d0d2/app/main.py#L93) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/db.py#L33](https://github.com/andrewtryder/unifi-netwatcher/blob/8ab259aacb37da7c2dbff03dc9ed151d1110d0d2/app/db.py#L33) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 39 · corpus total: 83548 · executor: x86_64
> example: [app/api/routes_devices.py#L42](https://github.com/andrewtryder/unifi-netwatcher/blob/8ab259aacb37da7c2dbff03dc9ed151d1110d0d2/app/api/routes_devices.py#L42)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 17 · corpus total: 56644 · executor: x86_64
> example: [app/main.py#L93](https://github.com/andrewtryder/unifi-netwatcher/blob/8ab259aacb37da7c2dbff03dc9ed151d1110d0d2/app/main.py#L93)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/db.py#L33](https://github.com/andrewtryder/unifi-netwatcher/blob/8ab259aacb37da7c2dbff03dc9ed151d1110d0d2/app/db.py#L33)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

