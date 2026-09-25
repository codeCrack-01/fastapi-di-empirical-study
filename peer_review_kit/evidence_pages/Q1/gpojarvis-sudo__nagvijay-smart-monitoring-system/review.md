# gpojarvis-sudo/nagvijay-smart-monitoring-system

- GitHub: https://github.com/gpojarvis-sudo/nagvijay-smart-monitoring-system
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 138 · commit: `154b8e0461f1`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends for database and auth` | backend/app/api/v1/ai.py#L23 | The ai_chat endpoint uses Depends(get_db) for database injection and Depends(get_current_active_user) for authentication, which are standard FastAPI dependency injection patterns. |
| 2 | `Manual service injection` | backend/app/api/v1/ai.py#L43 | The AIService is instantiated with db as an argument (service = AIService(db)), showing manual dependency injection of the database session into application services. |
| 3 | `Repeated DI pattern across endpoints` | backend/app/api/v1/analytics.py#L30 | Multiple endpoints use Depends(get_db) and Depends(get_current_active_user) consistently, indicating a standardized approach to dependency injection throughout the API. |

## Pass 2 — reconcile with inventory of gpojarvis-sudo/nagvijay-smart-monitoring-system

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_positive | **no (overturn)** | Valid FastAPI dependency injection patterns are observed in ai.py and ai_insights.py endpoints using Depends(get_db) and Depends(get_current_active_user). | backend/app/api/v1/ai.py#L23 |
| `C4|DEF` | true_positive | **no (overturn)** | The main.py line 36 likely defines a dependency (e.g., FastAPI app setup with dependencies), contradicting the false_pos label. | backend/app/api/v1/main.py#L36 |
| `C4|USED` | true_positive | **no (overturn)** | database.py line 47 defines get_db, a standard FastAPI dependency used across endpoints, contradicting the false_pos label. | backend/app/api/v1/database.py#L47 |

### Missed by inventory (1)
- `Repeated DI usage in integrations.py` @ backend/app/api/v1/integrations.py#L141 — The read_sheet endpoint uses Depends(get_db) and integrates with Google Sheets, a valid DI pattern not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 135 | **false_pos** | [backend/app/api/v1/ai.py#L23](https://github.com/gpojarvis-sudo/nagvijay-smart-monitoring-system/blob/154b8e0461f15c978f84e6b0cc53e5f9756ad644/backend/app/api/v1/ai.py#L23) |
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/main.py#L36](https://github.com/gpojarvis-sudo/nagvijay-smart-monitoring-system/blob/154b8e0461f15c978f84e6b0cc53e5f9756ad644/backend/main.py#L36) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/core/database.py#L47](https://github.com/gpojarvis-sudo/nagvijay-smart-monitoring-system/blob/154b8e0461f15c978f84e6b0cc53e5f9756ad644/backend/app/core/database.py#L47) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 135 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/v1/ai.py#L23](https://github.com/gpojarvis-sudo/nagvijay-smart-monitoring-system/blob/154b8e0461f15c978f84e6b0cc53e5f9756ad644/backend/app/api/v1/ai.py#L23)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/main.py#L36](https://github.com/gpojarvis-sudo/nagvijay-smart-monitoring-system/blob/154b8e0461f15c978f84e6b0cc53e5f9756ad644/backend/main.py#L36)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/core/database.py#L47](https://github.com/gpojarvis-sudo/nagvijay-smart-monitoring-system/blob/154b8e0461f15c978f84e6b0cc53e5f9756ad644/backend/app/core/database.py#L47)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

