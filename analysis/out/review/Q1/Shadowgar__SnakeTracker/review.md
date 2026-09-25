# Shadowgar/SnakeTracker

- GitHub: https://github.com/Shadowgar/SnakeTracker
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 5 · commit: `306f465623c5`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `Manual Dependency Construction` | src/snaketracker/bootstrap/application.py#L172 | Dependencies like SQLAlchemy repositories (SQLAlchemyHouseholdBootstrapRepository, SQLAlchemyIdentityRepository) and services (HouseholdBootstrapService) are instantiated directly within the build_... |
| 2 | `Lifespan Context Manager` | src/snaketracker/bootstrap/application.py#L172 | A custom lifespan context manager is defined and passed to create_application, which aligns with FastAPI's lifespan management pattern but does not involve dependency injection. |

## Pass 2 — reconcile with inventory of Shadowgar/SnakeTracker

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code examples (e.g., application.py:172) use manual lifespan context managers and direct dependency instantiation (e.g., SQLAlchemyHouseholdBootstrapRepository), which do not align with FastAPI... | src/snaketracker/bootstrap/application.py#L172 |

### Missed by inventory (2)
- `Manual dependency construction` @ src/snaketracker/bootstrap/application.py#L172 — The code instantiates dependencies (e.g., SQLAlchemyHouseholdBootstrapRepository) directly within build_application, which the static inventory may have failed to classify as a DI occurrence.
- `Custom lifespan context manager` @ src/snaketracker/bootstrap/application.py#L172 — The lifespan context manager is manually defined and passed to create_application, which the static inventory may not have recognized as part of FastAPI's DI system.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 5 | **false_pos** | [src/snaketracker/bootstrap/application.py#L172](https://github.com/Shadowgar/SnakeTracker/blob/306f465623c50f8a24513975fa85b2104d88d82d/src/snaketracker/bootstrap/application.py#L172) |

## `C4|DEF` — **false_pos**
> occurrences here: 5 · corpus total: 56644 · executor: x86_64
> example: [src/snaketracker/bootstrap/application.py#L172](https://github.com/Shadowgar/SnakeTracker/blob/306f465623c50f8a24513975fa85b2104d88d82d/src/snaketracker/bootstrap/application.py#L172)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

