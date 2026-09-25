# masumi-network/Citadel

- GitHub: https://github.com/masumi-network/Citadel
- Stars: 15 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 99 · commit: `564c9b31fb82`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Context-based Dependency Injection` | kb/cognee_client.py#L123 | Uses contextvars.ContextVar and contextmanager to inject '_QDRANT_SCOPE' state implicitly through context, avoiding explicit parameter passing. |
| 2 | `Context-based Dependency Injection` | kb/service.py#L45 | Employs capture_run_scope contextmanager with ContextVar to inject 'active capture run ID' state, decoupling dependent code from direct ID handling. |
| 3 | `Context-based Dependency Injection` | kb/qdrant_adapter.py#L78 | Leverages qdrant_scope contextmanager and ContextVar to inject '_QDRANT_SCOPE' state, enabling scoped operation tracking without explicit parameters. |

## Pass 2 — reconcile with inventory of masumi-network/Citadel

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `context-based_dependency_injection` | context-based_dependency_injection | yes | Code explicitly uses contextvars.ContextVar and contextmanager in kb/cognee_client.py:123, kb/service.py:45, and kb/qdrant_adapter.py:78 to inject state implicitly through context, confirming the f... | kb/cognee_client.py#L123 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 99 | **false_pos** | [kb/access.py#L1051](https://github.com/masumi-network/Citadel/blob/564c9b31fb82eecf16bee8dfb6015cd3b0de9c8f/kb/access.py#L1051) |

## `C4|DEF` — **false_pos**
> occurrences here: 99 · corpus total: 56644 · executor: x86_64
> example: [kb/access.py#L1051](https://github.com/masumi-network/Citadel/blob/564c9b31fb82eecf16bee8dfb6015cd3b0de9c8f/kb/access.py#L1051)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

