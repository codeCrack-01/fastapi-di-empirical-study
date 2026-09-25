# nmfs-ost/AA-SI_Workbench

- GitHub: https://github.com/nmfs-ost/AA-SI_Workbench
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 2 · commit: `7a0254438b21`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI Dependency Injection` | backend/tests/test_derived.py#L66 | The code shows a test fixture (_provider) creating a GcsProvider with a fake client, but this is manual test double setup, not FastAPI Depends-based DI. Static analysis confirms depends_total=0 and... |
| 2 | `No FastAPI Dependency Injection` | backend/tests/test_environment.py#L21 | The _clean_job fixture handles test isolation via pytest, not FastAPI DI. No Depends(), Security(), or yield-based dependency patterns are present. Static analysis confirms max_depth=0 and yield_de... |

## Pass 2 — reconcile with inventory of nmfs-ost/AA-SI_Workbench

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The test code uses pytest fixtures for test double setup (e.g., _provider fixture), which is standard test infrastructure, not FastAPI DI. No FastAPI-specific DI constructs like Depends(), Security... | backend/tests/test_derived.py#L66 |
| `C4|DEF` | false_pos | yes | The _clean_job fixture uses pytest for test isolation (monkeypatching environment variables and process cleanup), which is test infrastructure, not FastAPI DI. No FastAPI DI constructs are present.... | backend/tests/test_environment.py#L21 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 2 | **false_pos** | [backend/tests/test_derived.py#L66](https://github.com/nmfs-ost/AA-SI_Workbench/blob/7a0254438b2140b55e6133fdf9208ce017625cc1/backend/tests/test_derived.py#L66) |

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [backend/tests/test_derived.py#L66](https://github.com/nmfs-ost/AA-SI_Workbench/blob/7a0254438b2140b55e6133fdf9208ce017625cc1/backend/tests/test_derived.py#L66)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

