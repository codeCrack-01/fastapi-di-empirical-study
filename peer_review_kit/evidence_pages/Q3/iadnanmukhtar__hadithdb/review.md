# iadnanmukhtar/hadithdb

- GitHub: https://github.com/iadnanmukhtar/hadithdb
- Stars: 6 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 4 · commit: `c9e730fb1352`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of iadnanmukhtar/hadithdb

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code at services/chatkit/app.py:62 contains explicit instructions for an AI agent, which aligns with the structural fingerprint of directive instructions (C4|DEF). The panel's label of 'false_p... | services/chatkit/app.py#L62 |

### Missed by inventory (1)
- `System prompt encoding for AI agents` @ services/chatkit/app.py#L62 — The initial inventory did not capture the explicit instruction block in the LibraryChat.respond method as a DI occurrence, despite its clear directive language.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 4 | **false_pos** | [services/chatkit/app.py#L62](https://github.com/iadnanmukhtar/hadithdb/blob/c9e730fb13527290890424a7006e46283dcfd3be/services/chatkit/app.py#L62) |

## `C4|DEF` — **false_pos**
> occurrences here: 4 · corpus total: 56644 · executor: x86_64
> example: [services/chatkit/app.py#L62](https://github.com/iadnanmukhtar/hadithdb/blob/c9e730fb13527290890424a7006e46283dcfd3be/services/chatkit/app.py#L62)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

