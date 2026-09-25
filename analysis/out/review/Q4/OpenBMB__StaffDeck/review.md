# OpenBMB/StaffDeck

- GitHub: https://github.com/OpenBMB/StaffDeck
- Stars: 1465 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 829 · commit: `7adc7c84f61b`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Dependency Injection via FastAPI Depends` | backend/app/api/agents.py#L537 | The code uses FastAPI's Depends to inject the database session (db) and current_user, which is a form of dependency injection. This allows for loose coupling between route handlers and external ser... |

## Pass 2 — reconcile with inventory of OpenBMB/StaffDeck

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `dependency_injection_via_depends` | dependency_injection_via_depends | yes | Code consistently uses FastAPI Depends for injecting db sessions and current_user across multiple endpoints (e.g., get_agent_resources, update_agent_resources, import_agent_resources). | backend/app/api/agents.py#L537 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 663 | **false_pos** | [backend/app/api/agents.py#L102](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/api/agents.py#L102) |
| `C4|DEF` | C4 | 120 | **false_pos** | [backend/app/a2a/codex_adapter.py#L452](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/a2a/codex_adapter.py#L452) |
| `C1|BARE|PARAM` | C1 | 43 | **known** | [backend/app/api/general_skills.py#L77](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/api/general_skills.py#L77) |
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [backend/app/public_api/auth.py#L200](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/public_api/auth.py#L200) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/database.py#L3065](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/db/database.py#L3065) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 663 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/agents.py#L102](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/api/agents.py#L102)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 120 · corpus total: 56644 · executor: x86_64
> example: [backend/app/a2a/codex_adapter.py#L452](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/a2a/codex_adapter.py#L452)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 43 · corpus total: 18195 · executor: x86_64
> example: [backend/app/api/general_skills.py#L77](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/api/general_skills.py#L77)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [backend/app/public_api/auth.py#L200](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/public_api/auth.py#L200)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/database.py#L3065](https://github.com/OpenBMB/StaffDeck/blob/7adc7c84f61bd6cca13ff0380a811cbb3ae3c544/backend/app/db/database.py#L3065)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

