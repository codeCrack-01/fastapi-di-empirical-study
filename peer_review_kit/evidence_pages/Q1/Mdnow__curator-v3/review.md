# Mdnow/curator-v3

- GitHub: https://github.com/Mdnow/curator-v3
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 50 · commit: `6616da0efd89`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | backend/auth.py#L45 | The get_current_user function uses Depends(security) to inject authentication dependency. |
| 2 | `FastAPI Depends injection` | backend/main.py#L97 | The /api/me endpoint uses Depends(get_current_user) to inject user authentication. |
| 3 | `FastAPI Depends injection` | backend/routes/backup.py#L12 | The backup_data endpoint uses Depends(get_current_user) for authentication. |
| 4 | `FastAPI Depends injection` | backend/routes/chat.py#L387 | The ai_chat endpoint uses Depends(get_current_user) for user authentication. |
| 5 | `FastAPI Depends injection` | backend/routes/chat.py#L404 | The chat_upload endpoint uses Depends(get_current_user) for authentication. |
| 6 | `FastAPI Depends injection` | backend/routes/chat.py#L464 | The save_thought endpoint uses Depends(get_current_user) for user authentication. |
| 7 | `FastAPI Depends injection` | backend/routes/chat.py#L473 | The chat_history endpoint uses Depends(get_current_user) for authentication. |
| 8 | `FastAPI Depends injection` | backend/routes/chat.py#L494 | The clear_chat endpoint uses Depends(get_current_user) for user authentication. |
| 9 | `FastAPI Depends injection` | backend/routes/chat.py#L505 | The delete_thread endpoint uses Depends(get_current_user) for authentication. |
| 10 | `FastAPI Depends injection` | backend/routes/chat.py#L521 | The chat_threads endpoint uses Depends(get_current_user) for user authentication. |

## Pass 2 — reconcile with inventory of Mdnow/curator-v3

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses Depends(get_current_user) in multiple endpoints (e.g., /api/me, backup_data, ai_chat), which matches the canonical fingerprint for dependency injection via FastAPI's Depends() | backend/main.py#L97 |
| `C4|DEF` | true_pos | **no (overturn)** | The static inventory's single citation to backend/db.py#L48 is not present in the provided code excerpts, suggesting the label may be based on incomplete data. The code does not show any explicit '... | backend/db.py#L48 |

### Missed by inventory (2)
- `FastAPI Depends injection in chat.py endpoints` @ backend/routes/chat.py#L387 — The inventory missed 7+ instances of Depends(get_current_user) in chat.py endpoints (e.g., ai_chat, chat_upload, save_thought) that clearly match the C1|BARE|SIG fingerprint.
- `FastAPI Depends injection in notes.py endpoints` @ backend/routes/notes.py#L279 — The inventory missed Depends(get_current_user) in notes.py endpoints like create_note and update_note, which are valid C1|BARE|SIG cases.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 49 | **false_pos** | [backend/auth.py#L45](https://github.com/Mdnow/curator-v3/blob/6616da0efd8991b177ba67579bb82a589c151ce9/backend/auth.py#L45) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/db.py#L48](https://github.com/Mdnow/curator-v3/blob/6616da0efd8991b177ba67579bb82a589c151ce9/backend/db.py#L48) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 49 · corpus total: 83548 · executor: x86_64
> example: [backend/auth.py#L45](https://github.com/Mdnow/curator-v3/blob/6616da0efd8991b177ba67579bb82a589c151ce9/backend/auth.py#L45)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/db.py#L48](https://github.com/Mdnow/curator-v3/blob/6616da0efd8991b177ba67579bb82a589c151ce9/backend/db.py#L48)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

