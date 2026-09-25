# letya999/job_ftch

- GitHub: https://github.com/letya999/job_ftch
- Stars: 15 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 273 · commit: `587422d3821b`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `async context managers for dependency-like objects` | job_ftch/adapters/telegram_bot/handlers/sources.py#L215 | The `telegram_client_factory` async context manager creates and yields a Telegram client, suggesting a pattern of encapsulating dependencies within context managers. This could be a form of manual ... |
| 2 | `nested async context managers` | job_ftch/application/source_inputs.py#L111 | The `_run_factory` async context manager wraps `telegram_client_factory`, demonstrating a layered approach to managing dependencies. This suggests a pattern of composing context managers to handle ... |

## Pass 2 — reconcile with inventory of letya999/job_ftch

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code in docs_scripts/docs_lint.py contains text parsing utilities (iter_fences, iter_lines_outside_fences) that use state variables and regex but show no dependency injection patterns. The stat... | docs_scripts/docs_lint.py#L123 |

### Missed by inventory (1)
- `async context manager composition` @ job_ftch/application/source_inputs.py#L111 — The nested async context managers (_run_factory wrapping telegram_client_factory) demonstrate a compositional pattern that could be missed by inventory tools focused on simple DI patterns rather th...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 273 | **false_pos** | [docs_scripts/docs_lint.py#L591](https://github.com/letya999/job_ftch/blob/587422d3821b5f96e5b5d19dbad1b56ec2c30720/docs_scripts/docs_lint.py#L591) |

## `C4|DEF` — **false_pos**
> occurrences here: 273 · corpus total: 56644 · executor: x86_64
> example: [docs_scripts/docs_lint.py#L591](https://github.com/letya999/job_ftch/blob/587422d3821b5f96e5b5d19dbad1b56ec2c30720/docs_scripts/docs_lint.py#L591)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

