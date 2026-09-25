# Samarth-23-eng/scope-intelligence

- GitHub: https://github.com/Samarth-23-eng/scope-intelligence
- Stars: 24 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 6 · commit: `56ec42f1ff38`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of Samarth-23-eng/scope-intelligence

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No explicit code contradiction found; panel label remains valid based on available evidence. | api/main.py#L53 |

### Missed by inventory (1)
- `Context manager usage in tests` @ tests/test_retrieval.py#L136 — The `fake_connection` context manager in tests may represent a structural pattern not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 6 | **false_pos** | [api/main.py#L53](https://github.com/Samarth-23-eng/scope-intelligence/blob/56ec42f1ff38c3de45ac116a012367f474880d89/api/main.py#L53) |

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [api/main.py#L53](https://github.com/Samarth-23-eng/scope-intelligence/blob/56ec42f1ff38c3de45ac116a012367f474880d89/api/main.py#L53)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

