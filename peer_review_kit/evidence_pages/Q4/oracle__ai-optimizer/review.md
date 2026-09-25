# oracle/ai-optimizer

- GitHub: https://github.com/oracle/ai-optimizer
- Stars: 96 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 172 · commit: `b00294d00287`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Dependency Injection via Depends()` | src/server/app/api/deps.py#L20 | The verify_api_key function uses Depends(_api_key_header) to inject an APIKeyHeader dependency, demonstrating FastAPI's DI mechanism. This is a custom dependency that validates API keys. |
| 2 | `Router-level Dependency Injection` | src/server/app/api/mcp/router.py#L17 | The router.include_router calls use dependencies=[Depends(verify_api_key)] to apply the verify_api_key dependency to multiple endpoints, showing DI at the router level. |
| 3 | `Reused Dependency Across Routers` | src/server/app/api/v1/router.py#L35 | The same verify_api_key dependency is applied to multiple authenticated endpoints via dependencies=[Depends(verify_api_key)], indicating a centralized DI pattern for authentication. |

## Pass 2 — reconcile with inventory of oracle/ai-optimizer

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code excerpts show HTTP streaming logic (httpx.AsyncClient, aiter_text), not dependency injection. The initial labeling correctly identifies these as false positives for DI. | src/client/app/content/chatbot.py#L151 |
| `C1|BARE|PARAM` | known | yes | The router.include_router calls explicitly use dependencies=[Depends(verify_api_key)], which matches the known DI pattern for authentication. | src/server/app/api/mcp/router.py#L17 |
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The verify_api_key function uses Depends(_api_key_header) as a parameter dependency, which is valid DI. The false_pos label is incorrect. | src/server/app/api/deps.py#L20 |

### Missed by inventory (1)
- `Router-level DI in v1/router.py` @ src/server/app/api/v1/router.py#L35 — The inventory missed multiple instances of dependencies=[Depends(verify_api_key)] in v1/router.py's include_router calls (lines 35-80). These match the C1|BARE|PARAM pattern but were not counted in...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 155 | **false_pos** | [src/client/app/content/chatbot.py#L151](https://github.com/oracle/ai-optimizer/blob/b00294d002872e52204e426d60ed5072b6497f2b/src/client/app/content/chatbot.py#L151) |
| `C1|BARE|PARAM` | C1 | 16 | **known** | [src/server/app/api/mcp/router.py#L17](https://github.com/oracle/ai-optimizer/blob/b00294d002872e52204e426d60ed5072b6497f2b/src/server/app/api/mcp/router.py#L17) |
| `C1|BARE|SIG` | C1 | 1 | **false_pos** | [src/server/app/api/deps.py#L20](https://github.com/oracle/ai-optimizer/blob/b00294d002872e52204e426d60ed5072b6497f2b/src/server/app/api/deps.py#L20) |

## `C4|DEF` — **false_pos**
> occurrences here: 155 · corpus total: 56644 · executor: x86_64
> example: [src/client/app/content/chatbot.py#L151](https://github.com/oracle/ai-optimizer/blob/b00294d002872e52204e426d60ed5072b6497f2b/src/client/app/content/chatbot.py#L151)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 16 · corpus total: 18195 · executor: x86_64
> example: [src/server/app/api/mcp/router.py#L17](https://github.com/oracle/ai-optimizer/blob/b00294d002872e52204e426d60ed5072b6497f2b/src/server/app/api/mcp/router.py#L17)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 1 · corpus total: 83548 · executor: x86_64
> example: [src/server/app/api/deps.py#L20](https://github.com/oracle/ai-optimizer/blob/b00294d002872e52204e426d60ed5072b6497f2b/src/server/app/api/deps.py#L20)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

