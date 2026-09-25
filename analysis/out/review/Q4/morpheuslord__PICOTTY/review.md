# morpheuslord/PICOTTY

- GitHub: https://github.com/morpheuslord/PICOTTY
- Stars: 59 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 8 · commit: `f1d7d8f6aed8`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of morpheuslord/PICOTTY

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | yes | The code examples correctly implement async/await and async generators without issues, confirming the label as accurate. | firmware/tools/testhub.py#L504 |

### Missed by inventory (1)
- `async generator usage in db module` @ hub/src/picotty/hub/db.py#L339 — The inventory may have missed async generator patterns in the database module, such as `iter_output_text` and `iter_output_window`.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 8 | **false_pos** | [firmware/tools/testhub.py#L504](https://github.com/morpheuslord/PICOTTY/blob/f1d7d8f6aed81005fdf415cfc4c706b993d5a364/firmware/tools/testhub.py#L504) |

## `C4|DEF` — **false_pos**
> occurrences here: 8 · corpus total: 56644 · executor: x86_64
> example: [firmware/tools/testhub.py#L504](https://github.com/morpheuslord/PICOTTY/blob/f1d7d8f6aed81005fdf415cfc4c706b993d5a364/firmware/tools/testhub.py#L504)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

