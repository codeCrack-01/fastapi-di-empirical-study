# Yakhyobek1997/yagu-wise-ai

- GitHub: https://github.com/Yakhyobek1997/yagu-wise-ai
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 20 · commit: `94d760152efb`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of Yakhyobek1997/yagu-wise-ai

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code examples provided do not show any clear issues that would warrant a true positive for this fingerprint. The functions and methods appear to be correctly implemented without obvious code sm... | scripts/name_audit.py#L60 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 20 | **false_pos** | [scripts/name_audit.py#L60](https://github.com/Yakhyobek1997/yagu-wise-ai/blob/94d760152efb75b4373bd807068268e413d09240/scripts/name_audit.py#L60) |

## `C4|DEF` — **false_pos**
> occurrences here: 20 · corpus total: 56644 · executor: x86_64
> example: [scripts/name_audit.py#L60](https://github.com/Yakhyobek1997/yagu-wise-ai/blob/94d760152efb75b4373bd807068268e413d09240/scripts/name_audit.py#L60)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

