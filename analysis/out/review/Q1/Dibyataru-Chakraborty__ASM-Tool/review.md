# Dibyataru-Chakraborty/ASM-Tool

- GitHub: https://github.com/Dibyataru-Chakraborty/ASM-Tool
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 347 · commit: `57ab8f93ebed`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `DRY Violation` | backend/app/api/v1/asm_routes.py#L255 | Multiple route handlers (toggle_schedule, pause_resume_schedule, delete_schedule) repeat identical logic for retrieving schedules, modifying state, and committing changes. This violates DRY princip... |
| 2 | `Repeated Authorization Logic` | backend/app/api/v1/asm_routes.py#L270 | The org_id determination logic is duplicated across multiple endpoints (lines 270, 286, 304, 372, 397, 416, 422, 431, 443, 459). This could be centralized into a reusable authentication helper. |

## Pass 2 — reconcile with inventory of Dibyataru-Chakraborty/ASM-Tool

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `DRY_VIOLATION_SCHEDULE_ROUTES` | DRY Violation | yes | Multiple schedule route handlers (toggle_schedule, pause_resume_schedule, delete_schedule) repeat identical logic for retrieving schedules, modifying state, and committing changes. | backend/app/api/v1/asm_routes.py#L255 |
| `REPEATED_AUTHORIZATION_LOGIC` | Repeated Authorization Logic | yes | The org_id determination logic is duplicated across multiple endpoints (lines 270, 286, 304, 372, 397, 416, 422, 431, 443, 459). This could be centralized into a reusable authentication helper. | backend/app/api/v1/asm_routes.py#L270 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 343 | **false_pos** | [backend/app/api/v1/ai_analysis.py#L26](https://github.com/Dibyataru-Chakraborty/ASM-Tool/blob/57ab8f93ebed9d560727ce2681d656967c352fab/backend/app/api/v1/ai_analysis.py#L26) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/app/main.py#L19](https://github.com/Dibyataru-Chakraborty/ASM-Tool/blob/57ab8f93ebed9d560727ce2681d656967c352fab/backend/app/main.py#L19) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [backend/app/main.py#L88](https://github.com/Dibyataru-Chakraborty/ASM-Tool/blob/57ab8f93ebed9d560727ce2681d656967c352fab/backend/app/main.py#L88) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/utils/database.py#L44](https://github.com/Dibyataru-Chakraborty/ASM-Tool/blob/57ab8f93ebed9d560727ce2681d656967c352fab/backend/app/utils/database.py#L44) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 343 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/v1/ai_analysis.py#L26](https://github.com/Dibyataru-Chakraborty/ASM-Tool/blob/57ab8f93ebed9d560727ce2681d656967c352fab/backend/app/api/v1/ai_analysis.py#L26)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L19](https://github.com/Dibyataru-Chakraborty/ASM-Tool/blob/57ab8f93ebed9d560727ce2681d656967c352fab/backend/app/main.py#L19)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [backend/app/main.py#L88](https://github.com/Dibyataru-Chakraborty/ASM-Tool/blob/57ab8f93ebed9d560727ce2681d656967c352fab/backend/app/main.py#L88)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/utils/database.py#L44](https://github.com/Dibyataru-Chakraborty/ASM-Tool/blob/57ab8f93ebed9d560727ce2681d656967c352fab/backend/app/utils/database.py#L44)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

