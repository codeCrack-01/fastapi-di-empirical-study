# 4ch1m/pixoo-rest

- GitHub: https://github.com/4ch1m/pixoo-rest
- Stars: 331 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 7 · commit: `ef6819605ca2`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends() with Annotated parameters` | pixoo_rest/routers/draw.py#L27 | The 'image' function uses Annotated[ImageModel, Depends()] to inject a dependency. This is a standard FastAPI pattern where dependencies are declared via Depends() within Annotated type hints. |
| 2 | `FastAPI Depends() with Annotated parameters` | pixoo_rest/routers/send.py#L36 | The 'send_gif' function uses Annotated[GIFModel, Depends()] similarly to inject a dependency. Both routes use this pattern for their respective models. |

## Pass 2 — reconcile with inventory of 4ch1m/pixoo-rest

_Presented fingerprints:_ `C3|CLASS|EMPTY`, `C1|EMPTY|PARAM`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|EMPTY` | correct | **no (overturn)** | The code uses standard FastAPI pattern with Annotated[ImageModel, Depends()] for dependency injection, which is valid and not a false positive. | pixoo_rest/routers/draw.py#L27 |
| `C1|EMPTY|PARAM` | correct | **no (overturn)** | The code uses Annotated[GIFModel, Depends()] as a standard FastAPI parameter with dependency injection, which is valid and not a variant requiring special labeling. | pixoo_rest/routers/send.py#L36 |
| `C4|DEF` | correct | **no (overturn)** | The lifespan function in main.py:40 is a standard FastAPI lifespan handler using asynccontextmanager, which is valid and not a false positive. | pixoo_rest/main.py#L40 |

### Missed by inventory (2)
- `FastAPI Annotated[Model, Depends()] usage` @ pixoo_rest/routers/draw.py#L27 — The inventory missed that Annotated[ImageModel, Depends()] is a standard FastAPI pattern for dependency injection, which was incorrectly labeled as false_pos.
- `FastAPI Annotated[GIFModel, Depends()] usage` @ pixoo_rest/routers/send.py#L36 — The inventory missed that Annotated[GIFModel, Depends()] is a standard FastAPI pattern for dependency injection, which was incorrectly labeled as variant.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|EMPTY` | C3 | 4 | **false_pos** | [pixoo_rest/routers/draw.py#L27](https://github.com/4ch1m/pixoo-rest/blob/ef6819605ca2da24bcf51bd46b486fa4d25c4258/pixoo_rest/routers/draw.py#L27) |
| `C1|EMPTY|PARAM` | C1 | 2 | **variant** | [pixoo_rest/routers/draw.py#L27](https://github.com/4ch1m/pixoo-rest/blob/ef6819605ca2da24bcf51bd46b486fa4d25c4258/pixoo_rest/routers/draw.py#L27) |
| `C4|DEF` | C4 | 1 | **false_pos** | [pixoo_rest/main.py#L40](https://github.com/4ch1m/pixoo-rest/blob/ef6819605ca2da24bcf51bd46b486fa4d25c4258/pixoo_rest/main.py#L40) |

## `C3|CLASS|EMPTY` — **false_pos**
> occurrences here: 4 · corpus total: 89 · executor: x86_64
> example: [pixoo_rest/routers/draw.py#L27](https://github.com/4ch1m/pixoo-rest/blob/ef6819605ca2da24bcf51bd46b486fa4d25c4258/pixoo_rest/routers/draw.py#L27)
> **rule:** C3

> **evidence (model):** Annotated is used without a Depends(...) argument, which is required for FastAPI DI by the catalog rule C3.

## `C1|EMPTY|PARAM` — **variant**
> occurrences here: 2 · corpus total: 45 · executor: x86_64
> example: [pixoo_rest/routers/draw.py#L27](https://github.com/4ch1m/pixoo-rest/blob/ef6819605ca2da24bcf51bd46b486fa4d25c4258/pixoo_rest/routers/draw.py#L27)
> **rule:** C1

> **evidence (model):** Empty parameter in Depends() call, structurally different from standard C1 (function/object passed) but semantically equivalent as a dependency injection construct

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [pixoo_rest/main.py#L40](https://github.com/4ch1m/pixoo-rest/blob/ef6819605ca2da24bcf51bd46b486fa4d25c4258/pixoo_rest/main.py#L40)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

