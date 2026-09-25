# davidmonterocrespo24/DaveLovable

- GitHub: https://github.com/davidmonterocrespo24/DaveLovable
- Stars: 47 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 48 · commit: `7f97cda7090d`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Database session injection via Depends` | backend/app/api/chat.py#L23 | The route uses `db: Session = Depends(get_db)` to inject a database session. This is a standard FastAPI pattern where `get_db` is a dependency provider defined in `database.py` that yields a SQLAlc... |
| 2 | `Database session injection via Depends` | backend/app/api/projects.py#L56 | The `create_project_from_message` endpoint uses `db: Session = Depends(get_db)` to inject a database session, following the same pattern as in chat.py. This shows consistent use of dependency injec... |
| 3 | `Service method calls without explicit DI` | backend/app/api/chat.py#L75 | The code calls `ChatService.process_chat_message(db, project_id, chat_request)` directly, indicating that `ChatService` is not injected via Depends but rather used as a module-level dependency. Thi... |

## Pass 2 — reconcile with inventory of davidmonterocrespo24/DaveLovable

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 34 | **false_pos** | [backend/app/api/chat.py#L23](https://github.com/davidmonterocrespo24/DaveLovable/blob/7f97cda7090d6d1ba814a686de5240d04a6c9eff/backend/app/api/chat.py#L23) |
| `C4|DEF` | C4 | 13 | **false_pos** | [backend/app/api/chat.py#L34](https://github.com/davidmonterocrespo24/DaveLovable/blob/7f97cda7090d6d1ba814a686de5240d04a6c9eff/backend/app/api/chat.py#L34) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db/database.py#L24](https://github.com/davidmonterocrespo24/DaveLovable/blob/7f97cda7090d6d1ba814a686de5240d04a6c9eff/backend/app/db/database.py#L24) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 34 · corpus total: 83548 · executor: x86_64
> example: [backend/app/api/chat.py#L23](https://github.com/davidmonterocrespo24/DaveLovable/blob/7f97cda7090d6d1ba814a686de5240d04a6c9eff/backend/app/api/chat.py#L23)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 13 · corpus total: 56644 · executor: x86_64
> example: [backend/app/api/chat.py#L34](https://github.com/davidmonterocrespo24/DaveLovable/blob/7f97cda7090d6d1ba814a686de5240d04a6c9eff/backend/app/api/chat.py#L34)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db/database.py#L24](https://github.com/davidmonterocrespo24/DaveLovable/blob/7f97cda7090d6d1ba814a686de5240d04a6c9eff/backend/app/db/database.py#L24)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

