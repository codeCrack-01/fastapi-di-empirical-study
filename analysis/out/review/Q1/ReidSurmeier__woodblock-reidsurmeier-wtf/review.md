# ReidSurmeier/woodblock-reidsurmeier-wtf

- GitHub: https://github.com/ReidSurmeier/woodblock-reidsurmeier-wtf
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 14 · commit: `c82645b333ad`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of ReidSurmeier/woodblock-reidsurmeier-wtf

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code does not exhibit dependency injection patterns (e.g., no explicit dependency passing, service locators, or framework-specific DI usage). The flagged code shows standard async functions, im... | backend/analytics_api.py#L144 |

### Missed by inventory (1)
- `Async context managers and FastAPI lifespan hooks` @ main.py#L172 — The code uses FastAPI's lifespan context manager for model warmup, which involves framework-level dependency injection (e.g., async context managers). This pattern was not captured by the fingerpri...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 14 | **false_pos** | [backend/analytics_api.py#L144](https://github.com/ReidSurmeier/woodblock-reidsurmeier-wtf/blob/c82645b333ad4ae13ab31b033d6dc75da3eb7867/backend/analytics_api.py#L144) |

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [backend/analytics_api.py#L144](https://github.com/ReidSurmeier/woodblock-reidsurmeier-wtf/blob/c82645b333ad4ae13ab31b033d6dc75da3eb7867/backend/analytics_api.py#L144)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

