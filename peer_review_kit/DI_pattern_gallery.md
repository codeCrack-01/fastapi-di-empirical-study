# What FastAPI DI looks like — reviewer reference

This gallery shows **real source code** from the 327 in-sample repos. It is the shared "what am I confirming?" reference for the peer review.

## Part A — The four DI constructs (C1–C4)

C1–C4 are the **four syntactic forms** FastAPI provides for declaring a dependency. They are one feature (FastAPI's dependency-injection mechanism) spelled four ways — **not** four frameworks, and not a Python standard-library feature.

| ID | Name | Code form | FastAPI or Python? | Reference (online) |
|---|---|---|---|---|
| **C1** | `Depends` — parameter dependency | `def read_x(db: Session = Depends(get_db))` | **FastAPI** — `from fastapi import Depends`. Not in the Python stdlib. | https://fastapi.tiangolo.com/tutorial/dependencies/ |
| **C2** | `Security` — scoped security dependency | `def read_x(token: str = Security(oauth2_scheme, scopes=["me"]))` | **FastAPI** — `from fastapi import Security`. A `Depends` that additionally extracts OAuth2 security scopes. | https://fastapi.tiangolo.com/tutorial/security/ |
| **C3** | `Annotated` dependency (modern typed form) | `DbDep = Annotated[AsyncSession, Depends(get_db)]` | **Both.** `Annotated` is Python stdlib (`typing.Annotated`); the DI resolution is FastAPI's `Depends`. | https://docs.python.org/3/library/typing.html#typing.Annotated · https://fastapi.tiangolo.com/tutorial/dependencies/ |
| **C4** | Dependency with `yield` (generator dependency) | `def get_db() -> Iterator[Session]: try: yield session finally: close()` | **Both.** The `yield` mechanics are Python generators; treating the generator as a set-up/tear-down dependency is FastAPI. | https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/ |

These four are read from the **call site** (and, for C4, from the **definition**): the extractor counts `depends_calls`, `security_calls`, `annotated_depends`, and `yield_functions` in `corpus/reports/*.json`. `EX2` = `Depends`/`Security` imported from a non-FastAPI module; `Z` = repo with no C1–C4 at all.

### Are C1–C4 themselves "swappable"?

**Yes — as a set.** C1–C4 are four mutually swappable spellings of a single FastAPI injection mechanism. Re-expressing a dependency in another construct does not change its behavior, so the constructs form an interchangeable set:

| Pair | Swap type | Why |
|---|---|---|
| **C1 ⇄ C3** | full swap | same resolution; only annotation-vs-default-value spelling differs — the 933 pure `C1|C3` pairs observed |
| **C1 ⇄ C2** | full swap in practice | `Security()` without scopes resolves identically to `Depends()`; the census shows **0/163** calls pass `scopes`, so in the wild C2 is a labeled C1 |
| **C1/C3 ⇄ C4** | call-site swap | a yield-dependency is still consumed via `Depends(...)` / `Annotated[...]`; only the provider's definition form differs (adds setup/teardown) |

"Swappable" in the catalog is the **measured** side of this: a provider (e.g. `get_db`) written in two or more constructs within one repo is an *observed swap instance* (1,142 across the corpus; 933 of them pure `C1|C3`). That interference-free re-writing across constructs is exactly what lets the S1 benchmark renders in `experiment_proposal.md` §3.1 stay behavior-preserving.

## Part B — Fingerprints: every spelling of C1–C4, nothing more

A **fingerprint** (the `C1|BARE|SIG` strings in this gallery) is one exact spelling of one of the four constructs. It answers "*precisely how is this occurrence written?*" and is the enumerator that makes **all the variants** of the original C1–C4 patterns visible.

- **Every fingerprint starts with C1/C2/C3/C4.** Fingerprints are a finer partition *of* the four constructs, not extra categories: `C3|CLASS|BARE` is still a C3, `C1|EMPTY|PARAM` is still a C1. They never add a fifth construct.
- **Names are replaced by SHAPE classes**, so a fingerprint is repo-independent: identical patterns collapse and distinct spellings stay separate (per `analysis/novelty/fingerprints.py`).

Shape classes (used in the argument / type / annotated slots):

| Class | Meaning | Example |
|---|---|---|
| `BARE` | plain identifier | `Depends(get_db)` |
| `DOTTED` | dotted path | `Depends(core.current_principal)` |
| `CLASS` | Capitalized identifier (a type/class) | `Depends(AsyncSession)` · `Annotated[Session, …]` → `C3|CLASS|BARE` |
| `CALL` | call expression | `Depends(make_db())` |
| `EMPTY` | no argument | `Depends()` |
| `ELLIPSIS` | `...` | `Depends(...)` |
| `OTHER` | anything else | `Depends(<empty>)` forms |
| `SIG` / `PARAM` | C1 slot: in-function-signature vs plain default parameter | `C1|BARE|SIG` vs `C1|BARE|PARAM` |
| `USED` / `DEF` | C4 slot: used as a dependency vs defined but unwired | `C4|USED` vs `C4|DEF` |

Fingerprint grammar (per construct):

| Construct | Fingerprint | Slots |
|---|---|---|
| C1 | `C1|{shape}|{SIG,PARAM}` | shape of the `Depends(...)` argument; in-signature or not |
| C2 | `C2|{shape}|{scopes}` | argument shape; comma-joined OAuth2 scopes, or `ascopes` when none |
| C3 | `C3|{ann}|{dep}` | shape of the annotated type; shape of the inner `Depends(...)` argument |
| C4 | `C4|USED` / `C4|DEF` | whether the generator is wired as a dependency |

The LLM panel then labels each *distinct spelling* (never per repo):

| Label | Meaning (per `analysis/novelty/labels.py`) |
|---|---|
| `known` | expressible by exactly one catalog rule (C1–C4) |
| `variant` | semantically one of C1–C4, but a structurally different spelling |
| `novel` | genuinely new DI pattern outside C1–C4/EX2/Z |
| `false_pos` | not DI — the static extractor over-captured (e.g. non-FastAPI `Depends`) |
| `external_di` | DI from a non-FastAPI framework (flask, celery, dependency-injector, …) |

So when the gallery says *Over-capture (e.g. `C3|CLASS|BARE`)* it means: the panel labelled that *spelling* `false_pos`, but the spelling is often real DI — adjudicate the code, don't auto-dismiss.

A **swappable pattern** = the recurrence of this interchangeability in the wild: the same provider written in more than one of these ways (across constructs) within one repo.

## Swappable patterns (interchangeable DI — the benchmark arm set)

Same provider expressed through two-or-more constructs. Confirm these are genuinely interchangeable DI.

### `get_current_user` — 17 in-sample repo(s)

**Git-me-Harish/Mentora** · `ai_service/dependencies.py:80` · construct C1 ...

```python
return dict(user)
# ── Type aliases ──────────────────────────────────────────────────────────────
CurrentUser = Annotated[dict, Depends(get_current_user)]
DB = Annotated[asyncpg.Pool, Depends(get_db)]
Redis = Annotated[aioredis.Redis, Depends(get_redis)]
Qdrant = Annotated[QdrantClient, Depends(get_qdrant)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L80)

**GolubchikovKirill/InfraScope** · `app/api/deps.py:101` · construct C1 ...

```python
logger.debug("last_seen throttle check failed, skipping persist: %s", exc)
    if should_persist:
        background_tasks.add_task(_persist_last_seen, user.id, now)
    auth_events_total.labels(result="success", reason="token_valid").inc()
    return user
CurrentUser = Annotated[User, Depends(get_current_user)]
def get_current_active_superuser(current_user: CurrentUser) -> User:
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L101)

