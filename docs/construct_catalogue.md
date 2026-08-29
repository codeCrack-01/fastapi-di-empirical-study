# FastAPI DI Construct Catalogue

Canonical construct definitions for the study. **IDs are the operationalized IDs
used throughout `result_draft_01.md`, `analysis/aggregate.py`, and the slides.**
This table was renumbered on 2026-08-29 to eliminate the earlier ID collision
between this catalogue and the measured results (see "Operationalization status").

| ID | Construct | Example | Measured? |
|---|---|---|---|
| C1 | Depends | `Depends(get_db)` | Yes |
| C2 | Security | `Security(get_user)` | Yes |
| C3 | Annotated dependency | `Annotated[User, Depends(...)]` | Yes |
| C4 | Generator dependency | yield inside dependency | Yes |
| C5 | Router dependency | `APIRouter(dependencies=...)` | Yes |
| C6 | App dependency | `FastAPI(dependencies=...)` | Yes |
| C7 | Dependency override | `app.dependency_overrides[...]` | Yes |
| C8 | Callable class dependency | `Depends(MyDependency())` | Yes |
| C9 | Nested dependency | dependency depending on another dependency | **No — captured at graph level (RQ2), see below** |
| C10 | Parameterized dependency | factory-generated dependency | **No — deferred** |

## Operationalization status

The catalogue originally defined ten candidate constructs. **Eight (C1–C8) are
operationalized** as per-repo prevalence counters in the extractor
(`analysis/aggregate.py` `CONSTRUCTS`) and reported in `result_draft_01.md` §5.
This is the single canonical numbering: C1–C8 in this table match the C1–C8
reported in the results.

Two constructs are **not** operationalized. This is a deliberate, documented
decision, stated so the gap is visible rather than silent:

- **C9 — Nested dependency.** A nested dependency is not a distinct syntactic
  construct but a *graph-topological property*: a dependency that is itself the
  target of another dependency, i.e. a graph node with both an incoming and an
  outgoing edge. It is therefore captured by the dependency-graph analysis (RQ2)
  rather than as a per-repo syntactic counter — its effects appear in the
  measured graph metrics (median depth, fan-out hubs) rather than as a
  construct-prevalence percentage.
- **C10 — Parameterized dependency.** Marked "Maybe detectable" in the original
  catalogue. Factory-generated dependencies are not statically decidable from a
  call site in general, so counting them reliably would risk false positives. It
  is deferred; any future temporal/graph phase (RQ3) would reassess it.

No repository was asked or expected to exhibit every construct; prevalence is
reported per construct among the repos that use it.
