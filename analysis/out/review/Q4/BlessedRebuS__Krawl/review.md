# BlessedRebuS/Krawl

- GitHub: https://github.com/BlessedRebuS/Krawl
- Stars: 556 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 3 · commit: `fe9ec07df19a`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends() in APIRouter` | src/routes/honeypot.py#L96 | The code explicitly uses Depends(_track_honeypot_request) as a dependency for an APIRouter, which is FastAPI's standard dependency injection pattern. This injects the _track_honeypot_request functi... |

## Pass 2 — reconcile with inventory of BlessedRebuS/Krawl

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code at src/app.py#28 and src/metrics.py#71 does not contain dependency injection (DI) patterns. The lines show imports, configuration, and metric collection logic, not DI usage. | src/app.py#L28 |
| `C1|BARE|PARAM` | known | yes | The code at src/routes/honeypot.py#96 explicitly uses FastAPI's Depends() for dependency injection, matching the 'known' label. | src/routes/honeypot.py#L96 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 2 | **false_pos** | [src/app.py#L28](https://github.com/BlessedRebuS/Krawl/blob/fe9ec07df19a075d877b2e36bc63cd48004d32b7/src/app.py#L28) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [src/routes/honeypot.py#L96](https://github.com/BlessedRebuS/Krawl/blob/fe9ec07df19a075d877b2e36bc63cd48004d32b7/src/routes/honeypot.py#L96) |

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [src/app.py#L28](https://github.com/BlessedRebuS/Krawl/blob/fe9ec07df19a075d877b2e36bc63cd48004d32b7/src/app.py#L28)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [src/routes/honeypot.py#L96](https://github.com/BlessedRebuS/Krawl/blob/fe9ec07df19a075d877b2e36bc63cd48004d32b7/src/routes/honeypot.py#L96)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

