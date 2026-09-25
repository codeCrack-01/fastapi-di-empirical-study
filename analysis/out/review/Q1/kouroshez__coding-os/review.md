# kouroshez/coding-os

- GitHub: https://github.com/kouroshez/coding-os
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 283 · commit: `0d6b09610473`
- Fingerprints touching this repo: 3
- Label mix: novel=0 variant=0 known=0 false_pos=3 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI dependency injection with Depends()` | src/core/web/routes/board.py#L157 | The function board_task_detail uses _rl=Depends(make_rate_limit_dep(...)) and _m=Depends(make_metrics_dep(...)) to inject rate-limiting and metrics dependencies via FastAPI's Depends() mechanism. T... |
| 2 | `Reusable dependency factories` | src/core/web/routes/board.py#L157 | make_rate_limit_dep and make_metrics_dep are called as factories to create specific instances of dependencies, which are then injected into route handlers through Depends(). This allows shared logi... |

## Pass 2 — reconcile with inventory of kouroshez/coding-os

_Presented fingerprints:_ `C1|BARE|SIG`, `C4|DEF`, `C4|USED`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C1|BARE|SIG` | false_pos | **no (overturn)** | The code explicitly uses FastAPI's Depends() for rate-limiting and metrics injection in route handlers (e.g., board_task_detail). This is a valid and correct usage pattern, contradicting the 'false... | src/core/web/routes/board.py#L157 |
| `C4|DEF` | false_pos | **no (overturn)** | The code demonstrates dependency factory usage (make_rate_limit_dep, make_metrics_dep) as reusable dependency creation patterns. These are valid definitions, contradicting the 'false_pos' label. | src/core/web/routes/board.py#L157 |
| `C4|USED` | false_pos | **no (overturn)** | The code repeatedly uses dependency factories (make_rate_limit_dep, make_metrics_dep) in route handlers, demonstrating valid dependency injection patterns. This contradicts the 'false_pos' label. | src/core/web/routes/board.py#L157 |

### Missed by inventory (2)
- `FastAPI dependency injection with Depends()` @ src/core/web/routes/board.py#L157 — The inventory likely missed the widespread use of Depends() in route handlers for rate-limiting and metrics, which is a core pattern in the codebase.
- `Reusable dependency factory patterns` @ src/core/web/routes/board.py#L157 — The inventory likely missed the use of make_rate_limit_dep and make_metrics_dep as factory functions for creating dependency instances.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C1|BARE|SIG` | C1 | 152 | **false_pos** | [src/core/web/routes/board.py#L156](https://github.com/kouroshez/coding-os/blob/0d6b096104733141fb956694b9c6a6a0ed7d036d/src/core/web/routes/board.py#L156) |
| `C4|DEF` | C4 | 130 | **false_pos** | [src/cli/pr_commands.py#L1856](https://github.com/kouroshez/coding-os/blob/0d6b096104733141fb956694b9c6a6a0ed7d036d/src/cli/pr_commands.py#L1856) |
| `C4|USED` | C4 | 1 | **false_pos** | [src/core/web/_deps.py#L42](https://github.com/kouroshez/coding-os/blob/0d6b096104733141fb956694b9c6a6a0ed7d036d/src/core/web/_deps.py#L42) |

## `C1|BARE|SIG` — **false_pos**
> occurrences here: 152 · corpus total: 83548 · executor: x86_64
> example: [src/core/web/routes/board.py#L156](https://github.com/kouroshez/coding-os/blob/0d6b096104733141fb956694b9c6a6a0ed7d036d/src/core/web/routes/board.py#L156)

> **evidence (model):** The examples show parameters named 'current_principal' in function signatures but no actual Depends() calls or DI wiring; the fingerprint incorrectly labels bare parameter names as C1 dependencies

## `C4|DEF` — **false_pos**
> occurrences here: 130 · corpus total: 56644 · executor: x86_64
> example: [src/cli/pr_commands.py#L1856](https://github.com/kouroshez/coding-os/blob/0d6b096104733141fb956694b9c6a6a0ed7d036d/src/cli/pr_commands.py#L1856)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C4|USED` — **false_pos**
> occurrences here: 1 · corpus total: 1079 · executor: x86_64
> example: [src/core/web/_deps.py#L42](https://github.com/kouroshez/coding-os/blob/0d6b096104733141fb956694b9c6a6a0ed7d036d/src/core/web/_deps.py#L42)
> **rule:** C1

> **evidence (model):** The examples show function names (get_db/_get_db) as dependencies, not generator/yield functions as required by C4

