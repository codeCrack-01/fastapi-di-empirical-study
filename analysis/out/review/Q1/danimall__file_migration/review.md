# danimall/file_migration

- GitHub: https://github.com/danimall/file_migration
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 13 · commit: `15cda8d33161`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Manual Dependency Injection via App State` | src/filemig/app.py#L30 | The MigrationService is instantiated directly and stored in app.state.service, bypassing FastAPI's Depends() system. This is evident in the code: 'service = MigrationService(settings); app.state.se... |
| 2 | `Test Fixture Manual Injection` | tests/test_service_e2e.py#L110 | The test fixture 'service' manually injects fake dependencies (FakeDropbox, FakeDrive) into MigrationService: 'svc.dropbox = FakeDropbox(files); svc.drive = FakeDrive()'. |

## Pass 2 — reconcile with inventory of danimall/file_migration

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code explicitly uses manual DI via app.state.service, contradicting the false_pos label. | src/filemig/app.py#L30 |

### Missed by inventory (1)
- `Test fixture manual dependency injection` @ tests/test_service_e2e.py#L110 — The test fixture directly assigns fake dependencies (FakeDropbox, FakeDrive) to MigrationService instance properties, representing a DI occurrence not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 13 | **false_pos** | [src/filemig/app.py#L30](https://github.com/danimall/file_migration/blob/15cda8d3316131e827d0760c0effe486f7eccdd0/src/filemig/app.py#L30) |

## `C4|DEF` — **false_pos**
> occurrences here: 13 · corpus total: 56644 · executor: x86_64
> example: [src/filemig/app.py#L30](https://github.com/danimall/file_migration/blob/15cda8d3316131e827d0760c0effe486f7eccdd0/src/filemig/app.py#L30)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

