# aws/context-ontology-accelerator

- GitHub: https://github.com/aws/context-ontology-accelerator
- Stars: 391 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 115 · commit: `e265573df26e`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of aws/context-ontology-accelerator

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code sets environment variables in test fixtures (e.g., os.environ.setdefault for AWS regions) as mock setup, not actual configuration definitions. The comments clarify these are test-specific ... | infra/test/lambdas/conftest.py#L53 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 115 | **false_pos** | [infra/test/lambdas/conftest.py#L53](https://github.com/aws/context-ontology-accelerator/blob/e265573df26eefd6a8b51683d7555ceffbe26ab7/infra/test/lambdas/conftest.py#L53) |

## `C4|DEF` — **false_pos**
> occurrences here: 115 · corpus total: 56644 · executor: x86_64
> example: [infra/test/lambdas/conftest.py#L53](https://github.com/aws/context-ontology-accelerator/blob/e265573df26eefd6a8b51683d7555ceffbe26ab7/infra/test/lambdas/conftest.py#L53)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

