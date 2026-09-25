# Dhairya2289/Personal-AI-System

- GitHub: https://github.com/Dhairya2289/Personal-AI-System
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 1 · commit: `5e868eb7520a`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection Detected` | knowledge.py#L258 | The code excerpt shows no use of FastAPI dependency injection constructs like Depends, Security, or annotated dependencies. The static summary confirms depends_total=0, annotated_depends_total=0, a... |

## Pass 2 — reconcile with inventory of Dhairya2289/Personal-AI-System

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code at knowledge.py:258 contains no FastAPI dependency injection constructs (e.g., Depends, Security, annotated dependencies). The static summary confirms depends_total=0, annotated_depends_to... | knowledge.py#L258 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 1 | **false_pos** | [knowledge.py#L258](https://github.com/Dhairya2289/Personal-AI-System/blob/5e868eb7520ae859b242bd58ec8c9702cbae5bf8/knowledge.py#L258) |

## `C4|DEF` — **false_pos**
> occurrences here: 1 · corpus total: 56644 · executor: x86_64
> example: [knowledge.py#L258](https://github.com/Dhairya2289/Personal-AI-System/blob/5e868eb7520ae859b242bd58ec8c9702cbae5bf8/knowledge.py#L258)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