- +15 more in-sample repo(s): `IBM/docling-pipelines`; `Lawofall/AgentCore`; `TECHLETES/techletes-tooling`; `acgs-ai/enhanced-agent-bus`; `christian-meyndt/personal-finance-tracker`; `dmfenton/CodeMonet`...

### `get_db` — 13 in-sample repo(s)

**AristaLabs/smeme** · `smeme/api/health.py:28` · construct C1 ...

```python
return {
        "status": "healthy",
        "version": settings.version,
        "environment": settings.environment,
    }
@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Database health check."""
    try:
        await db.execute(text("SELECT 1"))
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/api/health.py#L28)

**AydinTHR/aimentum** · `backend/app/db.py:46` · construct C1 ...

```python
return sessionmaker(bind=get_engine(), expire_on_commit=False)
def get_db() -> Iterator[Session]:
    with get_sessionmaker()() as session:
        yield session
DbSession = Annotated[Session, Depends(get_db)]
SessionFactory = Callable[[], AbstractContextManager[Session]]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/db.py#L46)

- +11 more in-sample repo(s): `COS301-SE-2026/Gesture-Based-Drone-Control`; `GolubchikovKirill/InfraScope`; `TECHLETES/techletes-tooling`; `mayldute/tour-pass-api`; `nkswalih/skyrict`; `orqestraai/orqestra-demo`...

### `get_settings` — 10 in-sample repo(s)

**DavidFerj/agentic-platform-baseline** · `gcp/services/control-plane/src/platform_api/api/routes/platform.py:16` · construct C1 ...

```python
from platform_api.contracts.operational import PlatformInfo
from platform_api.core.config import Settings
router = APIRouter(tags=["platform"])
@router.get("/platform", response_model=PlatformInfo)
async def platform_information(
    settings: Annotated[Settings, Depends(get_settings)],
) -> PlatformInfo:
    """Describe the implemented foundation without overstating future capability."""
    return PlatformInfo(
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/DavidFerj/agentic-platform-baseline/blob/4c6cba09eb62031d03bb510288726012431d696d/gcp/services/control-plane/src/platform_api/api/routes/platform.py#L16)

**IanShaw027/openmail** · `backend/app/deps.py:14` · construct C1 ...

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.config import Settings, get_settings
from app.db import get_db
DbDep = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/IanShaw027/openmail/blob/96566a710d5440d1ec5d1729e96b2b42754c735c/backend/app/deps.py#L14)

- +8 more in-sample repo(s): `JafarMahmood123/IntelliLect`; `breim/TAlib-altcoins-api`; `lss100200/omnibase`; `maltewinckler/swen`; `ringlochid/banksia`; `verticalpartnersai-sketch/haz-que-vuelva-lw-dr`...

### `get_session` — 5 in-sample repo(s)

**CPL-Compliance/software-engineer-assessment-guardian-fastapi** · `src/db/session.py:18` · construct C1 ...

```python
session_factory = async_sessionmaker(engine, expire_on_commit=False)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
SessionDep = Annotated[AsyncSession, Depends(get_session)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/CPL-Compliance/software-engineer-assessment-guardian-fastapi/blob/557d2be356582d9c54916527331182847eb0a3f6/src/db/session.py#L18)

**JafarMahmood123/IntelliLect** · `backend/RagService/app/api/dependencies.py:75` · construct C1 ...

```python
logger = logging.getLogger("knowledge.api")
# --- Composition root ---------------------------------------------------------
# This module is the only place where API code names concrete infrastructure
# classes. Everything downstream depends on the port abstractions.
SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
def get_document_repository(session
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/JafarMahmood123/IntelliLect/blob/a7e19a4fd26b8bd32f5fd57df20a05df7eeea3a8/backend/RagService/app/api/dependencies.py#L75)

- +3 more in-sample repo(s): `MKRWW/wortlaut`; `dock108dev/money-map`; `eseifert/altero`

### `get_db_session` — 5 in-sample repo(s)

**GregB712/Loomi-Brain** · `apps/api/src/loomi_api/api/dependencies.py:12` · construct C1 ...

```python
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from loomi_api.auth.service import AuthenticatedOwner, authenticate_session, verify_csrf
from loomi_api.config import Settings
from loomi_api.db.session import get_db_session
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
def get_settings_from_app(request: Request) -> Settings:
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/api/dependencies.py#L12)

**maltewinckler/swen** · `services/backend/src/swen/presentation/api/dependencies.py:176` · construct C1 ...

```python
# -----------------------------------------------------------------------------
# Current User (JWT Authentication)
# -----------------------------------------------------------------------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    identity_repo_factory: IdentityRepositoryFactory = Depends(
        get_identity_repository_factory,
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L176)

- +3 more in-sample repo(s): `ringlochid/banksia`; `vstorm-co/agenticos`; `yag-im/accountsvc`

### `require_admin` — 5 in-sample repo(s)

**its-spark-dev/toollayer-ai** · `apps/control-plane/backend/control_plane/dependencies.py:62` · construct C1 ...

```python
token: Annotated[str | None, Header(alias=SERVICE_HEADER)] = None,
) -> str:
    """Authenticate a runtime service and return a subject for logging."""
    if token is None or not secrets.compare_digest(token, settings.service_token):
        raise Unauthenticated("a valid service token is required")
    return "runtime"
