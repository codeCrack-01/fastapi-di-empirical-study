| ID | Construct | Example | Detectable? | Priority |
|---|---|---|---|---|
| C1 | Depends | `Depends(get_db)` | Yes | High |
| C2 | Security | `Security(get_user)` | Yes | High |
| C3 | Annotated dependency | `Annotated[User, Depends(...)]` | Yes | High |
| C4 | Generator dependency | yield inside dependency | Yes | High |
| C5 | Router dependency | `APIRouter(dependencies=...)` | Yes | High |
| C6 | App dependency | `FastAPI(dependencies=...)` | Yes | High |
| C7 | Nested dependency | dependency depending on another dependency | Yes | High |
| C8 | Dependency override | `app.dependency_overrides[...]` | Yes | Medium |
| C9 | Callable class dependency | `Depends(MyDependency())` | Yes | Medium |
| C10 | Parameterized dependency | factory-generated dependency | Maybe | Low |
