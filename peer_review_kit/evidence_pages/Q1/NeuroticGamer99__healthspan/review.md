# NeuroticGamer99/healthspan

- GitHub: https://github.com/NeuroticGamer99/healthspan
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 27 · commit: `2152ca403acb`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection via Depends` | src/healthspan/api_security.py#L376 | The `require()` function returns `params.Depends(...)` objects, which is FastAPI's standard pattern for declaring route dependencies. This injects scope validation logic into API routes via the `de... |
| 2 | `FastAPI dependency injection via Depends` | src/healthspan/api_security.py#L382 | The same `require()` function explicitly constructs `Depends(_PublicMarker())` and `Depends(_ScopedRequirement(...))` objects, demonstrating the use of FastAPI's dependency injection system to enfo... |

## Pass 2 — reconcile with inventory of NeuroticGamer99/healthspan

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts for C4|DEF (lines 1405, 52, 394) do not contain FastAPI dependency injection patterns. The static instrument's label as false_pos is correct because no DI occurs in these lines. | src/healthspan/api_security.py#L394 |
| `C1|BARE|PARAM` | known | yes | The code excerpts for C1|BARE|PARAM (lines 376, 382) explicitly use FastAPI's `Depends(...)` pattern for dependency injection, confirming the label as known. | src/healthspan/api_security.py#L376 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 25 | **false_pos** | [scripts/bot_review.py#L1405](https://github.com/NeuroticGamer99/healthspan/blob/2152ca403acbf22a7aa9a698c6f564af9efb01a5/scripts/bot_review.py#L1405) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [src/healthspan/api_security.py#L376](https://github.com/NeuroticGamer99/healthspan/blob/2152ca403acbf22a7aa9a698c6f564af9efb01a5/src/healthspan/api_security.py#L376) |

## `C4|DEF` — **false_pos**
> occurrences here: 25 · corpus total: 56644 · executor: x86_64
> example: [scripts/bot_review.py#L1405](https://github.com/NeuroticGamer99/healthspan/blob/2152ca403acbf22a7aa9a698c6f564af9efb01a5/scripts/bot_review.py#L1405)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [src/healthspan/api_security.py#L376](https://github.com/NeuroticGamer99/healthspan/blob/2152ca403acbf22a7aa9a698c6f564af9efb01a5/src/healthspan/api_security.py#L376)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

