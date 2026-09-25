# ranasl62/ehr-risk-framework

- GitHub: https://github.com/ranasl62/ehr-risk-framework
- Stars: 23 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 10 · commit: `6cc79dc184c5`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based dependency injection` | api/framework_routes.py#L17 | AuthDep = Depends(require_api_key_if_configured) creates a dependency for API key authentication, a common FastAPI pattern |
| 2 | `Reusable dependency objects` | api/main.py#L29 | AuthDep = Depends(...) is defined at the module level for reuse across routes |
| 3 | `Custom dependency injection` | api/main.py#L115 | ArtifactDep = Depends(artifact_dep) injects a model artifact dependency with test override capability |
| 4 | `Test dependency overriding` | tests/conftest.py#L27 | app.dependency_overrides[artifact_dep] = _fake_artifact demonstrates test-time dependency mocking |

## Pass 2 — reconcile with inventory of ranasl62/ehr-risk-framework

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts do not show any instances of C4|DEF pattern (e.g., no explicit dependency injection with parameters). The panel's label aligns with the absence of such patterns in the provided code. | api/main.py#L33 |
| `C1|BARE|PARAM` | known | yes | The code explicitly uses FastAPI's Depends() for authentication and artifact injection (e.g., AuthDep = Depends(...)), which matches the C1|BARE|PARAM fingerprint. | api/framework_routes.py#L17 |

### Missed by inventory (1)
- `Test dependency overriding (e.g., app.dependency_overrides[artifact_dep] = _fake_artifact)` @ tests/conftest.py#L27 — The inventory did not capture test-specific dependency overriding patterns, which are critical for mocking in test fixtures.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 6 | **false_pos** | [api/main.py#L33](https://github.com/ranasl62/ehr-risk-framework/blob/6cc79dc184c525918987e187b98807f7ca490ad8/api/main.py#L33) |
| `C1|BARE|PARAM` | C1 | 4 | **known** | [api/framework_routes.py#L17](https://github.com/ranasl62/ehr-risk-framework/blob/6cc79dc184c525918987e187b98807f7ca490ad8/api/framework_routes.py#L17) |

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [api/main.py#L33](https://github.com/ranasl62/ehr-risk-framework/blob/6cc79dc184c525918987e187b98807f7ca490ad8/api/main.py#L33)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 4 · corpus total: 18195 · executor: x86_64
> example: [api/framework_routes.py#L17](https://github.com/ranasl62/ehr-risk-framework/blob/6cc79dc184c525918987e187b98807f7ca490ad8/api/framework_routes.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

