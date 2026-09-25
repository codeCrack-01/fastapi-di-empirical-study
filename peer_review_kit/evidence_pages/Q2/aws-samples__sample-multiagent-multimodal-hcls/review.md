# aws-samples/sample-multiagent-multimodal-hcls

- GitHub: https://github.com/aws-samples/sample-multiagent-multimodal-hcls
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 2 · commit: `06db2a5fbec3`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No FastAPI Dependency Injection` | main_agent.py#L271 | The code defines an @app.entrypoint function but does not use FastAPI's Depends() or other DI mechanisms. The Agent is instantiated directly with hardcoded parameters rather than injected dependenc... |
| 2 | `No FastAPI Dependency Injection` | mcp_servers/pubmed/pubmed.py#L58 | The lazy_load() method uses urllib and json directly without any FastAPI dependency injection patterns. No Depends() or similar constructs are present. |

## Pass 2 — reconcile with inventory of aws-samples/sample-multiagent-multimodal-hcls

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code does not use FastAPI's dependency injection mechanisms (e.g., Depends()) in the cited locations. The Agent is instantiated directly with hardcoded parameters, and the lazy_load() method us... | main_agent.py#L271 |
| `C4|DEF` | false_pos | yes | No FastAPI dependency injection is present in the pubmed.py lazy_load() method. The code uses urllib and json directly without DI constructs. | mcp_servers/pubmed/pubmed.py#L58 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 2 | **false_pos** | [main_agent.py#L271](https://github.com/aws-samples/sample-multiagent-multimodal-hcls/blob/06db2a5fbec3ca7ea133636db4860a62f2210f6b/main_agent.py#L271) |

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [main_agent.py#L271](https://github.com/aws-samples/sample-multiagent-multimodal-hcls/blob/06db2a5fbec3ca7ea133636db4860a62f2210f6b/main_agent.py#L271)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

