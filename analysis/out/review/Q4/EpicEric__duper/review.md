# EpicEric/duper

- GitHub: https://github.com/EpicEric/duper
- Stars: 38 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 1 · commit: `e6deb0cd99b7`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=1 false_pos=0 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends usage` | duper-python/python/duper/fastapi.py#L111 | The code explicitly returns Depends(_get_duper_body), which is FastAPI's standard pattern for declaring dependencies. This indicates that _get_duper_body is a dependency that must be resolved befor... |

## Pass 2 — reconcile with inventory of EpicEric/duper

_Presented fingerprints:_ `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | correct usage of FastAPI Depends | **no (overturn)** | The code explicitly returns Depends(_get_duper_body), which is the standard FastAPI pattern for declaring dependencies. This is not a bare parameter but a properly annotated dependency. | duper-python/python/duper/fastapi.py#L111 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 1 | **known** | [duper-python/python/duper/fastapi.py#L111](https://github.com/EpicEric/duper/blob/e6deb0cd99b7970f16e8d63629b2d6c243e3a8bf/duper-python/python/duper/fastapi.py#L111) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [duper-python/python/duper/fastapi.py#L111](https://github.com/EpicEric/duper/blob/e6deb0cd99b7970f16e8d63629b2d6c243e3a8bf/duper-python/python/duper/fastapi.py#L111)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

