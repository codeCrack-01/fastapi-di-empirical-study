# DGuckert/Butler

- GitHub: https://github.com/DGuckert/Butler
- Stars: 66 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 53 · commit: `0fd3962d66cf`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Service Locator` | main.py#L762 | The code directly imports and uses functions from the 'spotify' module (e.g., make_state, build_auth_url, disconnect) without injecting them as dependencies. This resembles the Service Locator patt... |

## Pass 2 — reconcile with inventory of DGuckert/Butler

_Presented fingerprints:_ `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `Service Locator @ main.py:762` | Service Locator @ main.py:762 | **no (overturn)** | The code does not use a service locator pattern; it directly imports functions from the 'spotify' module, which is a normal module import, not a centralized service registry. | main.py#L762 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 53 | **false_pos** | [auth.py#L25](https://github.com/DGuckert/Butler/blob/0fd3962d66cfef604dfaafba21b2e1e827e9841e/auth.py#L25) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 53 · corpus total: 83548 · executor: x86_64
> example: [auth.py#L25](https://github.com/DGuckert/Butler/blob/0fd3962d66cfef604dfaafba21b2e1e827e9841e/auth.py#L25)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

