# mrwogu/factory-droid-openai

- GitHub: https://github.com/mrwogu/factory-droid-openai
- Stars: 24 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 49 · commit: `28593bc52bbb`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI built-in dependency injection` | src/factory_droid_openai/app.py#L1163 | The route handler for '/v1/models' uses dependencies=[Depends(require_auth)] to inject an authentication dependency. This is FastAPI's standard DI mechanism where dependencies are declared via Depe... |
| 2 | `Repeated use of same dependency` | src/factory_droid_openai/app.py#L1195 | Multiple endpoints (models, retrieve_model, session_context, etc.) all use dependencies=[Depends(require_auth)] to inject the same require_auth dependency, indicating a centralized authentication c... |
| 3 | `No custom DI infrastructure` | src/factory_droid_openai/app.py#L1224 | The code does not implement custom dependency providers, factories, or containers. All DI is handled through FastAPI's built-in Depends() system without additional abstraction layers. |

## Pass 2 — reconcile with inventory of mrwogu/factory-droid-openai

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C2|ELLIPSIS|ascopes`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code uses FastAPI's built-in DI via Depends() for authentication, which is a valid DI occurrence. The panel's 'false_pos' label incorrectly dismisses real DI usage. | src/factory_droid_openai/app.py#L1163 |
| `C1|BARE|PARAM` | known | yes | Multiple endpoints use dependencies=[Depends(require_auth)], which matches the 'BARE|PARAM' pattern of injecting a parameterized dependency. | src/factory_droid_openai/app.py#L1163 |
| `C2|ELLIPSIS|ascopes` | variant | yes | The code does not contain any 'ascopes' syntax, so the 'variant' label likely refers to an ellipsis (...) in a parameter list, which is valid Python but not DI-related. | src/factory_droid_openai/app.py#L116 |

### Missed by inventory (1)
- `FastAPI's built-in DI via Depends()` @ src/factory_droid_openai/app.py#L1163 — The inventory may have misclassified C4|DEF as false_pos, but the code's use of Depends() is valid DI and should be labeled as 'known' or 'variant'.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 40 | **false_pos** | [scripts/e2e_matrix.py#L1306](https://github.com/mrwogu/factory-droid-openai/blob/28593bc52bbbef75d81d4ce8081bf2a60a586ae9/scripts/e2e_matrix.py#L1306) |
| `C1|BARE|PARAM` | C1 | 8 | **known** | [src/factory_droid_openai/app.py#L1163](https://github.com/mrwogu/factory-droid-openai/blob/28593bc52bbbef75d81d4ce8081bf2a60a586ae9/src/factory_droid_openai/app.py#L1163) |
| `C2|ELLIPSIS|ascopes` | C2 | 1 | **variant** | [src/factory_droid_openai/app.py#L116](https://github.com/mrwogu/factory-droid-openai/blob/28593bc52bbbef75d81d4ce8081bf2a60a586ae9/src/factory_droid_openai/app.py#L116) |

## `C4|DEF` — **false_pos**
> occurrences here: 40 · corpus total: 56644 · executor: x86_64
> example: [scripts/e2e_matrix.py#L1306](https://github.com/mrwogu/factory-droid-openai/blob/28593bc52bbbef75d81d4ce8081bf2a60a586ae9/scripts/e2e_matrix.py#L1306)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 8 · corpus total: 18195 · executor: x86_64
> example: [src/factory_droid_openai/app.py#L1163](https://github.com/mrwogu/factory-droid-openai/blob/28593bc52bbbef75d81d4ce8081bf2a60a586ae9/src/factory_droid_openai/app.py#L1163)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C2|ELLIPSIS|ascopes` — **variant**
> occurrences here: 1 · corpus total: 116 · executor: x86_64
> example: [src/factory_droid_openai/app.py#L116](https://github.com/mrwogu/factory-droid-openai/blob/28593bc52bbbef75d81d4ce8081bf2a60a586ae9/src/factory_droid_openai/app.py#L116)
> **rule:** C2

> **evidence (model):** The use of ellipsis (...) in Security dependencies (e.g., Security(...)) is a structural variation of the standard C2 pattern (Security(...) with scopes).