AdminDep = Annotated[str, Depends(require_admin)]
ServiceDep = Annotated[str, Depends(require_ser
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/its-spark-dev/toollayer-ai/blob/c142a39b57ddc6ba1c2940d7307f31a8c53733a3/apps/control-plane/backend/control_plane/dependencies.py#L62)

**maltewinckler/swen** · `services/backend/src/swen/presentation/api/dependencies.py:317` · construct C1 ...

```python
AdapterFactory, Depends(get_identity_adapter_factory)
]
# User + Admin auth dependencies
AuthenticatedUserDep = Annotated[UserContext, Depends(get_current_user)]
AdminUserDep = Annotated[UserContext, Depends(require_admin)]
# Repository factories
RepoFactoryDep = Annotated[RepositoryFactory, Depends(get_repository_factory)]
IdentityRepoFactoryDep = Annotated[
    IdentityRepositoryFactory,
    Depends(get_identity_re
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/maltewinckler/swen/blob/157bc9b3b943cbcd4be623b82e02e1cbd332913e/services/backend/src/swen/presentation/api/dependencies.py#L317)

- +3 more in-sample repo(s): `prdariomarques-ship-it/ship-it`; `volcengine/vePhone`; `wq147/bookmark-navigation`

### `reusable_oauth2` — 4 in-sample repo(s)

**GolubchikovKirill/InfraScope** · `app/api/deps.py:35` · construct C1 ...

```python
_LAST_SEEN_THROTTLE_SECONDS = 300
def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/deps.py#L35)

**TECHLETES/techletes-tooling** · `apps/engineering-cockpit/backend/api/deps.py:32` · construct C1 ...

```python
def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request-scoped dependencies."""
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str | None, Depends(reusable_oauth2)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/TECHLETES/techletes-tooling/blob/8d56b22502cc10832ffcbfcc965f8969bd6734e6/apps/engineering-cockpit/backend/api/deps.py#L32)

- +2 more in-sample repo(s): `orqestraai/orqestra-demo`; `pafful/fastapi-app-main`

### `security` — 3 in-sample repo(s)

**Git-me-Harish/Mentora** · `ai_service/dependencies.py:45` · construct C1 ...

```python
async def get_qdrant(request: Request) -> QdrantClient:
    return request.state.qdrant
# ── Auth ──────────────────────────────────────────────────────────────────────
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: asyncpg.Pool = Depends(get_db),
) -> dict:
    """
    Decode JWT, verify user exists and is active.
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/Git-me-Harish/Mentora/blob/8d5115980c43e5f7cb25464e54c73fff766b307f/ai_service/dependencies.py#L45)

**IBM/docling-pipelines** · `src/docpipe/api/auth/dependencies.py:33` · construct C1 ...

```python
Returns:
        JWT configuration instance
    """
    return JWTConfig()
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    jwt_config: Annotated[JWTConfig, Depends(get_jwt_config)],
) -> User:
    """FastAPI dependency to extract and validate current user from JWT.
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/auth/dependencies.py#L33)

- +1 more in-sample repo(s): `dmfenton/CodeMonet`

### `require_csrf` — 3 in-sample repo(s)

**GregB712/Loomi-Brain** · `apps/api/src/loomi_api/api/dependencies.py:40` · construct C1 ...

```python
request: Request,
    owner: OwnerContext,
) -> AuthenticatedOwner:
    settings = get_settings_from_app(request)
    verify_csrf(owner, request.headers.get(settings.csrf_header_name))
    return owner
CsrfOwnerContext = Annotated[AuthenticatedOwner, Depends(require_csrf)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/GregB712/Loomi-Brain/blob/6ddba737683fbbcd5b8881127a61498cc0dd4e32/apps/api/src/loomi_api/api/dependencies.py#L40)

**eseifert/altero** · `src/altero/api/routes/web.py:256` · construct C1 ...

```python
def require_csrf(request: Request) -> None:
    """Refuse an unsafe request whose header does not match its cookie."""
    cookie = request.cookies.get(CSRF_COOKIE)
    header = request.headers.get(CSRF_HEADER)
    if not cookie or not header or not secrets.compare_digest(cookie, header):
        raise HTTPException(status_code=403, detail="Missing or invalid CSRF token")
CsrfDep = Annotated[None, Depends(require_csr
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/eseifert/altero/blob/c198ef6a3aec23d1c47f7245ce5c0eb58d95c405/src/altero/api/routes/web.py#L256)

- +1 more in-sample repo(s): `volcengine/vePhone`

### `oauth2_scheme` — 3 in-sample repo(s)

**IBM/docling-pipelines** · `src/docpipe/api/auth/dependencies.py:79` · construct C1 ...

```python
)
    logger.debug(f"Authenticated user: {username}")
    return user
async def get_current_user_oauth2(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    jwt_config: Annotated[JWTConfig, Depends(get_jwt_config)],
) -> User | None:
    """FastAPI dependency to extract user from OAuth2 token.
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/IBM/docling-pipelines/blob/1fa3dda3bceea72a9c47753a61b01a465ae50dbc/src/docpipe/api/auth/dependencies.py#L79)

