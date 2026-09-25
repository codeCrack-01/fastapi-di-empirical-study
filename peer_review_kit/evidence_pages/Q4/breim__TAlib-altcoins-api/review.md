# breim/TAlib-altcoins-api

- GitHub: https://github.com/breim/TAlib-altcoins-api
- Stars: 24 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 5 · commit: `ad12f9307985`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends` | src/talib_altcoins_api/api/indicators.py#L99 | The 'settings' parameter uses 'Depends(get_settings)' to inject a Settings object, which is a standard FastAPI dependency injection pattern. This is explicitly shown in the code excerpt with 'Annot... |

## Pass 2 — reconcile with inventory of breim/TAlib-altcoins-api

_Presented fingerprints:_ `C3|CLASS|BARE`, `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's 'Depends(get_settings)' for dependency injection, which is a canonical DI pattern. The label 'false_pos' incorrectly dismisses this as non-DI. | src/talib_altcoins_api/api/indicators.py#L99 |
| `C4|DEF` | false_pos | yes | The test fixture '_reset_caches' does not involve FastAPI dependency injection patterns (e.g., no 'Depends' or similar constructs). The label 'false_pos' correctly identifies this as non-DI. | tests/conftest.py#L23 |
| `C1|BARE|PARAM` | known | yes | The parameters 'exchange' and 'symbol' use FastAPI's 'Annotated' with 'Query' validations, which are part of the DI system. The label 'known' correctly identifies this as DI. | src/talib_altcoins_api/api/indicators.py#L99 |

### Missed by inventory (1)
- `FastAPI dependency injection via 'Depends' in endpoint parameters` @ src/talib_altcoins_api/api/indicators.py#L99 — The inventory's 'C3|CLASS|BARE' fingerprint was labeled 'false_pos', but the code explicitly uses 'Depends(get_settings)' for DI, which should be classified as a true DI occurrence.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C3|CLASS|BARE` | C3 | 2 | **false_pos** | [src/talib_altcoins_api/api/indicators.py#L99](https://github.com/breim/TAlib-altcoins-api/blob/ad12f93079856f9d36c91effea4161a6d371e6ba/src/talib_altcoins_api/api/indicators.py#L99) |
| `C4|DEF` | C4 | 2 | **false_pos** | [tests/conftest.py#L23](https://github.com/breim/TAlib-altcoins-api/blob/ad12f93079856f9d36c91effea4161a6d371e6ba/tests/conftest.py#L23) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [src/talib_altcoins_api/api/indicators.py#L99](https://github.com/breim/TAlib-altcoins-api/blob/ad12f93079856f9d36c91effea4161a6d371e6ba/src/talib_altcoins_api/api/indicators.py#L99) |

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 2 · corpus total: 20139 · executor: x86_64
> example: [src/talib_altcoins_api/api/indicators.py#L99](https://github.com/breim/TAlib-altcoins-api/blob/ad12f93079856f9d36c91effea4161a6d371e6ba/src/talib_altcoins_api/api/indicators.py#L99)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [tests/conftest.py#L23](https://github.com/breim/TAlib-altcoins-api/blob/ad12f93079856f9d36c91effea4161a6d371e6ba/tests/conftest.py#L23)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [src/talib_altcoins_api/api/indicators.py#L99](https://github.com/breim/TAlib-altcoins-api/blob/ad12f93079856f9d36c91effea4161a6d371e6ba/src/talib_altcoins_api/api/indicators.py#L99)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

