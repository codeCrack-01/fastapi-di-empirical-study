# sandraschi/calibremcp

- GitHub: https://github.com/sandraschi/calibremcp
- Stars: 38 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 70 · commit: `6a7dc62cb0ac`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | mcpb/src/api/libraries.py#L36 | The line 'db: Session = Depends(get_db)' shows FastAPI's Depends() being used to inject a database session. This is a clear example of dependency injection where get_db is a dependency provider fun... |
| 2 | `FastAPI Depends injection` | mcpb/src/api/libraries.py#L59 | Another instance of 'db: Session = Depends(get_db)' in the create_library endpoint demonstrates the same DI pattern for database session injection. |
| 3 | `FastAPI Depends injection` | mcpb/src/api/libraries.py#L76 | The get_library endpoint also uses 'db: Session = Depends(get_db)', showing consistent use of FastAPI's dependency injection system across multiple endpoints. |

## Pass 2 — reconcile with inventory of sandraschi/calibremcp

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_positive | **no (overturn)** | The code explicitly uses FastAPI's Depends() for database session injection, which matches the DI pattern this fingerprint is intended to capture. | mcpb/src/api/libraries.py#L36 |
| `C1|BARE|SIG` | true_positive | **no (overturn)** | The code contains valid FastAPI dependency injection signatures (e.g., 'db: Session = Depends(get_db)') that directly match the BARE|SIG pattern. | mcpb/src/api/libraries.py#L59 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 46 | **false_pos** | [calibre_plugin/ollama_client.py#L76](https://github.com/sandraschi/calibremcp/blob/6a7dc62cb0ac2a231225bfb995b498412c44f4a4/calibre_plugin/ollama_client.py#L76) |
| `C1|BARE|SIG` | C1 | 24 | **false_pos** | [mcpb/src/api/libraries.py#L36](https://github.com/sandraschi/calibremcp/blob/6a7dc62cb0ac2a231225bfb995b498412c44f4a4/mcpb/src/api/libraries.py#L36) |

## `C4|DEF` — **false_pos**
> occurrences here: 46 · corpus total: 56644 · executor: x86_64
> example: [calibre_plugin/ollama_client.py#L76](https://github.com/sandraschi/calibremcp/blob/6a7dc62cb0ac2a231225bfb995b498412c44f4a4/calibre_plugin/ollama_client.py#L76)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 24 · corpus total: 83548 · executor: x86_64
> example: [mcpb/src/api/libraries.py#L36](https://github.com/sandraschi/calibremcp/blob/6a7dc62cb0ac2a231225bfb995b498412c44f4a4/mcpb/src/api/libraries.py#L36)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