**suzu-devworks/examples-py** · `packages/web/examples-fastapi/scripts/tutorials/security/main.py:95` · construct C1 ...

```python
expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/suzu-devworks/examples-py/blob/d3773959f350c3e58af1c4bedffd7d468d077f24/packages/web/examples-fastapi/scripts/tutorials/security/main.py#L95)

- +1 more in-sample repo(s): `vstorm-co/agenticos`

### `get_user_service` — 3 in-sample repo(s)

**Turing222/dewflow** · `backend/api/deps/auth.py:44` · construct C1 ...

```python
except PydanticValidationError as exc:
        raise app_validation_error(
            "请求参数校验失败", details={"errors": exc.errors()}
        ) from exc
async def get_current_user(
    uow: AbstractUnitOfWork = Depends(get_uow),
    token: str = Depends(reusable_oauth2),
    user_service: UserService = Depends(get_user_service),
) -> User:
    try:
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/Turing222/dewflow/blob/37485f26b1db154b61927f6ef60a5776e914955b/backend/api/deps/auth.py#L44)

**vstorm-co/agenticos** · `backend/app/api/deps.py:115` · construct C1 ...

```python
def get_oauth_exchange_service(redis: Redis) -> OAuthExchangeService:
    """Create OAuthExchangeService instance with the Redis client."""
    return OAuthExchangeService(redis)
UserSvc = Annotated[UserService, Depends(get_user_service)]
SessionSvc = Annotated[SessionService, Depends(get_session_service)]
ImpersonationSvc = Annotated[ImpersonationService, Depends(get_impersonation_service)]
OAuthExchangeSvc = Annota
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L115)

- +1 more in-sample repo(s): `yag-im/accountsvc`

### `require_session` — 3 in-sample repo(s)

**georgejieh/REED** · `backend/app/api/wizard.py:36` · construct C1 ...

```python
from app.intake.policy import OutboundUrlPolicy, UnsafeOutboundUrl
from app.providers.openai_compatible import validate_provider_endpoint
from app.secrets.base import SecretStore
from app.secrets.keyring_store import SecretStoreUnavailable
router = APIRouter(prefix="/api/wizard", tags=["wizard"])
MutationAuth = Annotated[None, Depends(require_mutation_auth)]
SessionAuth = Annotated[None, Depends(require_session)]
cla
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/georgejieh/REED/blob/1991e94aad749635dbc7f36ce0a35bc6c5712667/backend/app/api/wizard.py#L36)

**volcengine/vePhone** · `Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py:53` · construct C1 ...

```python
def require_user(auth_session: CurrentSession, db: Database) -> User:
    user = db.get(User, auth_session.user_id)
    if user is None or user.status != "active":
        raise api_error(401, "authentication_required", "Authentication required")
    return user
CurrentUser = Annotated[User, Depends(require_user)]
def require_admin(user: CurrentUser) -> User:
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/volcengine/vePhone/blob/dc3f489dfbd79cc9ef1bbec915cee6767e65d8d5/Quick Start/ComputerUseAgent/src/cua_platform/api/deps.py#L53)

- +1 more in-sample repo(s): `wq147/bookmark-navigation`

### `get_database` — 2 in-sample repo(s)

**DavidFerj/agentic-platform-baseline** · `gcp/services/control-plane/src/platform_api/api/routes/health.py:28` · construct C1 ...

```python
@router.get(
    "/ready",
    response_model=HealthResponse,
    responses={503: {"model": ProblemDetail}},
)
async def readiness(
    database: Annotated[DatabaseGateway, Depends(get_database)],
) -> HealthResponse:
    """Confirm that required control-plane dependencies are available."""
    try:
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/DavidFerj/agentic-platform-baseline/blob/4c6cba09eb62031d03bb510288726012431d696d/gcp/services/control-plane/src/platform_api/api/routes/health.py#L28)

**derekrivers/atlas** · `atlas/api/dependencies.py:110` · construct C1 ...

```python
def get_operator_session_service(request: Request) -> OperatorSessionService:
    """Return the writable-session service installed during app startup."""
    service: OperatorSessionService = request.app.state.operator_session_service
    return service
OperatorSessionServiceDependency = Annotated[
    OperatorSessionService,
    Depends(get_operator_session_service),
]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/derekrivers/atlas/blob/c80d8ce4f698cfd946c08301af02ee36231c32c9/atlas/api/dependencies.py#L110)

### `get_auth_context` — 2 in-sample repo(s)

**EndofTimeWorks/pluris-haven** · `server/pluris_server/dependencies.py:75` · construct C1 ...

```python
def require_friends_enabled(settings: Annotated[Settings, Depends(settings_from_request)]) -> None:
    if not settings.friends_enabled:
        raise HTTPException(status_code=503, detail="Friend connections are not enabled")
