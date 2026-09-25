# PurpleAILAB/Decepticon

- GitHub: https://github.com/PurpleAILAB/Decepticon
- Stars: 5001 (covariates)
- Quadrant: Q4
- Stratum: S4 · DI nodes: 112 · commit: `31e1c8e786c8`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=1 known=1 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends-based authentication injection` | packages/decepticon/decepticon/sandbox_server/app.py#L296 | The code uses Depends(auth) in endpoint definitions (e.g., @app.post("/execute") def execute(..., _: Annotated[None, Depends(auth)]). This injects an authentication dependency into multiple endpoin... |
| 2 | `API key validation via Depends` | packages/decepticon/decepticon/skillogy/server/app.py#L112 | The code defines _require_key as a dependency function and uses Depends(_require_key) in route protection (_protected = [Depends(_require_key)]), demonstrating DI for API key validation. |

## Pass 2 — reconcile with inventory of PurpleAILAB/Decepticon

_Presented fingerprints:_ `C4|DEF`, `C3|ELLIPSIS|BARE`, `C1|BARE|PARAM`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true | **no (overturn)** | The code explicitly uses Depends(auth) in multiple endpoints (e.g., @app.post("/execute") def execute(..., _: Annotated[None, Depends(auth)]), which is a valid DI occurrence, not a false positive. | packages/decepticon/decepticon/sandbox_server/app.py#L296 |
| `C3|ELLIPSIS|BARE` | variant | yes | The code uses Annotated[None, Depends(auth)] in parameter definitions, which aligns with the "variant" label as a specific DI pattern variation. | packages/decepticon/decepticon/sandbox_server/app.py#L296 |
| `C1|BARE|PARAM` | known | yes | The code uses Depends(auth) in parameter definitions (e.g., _: Annotated[None, Depends(auth)]), which matches the "known" label for established DI patterns. | packages/decepticon/decepticon/sandbox_server/app.py#L296 |

### Missed by inventory (1)
- `Depends-based API key validation` @ packages/decepticon/decepticon/skillogy/server/app.py#L112 — The code defines _require_key as a dependency function and uses Depends(_require_key) for route protection, which is a DI occurrence not captured by the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 78 | **false_pos** | [benchmark/providers/exploitbench.py#L751](https://github.com/PurpleAILAB/Decepticon/blob/31e1c8e786c83bb20f5c3d9ebc482cf9fb8ffa06/benchmark/providers/exploitbench.py#L751) |
| `C3|ELLIPSIS|BARE` | C3 | 22 | **variant** | [packages/decepticon/decepticon/sandbox_server/app.py#L296](https://github.com/PurpleAILAB/Decepticon/blob/31e1c8e786c83bb20f5c3d9ebc482cf9fb8ffa06/packages/decepticon/decepticon/sandbox_server/app.py#L296) |
| `C1|BARE|PARAM` | C1 | 12 | **known** | [packages/decepticon/decepticon/sandbox_server/app.py#L296](https://github.com/PurpleAILAB/Decepticon/blob/31e1c8e786c83bb20f5c3d9ebc482cf9fb8ffa06/packages/decepticon/decepticon/sandbox_server/app.py#L296) |

## `C4|DEF` — **false_pos**
> occurrences here: 78 · corpus total: 56644 · executor: x86_64
> example: [benchmark/providers/exploitbench.py#L751](https://github.com/PurpleAILAB/Decepticon/blob/31e1c8e786c83bb20f5c3d9ebc482cf9fb8ffa06/benchmark/providers/exploitbench.py#L751)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 22 · corpus total: 1113 · executor: x86_64
> example: [packages/decepticon/decepticon/sandbox_server/app.py#L296](https://github.com/PurpleAILAB/Decepticon/blob/31e1c8e786c83bb20f5c3d9ebc482cf9fb8ffa06/packages/decepticon/decepticon/sandbox_server/app.py#L296)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

## `C1|BARE|PARAM` — **known**
> occurrences here: 12 · corpus total: 18195 · executor: x86_64
> example: [packages/decepticon/decepticon/sandbox_server/app.py#L296](https://github.com/PurpleAILAB/Decepticon/blob/31e1c8e786c83bb20f5c3d9ebc482cf9fb8ffa06/packages/decepticon/decepticon/sandbox_server/app.py#L296)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

