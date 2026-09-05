# RQ2 — usage & dynamic relationships (mixed methods)

- **Corpus:** 351 accepted repos (census).

- **Depends() call sites (production):** 22711 across 262 repos; 4 argument-shape categories


## Tier A — quantitative facets

### Depends() argument shapes

| Shape | Calls | % calls | Repos |
|---|---|---|---|
| bare function | 22005 | 96.9% | 256 |
| placeholder | 423 | 1.9% | 24 |
| module alias (mod.x) | 258 | 1.1% | 8 |
| title-case class | 19 | 0.1% | 5 |
| classmethod (Cls.meth) | 6 | 0.0% | 1 |

### Security() OAuth2 scopes

- **143** `Security()` call sites across **33** repos; **0 (0.0%)** pass `scopes=[...]` (0.0% of Security-using repos). The OAuth2 scopes feature is effectively unadopted.

### Dependency-graph relationship topology

- **253/351** repos have a non-empty graph; 14927 function nodes + 625 class nodes; 20904 directed edges.

- **208** fan-in hub nodes with >=10 dependents. Top hubs: get_db (4332), get_session (1716), get_current_user (1299), require_admin (1134), require_user (629), require_role (450), get_current_active_user (418), get_db_session (396).

- Median graph depth 2, max 7; **98** repos have any unresolved dependency.


### Annotated[...] type-role frequencies (top)

| Type | Calls | Repos |
|---|---|---|
| User | 671 | 17 |
| AsyncSession | 401 | 21 |
| str | 365 | 18 |
| Session | 270 | 16 |
| UserPrincipal | 180 | 1 |
| AuditSink | 142 | 1 |
| ... | 103 | 29 |
| AuthIdentity | 98 | 1 |
| Settings | 95 | 15 |
| CurrentAdminUser | 76 | 1 |
| Actor | 72 | 1 |
| OrgAccessIndex | 72 | 1 |

## Tier B — qualitative idiom catalog (low n, not statistical)

| Idiom | Repos | Evidence |
|---|---|---|
| classmethod-as-dependency (`.as_form`/`.as_dependency`) | 1 | .as_form |
| class-as-dependency (`Depends(MyClass)`) | 14 distinct classes / 5 repos | API_KEY_HEADER, AttachmentRepo, AttachmentService, AttachmentStore, HTTPBearer, ImageRepo, ImageService, ImageStore ... |
| `provide_*` service-locator dialect | 1 repos | provider namespace |
| `current_*` context/request-scope injection | 12 repos | context objects |
| `*Repository`-typed injection | 0 repos | repository pattern |
| module-alias dependencies (`mod.dep`) | 8 repos | namespaced deps |

**Caveat (honest reporting):** Tier B idioms have very low counts and are reported as *discovered patterns with explicit n*, not as statistical findings. They are qualitative evidence of how practitioners extend the documented API.

**Note on `.as_dependency`:** a second classmethod-DI variant (`Class.as_dependency`) exists in `mealie-recipes/mealie`, but that repo is not in the current 351-repo accepted census, so it is reported here as an observed out-of-corpus idiom rather than a census count.