Db = Annotated[AsyncSession, Depends(get_db)]
CurrentAuth = Annotated[AuthContext, Depends(get_auth_context)]
AppSettings = Annotated[Settings, Depends(settings_from_request)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L75)

**vstorm-co/agenticos** · `backend/app/api/deps.py:602` · construct C1 ...

```python
Endpoints check permissions, never role names - so re-shaping a role is a
    change to `ROLE_PERMS` alone. For a resource permission this guards the
    *kind* of thing; which rows are reachable is
    :func:`app.services.access.resolve_access`.
    Usage::
        @router.post("/agents", dependencies=[Depends(require(Perm.AGENTS_EDIT))])
        async def create_agent(...): ...
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/vstorm-co/agenticos/blob/7cff550b2fa545a7746e4480c463ca0c6c1cd37e/backend/app/api/deps.py#L602)

## Context-bound patterns (reported, not generic)

Single-repo providers, non-plain argument shapes, closures/parameterized dependencies, or pass-2 non-native mechanisms.

### `[mechanism]` — 18 in-sample repo(s)

**7finger0x/ht** · `services/api/app/auth.py:32` · construct C1 ...

```python
credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthContext:
    return authenticate_request(request, credentials)
def require_scopes(*required_scopes: str):
    def dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ) -> AuthContext:
        context = authenticate_request(request, credentials)
        missing = 
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/services/api/app/auth.py#L32)

**EndofTimeWorks/pluris-haven** · `server/pluris_server/routers/friends.py:40` · construct C1 ...

