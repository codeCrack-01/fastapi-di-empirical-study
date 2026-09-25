# MitCaine/Nutrition-App

- GitHub: https://github.com/MitCaine/Nutrition-App
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 172 · commit: `658f7880c138`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Exception Handling Duplication` | apps/backend/app/api/v1/routers/foods.py#L144 | Multiple routes (update_food, delete_food, duplicate_food) have identical try-except blocks handling LookupError, RecipeProjectionMutationError, and ValueError, leading to code duplication. This pa... |
| 2 | `Service Layer Abstraction` | apps/backend/app/api/v1/routers/foods.py#L144 | The use of _service(db) and _complete_service(db) demonstrates a clear separation between route handlers and business logic, aligning with the Service Layer pattern. This abstraction is consistent ... |

## Pass 2 — reconcile with inventory of MitCaine/Nutrition-App

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `exception_handling_duplication` | Exception Handling Duplication | yes | Multiple routes in foods.py and logs.py have identical try-except blocks handling specific exceptions, leading to code duplication. | apps/backend/app/api/v1/routers/foods.py#L144 |
| `service_layer_abstraction` | Service Layer Abstraction | yes | The use of _service(db) and _complete_service(db) demonstrates a clear separation between route handlers and business logic, aligning with the Service Layer pattern. | apps/backend/app/api/v1/routers/foods.py#L144 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 94 | **false_pos** | [apps/backend/app/api/v1/routers/calendar.py#L24](https://github.com/MitCaine/Nutrition-App/blob/658f7880c138bd24e32edb8e23637dd63792fb36/apps/backend/app/api/v1/routers/calendar.py#L24) |
| `C4|DEF` | C4 | 76 | **false_pos** | [apps/backend/app/main.py#L199](https://github.com/MitCaine/Nutrition-App/blob/658f7880c138bd24e32edb8e23637dd63792fb36/apps/backend/app/main.py#L199) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [apps/backend/app/main.py#L50](https://github.com/MitCaine/Nutrition-App/blob/658f7880c138bd24e32edb8e23637dd63792fb36/apps/backend/app/main.py#L50) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/backend/app/dependencies/database.py#L8](https://github.com/MitCaine/Nutrition-App/blob/658f7880c138bd24e32edb8e23637dd63792fb36/apps/backend/app/dependencies/database.py#L8) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 94 · corpus total: 83548 · executor: x86_64
> example: [apps/backend/app/api/v1/routers/calendar.py#L24](https://github.com/MitCaine/Nutrition-App/blob/658f7880c138bd24e32edb8e23637dd63792fb36/apps/backend/app/api/v1/routers/calendar.py#L24)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 76 · corpus total: 56644 · executor: x86_64
> example: [apps/backend/app/main.py#L199](https://github.com/MitCaine/Nutrition-App/blob/658f7880c138bd24e32edb8e23637dd63792fb36/apps/backend/app/main.py#L199)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [apps/backend/app/main.py#L50](https://github.com/MitCaine/Nutrition-App/blob/658f7880c138bd24e32edb8e23637dd63792fb36/apps/backend/app/main.py#L50)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/backend/app/dependencies/database.py#L8](https://github.com/MitCaine/Nutrition-App/blob/658f7880c138bd24e32edb8e23637dd63792fb36/apps/backend/app/dependencies/database.py#L8)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

