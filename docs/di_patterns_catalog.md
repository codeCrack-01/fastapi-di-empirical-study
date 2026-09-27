# DI Patterns explored in the FastAPI literature

> **SUPERSEDED IN PART (2026-09-28).** This document predates the retirement of
> the LLM strategy-attribution census. That census assigned S1-S4 to all 2,179
> repositories using `qwen3:14b`; it matched the deterministic extractor on only
> **56.4%** of repositories, and inspection showed the evidence packs it read
> contained a real `Depends` call in just **8%** of cases -- the token `settings`
> in the pack builder's keyword vocabulary matched benign configuration
> identifiers and consumed 63% of all excerpt slots. Its strategy counts
> (S1 1,188 / S2 712 / S3 268 / S4 11) are **withdrawn** and appear below only
> as a record of prior belief. The 327-repository peer review that was built to
> validate them is also retired and has been deleted.
>
> Still valid: any figure described as **construct presence** (does the extractor
> find `Depends`/`Security`/`Annotated` call sites), which is a statement about
> the extractor's output rather than about a repository's dominant strategy.
> **Not valid:** any statement that a strategy population has a known share.
> Manual (S3) and external (S4) strategy prevalence is currently *unquantified*.
>
> Authoritative replacement: `docs/audit_preregistration.md`
> (branch `prereg/census-validation`, commit `670af3b`).

> Draft for a paper subsection defining the dependency-injection patterns this
> study explores. **Base patterns only** — derived/composite variants are
> intentionally excluded from the catalog below. Counts are from the 2,179-repo
> census (see `result_draft_01.md`).

## Constructs are mutually swappable

The four base patterns below are **mutually swappable spellings of a single
FastAPI injection mechanism**: re-expressing a dependency in a different
construct does not change its behavior, so C1–C4 form an interchangeable set.

| Pair | Swap type | Why |
|---|---|---|
| C1 ⇄ C3 | full swap | same resolution; only annotation-vs-default-value spelling differs |
| C1 ⇄ C2 | full swap in practice | `Security()` without scopes resolves identically to `Depends()`; the census shows 0/620 calls pass `scopes`, so in the wild C2 is a labeled C1 |
| C1/C3 ⇄ C4 | call-site swap | a yield-dependency is still consumed via `Depends(...)`/`Annotated[...]`; only the provider's definition form differs (adds setup/teardown) |

The swappable-pattern catalog (`analysis/swappable/out/catalog.json`;
1,142 swap instances, 933 of them pure `C1|C3`) operationalizes the claim at the
provider level: a provider written in two or more constructs within one repo is
an *observed swap instance*. This interchangeability is also the premise of the
S2-strategy renders in `experiment_proposal.md` §3.1, which re-write real
dependencies across construct forms without changing behavior.

## Base patterns

### 1. `Depends(fn)` — bare function reference

The baseline construct. A handler declares a parameter whose value comes from
calling `fn()`. FastAPI resolves the call and injects the return value before
invoking the handler.

```python
def get_db():
    return DBSession()

@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

**Differs from others:** has no scope, type, or lifecycle metadata of its own —
it is the raw mechanism every other pattern builds on. Most common in the
corpus: 62.9% of repos, 98,243 call sites, 96.6% of which pass a plain bare
function reference.

### 2. `Annotated[T, Depends(fn)]` — typed injection

Declares the dependency inside the parameter's *type annotation* rather than
its default value. The declared type stays visible to the type checker *and* to
FastAPI's request validation.

```python
def get_current_user() -> User:
    ...

@app.get("/me")
def me(current: Annotated[User, Depends(get_current_user)]):
    return current
```

**Differs from others:** the metadata lives in the annotation, not the default
value, so the parameter type remains explicit; the parameter itself keeps no
runnable default. FastAPI's docs (v0.95+) prefer this form. Present in 25.9%
of repos.

### 3. `Security(fn[, scopes=...])` — auth/authz injection

Uses the same resolver as `Depends(fn)` but is semantically restricted to
authentication and authorization schemes, and is advertised to FastAPI's
OpenAPI security scheme.

```python
def require_user(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> User:
    ...

@app.get("/protected")
def protected(user: User = Security(require_user)):
    return user
```

**Differs from others:** identical injection mechanism to `Depends(fn)`; the
distinction is *documentational and semantic* — it marks the dependency as a
security scheme. Corpus finding: 4.8% of repos use it, and in the entire
corpus **no call site passes `scopes=[...]`**, so it is used purely as an
auth/authz gate, never with the advertised fine-grained scopes.

### 4. Generator / yield — lifecycle dependency

A dependency implemented as a generator. Code before the `yield` runs before
the handler; code after it runs after the response completes — a natural fit
for resource setup/teardown (DB sessions, client connections).

```python
def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

**Differs from others:** the only base pattern with a *scope/lifetime*. Whereas
`Depends(fn)` is fire-and-return, the `yield` boundary turns the dependency into
a start/stop wrapper around the handler. Second-most common pattern: 34.8% of
repos, more than `Annotated` (17.6%).

## Community / Python-default idioms (derived, low-n)

Derived patterns build on the base ones; they are not unique base patterns
themselves and are excluded from the catalog above. Recorded for completeness
from the corpus (§6.2 of `result_draft_01.md`), all low-frequency:

| Idiom | Repos | Note |
|---|---|---|
| zero-DI / direct call | 805 (36.9%) | real apps that never invoke the DI system at all — the headline finding *(construct-presence: no `Depends`/`Security`/`Annotated` call site detected. This is **not** the S1 strategy population — the retired strategy-attribution census that supplied that number disagreed with the extractor on 56.4% of repositories and has been withdrawn; see `methodology_journal.md` §3.2. How much undetected DI hides in this cohort is bounded by the pre-registered audit in `docs/audit_preregistration.md`.)* |
| `current_*` request-scope injection | 76 | request-scoped context objects injected via DI |
| class-as-dependency `Depends(MyClass)` | 28 | constructor-injected classes (38 distinct classes) |
| module-alias deps `deps.get_x` | 54 | namespaced dependency getters |
| `provide_*` service-locator dialect | 3 | DIY service locator over DI |
| classmethod-as-dependency (`.as_form`) | 6 | Pydantic models doubling as form-parsing dependencies |

> Data-consistency note: unresolved-reference IQR is stated as 0–3.6% in the
> verified data (`result_draft_01.md` §7, q3 = 3.625), not the 0–3.4% that
> appeared in an earlier draft.