```python
digest_friend_code,
    digest_legacy_friend_code,
    new_friend_code,
)
router = APIRouter(
    prefix="/v1/friends",
    tags=["friends"],
    dependencies=[Depends(require_friends_enabled)],
)
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/routers/friends.py#L40)

- +16 more in-sample repo(s): `EssenceSentry/relay`; `GlacierEQ/ECHO`; `InfoSecInnovations/shabti`; `MoMoM101/RAG-ReActAgent`; `MoMoM101/RAG-ReActAgent`; `Pratzz14/Phys.io`...

### `<empty>` — 10 in-sample repo(s)

**4ch1m/pixoo-rest** · `pixoo_rest/routers/draw.py:27` · construct C1 ...

```python
)
router = APIRouter(tags=[APITags.DRAW])
pixoo = get_pixoo()
@router.post('/image', response_model=ResponseModel)
async def image(image_model: Annotated[ImageModel, Depends()], image_file: Annotated[UploadFile, File(description='The image to display. (Automatically gets resized.)')]) -> ResponseModel:
    image_data = await image_file.read()
    pixoo.draw_image_at_location(
```
- fingerprint: `C1|EMPTY|PARAM` — [open on GitHub](https://github.com/4ch1m/pixoo-rest/blob/ef6819605ca2da24bcf51bd46b486fa4d25c4258/pixoo_rest/routers/draw.py#L27)

**GolubchikovKirill/InfraScope** · `app/api/routes/auth.py:73` · construct C1 ...

```python
@router.post("/login")
@limiter.limit("5/minute")
def login_access_token(
    request: Request,
    response: Response,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""
    # `request` is required by the rate limiter decorator context.
```
- fingerprint: `C1|EMPTY|PARAM` — [open on GitHub](https://github.com/GolubchikovKirill/InfraScope/blob/1f8e7b04572af419304cd115187c0593880243fb/app/api/routes/auth.py#L73)

- +8 more in-sample repo(s): `TECHLETES/techletes-tooling`; `Turing222/dewflow`; `Uranus313/loan-system`; `christian-meyndt/personal-finance-tracker`; `gmlrep/tasker`; `orqestraai/orqestra-demo`...

### `_session_dep` — 1 in-sample repo(s)

**acgs-ai/ACGS** · `packages/acgs-control-plane/src/acgs_control_plane/app.py:229` · construct C1 ...

```python
def _session_dep(request: Request) -> Iterator[Session]:
    session: Session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()
SessionDep = Annotated[Session, Depends(_session_dep)]
def _principal_dep(
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/acgs-ai/ACGS/blob/81de59eabacd261b8396c3dbe30178f0b84b5475/packages/acgs-control-plane/src/acgs_control_plane/app.py#L229)

### `require_authenticated_principal` — 1 in-sample repo(s)

**7finger0x/ht** · `services/api/app/main.py:83` · construct C1 ...

```python
)
AuthenticatedPrincipal = Annotated[AuthContext, Depends(require_authenticated_principal)]
DecisionWriter = Annotated[AuthContext, Depends(require_scopes("decisions:create"))]
ExecutionWriter = Annotated[AuthContext, Depends(require_scopes("executions:create"))]
ExecutionApprover = Annotated[AuthContext, Depends(require_scopes("executions:approve"))]
AuditReader = Annotated[AuthContext, Depends(require_scopes("audit
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/7finger0x/ht/blob/f063670ecee51edc0224d2ec1518c41298ea1fa4/services/api/app/main.py#L83)

### `_get_openai_client` — 1 in-sample repo(s)

**AristaLabs/smeme** · `smeme/core/dependencies.py:51` · construct C1 ...

```python
# OpenAI client
OpenAIClientDep = Annotated[AsyncOpenAI, Depends(_get_openai_client)]
# Tavily client (web search for agentic generation)
TavilyClientDep = Annotated[AsyncTavilyClient, Depends(_get_tavily_client)]
# User authentication
CurrentUser = Annotated[User, Depends(_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(_current_active_verified_user)]
CurrentSuperuser = Annotated[User, Depends(_c
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L51)

### `_get_tavily_client` — 1 in-sample repo(s)

**AristaLabs/smeme** · `smeme/core/dependencies.py:54` · construct C1 ...

```python
# OpenAI client
OpenAIClientDep = Annotated[AsyncOpenAI, Depends(_get_openai_client)]
# Tavily client (web search for agentic generation)
TavilyClientDep = Annotated[AsyncTavilyClient, Depends(_get_tavily_client)]
# User authentication
CurrentUser = Annotated[User, Depends(_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(_current_active_verified_user)]
CurrentSuperuser = Annotated[User, Depends(_c
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L54)

### `_current_active_user` — 1 in-sample repo(s)

**AristaLabs/smeme** · `smeme/core/dependencies.py:57` · construct C1 ...

```python
# OpenAI client
OpenAIClientDep = Annotated[AsyncOpenAI, Depends(_get_openai_client)]
# Tavily client (web search for agentic generation)
TavilyClientDep = Annotated[AsyncTavilyClient, Depends(_get_tavily_client)]
# User authentication
CurrentUser = Annotated[User, Depends(_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(_current_active_verified_user)]
CurrentSuperuser = Annotated[User, Depends(_c
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L57)

### `_current_active_verified_user` — 1 in-sample repo(s)

**AristaLabs/smeme** · `smeme/core/dependencies.py:58` · construct C1 ...

```python
# OpenAI client
OpenAIClientDep = Annotated[AsyncOpenAI, Depends(_get_openai_client)]
# Tavily client (web search for agentic generation)
TavilyClientDep = Annotated[AsyncTavilyClient, Depends(_get_tavily_client)]
# User authentication
CurrentUser = Annotated[User, Depends(_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(_current_active_verified_user)]
CurrentSuperuser = Annotated[User, Depends(_c
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L58)

### `_current_superuser` — 1 in-sample repo(s)

**AristaLabs/smeme** · `smeme/core/dependencies.py:59` · construct C1 ...

```python
# OpenAI client
OpenAIClientDep = Annotated[AsyncOpenAI, Depends(_get_openai_client)]
# Tavily client (web search for agentic generation)
TavilyClientDep = Annotated[AsyncTavilyClient, Depends(_get_tavily_client)]
# User authentication
CurrentUser = Annotated[User, Depends(_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(_current_active_verified_user)]
CurrentSuperuser = Annotated[User, Depends(_c
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L59)

### `_get_current_user_optional` — 1 in-sample repo(s)

**AristaLabs/smeme** · `smeme/core/dependencies.py:60` · construct C1 ...

```python
# OpenAI client
OpenAIClientDep = Annotated[AsyncOpenAI, Depends(_get_openai_client)]
# Tavily client (web search for agentic generation)
TavilyClientDep = Annotated[AsyncTavilyClient, Depends(_get_tavily_client)]
# User authentication
CurrentUser = Annotated[User, Depends(_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(_current_active_verified_user)]
CurrentSuperuser = Annotated[User, Depends(_c
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L60)

### `_get_user_manager` — 1 in-sample repo(s)

**AristaLabs/smeme** · `smeme/core/dependencies.py:63` · construct C1 ...

```python
# OpenAI client
OpenAIClientDep = Annotated[AsyncOpenAI, Depends(_get_openai_client)]
# Tavily client (web search for agentic generation)
TavilyClientDep = Annotated[AsyncTavilyClient, Depends(_get_tavily_client)]
# User authentication
CurrentUser = Annotated[User, Depends(_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(_current_active_verified_user)]
CurrentSuperuser = Annotated[User, Depends(_c
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/core/dependencies.py#L63)

### `require_owned_generation_by_thread_id` — 1 in-sample repo(s)

**AristaLabs/smeme** · `smeme/decision_tree/generation/agentic/ownership.py:42` · construct C1 ...

```python
)
    if generation is None:
        raise _not_found()
    return generation
OwnedGenerationByThreadFormDep = Annotated[
    InProgressDecisionTreeGeneration,
    Depends(require_owned_generation_by_thread_id),
]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/decision_tree/generation/agentic/ownership.py#L42)

### `get_calendar` — 1 in-sample repo(s)

**AydinTHR/aimentum** · `backend/app/services/calendar.py:252` · construct C1 ...

```python
return "fake-calendar-id"
@lru_cache(maxsize=1)
def get_calendar() -> CalendarService:
    return GoogleCalendarService()
CalendarDep = Annotated[CalendarService, Depends(get_calendar)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/services/calendar.py#L252)

### `get_push_transport` — 1 in-sample repo(s)

**AydinTHR/aimentum** · `backend/app/services/push.py:140` · construct C1 ...

```python
return outcomes
@lru_cache(maxsize=1)
def get_push_transport() -> PushTransport:
    return WebPushTransport()
PushDep = Annotated[PushTransport, Depends(get_push_transport)]
```
- fingerprint: `C1|BARE|PARAM` — [open on GitHub](https://github.com/AydinTHR/aimentum/blob/39add614f85c1668034d2adf950d9960763303b8/backend/app/services/push.py#L140)

## Over-capture (flagged for adjudication, not auto-dismissed)

Fingerprints the single-rater panel labelled false_pos but which often ARE real DI (e.g. `C3|CLASS|BARE`, `C4|USED`). Reviewers should adjudicate, not blanket-accept the label.

### `get_db` — 45 in-sample repo(s)

**7-Blocks/Kepler** · `backend/api/v1/endpoints/agents.py:46` · construct C1 ...

```python
"current_step":  run.current_step,
        "started_at":    _dt(run.started_at),
        "completed_at":  _dt(run.completed_at),
        "decisions":     decisions,
    }
@router.post("/trigger/{collision_id}", response_model=APIResponse[dict])
def trigger_agent_mitigation_workflow(collision_id: int, db: Session = Depends(get_db)):
    collision = db.query(CollisionPrediction).filter(CollisionPrediction.id == collisi
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/7-Blocks/Kepler/blob/7497a93f6d829b1e3cf491c31c16f749ae01d47e/backend/api/v1/endpoints/agents.py#L46)

**ActiveInferenceInstitute/ActiveInferAnts** · `6_API/Knowledge_API.py:239` · construct C1 ...

```python
# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@app.post("/api/knowledge/", response_model=dict[str, Any], status_code=201)
def create_knowledge(
    knowledge: KnowledgeBase,
    db: Session = Depends(get_db),
    _: str | None = Depends(get_api_key),
):
    try:
        existing = (
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/ActiveInferenceInstitute/ActiveInferAnts/blob/1dea3cd6a65a999b14b2ca3fd52542e395a33624/6_API/Knowledge_API.py#L239)

- +43 more in-sample repo(s): `Adejare-ml/News-Intelligence-System`; `AlphaHorizon-AI/Shogun`; `Dibyataru-Chakraborty/ASM-Tool`; `DockVault/vault`; `GG-Angel/overplayed`; `Lawofall/AgentCore`...

### `get_session` — 9 in-sample repo(s)

**Devathmaj/VoucherBot** · `voucherbot/api/routers/health.py:13` · construct C1 ...

```python
from voucherbot.api.rate_limit import health_rate_limit
from voucherbot.database.connection import get_session
router = APIRouter(tags=["health"])
@router.head("/health", dependencies=[Depends(health_rate_limit)])
@router.get("/health", dependencies=[Depends(health_rate_limit)])
async def health_check(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    await session.execute(text("SELECT count(*) FROM
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/Devathmaj/VoucherBot/blob/4e5d823175aae665736c4ccc23033d3127df8ecf/voucherbot/api/routers/health.py#L13)

**Joulenap/joulenap** · `backend/app/api/dashboard.py:62` · construct C1 ...

```python
pbss: list[PbsEntry]
@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    request: Request,
    store: ConfigStore = Depends(get_config_store),
    scheduler: Scheduler = Depends(get_scheduler),
    job_service: JobService = Depends(get_job_service),
    session: Session = Depends(get_session),
) -> DashboardResponse:
    authorize_api_key(request, store)
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/Joulenap/joulenap/blob/5bba11d7184982ff7b605982835cd6f48295adc7/backend/app/api/dashboard.py#L62)

- +7 more in-sample repo(s): `OpenBMB/StaffDeck`; `TryCaspian/caspian-sdk`; `b1rdmania/legalise`; `cjbaxt/house-lights`; `darkspock/ddd_python_sample`; `gnt-ai/gnt`...

### `get_db_session` — 3 in-sample repo(s)

**latheeshmahendran/soloV1** · `backend/api/v1/endpoints/conversation.py:40` · construct C1 ...

```python
)
from backend.services.conversation_service import ConversationService
router = APIRouter(prefix="/conversation", tags=["Conversation"])
def _get_conversation_service(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> ConversationService:
    """Factory dependency for ConversationService.
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/latheeshmahendran/soloV1/blob/c86c2c89fe3ce18e39c078b8bffb63b3f4f3f3fb/backend/api/v1/endpoints/conversation.py#L40)

**mic1on/onestep** · `apps/control-plane/backend/src/onestep_control_plane_api/api/routers/agent_ws.py:350` · construct C1 ...

```python
publish_ui_stream_event("commands")
    return "ok"
@router.websocket("/ws")
async def agent_ws(
    websocket: WebSocket,
    auth: WebSocketIngestAuth = Depends(require_websocket_ingest_token),
    db: Session = Depends(get_db_session),
) -> None:
    await websocket.accept(subprotocol=auth.accepted_subprotocol)
    send_queue: asyncio.Queue[dict[str, object]] = asyncio.Queue()
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/mic1on/onestep/blob/59e12c57363161e2b150ed06bdacd6604a80bd05/apps/control-plane/backend/src/onestep_control_plane_api/api/routers/agent_ws.py#L350)

- +1 more in-sample repo(s): `thulasidharan96/API-Gateway`

### `get_user_db` — 2 in-sample repo(s)

**AristaLabs/smeme** · `smeme/auth/manager.py:43` · construct C1 ...

```python
logger.info("User %s logged in", user.id)
async def get_user_db(session: AsyncSession = Depends(get_db)):
    """Get user database adapter."""
    yield SQLAlchemyUserDatabase(session, User)
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Get user manager instance."""
    yield UserManager(user_db)
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/auth/manager.py#L43)

**transformerlab/nebula-tower** · `api.py:82` · construct C1 ...

```python
async with async_session_maker() as session:
        yield session
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = os.environ.get("JWT_SECRET", "CHANGE_ME")
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L82)

### `get_user_manager` — 2 in-sample repo(s)

**AristaLabs/smeme** · `smeme/auth/manager.py:43` · construct C1 ...

```python
logger.info("User %s logged in", user.id)
async def get_user_db(session: AsyncSession = Depends(get_db)):
    """Get user database adapter."""
    yield SQLAlchemyUserDatabase(session, User)
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Get user manager instance."""
    yield UserManager(user_db)
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/AristaLabs/smeme/blob/5ac62e9ff6b473ff3b13fde038bbb83d6f07b42b/smeme/auth/manager.py#L43)

**transformerlab/nebula-tower** · `api.py:226` · construct C1 ...

```python
from_attributes = True
@app.get("/admin/api/users", response_model=list[AdminUserRead], dependencies=[Depends(current_superuser)])
async def list_users(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users
@app.patch("/admin/api/users/{user_id}", response_model=AdminUserRead, dependencies=[Depends(current_superuser)])

```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L226)

### `get_redis` — 1 in-sample repo(s)

**GG-Angel/overplayed** · `apps/api/src/cache/client.py:91` · construct C1 ...

```python
await self.redis.delete(*keys)
        logger.debug(f"Deleted {len(keys)} cached value(s)")
    @staticmethod
    def key(*parts: str) -> str:
        return ":".join(parts)
def get_redis_client(redis: Redis = Depends(get_redis)) -> RedisClient:
    return RedisClient(redis=redis)
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/GG-Angel/overplayed/blob/0ae33e785f611238c276f8b65586d9cce945a76f/apps/api/src/cache/client.py#L91)

### `get_scraper` — 1 in-sample repo(s)

**Tanishpd/linkedin-insights-microservice** · `app/api/routes.py:122` · construct C1 ...

```python
await cache_service.set(cache_key, response)
    return response
@router.get("/pages/{page_id}", summary="Get specific page by page_id")
async def get_page_by_id(
    page_id: str,
    scraper: LinkedInScraper = Depends(get_scraper)
) -> Dict[str, Any]:
    """
    Get page details by page_id.
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/Tanishpd/linkedin-insights-microservice/blob/118f5d4c7cb2ef4ca367313e50adfab2712fd434/app/api/routes.py#L122)

### `_get_db` — 1 in-sample repo(s)

**databrickslabs/lakemeter-oss** · `backend/app/auth/databricks_auth.py:155` · construct C1 ...

```python
def _get_db() -> Generator[Session, None, None]:
    """Get database session - avoids circular import."""
    from app.database import get_db
    yield from get_db()
async def get_current_user(
    request: Request,
    db: Session = Depends(_get_db)
) -> "User":
    """
    FastAPI dependency to get the current authenticated user.
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/databrickslabs/lakemeter-oss/blob/ab0dfcbfdc1627ea77d052d44b97be7860e34a48/backend/app/auth/databricks_auth.py#L155)

### `get_tenant_db` — 1 in-sample repo(s)

**lss100200/omnibase** · `backend/src/omnibase/agent_registry/router.py:87` · construct C1 ...

```python
status_code=status.HTTP_201_CREATED,
)
def create_custom_agent(
    workspace_id: str,
    payload: AgentBuilderCreate,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=128),
    ctx: TenantContext = Depends(get_current_tenant),
    db: Session = Depends(get_tenant_db),
) -> AgentBuilderCreateResult:
    """Create a sealed, low-risk, tool-free Agent and optiona
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/agent_registry/router.py#L87)

### `get_current_principal` — 1 in-sample repo(s)

**lss100200/omnibase** · `backend/src/omnibase/agent_skills/router.py:86` · construct C1 ...

```python
q: str | None = Query(
        default=None,
        min_length=1,
        max_length=80,
        pattern=r"^[^\x00-\x1f\x7f]+$",
    ),
    category: str | None = Query(default=None, min_length=1, max_length=32),
    role: str | None = Query(default=None, min_length=1, max_length=16),
    principal: CurrentPrincipal = Depends(get_current_principal),
) -> NativeSkillList:
    del principal
    try:
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/agent_skills/router.py#L86)

### `get_gateway_db` — 1 in-sample repo(s)

**lss100200/omnibase** · `backend/src/omnibase/capability_gateway/router.py:149` · construct C1 ...

```python
response_model=DataSchemaResponse,
    operation_id="gateway_data_schema_read",
    responses=_RESPONSES,
)
def read_data_schema(
    payload: ResourceRequest,
    credential: WorkloadCredential = Depends(get_workload_credential),
    session: Session = Depends(get_gateway_db),
    service: GatewayService = Depends(get_gateway_service),
    request_id: str = Depends(get_request_id),
) -> DataSchemaResponse:
    retur
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/lss100200/omnibase/blob/96711e8ef193184022b53c582d463ac6fecfb089/backend/src/omnibase/capability_gateway/router.py#L149)

### `get_async_session` — 1 in-sample repo(s)

**transformerlab/nebula-tower** · `api.py:71` · construct C1 ...

```python
is_verified: Optional[bool] = None
# Dependencies to provide DB and user manager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_
```
- fingerprint: `C1|BARE|SIG` — [open on GitHub](https://github.com/transformerlab/nebula-tower/blob/61819660f743d8cbb400c9791d0a5b9c1e305a0c/api.py#L71)

### `get_catalog_db` — 1 in-sample repo(s)

**whitebreadisu/hyperspacevault** · `backend/app/database.py:185` · construct C4 ...

```python
gate on verification. Routes that need the stronger check add
    Depends(require_verified_email) alongside this one; since both hang
    off get_current_identity, the token is still only verified once per
    request.
    """
    firebase_uid, email, _ = identity
    db, conn = _open_authenticated_session(request, firebase_uid, email)
    try:
        yield db
    finally:
        db.close()
        conn.close()
```
- fingerprint: `C4|USED` — [open on GitHub](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/database.py#L185)

### `get_optional_db` — 1 in-sample repo(s)

**whitebreadisu/hyperspacevault** · `backend/app/database.py:271` · construct C4 ...

```python
yield db
    finally:
        db.close()
        conn.close()
def get_optional_db(
    request: Request,
    identity: Optional[tuple[str, str, bool]] = Depends(get_optional_identity),
):
    """FastAPI dependency: optional-auth session for GET /api/base-cards/{id}
    (BL-56 / ADR-0008 build-time refinement). Unlike the fully public catalog
```
- fingerprint: `C4|USED` — [open on GitHub](https://github.com/whitebreadisu/hyperspacevault/blob/b821a69e7c06df99a83f3daeca1c70e8594e790d/backend/app/database.py#L271)

## Notes

- Excerpts are pinned to study commits; `[open on GitHub]` links jump to the exact line.
- Snippets are truncated for the digestible view; full code is on GitHub and in the per-repo evidence pages.
