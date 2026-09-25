# coinbase/cdp-sdk

- GitHub: https://github.com/coinbase/cdp-sdk
- Stars: 191 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 10 · commit: `193fab819ea9`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of coinbase/cdp-sdk

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | All instances are in test files using standard mocking patterns for unit testing (e.g., patching API calls, mocking responses). These are legitimate test constructs, not actual DI issues. | python/cdp/test/test_cdp_api_client_public_operations.py#L12 |

### Missed by inventory (3)
- `Global mock for analytics.send_event` @ python/conftest.py#L11 — A global mock for analytics events is present but not captured in the initial inventory.
- `Mocking auth headers in network error tests` @ python/cdp/test/test_network_errors.py#L27 — A mock for auth headers is present but not captured in the initial inventory.
- `CDP client fixture with base_path configuration` @ python/cdp/test/test_e2e.py#L120 — A fixture creating and configuring a CDP client is present but not captured in the initial inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 10 | **false_pos** | [python/cdp/test/test_cdp_api_client_public_operations.py#L12](https://github.com/coinbase/cdp-sdk/blob/193fab819ea966b47cde3724a34ed5ea513f0a4d/python/cdp/test/test_cdp_api_client_public_operations.py#L12) |

## `C4|DEF` — **false_pos**
> occurrences here: 10 · corpus total: 56644 · executor: x86_64
> example: [python/cdp/test/test_cdp_api_client_public_operations.py#L12](https://github.com/coinbase/cdp-sdk/blob/193fab819ea966b47cde3724a34ed5ea513f0a4d/python/cdp/test/test_cdp_api_client_public_operations.py#L12)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

