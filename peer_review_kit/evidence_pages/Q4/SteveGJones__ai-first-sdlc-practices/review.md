# SteveGJones/ai-first-sdlc-practices

- GitHub: https://github.com/SteveGJones/ai-first-sdlc-practices
- Stars: 41 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 7 · commit: `b8f639ff52d2`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `No Dependency Injection Detected` | plugins/sdlc-assured/scripts/assured/evidence_adapters.py#L24 | Classes like PythonCommentAdapter and MarkdownHtmlCommentAdapter are manually instantiated and do not use FastAPI's Depends() or similar DI mechanisms. Parameters like 'files' and 'project_root' ar... |
| 2 | `No Dependency Injection Detected` | plugins/sdlc-assured/scripts/assured/evidence_index.py#L71 | Adapters are directly instantiated (e.g., PythonCommentAdapter()) and added to a list, indicating manual object creation rather than dependency injection. |
| 3 | `No Dependency Injection Detected` | tests/integration/delegation-smoke/fixtures/miniproject/tests/test_app.py#L8 | The 'client' fixture uses Flask's test_client() directly, not FastAPI's dependency injection system. |

## Pass 2 — reconcile with inventory of SteveGJones/ai-first-sdlc-practices

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | No dependency injection mechanisms (e.g., FastAPI Depends(), constructor injection) are present in the code. Classes like PythonCommentAdapter and MarkdownHtmlCommentAdapter are manually instantiat... | plugins/sdlc-assured/scripts/assured/evidence_adapters.py#L24 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 7 | **false_pos** | [plugins/sdlc-assured/scripts/assured/evidence_adapters.py#L24](https://github.com/SteveGJones/ai-first-sdlc-practices/blob/b8f639ff52d25d705fa4fa242c5bf7aacf3711e0/plugins/sdlc-assured/scripts/assured/evidence_adapters.py#L24) |

## `C4|DEF` — **false_pos**
> occurrences here: 7 · corpus total: 56644 · executor: x86_64
> example: [plugins/sdlc-assured/scripts/assured/evidence_adapters.py#L24](https://github.com/SteveGJones/ai-first-sdlc-practices/blob/b8f639ff52d25d705fa4fa242c5bf7aacf3711e0/plugins/sdlc-assured/scripts/assured/evidence_adapters.py#L24)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

