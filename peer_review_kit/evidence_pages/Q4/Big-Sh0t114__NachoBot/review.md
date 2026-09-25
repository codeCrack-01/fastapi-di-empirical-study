# Big-Sh0t114/NachoBot

- GitHub: https://github.com/Big-Sh0t114/NachoBot
- Stars: 197 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 29 · commit: `f86df60d74c7`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of Big-Sh0t114/NachoBot

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | false_pos | **no (overturn)** | The code correctly implements error handling and async context managers, contradicting the 'false_pos' label. | NachoBot-Multimodal-Adapter/src/tts/backends/Vox/tts_model.py#L238 |

### Missed by inventory (1)
- `async context managers with proper error handling` @ NachoBot-Multimodal-Adapter/src/tts/backends/Vox/tts_model.py#L238 — The inventory may have missed patterns related to robust async error handling in HTTP clients.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 29 | **false_pos** | [NachoBot-Multimodal-Adapter/src/tts/backends/Vox/tts_model.py#L238](https://github.com/Big-Sh0t114/NachoBot/blob/f86df60d74c71d94c3505b6f20a7d35fe9af3373/NachoBot-Multimodal-Adapter/src/tts/backends/Vox/tts_model.py#L238) |

## `C4|DEF` — **false_pos**
> occurrences here: 29 · corpus total: 56644 · executor: x86_64
> example: [NachoBot-Multimodal-Adapter/src/tts/backends/Vox/tts_model.py#L238](https://github.com/Big-Sh0t114/NachoBot/blob/f86df60d74c71d94c3505b6f20a7d35fe9af3373/NachoBot-Multimodal-Adapter/src/tts/backends/Vox/tts_model.py#L238)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

