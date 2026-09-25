# PodZonePlatformEngineering/gitopsapi

- GitHub: https://github.com/PodZonePlatformEngineering/gitopsapi
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 14 · commit: `baad3c0b3cdd`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection with Custom Callable Classes` | src/gitopsgui/api/auth.py#L60 | The _RoleChecker class implements __call__ with a Depends(_extract_caller) parameter, creating a reusable dependency that FastAPI can resolve. This matches FastAPI's pattern of using callable class... |

## Pass 2 — reconcile with inventory of PodZonePlatformEngineering/gitopsapi

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code in the cited lines (e.g., lifespan functions) uses asynccontextmanager, which is a dependency but not a FastAPI DI occurrence. The panel's label holds. | embedded-agents/telegram-notifier/agent/main.py#L61 |
| `C1|BARE|PARAM` | known | yes | The require_role function correctly returns Depends(_RoleChecker), a known FastAPI DI pattern. | src/gitopsgui/api/auth.py#L75 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The __call__ method in _RoleChecker uses Depends(_extract_caller), a valid FastAPI DI occurrence. The panel's label is incorrect. | src/gitopsgui/api/auth.py#L60 |

### Missed by inventory (1)
- `Custom callable class as FastAPI dependency (_RoleChecker)` @ src/gitopsgui/api/auth.py#L60 — The inventory did not capture this explicit DI pattern involving a custom class with __call__ and Depends.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 12 | **false_pos** | [embedded-agents/telegram-notifier/agent/main.py#L61](https://github.com/PodZonePlatformEngineering/gitopsapi/blob/baad3c0b3cdd5571b1d828ed5049de2453d0c58d/embedded-agents/telegram-notifier/agent/main.py#L61) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [src/gitopsgui/api/auth.py#L75](https://github.com/PodZonePlatformEngineering/gitopsapi/blob/baad3c0b3cdd5571b1d828ed5049de2453d0c58d/src/gitopsgui/api/auth.py#L75) |
| `C1|BARE|SIG` | C1 | 1 | **false_pos** | [src/gitopsgui/api/auth.py#L60](https://github.com/PodZonePlatformEngineering/gitopsapi/blob/baad3c0b3cdd5571b1d828ed5049de2453d0c58d/src/gitopsgui/api/auth.py#L60) |

## `C4|DEF` — **false_pos**
> occurrences here: 12 · corpus total: 56644 · executor: x86_64
> example: [embedded-agents/telegram-notifier/agent/main.py#L61](https://github.com/PodZonePlatformEngineering/gitopsapi/blob/baad3c0b3cdd5571b1d828ed5049de2453d0c58d/embedded-agents/telegram-notifier/agent/main.py#L61)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [src/gitopsgui/api/auth.py#L75](https://github.com/PodZonePlatformEngineering/gitopsapi/blob/baad3c0b3cdd5571b1d828ed5049de2453d0c58d/src/gitopsgui/api/auth.py#L75)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 1 · corpus total: 83548 · executor: x86_64
> example: [src/gitopsgui/api/auth.py#L60](https://github.com/PodZonePlatformEngineering/gitopsapi/blob/baad3c0b3cdd5571b1d828ed5049de2453d0c58d/src/gitopsgui/api/auth.py#L60)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

