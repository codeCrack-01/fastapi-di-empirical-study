# zeroday0619/KotonohaInterpreter

- GitHub: https://github.com/zeroday0619/KotonohaInterpreter
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 40 · commit: `fb56b047b320`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of zeroday0619/KotonohaInterpreter

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code in the provided lines does not appear to be a false positive. The methods in _prometheus.py are correctly implementing metrics collection, and the error handling in _llm.py is standard pra... | src/kotonoha/_prometheus.py#L243 |

### Missed by inventory (1)
- `Error handling in async methods` @ src/kotonoha/clients/_llm.py#L111 — The error handling pattern in stream_chat() was not captured by the initial inventory, despite being a common code smell.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 40 | **false_pos** | [src/kotonoha/_prometheus.py#L243](https://github.com/zeroday0619/KotonohaInterpreter/blob/fb56b047b3206363b873100ab5f9bc96a6268318/src/kotonoha/_prometheus.py#L243) |

## `C4|DEF` — **false_pos**
> occurrences here: 40 · corpus total: 56644 · executor: x86_64
> example: [src/kotonoha/_prometheus.py#L243](https://github.com/zeroday0619/KotonohaInterpreter/blob/fb56b047b3206363b873100ab5f9bc96a6268318/src/kotonoha/_prometheus.py#L243)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

