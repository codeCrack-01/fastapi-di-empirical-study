# dzhalaevd/Donatello

- GitHub: https://github.com/dzhalaevd/Donatello
- Stars: 135 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 4 · commit: `8470c4542a57`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Custom provider-based DI (likely Dishka)` | backend/src/infra/ioc/adapters.py#L57 | The code shows @provide decorators with scope annotations (Scope.APP/REQUEST) and async generator providers yielding AsyncSession objects. This matches Dishka's pattern of using provider functions ... |

## Pass 2 — reconcile with inventory of dzhalaevd/Donatello

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses DI patterns with @provide decorators, async generator providers, and scope annotations (Scope.APP/REQUEST) in backend/src/infra/ioc/adapters.py:57, which aligns with Dishka... | backend/src/infra/ioc/adapters.py#L57 |

### Missed by inventory (1)
- `Dishka-based provider DI with @provide decorators and scope annotations` @ backend/src/infra/ioc/adapters.py#L57 — The inventory did not capture the explicit use of Dishka's DI framework through provider functions with scope annotations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [backend/src/infra/db/main.py#L11](https://github.com/dzhalaevd/Donatello/blob/8470c4542a57e0ad25f05da1619d9cfc6a32f111/backend/src/infra/db/main.py#L11) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [backend/src/infra/db/main.py#L11](https://github.com/dzhalaevd/Donatello/blob/8470c4542a57e0ad25f05da1619d9cfc6a32f111/backend/src/infra/db/main.py#L11)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

