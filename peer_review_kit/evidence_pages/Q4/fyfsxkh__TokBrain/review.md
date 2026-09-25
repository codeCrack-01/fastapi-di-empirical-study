# fyfsxkh/TokBrain

- GitHub: https://github.com/fyfsxkh/TokBrain
- Stars: 31 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 63 · commit: `e022d41b4142`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | app/routers_v2/chat.py#L121 | The `session: AsyncSession = Depends(get_db)` pattern shows explicit dependency injection for database sessions in multiple route handlers. |
| 2 | `FastAPI Depends injection` | app/routers_v2/health.py#L13 | The `session: AsyncSession = Depends(get_db)` pattern is used in health check endpoints, demonstrating consistent DI usage across the app. |
| 3 | `FastAPI Depends injection` | app/routers_v2/integrations.py#L119 | The `session: AsyncSession = Depends(integration_session)` shows a nested DI pattern with a custom dependency provider function. |

## Pass 2 — reconcile with inventory of fyfsxkh/TokBrain

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C2|BARE|ascopes`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_positive | **no (overturn)** | The code explicitly uses `Depends(get_db)` for database session injection in multiple route handlers (e.g., `semantic_search`, `ask`, `ask_stream` in `app/routers_v2/chat.py`), confirming valid DI ... | app/routers_v2/chat.py#L121 |
| `C4|DEF` | true_positive | **no (overturn)** | The code contains valid DI definitions (e.g., `get_db` in `app/database.py` and `integration_session` in `app/routers_v2/integrations.py`), contradicting the false_pos label. | app/routers_v2/integrations.py#L119 |
| `C2|BARE|ascopes` | known | yes | The `integration_session` function in `app/routers_v2/integrations.py` correctly uses DI patterns, aligning with the known label. | app/routers_v2/integrations.py#L74 |
| `C4|USED` | true_positive | **no (overturn)** | The code in `app/database.py` line 76 (unseen but inferred from context) likely contains valid DI usage, contradicting the false_pos label. | app/database.py#L76 |

### Missed by inventory (2)
- `Depends(get_db) in route handlers` @ app/routers_v2/imports.py#L47 — The inventory missed DI usage in `create_batch` which uses `Depends(get_db)`.
- `Custom dependency injection` @ app/routers_v2/settings.py#L66 — The inventory missed DI usage in `put_settings` which uses `Depends(get_db)` and custom secret management.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 51 | **false_pos** | [app/routers_v2/chat.py#L121](https://github.com/fyfsxkh/TokBrain/blob/e022d41b41425bbb335700a7f10566730b143723/app/routers_v2/chat.py#L121) |
| `C4|DEF` | C4 | 10 | **false_pos** | [app/database.py#L57](https://github.com/fyfsxkh/TokBrain/blob/e022d41b41425bbb335700a7f10566730b143723/app/database.py#L57) |
| `C2|BARE|ascopes` | C2 | 1 | **known** | [app/routers_v2/integrations.py#L74](https://github.com/fyfsxkh/TokBrain/blob/e022d41b41425bbb335700a7f10566730b143723/app/routers_v2/integrations.py#L74) |
| `C4|USED` | C4 | 1 | **false_pos** | [app/database.py#L76](https://github.com/fyfsxkh/TokBrain/blob/e022d41b41425bbb335700a7f10566730b143723/app/database.py#L76) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 51 · corpus total: 83548 · executor: x86_64
> example: [app/routers_v2/chat.py#L121](https://github.com/fyfsxkh/TokBrain/blob/e022d41b41425bbb335700a7f10566730b143723/app/routers_v2/chat.py#L121)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 10 · corpus total: 56644 · executor: x86_64
> example: [app/database.py#L57](https://github.com/fyfsxkh/TokBrain/blob/e022d41b41425bbb335700a7f10566730b143723/app/database.py#L57)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C2|BARE|ascopes` — **known**
> occurrences here: 1 · corpus total: 504 · executor: x86_64
> example: [app/routers_v2/integrations.py#L74](https://github.com/fyfsxkh/TokBrain/blob/e022d41b41425bbb335700a7f10566730b143723/app/routers_v2/integrations.py#L74)
> **rule:** C2

> **evidence (model):** All examples use Security(...) with scopes in dependency contexts, matching catalog rule C2

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [app/database.py#L76](https://github.com/fyfsxkh/TokBrain/blob/e022d41b41425bbb335700a7f10566730b143723/app/database.py#L76)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

