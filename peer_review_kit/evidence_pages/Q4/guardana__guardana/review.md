# guardana/guardana

- GitHub: https://github.com/guardana/guardana
- Stars: 89 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 190 · commit: `7d3762545ee0`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Iterator Pattern` | packages/guardana-core/src/guardana/core/trace/load.py#L277 | The `_records` function uses `yield` to produce items one at a time, allowing efficient memory usage when processing large JSONL files. This aligns with the Iterator Pattern, which provides a way t... |
| 2 | `Iterator Pattern` | packages/guardana-core/src/guardana/core/trace/model.py#L148 | Methods like `of_kind`, `children`, and `after` return generator expressions (e.g., `(s for s in self.spans if s.kind is kind)`), which implement the Iterator Pattern by enabling sequential access ... |
| 3 | `Generator Pattern` | packages/guardana-core/src/guardana/core/trajectory/model.py#L53 | The `calls` method uses a generator to iterate over `ToolCall` objects, demonstrating the Generator Pattern for memory-efficient traversal of step invocations. |
| 4 | `Resource Management` | packages/guardana-core/tests/test_mcp_redirect_guard.py#L53 | The `server` fixture uses a context manager (`yield` with `try/finally`) to start and stop a server, ensuring resources are properly released. This follows the Resource Management Pattern, common i... |
| 5 | `Strategy Pattern` | packages/guardana-core/tests/test_rule.py#L19 | The `_AlwaysFinds` class implements a rule with a `run` method that yields findings. This aligns with the Strategy Pattern, where different rules (strategies) can be plugged in to achieve varying b... |

## Pass 2 — reconcile with inventory of guardana/guardana

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|ELLIPSIS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `packages/guardana-core/src/guardana/core/trace/load.py:277` | Iterator Pattern | yes | The `_records` function uses `yield` to process JSONL files line by line, aligning with the Iterator Pattern for memory-efficient traversal. | packages/guardana-core/src/guardana/core/trace/load.py#L277 |
| `packages/guardana-core/src/guardana/core/trace/model.py:148` | Iterator Pattern | yes | Methods like `of_kind`, `children`, and `after` return generator expressions, enabling sequential access to spans without loading all data at once. | packages/guardana-core/src/guardana/core/trace/model.py#L148 |
| `packages/guardana-core/src/guardana/core/trajectory/model.py:53` | Generator Pattern | yes | The `calls` method uses a generator to iterate over `ToolCall` objects, demonstrating the Generator Pattern for memory-efficient traversal. | packages/guardana-core/src/guardana/core/trajectory/model.py#L53 |
| `packages/guardana-core/tests/test_mcp_redirect_guard.py:53` | Resource Management | yes | The `server` fixture uses a context manager with `yield` and `try/finally` to manage the server's lifecycle, ensuring proper resource release. | packages/guardana-core/tests/test_mcp_redirect_guard.py#L53 |
| `packages/guardana-core/tests/test_rule.py:19` | Strategy Pattern | yes | The `_AlwaysFinds` class implements a rule with a `run` method that yields findings, aligning with the Strategy Pattern for pluggable behaviors. | packages/guardana-core/tests/test_rule.py#L19 |

### Missed by inventory (2)
- `Test Fixture Pattern` @ packages/guardana-core/tests/test_mcp_redirect_guard.py#L53 — The `server` fixture uses `@pytest.fixture` to manage test resources, which is a test fixture pattern but was not explicitly noted in the initial observations.
- `Iterator Pattern` @ packages/guardana-core/tests/_roundtrip.py#L38 — The `leaves` function uses a generator to walk through dataclass fields, which is another example of the Iterator Pattern but was not mentioned in the initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 186 | **false_pos** | [examples/custom_rule/src/acme_rules/approved_model.py#L44](https://github.com/guardana/guardana/blob/7d3762545ee0e6e6a1417dfa6546fff769cf367f/examples/custom_rule/src/acme_rules/approved_model.py#L44) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [packages/guardana-server/src/guardana/server/app.py#L114](https://github.com/guardana/guardana/blob/7d3762545ee0e6e6a1417dfa6546fff769cf367f/packages/guardana-server/src/guardana/server/app.py#L114) |
| `C3|ELLIPSIS|BARE` | C3 | 2 | **variant** | [packages/guardana-server/src/guardana/server/app.py#L114](https://github.com/guardana/guardana/blob/7d3762545ee0e6e6a1417dfa6546fff769cf367f/packages/guardana-server/src/guardana/server/app.py#L114) |

## `C4|DEF` — **false_pos**
> occurrences here: 186 · corpus total: 56644 · executor: x86_64
> example: [examples/custom_rule/src/acme_rules/approved_model.py#L44](https://github.com/guardana/guardana/blob/7d3762545ee0e6e6a1417dfa6546fff769cf367f/examples/custom_rule/src/acme_rules/approved_model.py#L44)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [packages/guardana-server/src/guardana/server/app.py#L114](https://github.com/guardana/guardana/blob/7d3762545ee0e6e6a1417dfa6546fff769cf367f/packages/guardana-server/src/guardana/server/app.py#L114)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 2 · corpus total: 1113 · executor: x86_64
> example: [packages/guardana-server/src/guardana/server/app.py#L114](https://github.com/guardana/guardana/blob/7d3762545ee0e6e6a1417dfa6546fff769cf367f/packages/guardana-server/src/guardana/server/app.py#L114)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

