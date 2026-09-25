# 404GamerNotFound/TBC-camera-manager

- GitHub: https://github.com/404GamerNotFound/TBC-camera-manager
- Stars: 28 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 6 · commit: `20e3419ca543`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of 404GamerNotFound/TBC-camera-manager

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The cited code excerpts do not show clear DI patterns that would warrant a true positive. The database connection setup, lifespan management, and WebDAV handling appear to be standard implementatio... | app/tbc/webdav_client.py#L85 |

### Missed by inventory (1)
- `asynccontextmanager usage in test setup` @ tests/test_mcp_server.py#L64 — The test code uses asynccontextmanager for lifespan management, which could be a DI-related pattern but was not captured in the initial inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 6 | **false_pos** | [app/tbc/database.py#L717](https://github.com/404GamerNotFound/TBC-camera-manager/blob/20e3419ca54357a31d0c5f677b54f78888d419a8/app/tbc/database.py#L717) |

## `C4|DEF` — **false_pos**
> occurrences here: 6 · corpus total: 56644 · executor: x86_64
> example: [app/tbc/database.py#L717](https://github.com/404GamerNotFound/TBC-camera-manager/blob/20e3419ca54357a31d0c5f677b54f78888d419a8/app/tbc/database.py#L717)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

