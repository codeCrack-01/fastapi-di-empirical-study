# RQ2 — usage & dynamic relationships (mixed methods)

- **Corpus:** 2179 accepted repos (census).

- **Depends() call sites (production):** 98243 across 1371 repos; 4 argument-shape categories


## Tier A — quantitative facets

### Depends() argument shapes

| Shape | Calls | % calls | Repos |
|---|---|---|---|
| bare function | 94889 | 96.6% | 1354 |
| module alias (mod.x) | 2433 | 2.5% | 54 |
| placeholder | 720 | 0.7% | 120 |
| title-case class | 178 | 0.2% | 28 |
| classmethod (Cls.meth) | 23 | 0.0% | 4 |

### Security() OAuth2 scopes

- **620** `Security()` call sites across **104** repos; **0 (0.0%)** pass `scopes=[...]` (0.0% of Security-using repos). The OAuth2 scopes feature is effectively unadopted.

### Dependency-graph relationship topology

- **1338/2179** repos have a non-empty graph; 62200 function nodes + 2682 class nodes; 90863 directed edges.

- **708** fan-in hub nodes with >=10 dependents. Top hubs: get_db (24014), get_current_user (11432), get_session (5014), require_admin (3030), require_permission (1764), get_db_session (1390), require_role (1349), require_user (960).

- Median graph depth 2.0, max 7; **521** repos have any unresolved dependency.


### Annotated[...] type-role frequencies (top)

| Type | Calls | Repos |
|---|---|---|
| AsyncSession | 2435 | 103 |
| User | 2133 | 86 |
| ActorContext | 1630 | 1 |
| KernelContainer | 1312 | 1 |
| Session | 1107 | 78 |
| ... | 1104 | 148 |
| Principal | 739 | 23 |
| str | 734 | 77 |
| AuthPrincipal | 613 | 2 |
| Settings | 522 | 67 |
| dict | 282 | 14 |
| Actor | 247 | 6 |

## Tier B — qualitative idiom catalog (low n, not statistical)

| Idiom | Repos | Evidence |
|---|---|---|
| classmethod-as-dependency (`.as_form`/`.as_dependency`) | 6 | .as_form, .from_query_parameters, .has_permission, .is_authed, .is_authed_optional, .require_role |
| class-as-dependency (`Depends(MyClass)`) | 38 distinct classes / 28 repos | APIKeyAuth, APIKeyHeader, API_KEY_HEADER, AdminOnly, ArrestService, AttachmentRepo, AttachmentService, AttachmentStore ... |
| `provide_*` service-locator dialect | 3 repos | provider namespace |
| `current_*` context/request-scope injection | 76 repos | context objects |
| `*Repository`-typed injection | 1 repos | repository pattern |
| module-alias dependencies (`mod.dep`) | 54 repos | namespaced deps |

**Caveat (honest reporting):** Tier B idioms have very low counts and are reported as *discovered patterns with explicit n*, not as statistical findings. They are qualitative evidence of how practitioners extend the documented API.

**Note on `.as_dependency`:** a second classmethod-DI variant (`Class.as_dependency`) exists in `mealie-recipes/mealie`, but that repo is not in the current 2179-repo accepted census, so it is reported here as an observed out-of-corpus idiom rather than a census count.

