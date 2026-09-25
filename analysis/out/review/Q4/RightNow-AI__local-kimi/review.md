# RightNow-AI/local-kimi

- GitHub: https://github.com/RightNow-AI/local-kimi
- Stars: 34 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 43 · commit: `4552f88fb994`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of RightNow-AI/local-kimi

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts show no explicit dependency injection patterns (e.g., interfaces, abstract classes, or DI containers). The functions manage state/overrides manually via global dictionaries or loc... | engine/kernels/registry.py#L189 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 43 | **false_pos** | [engine/kernels/registry.py#L189](https://github.com/RightNow-AI/local-kimi/blob/4552f88fb994d6f649f3a07fb592cc595de8149a/engine/kernels/registry.py#L189) |

## `C4|DEF` — **false_pos**
> occurrences here: 43 · corpus total: 56644 · executor: x86_64
> example: [engine/kernels/registry.py#L189](https://github.com/RightNow-AI/local-kimi/blob/4552f88fb994d6f649f3a07fb592cc595de8149a/engine/kernels/registry.py#L189)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

