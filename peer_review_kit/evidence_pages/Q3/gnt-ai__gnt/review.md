# gnt-ai/gnt

- GitHub: https://github.com/gnt-ai/gnt
- Stars: 10 (covariates)
- Quadrant: Q3
- Stratum: S3 · DI nodes: 158 · commit: `59a743d144ce`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=0 known=1 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Best-effort error handling` | apps/api/src/gnt/routers/github.py#L152 | The code uses a try-except block around uninstall_app(installation_id) with a bare pass, which is a best-effort approach. This could leave the system in an inconsistent state if uninstallation fail... |
| 2 | `State parameter verification` | apps/api/src/gnt/routers/github.py#L182 | The code generates a state parameter bound to org.org_id and user_id, which is used in the install URL. This is a common practice in OAuth flows to prevent CSRF attacks, and the comment references ... |
| 3 | `HMAC signature verification` | apps/api/src/gnt/routers/github_webhook.py#L61 | The webhook handler uses HMAC with SHA256 to verify the signature of incoming requests, which is standard for GitHub webhooks. This ensures the request is from GitHub and not a spoofed request. |
| 4 | `Single connection per org` | apps/api/src/gnt/routers/github.py#L152 | The code assumes a single installation_id per org, and uninstalling once revokes access to all connected rows. This is a design choice to avoid redundant uninstall calls, as noted in the comment. |

## Pass 2 — reconcile with inventory of gnt-ai/gnt

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C1|BARE|PARAM`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `github_uninstall_best_effort` | best-effort uninstallation | yes | The code correctly implements a best-effort uninstallation strategy with a try-except block, as documented in the comment. This aligns with the design choice to prioritize deleting database rows fo... | apps/api/src/gnt/routers/github.py#L152 |
| `github_state_verification` | state parameter verification | yes | The code properly generates and verifies the state parameter bound to org.org_id and user_id, as referenced in app_auth.verify_install_state. This prevents CSRF attacks and ensures callback trust. | apps/api/src/gnt/routers/github.py#L182 |
| `github_webhook_hmac` | HMAC signature verification | yes | The webhook handler correctly uses HMAC with SHA256 to verify GitHub signatures, ensuring request authenticity. This matches standard GitHub webhook practices. | apps/api/src/gnt/routers/github_webhook.py#L61 |
| `single_installation_per_org` | single installation_id per org | yes | The code assumes a single installation_id per org, which is explicitly documented. This design choice avoids redundant uninstall calls and aligns with the comment's explanation. | apps/api/src/gnt/routers/github.py#L152 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 139 | **false_pos** | [apps/api/src/gnt/auth/better_auth.py#L80](https://github.com/gnt-ai/gnt/blob/59a743d144cef01c4deb1354e97b06013f6ebe3d/apps/api/src/gnt/auth/better_auth.py#L80) |
| `C4|DEF` | C4 | 17 | **false_pos** | [apps/api/src/gnt/db/session.py#L24](https://github.com/gnt-ai/gnt/blob/59a743d144cef01c4deb1354e97b06013f6ebe3d/apps/api/src/gnt/db/session.py#L24) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [apps/api/src/gnt/routers/webhooks.py#L29](https://github.com/gnt-ai/gnt/blob/59a743d144cef01c4deb1354e97b06013f6ebe3d/apps/api/src/gnt/routers/webhooks.py#L29) |
| `C4|USED` | C4 | 1 | **false_pos** | [apps/api/src/gnt/db/session.py#L19](https://github.com/gnt-ai/gnt/blob/59a743d144cef01c4deb1354e97b06013f6ebe3d/apps/api/src/gnt/db/session.py#L19) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 139 · corpus total: 83548 · executor: x86_64
> example: [apps/api/src/gnt/auth/better_auth.py#L80](https://github.com/gnt-ai/gnt/blob/59a743d144cef01c4deb1354e97b06013f6ebe3d/apps/api/src/gnt/auth/better_auth.py#L80)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 17 · corpus total: 56644 · executor: x86_64
> example: [apps/api/src/gnt/db/session.py#L24](https://github.com/gnt-ai/gnt/blob/59a743d144cef01c4deb1354e97b06013f6ebe3d/apps/api/src/gnt/db/session.py#L24)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [apps/api/src/gnt/routers/webhooks.py#L29](https://github.com/gnt-ai/gnt/blob/59a743d144cef01c4deb1354e97b06013f6ebe3d/apps/api/src/gnt/routers/webhooks.py#L29)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [apps/api/src/gnt/db/session.py#L19](https://github.com/gnt-ai/gnt/blob/59a743d144cef01c4deb1354e97b06013f6ebe3d/apps/api/src/gnt/db/session.py#L19)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

