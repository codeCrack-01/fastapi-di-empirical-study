# shu0411/trade-lab

- GitHub: https://github.com/shu0411/trade-lab
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 9 · commit: `ef611f8ce056`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | backend/app/routers/analysis.py#L27 | The summary() function uses store: EntryStore = Depends(get_entry_store) to inject an EntryStore dependency |
| 2 | `FastAPI Depends injection` | backend/app/routers/analysis.py#L42 | The patterns() function uses store: EntryStore = Depends(get_entry_store) for dependency injection |
| 3 | `FastAPI Depends injection` | backend/app/routers/analysis.py#L63 | The reasons() function uses store: EntryStore = Depends(get_entry_store) to inject the EntryStore |
| 4 | `FastAPI Depends injection` | backend/app/routers/entries.py#L20 | list_entries() uses store: EntryStore = Depends(get_entry_store) for dependency injection |
| 5 | `FastAPI Depends injection` | backend/app/routers/entries.py#L32 | create_entry() uses store: EntryStore = Depends(get_entry_store) to inject the EntryStore |
| 6 | `FastAPI Depends injection` | backend/app/routers/entries.py#L39 | get_entry() uses store: EntryStore = Depends(get_entry_store) for dependency injection |
| 7 | `FastAPI Depends injection` | backend/app/routers/entries.py#L48 | update_entry() uses store: EntryStore = Depends(get_entry_store) to inject the EntryStore |
| 8 | `FastAPI Depends injection` | backend/app/routers/entries.py#L56 | delete_entry() uses store: EntryStore = Depends(get_entry_store) for dependency injection |

## Pass 2 — reconcile with inventory of shu0411/trade-lab

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code correctly uses FastAPI Depends injection for dependency management, which aligns with the structural fingerprint's canonical form. | backend/app/routers/analysis.py#L27 |
| `C4|DEF` | true_pos | **no (overturn)** | The code in the test fixture correctly implements a mock store method, which is a valid use case for the structural fingerprint. | backend/tests/conftest.py#L54 |

### Missed by inventory (5)
- `FastAPI Depends injection` @ backend/app/routers/entries.py#L20 — The inventory missed this instance of Depends injection in the entries router's list_entries endpoint.
- `FastAPI Depends injection` @ backend/app/routers/entries.py#L32 — The inventory missed this instance of Depends injection in the entries router's create_entry endpoint.
- `FastAPI Depends injection` @ backend/app/routers/entries.py#L39 — The inventory missed this instance of Depends injection in the entries router's get_entry endpoint.
- `FastAPI Depends injection` @ backend/app/routers/entries.py#L48 — The inventory missed this instance of Depends injection in the entries router's update_entry endpoint.
- `FastAPI Depends injection` @ backend/app/routers/entries.py#L56 — The inventory missed this instance of Depends injection in the entries router's delete_entry endpoint.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 8 | **false_pos** | [backend/app/routers/analysis.py#L27](https://github.com/shu0411/trade-lab/blob/ef611f8ce0561782dac5bca82be3d54f7027f941/backend/app/routers/analysis.py#L27) |
| `C4|DEF` | C4 | 1 | **false_pos** | [backend/tests/conftest.py#L54](https://github.com/shu0411/trade-lab/blob/ef611f8ce0561782dac5bca82be3d54f7027f941/backend/tests/conftest.py#L54) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 8 · corpus total: 83548 · executor: x86_64
> example: [backend/app/routers/analysis.py#L27](https://github.com/shu0411/trade-lab/blob/ef611f8ce0561782dac5bca82be3d54f7027f941/backend/app/routers/analysis.py#L27)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [backend/tests/conftest.py#L54](https://github.com/shu0411/trade-lab/blob/ef611f8ce0561782dac5bca82be3d54f7027f941/backend/tests/conftest.py#L54)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

