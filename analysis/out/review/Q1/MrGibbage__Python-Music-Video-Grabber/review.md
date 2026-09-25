# MrGibbage/Python-Music-Video-Grabber

- GitHub: https://github.com/MrGibbage/Python-Music-Video-Grabber
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 73 · commit: `02d95b4f796c`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | music_video_grabber/main.py#L340 | The code uses FastAPI's Depends() pattern for dependency injection, evident in lines like 'db: Database = Depends(get_db)' and 'settings: Settings = Depends(get_settings)' which inject database and... |
| 2 | `FastAPI Depends injection` | music_video_grabber/main.py#L342 | Another instance of FastAPI's Depends() pattern for injecting dependencies, specifically the database connection in the media_info endpoint. |
| 3 | `FastAPI Depends injection` | music_video_grabber/main.py#L400 | The review_queue endpoint uses Depends() to inject the database dependency, demonstrating the consistent use of FastAPI's DI pattern throughout the codebase. |
| 4 | `FastAPI Depends injection` | music_video_grabber/main.py#L423 | The approve_candidate endpoint employs Depends() to inject the database and settings dependencies, further illustrating the DI pattern in action. |

## Pass 2 — reconcile with inventory of MrGibbage/Python-Music-Video-Grabber

_Presented fingerprints:_ `C1|BARE|SIG`, `C1|BARE|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `fastapi_depends_injection_1` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends() pattern for dependency injection in the media_info endpoint. | music_video_grabber/main.py#L340 |
| `fastapi_depends_injection_2` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends() pattern for dependency injection in the review_queue endpoint. | music_video_grabber/main.py#L400 |
| `fastapi_depends_injection_3` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends() pattern for dependency injection in the approve_candidate endpoint. | music_video_grabber/main.py#L423 |
| `fastapi_depends_injection_4` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends() pattern for dependency injection in the retry_job endpoint. | music_video_grabber/main.py#L471 |
| `fastapi_depends_injection_5` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends() pattern for dependency injection in the acknowledge_failed_job endpoint. | music_video_grabber/main.py#L486 |
| `fastapi_depends_injection_6` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends() pattern for dependency injection in the cancel_job endpoint. | music_video_grabber/main.py#L504 |
| `fastapi_depends_injection_7` | FastAPI Depends injection | yes | The code correctly uses FastAPI's Depends() pattern for dependency injection in the queue_catalog_import endpoint. | music_video_grabber/main.py#L521 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 43 | **false_pos** | [music_video_grabber/main.py#L59](https://github.com/MrGibbage/Python-Music-Video-Grabber/blob/02d95b4f796ca700d298b4125fed45432bb13d96/music_video_grabber/main.py#L59) |
| `C1|BARE|PARAM` | C1 | 27 | **known** | [music_video_grabber/main.py#L176](https://github.com/MrGibbage/Python-Music-Video-Grabber/blob/02d95b4f796ca700d298b4125fed45432bb13d96/music_video_grabber/main.py#L176) |
| `C4|DEF` | C4 | 3 | **false_pos** | [music_video_grabber/db.py#L177](https://github.com/MrGibbage/Python-Music-Video-Grabber/blob/02d95b4f796ca700d298b4125fed45432bb13d96/music_video_grabber/db.py#L177) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 43 · corpus total: 83548 · executor: x86_64
> example: [music_video_grabber/main.py#L59](https://github.com/MrGibbage/Python-Music-Video-Grabber/blob/02d95b4f796ca700d298b4125fed45432bb13d96/music_video_grabber/main.py#L59)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 27 · corpus total: 18195 · executor: x86_64
> example: [music_video_grabber/main.py#L176](https://github.com/MrGibbage/Python-Music-Video-Grabber/blob/02d95b4f796ca700d298b4125fed45432bb13d96/music_video_grabber/main.py#L176)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|DEF` — **false_pos**
> occurrences here: 3 · corpus total: 56644 · executor: x86_64
> example: [music_video_grabber/db.py#L177](https://github.com/MrGibbage/Python-Music-Video-Grabber/blob/02d95b4f796ca700d298b4125fed45432bb13d96/music_video_grabber/db.py#L177)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

