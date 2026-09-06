# RQ2 — usage & dynamic relationships (mixed methods)

- **Corpus:** 402 accepted repos (census).

- **Depends() call sites (production):** 25166 across 303 repos; 4 argument-shape categories


## Tier A — quantitative facets

### Depends() argument shapes

| Shape | Calls | % calls | Repos |
|---|---|---|---|
| bare function | 24444 | 97.1% | 297 |
| placeholder | 429 | 1.7% | 27 |
| module alias (mod.x) | 266 | 1.1% | 11 |
| title-case class | 21 | 0.1% | 7 |
| classmethod (Cls.meth) | 6 | 0.0% | 1 |

### Security() OAuth2 scopes

- **163** `Security()` call sites across **42** repos; **0 (0.0%)** pass `scopes=[...]` (0.0% of Security-using repos). The OAuth2 scopes feature is effectively unadopted.

### Dependency-graph relationship topology

- **294/402** repos have a non-empty graph; 16494 function nodes + 728 class nodes; 23223 directed edges.

- **227** fan-in hub nodes with >=10 dependents. Top hubs: get_db (4683), get_session (1732), get_current_user (1471), require_admin (1175), require_user (635), get_db_session (537), get_current_active_user (463), require_role (454).

- Median graph depth 2.0, max 7; **114** repos have any unresolved dependency.


### Annotated[...] type-role frequencies (top)

| Type | Calls | Repos |
|---|---|---|
| User | 749 | 19 |
| AsyncSession | 616 | 26 |
| str | 458 | 21 |
| Session | 355 | 19 |
| Principal | 235 | 7 |
| UserPrincipal | 180 | 1 |
| ... | 169 | 36 |
| Settings | 142 | 19 |
| AuditSink | 142 | 1 |
| AuthIdentity | 98 | 1 |
| Any | 93 | 5 |
| CurrentAdminUser | 76 | 1 |

## Tier B — qualitative idiom catalog (low n, not statistical)

| Idiom | Repos | Evidence |
|---|---|---|
| classmethod-as-dependency (`.as_form`/`.as_dependency`) | 1 | .as_form |
| class-as-dependency (`Depends(MyClass)`) | 14 distinct classes / 7 repos | API_KEY_HEADER, AttachmentRepo, AttachmentService, AttachmentStore, HTTPBearer, ImageRepo, ImageService, ImageStore ... |
| `provide_*` service-locator dialect | 1 repos | provider namespace |
| `current_*` context/request-scope injection | 15 repos | context objects |
| `*Repository`-typed injection | 0 repos | repository pattern |
| module-alias dependencies (`mod.dep`) | 11 repos | namespaced deps |

**Caveat (honest reporting):** Tier B idioms have very low counts and are reported as *discovered patterns with explicit n*, not as statistical findings. They are qualitative evidence of how practitioners extend the documented API.

**Note on `.as_dependency`:** a second classmethod-DI variant (`Class.as_dependency`) exists in `mealie-recipes/mealie`, but that repo is not in the current 402-repo accepted census, so it is reported here as an observed out-of-corpus idiom rather than a census count.

