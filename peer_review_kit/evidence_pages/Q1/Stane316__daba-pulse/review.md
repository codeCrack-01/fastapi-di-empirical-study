# Stane316/daba-pulse

- GitHub: https://github.com/Stane316/daba-pulse
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 1 · commit: `6b2495552c08`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `custom lifespan-based initialization` | backend/app/main.py#L26 | The code defines an async lifespan context manager that uses get_settings() and store.load() for initialization, suggesting manual dependency management rather than FastAPI's standard Depends() pat... |

## Pass 2 — reconcile with inventory of Stane316/daba-pulse

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code defines a lifespan context manager for FastAPI, which is a valid form of dependency management (initializing data loading and configuration). This is not a false positive but a legitimate ... | backend/app/main.py#L26 |

### Missed by inventory (1)
- `custom lifespan-based initialization` @ backend/app/main.py#L26 — The inventory did not capture the use of FastAPI's lifespan context manager as a DI mechanism, which is explicitly implemented here.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/app/main.py#L26](https://github.com/Stane316/daba-pulse/blob/6b2495552c08a1293e146cde82aa1d5e4c6a65ca/backend/app/main.py#L26) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/app/main.py#L26](https://github.com/Stane316/daba-pulse/blob/6b2495552c08a1293e146cde82aa1d5e4c6a65ca/backend/app/main.py#L26)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

