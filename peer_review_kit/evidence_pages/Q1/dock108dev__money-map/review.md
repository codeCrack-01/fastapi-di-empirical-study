# dock108dev/money-map

- GitHub: https://github.com/dock108dev/money-map
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 105 · commit: `06a49440c4b9`
- Fingerprints touching this repo: 5
- Label mix: novel=0 variant=0 known=1 false_pos=4 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends injection` | src/paycheck_map/api.py#L67 | Multiple endpoints use Depends(get_session) to inject Session objects, e.g. 'session: Session = Depends(get_session)' in get_overview(), get_accounts(), and get_account_detail() |
| 2 | `Multiple dependency types` | src/paycheck_map/api_plaid.py#L68 | Endpoints use both Depends(get_session) for database sessions and Depends(get_secret_store) for secret management, showing multiple dependency injection points |
| 3 | `Custom dependency guards` | src/paycheck_map/api_plaid.py#L69 | credential_mutation_guard() is used as a dependency via Depends() to serialize credential changes, demonstrating custom dependency injection patterns |

## Pass 2 — reconcile with inventory of dock108dev/money-map

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`, `C3|CLASS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | known | **no (overturn)** | Standard FastAPI dependency injection via Depends(get_session) is valid and widely used in the codebase (e.g., get_overview(), get_accounts(), get_account_detail()) | src/paycheck_map/api.py#L67 |
| `C4|DEF` | known | **no (overturn)** | No evidence of invalid dependency definitions in the provided code excerpts; multiple dependency types (e.g., Depends(get_session), Depends(get_secret_store)) are explicitly used in api_plaid.py | src/paycheck_map/api_plaid.py#L68 |
| `C1|BARE|USED` | known | **no (overturn)** | Custom dependency guards (e.g., credential_mutation_guard()) are valid and explicitly used in api_plaid.py for credential management | src/paycheck_map/api_plaid.py#L69 |

### Missed by inventory (2)
- `Custom dependency guards with Depends()` @ src/paycheck_map/api_plaid.py#L69 — The inventory did not capture the use of custom dependency guards like credential_mutation_guard() which are explicitly used in route definitions
- `Multiple dependency injection points in single endpoint` @ src/paycheck_map/api_plaid.py#L82 — The inventory failed to recognize that endpoints can have multiple dependency injection points (e.g., Depends(get_session) + Depends(get_secret_store))

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 67 | **false_pos** | [src/paycheck_map/api.py#L67](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/api.py#L67) |
| `C4|DEF` | C4 | 28 | **false_pos** | [src/paycheck_map/adapters/canonical_ledger.py#L147](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/adapters/canonical_ledger.py#L147) |
| `C1|BARE|PARAM` | C1 | 7 | **known** | [src/paycheck_map/api_housing.py#L16](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/api_housing.py#L16) |
| `C4|USED` | C4 | 2 | **false_pos** | [src/paycheck_map/api_plaid.py#L55](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/api_plaid.py#L55) |
| `C3|CLASS|BARE` | C3 | 1 | **false_pos** | [src/paycheck_map/api_housing.py#L16](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/api_housing.py#L16) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 67 · corpus total: 83548 · executor: x86_64
> example: [src/paycheck_map/api.py#L67](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/api.py#L67)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 28 · corpus total: 56644 · executor: x86_64
> example: [src/paycheck_map/adapters/canonical_ledger.py#L147](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/adapters/canonical_ledger.py#L147)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 7 · corpus total: 18195 · executor: x86_64
> example: [src/paycheck_map/api_housing.py#L16](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/api_housing.py#L16)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 2 · corpus total: 1079 · executor: x86_64
> example: [src/paycheck_map/api_plaid.py#L55](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/api_plaid.py#L55)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 1 · corpus total: 20139 · executor: x86_64
> example: [src/paycheck_map/api_housing.py#L16](https://github.com/dock108dev/money-map/blob/06a49440c4b9b2c5586df414a9f4ef278d39afd7/src/paycheck_map/api_housing.py#L16)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

