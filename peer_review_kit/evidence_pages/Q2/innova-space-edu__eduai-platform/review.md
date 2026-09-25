# innova-space-edu/eduai-platform

- GitHub: https://github.com/innova-space-edu/eduai-platform
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 4 · commit: `68bbb51adba6`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=1 false_pos=0 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI route-level dependencies` | services/openvoice-space/app.py#L150 | Dependencies are specified via the `dependencies` parameter in route decorators, e.g., `dependencies=[Depends(require_internal_token)]` for `/voices/{voice_id}/status` and `/voices/process` endpoints. |

## Pass 2 — reconcile with inventory of innova-space-edu/eduai-platform

_Presented fingerprints:_ `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|PARAM` | known | yes | The code confirms four endpoints with `dependencies=[Depends(...)]`: /voices/{voice_id}/status (L150), /voices/process (L162), /voices/synthesize (L198), and /voices/{voice_id} (L242). | services/openvoice-space/app.py#L242 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|PARAM` | C1 | 4 | **known** | [services/openvoice-space/app.py#L150](https://github.com/innova-space-edu/eduai-platform/blob/68bbb51adba65135364ee3dba0ee9b55619b7a97/services/openvoice-space/app.py#L150) |

## `C1|BARE|PARAM` — **known**
> occurrences here: 4 · corpus total: 18195 · executor: x86_64
> example: [services/openvoice-space/app.py#L150](https://github.com/innova-space-edu/eduai-platform/blob/68bbb51adba65135364ee3dba0ee9b55619b7a97/services/openvoice-space/app.py#L150)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

