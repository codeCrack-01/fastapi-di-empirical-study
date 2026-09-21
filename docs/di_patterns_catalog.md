# DI Patterns explored in the FastAPI literature

> Draft for a paper subsection defining the dependency-injection patterns this
> study explores. **Base patterns only** — derived/composite variants are
> intentionally excluded from the catalog below. Counts are from the 402-repo
> corpus (see `result_draft_01.md`).

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
corpus: 75.4% of repos, 25,166 call sites, 97.1% of which pass a plain bare
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
security scheme. Corpus finding: 10.4% of repos use it, and in the entire
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
a start/stop wrapper around the handler. Second-most common pattern: 40.3% of
repos, more than `Annotated` (25.9%).

## Community / Python-default idioms (derived, low-n)

Derived patterns build on the base ones; they are not unique base patterns
themselves and are excluded from the catalog above. Recorded for completeness
from the corpus (§6.2 of `result_draft_01.md`), all low-frequency:

| Idiom | Repos | Note |
|---|---|---|
| zero-DI / direct call | 98 (24.4%) | real apps that never invoke the DI system at all — the headline finding |
| `current_*` request-scope injection | 15 | request-scoped context objects injected via DI |
| class-as-dependency `Depends(MyClass)` | 7 | constructor-injected classes |
| module-alias deps `deps.get_x` | 11 | namespaced dependency getters |
| `provide_*` service-locator dialect | 1 | DIY service locator over DI |
| classmethod-as-dependency (`.as_form`) | 1 | Pydantic model doubling as a form-parsing dependency |

> Data-consistency note: unresolved-reference IQR is stated as 0–3.6% in the
> verified data (`result_draft_01.md` §7, q3 = 3.625), not the 0–3.4% that
> appeared in an earlier draft.