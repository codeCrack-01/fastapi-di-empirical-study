# Kirov-Dynamics-Technology/kirov-secure-api-gateway

- GitHub: https://github.com/Kirov-Dynamics-Technology/kirov-secure-api-gateway
- Stars: 1 (covariates)
- Quadrant: Q2
- Stratum: S2 · DI nodes: 2 · commit: `4ad255b5451e`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Non-standard use of Depends in parameter defaults` | server/middleware/auth.py#L16 | The function verify_jwt uses Depends(bearer_scheme) as the default value for the credentials parameter, which is unconventional. FastAPI typically uses Depends as a type hint rather than in default... |
| 2 | `Repeated non-standard DI pattern` | server/middleware/auth.py#L73 | The verify_service_token function replicates the same non-standard pattern as verify_jwt, using Depends(bearer_scheme) in the credentials parameter's default value. |

## Pass 2 — reconcile with inventory of Kirov-Dynamics-Technology/kirov-secure-api-gateway

_Presented fingerprints:_ `C1|BARE|SIG`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The code explicitly uses dependency injection via Depends(bearer_scheme) in both functions, even though the pattern is unconventional. This constitutes valid DI, contradicting the 'false_pos' label. | server/middleware/auth.py#L16 |
| `C1|BARE|SIG` | true_pos | **no (overturn)** | The verify_service_token function also uses Depends(bearer_scheme) in a non-standard way, confirming valid DI usage that should not be labeled as false positives. | server/middleware/auth.py#L73 |

### Missed by inventory (2)
- `Non-standard DI pattern: using Depends() in parameter defaults` @ server/middleware/auth.py#L16 — The inventory did not account for this unconventional DI pattern, which is functionally equivalent to standard DI but syntactically divergent.
- `Repeated non-standard DI pattern` @ server/middleware/auth.py#L73 — The inventory missed this second occurrence of the same non-standard DI pattern, which reinforces the presence of a valid but unconventional DI practice.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 2 | **false_pos** | [server/middleware/auth.py#L16](https://github.com/Kirov-Dynamics-Technology/kirov-secure-api-gateway/blob/4ad255b5451ea78b977e468fd23f51de474bfb64/server/middleware/auth.py#L16) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 2 · corpus total: 83548 · executor: x86_64
> example: [server/middleware/auth.py#L16](https://github.com/Kirov-Dynamics-Technology/kirov-secure-api-gateway/blob/4ad255b5451ea78b977e468fd23f51de474bfb64/server/middleware/auth.py#L16)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

