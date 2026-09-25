# MSKazemi/kubeintellect

- GitHub: https://github.com/MSKazemi/kubeintellect
- Stars: 5 (covariates)
- Quadrant: Q3
- Stratum: S2 · DI nodes: 191 · commit: `275e41d9c23d`
- Fingerprints touching this repo: 2
- Label mix: novel=0 variant=0 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of MSKazemi/kubeintellect

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `protocol_handshake` | protocol_handshake | yes | Code correctly implements SSE protocol handshake with version and session_id in first frame | v2/app/api/v1/endpoints/chat_completions.py#L24 |
| `stream_termination` | stream_termination | yes | Code explicitly sends [DONE] sentinel at stream end matching test expectations | v2/app/api/v1/endpoints/chat_completions.py#L24 |
| `event_replay` | event_replay | yes | Replay endpoint correctly streams stored history events followed by [DONE] | v2/app/api/v1/endpoints/events.py#L15 |
| `content_type_validation` | content_type_validation | yes | Code sets text/event-stream content type as tests verify | v2/app/api/v1/endpoints/chat_completions.py#L24 |

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 190 | **false_pos** | [deploy/huggingface-space/app.py#L163](https://github.com/MSKazemi/kubeintellect/blob/275e41d9c23d85e375019ab8a366677d192e871c/deploy/huggingface-space/app.py#L163) |
| `C1|BARE|PARAM` | C1 | 1 | **known** | [v4/packages/kubeintellect-server/app/api/v1/router.py#L47](https://github.com/MSKazemi/kubeintellect/blob/275e41d9c23d85e375019ab8a366677d192e871c/v4/packages/kubeintellect-server/app/api/v1/router.py#L47) |

## `C4|DEF` — **false_pos**
> occurrences here: 190 · corpus total: 56644 · executor: x86_64
> example: [deploy/huggingface-space/app.py#L163](https://github.com/MSKazemi/kubeintellect/blob/275e41d9c23d85e375019ab8a366677d192e871c/deploy/huggingface-space/app.py#L163)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 1 · corpus total: 18195 · executor: x86_64
> example: [v4/packages/kubeintellect-server/app/api/v1/router.py#L47](https://github.com/MSKazemi/kubeintellect/blob/275e41d9c23d85e375019ab8a366677d192e871c/v4/packages/kubeintellect-server/app/api/v1/router.py#L47)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

