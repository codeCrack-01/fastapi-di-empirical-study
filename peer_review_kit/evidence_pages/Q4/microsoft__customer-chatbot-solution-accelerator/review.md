# microsoft/customer-chatbot-solution-accelerator

- GitHub: https://github.com/microsoft/customer-chatbot-solution-accelerator
- Stars: 46 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 26 · commit: `cb86d1153df3`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=0 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends for authentication` | chat-app/backend/app/routers/chat.py#L89 | The `get_chat_sessions` endpoint uses `Depends(get_current_user_optional)` to inject authentication logic, which is a standard FastAPI dependency injection pattern for handling user authentication. |
| 2 | `FastAPI Depends for authentication` | scenario-app/backend/app/routers/auth.py#L102 | The `logout` endpoint uses `Depends(get_current_user)` to inject the current user, demonstrating FastAPI's dependency injection for authentication. |
| 3 | `FastAPI Depends for authentication` | scenario-app/backend/app/routers/banking_transactions.py#L12 | The `get_transactions` endpoint uses `Depends(get_current_user)` to inject authentication, showing a consistent pattern across multiple routers. |

## Pass 2 — reconcile with inventory of microsoft/customer-chatbot-solution-accelerator

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses FastAPI's `Depends()` for authentication injection in endpoints like `get_chat_sessions` (chat.py:L89), which aligns with canonical DI patterns. | chat-app/backend/app/routers/chat.py#L89 |
| `C4|DEF` | false_pos | yes | The test code in `conftest.py` uses pytest fixtures and Playwright, not FastAPI's `Depends()` for DI. No DI occurrences are present here. | tests/e2e-test/tests/conftest.py#L18 |

### Missed by inventory (2)
- `FastAPI Depends for authentication` @ scenario-app/backend/app/routers/auth.py#L102 — The `logout` endpoint uses `Depends(get_current_user)` for authentication, a valid DI occurrence missed by the inventory.
- `FastAPI Depends for authentication` @ scenario-app/backend/app/routers/banking_transactions.py#L12 — The `get_transactions` endpoint uses `Depends(get_current_user)` for authentication, another valid DI occurrence missed by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 24 | **false_pos** | [chat-app/backend/app/routers/chat.py#L89](https://github.com/microsoft/customer-chatbot-solution-accelerator/blob/cb86d1153df30a1bc6e744d74d3ff583764cd154/chat-app/backend/app/routers/chat.py#L89) |
| `C4|DEF` | C4 | 2 | **false_pos** | [tests/e2e-test/tests/conftest.py#L18](https://github.com/microsoft/customer-chatbot-solution-accelerator/blob/cb86d1153df30a1bc6e744d74d3ff583764cd154/tests/e2e-test/tests/conftest.py#L18) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 24 · corpus total: 83548 · executor: x86_64
> example: [chat-app/backend/app/routers/chat.py#L89](https://github.com/microsoft/customer-chatbot-solution-accelerator/blob/cb86d1153df30a1bc6e744d74d3ff583764cd154/chat-app/backend/app/routers/chat.py#L89)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 2 · corpus total: 56644 · executor: x86_64
> example: [tests/e2e-test/tests/conftest.py#L18](https://github.com/microsoft/customer-chatbot-solution-accelerator/blob/cb86d1153df30a1bc6e744d74d3ff583764cd154/tests/e2e-test/tests/conftest.py#L18)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

