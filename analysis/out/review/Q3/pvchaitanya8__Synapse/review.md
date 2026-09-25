# pvchaitanya8/Synapse

- GitHub: https://github.com/pvchaitanya8/Synapse
- Stars: 10 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 207 · commit: `d15cf386967f`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection for router-level dependencies` | backend/api/v1/analytics.py#L37 | The APIRouter is configured with dependencies=[Depends(set_rls_context)], indicating that the set_rls_context function is injected at the router level for all endpoints under /analytics. |
| 2 | `FastAPI Depends injection for endpoint parameters` | backend/api/v1/analytics.py#L64 | The ingest_events endpoint uses db: AsyncSession = Depends(get_db) and user_id: UUID = Depends(get_current_user_id), demonstrating parameter-level dependency injection for database sessions and use... |
| 3 | `Recurring router-level RLS context injection` | backend/api/v1/attachments.py#L20 | The attachments router also uses dependencies=[Depends(set_rls_context)], showing this is a recurring pattern across multiple routers for row-level security context setup. |
| 4 | `Database session injection in multiple endpoints` | backend/api/v1/auth.py#L216 | The google_callback endpoint includes db: AsyncSession = Depends(get_db), illustrating that database session injection is a common pattern across authentication-related endpoints. |

## Pass 2 — reconcile with inventory of pvchaitanya8/Synapse

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|DEF`, `C4|USED`

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 164 | **false_pos** | [backend/api/v1/analytics.py#L64](https://github.com/pvchaitanya8/Synapse/blob/d15cf386967f89e4d1e779d422ca28ae4f814ca7/backend/api/v1/analytics.py#L64) |
| `C1|BARE|PARAM` | C1 | 25 | **known** | [backend/api/v1/analytics.py#L37](https://github.com/pvchaitanya8/Synapse/blob/d15cf386967f89e4d1e779d422ca28ae4f814ca7/backend/api/v1/analytics.py#L37) |
| `C4|DEF` | C4 | 17 | **false_pos** | [backend/main.py#L69](https://github.com/pvchaitanya8/Synapse/blob/d15cf386967f89e4d1e779d422ca28ae4f814ca7/backend/main.py#L69) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/db/session.py#L94](https://github.com/pvchaitanya8/Synapse/blob/d15cf386967f89e4d1e779d422ca28ae4f814ca7/backend/db/session.py#L94) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 164 · corpus total: 83548 · executor: x86_64
> example: [backend/api/v1/analytics.py#L64](https://github.com/pvchaitanya8/Synapse/blob/d15cf386967f89e4d1e779d422ca28ae4f814ca7/backend/api/v1/analytics.py#L64)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 25 · corpus total: 18195 · executor: x86_64
> example: [backend/api/v1/analytics.py#L37](https://github.com/pvchaitanya8/Synapse/blob/d15cf386967f89e4d1e779d422ca28ae4f814ca7/backend/api/v1/analytics.py#L37)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 17 · corpus total: 56644 · executor: x86_64
> example: [backend/main.py#L69](https://github.com/pvchaitanya8/Synapse/blob/d15cf386967f89e4d1e779d422ca28ae4f814ca7/backend/main.py#L69)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/db/session.py#L94](https://github.com/pvchaitanya8/Synapse/blob/d15cf386967f89e4d1e779d422ca28ae4f814ca7/backend/db/session.py#L94)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

