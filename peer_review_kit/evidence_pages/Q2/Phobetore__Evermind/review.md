# Phobetore/Evermind

- GitHub: https://github.com/Phobetore/Evermind
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 61 · commit: `4d1a697a59f7`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection for database connection` | backend/app/routers/__init__.py#L15 | The 'db' parameter uses Depends(get_db) to inject a database connection, a common FastAPI DI pattern. |
| 2 | `FastAPI Depends injection for database connection` | backend/app/routers/characters.py#L15 | The 'list_characters' endpoint uses Depends(get_db) to inject the database connection as a dependency. |
| 3 | `FastAPI Depends injection for database connection` | backend/app/routers/connections.py#L15 | The 'test_connection' endpoint uses Depends(get_db) to inject the database connection. |
| 4 | `FastAPI Depends injection for database connection` | backend/app/routers/conversations.py#L15 | Multiple endpoints in this file use Depends(get_db) to inject the database connection. |
| 5 | `FastAPI Depends injection for database connection` | backend/app/routers/library.py#L15 | The 'list_library' endpoint uses Depends(get_db) to inject the database connection. |

## Pass 2 — reconcile with inventory of Phobetore/Evermind

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `db_depends_usage` | Consistent use of Depends(get_db) for database injection | yes | All endpoints requiring database access correctly use Depends(get_db) to inject the connection. | backend/app/routers/conversations.py#L15 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 48 | **false_pos** | [backend/app/routers/__init__.py#L18](https://github.com/Phobetore/Evermind/blob/4d1a697a59f7c629ba4b3629d1de8cb3afeef756/backend/app/routers/__init__.py#L18) |
| `C4|DEF` | C4 | 12 | **false_pos** | [backend/app/cards/png.py#L16](https://github.com/Phobetore/Evermind/blob/4d1a697a59f7c629ba4b3629d1de8cb3afeef756/backend/app/cards/png.py#L16) |
| `C4|USED` | C4 | 1 | **false_pos** | [backend/app/db.py#L46](https://github.com/Phobetore/Evermind/blob/4d1a697a59f7c629ba4b3629d1de8cb3afeef756/backend/app/db.py#L46) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 48 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routers/__init__.py#L18](https://github.com/Phobetore/Evermind/blob/4d1a697a59f7c629ba4b3629d1de8cb3afeef756/backend/app/routers/__init__.py#L18)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 12 · corpus total: 56644 · executor: x86_64
> example: [backend/app/cards/png.py#L16](https://github.com/Phobetore/Evermind/blob/4d1a697a59f7c629ba4b3629d1de8cb3afeef756/backend/app/cards/png.py#L16)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [backend/app/db.py#L46](https://github.com/Phobetore/Evermind/blob/4d1a697a59f7c629ba4b3629d1de8cb3afeef756/backend/app/db.py#L46)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

