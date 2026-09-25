# toddawhittaker/ipeds-oracle

- GitHub: https://github.com/toddawhittaker/ipeds-oracle
- Stars: 2 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 91 · commit: `c5400992da91`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `DRY Principle` | backend/app/routers/keys.py#L100 | The `relabel_key` function reuses the `KeyCreate` model for updating labels instead of creating a new model, avoiding duplication of fields and validation logic. This aligns with the DRY (Don't Rep... |
| 2 | `Consistent Access Control` | backend/app/routers/keys.py#L100 | The `revoke_key` function enforces that users can only interact with their own keys (via `row['user_id'] == user['id']` check), ensuring consistent access control rules across the application. This... |
| 3 | `Generator Reuse` | backend/app/llm.py#L1109 | The `_final_events` generator is reused across different code paths to produce a standardized event sequence. This promotes modularity and reduces code duplication by centralizing event generation ... |
| 4 | `Graceful Degradation` | backend/app/main.py#L90 | The lifespan context manager logs configuration warnings (e.g., missing model) instead of raising errors, allowing the app to start even with incomplete settings. This implements graceful degradati... |
| 5 | `Rate Limiting` | backend/app/routers/chat.py#L440 | The `enforce_chat_rate_limit` function prevents abuse by limiting the number of chat turns per user. This enforces a security and resource management pattern to avoid provider cost overruns or deni... |

## Pass 2 — reconcile with inventory of toddawhittaker/ipeds-oracle

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|SIG`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `DRY Principle @ backend/app/routers/keys.py:100` | DRY Principle @ backend/app/routers/keys.py:100 | yes | The `relabel_key` function reuses `KeyCreate` for updates, avoiding duplication of fields and validation logic. | backend/app/routers/keys.py#L100 |
| `Consistent Access Control @ backend/app/routers/keys.py:100` | Consistent Access Control @ backend/app/routers/keys.py:100 | yes | The `revoke_key` function checks `row['user_id'] == user['id']` to enforce access control, preventing information leakage. | backend/app/routers/keys.py#L100 |
| `Generator Reuse @ backend/app/llm.py:1109` | Generator Reuse @ backend/app/llm.py:1109 | yes | The `_final_events` generator is reused across code paths to standardize event sequences. | backend/app/llm.py#L1109 |
| `Graceful Degradation @ backend/app/main.py:90` | Graceful Degradation @ backend/app/main.py:90 | yes | The lifespan context manager logs configuration warnings instead of raising errors, allowing the app to start with incomplete settings. | backend/app/main.py#L90 |
| `Rate Limiting @ backend/app/routers/chat.py:440` | Rate Limiting @ backend/app/routers/chat.py:440 | yes | The `enforce_chat_rate_limit` function limits chat turns per user to prevent abuse and cost overruns. | backend/app/routers/chat.py#L440 |

### Missed by inventory (2)
- `Async Context Manager Usage` @ backend/app/main.py#L90 — The `lifespan` async context manager ensures proper setup/teardown, but this pattern was not explicitly noted in initial observations.
- `Testing for Exhaustion Degradation` @ backend/tests/test_chat_router.py#L757 — Tests explicitly verify that exhaustion states are persisted to `usage_log`, but this was not captured in initial observations.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 62 | **false_pos** | [backend/app/llm.py#L1109](https://github.com/toddawhittaker/ipeds-oracle/blob/c5400992da91c9ffd0f1f687a8852126f43aefa6/backend/app/llm.py#L1109) |
| `C1|BARE|SIG` | C1 | 27 | **false_pos** | [backend/app/auth.py#L443](https://github.com/toddawhittaker/ipeds-oracle/blob/c5400992da91c9ffd0f1f687a8852126f43aefa6/backend/app/auth.py#L443) |
| `C1|BARE|PARAM` | C1 | 2 | **known** | [backend/app/routers/admin.py#L28](https://github.com/toddawhittaker/ipeds-oracle/blob/c5400992da91c9ffd0f1f687a8852126f43aefa6/backend/app/routers/admin.py#L28) |

## `C4|DEF` — **false_pos**
> occurrences here: 62 · corpus total: 56644 · executor: x86_64
> example: [backend/app/llm.py#L1109](https://github.com/toddawhittaker/ipeds-oracle/blob/c5400992da91c9ffd0f1f687a8852126f43aefa6/backend/app/llm.py#L1109)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 27 · corpus total: 83548 · executor: x86_64
> example: [backend/app/auth.py#L443](https://github.com/toddawhittaker/ipeds-oracle/blob/c5400992da91c9ffd0f1f687a8852126f43aefa6/backend/app/auth.py#L443)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C1|BARE|PARAM` — **known**
> occurrences here: 2 · corpus total: 18195 · executor: x86_64
> example: [backend/app/routers/admin.py#L28](https://github.com/toddawhittaker/ipeds-oracle/blob/c5400992da91c9ffd0f1f687a8852126f43aefa6/backend/app/routers/admin.py#L28)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

