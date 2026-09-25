# langwatch/langwatch

- GitHub: https://github.com/langwatch/langwatch
- Stars: 3476 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 71 · commit: `3d3dc1042097`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of langwatch/langwatch

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses @langwatch.trace and langwatch.get_current_trace().autotrack_openai_calls() to instrument OpenAI calls, which matches the fingerprint's structural pattern. | mcp/typescript/tests/fixtures/fastapi/fastapi_app_expected.py#L24 |
| `C4|DEF` | true_pos | **no (overturn)** | The Python example sdks/python/examples/fastapi_app.py line 24 shows identical instrumentation with @langwatch.trace and autotrack_openai_calls(), confirming real usage. | sdks/python/examples/fastapi_app.py#L24 |

### Missed by inventory (2)
- `Async generator instrumentation with langwatch.span` @ sdks/python/src/langwatch/telemetry/span.py#L590 — The code handles async generators with langwatch.span context managers, which the inventory may have missed as a distinct pattern.
- `Custom model tracking in streaming functions` @ sdks/python/examples/generic_bot_async_streaming.py#L12 — The stream_tokens function uses langwatch.span to track custom models, a pattern not captured by the inventory's existing fingerprints.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 71 | **false_pos** | [mcp/typescript/tests/fixtures/fastapi/fastapi_app_expected.py#L24](https://github.com/langwatch/langwatch/blob/3d3dc1042097e8433e217ad88c833db7f46226be/mcp/typescript/tests/fixtures/fastapi/fastapi_app_expected.py#L24) |

## `C4|DEF` — **false_pos**
> occurrences here: 71 · corpus total: 56644 · executor: x86_64
> example: [mcp/typescript/tests/fixtures/fastapi/fastapi_app_expected.py#L24](https://github.com/langwatch/langwatch/blob/3d3dc1042097e8433e217ad88c833db7f46226be/mcp/typescript/tests/fixtures/fastapi/fastapi_app_expected.py#L24)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

