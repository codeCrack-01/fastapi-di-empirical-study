"""Convert vstorm-co server.py from S2 (app.state via Depends) to S4
(dependency-injector container wired with Depends(Provide[...])).

Keeps the exact per-route guards (ServiceAuth / AuthorizedSession), the same
`check_service_token` / `check_session_token` calls, and therefore the same
work per request. Only the service's *source* is moved from request.app.state
to a dependency-injector DeclarativeContainer.

Usage: <repo>/../../scripts/.toolenv/bin/python s4_patch.py <repo>/server.py <repo>/pyproject.toml
"""

import sys

OLD_BLOCK = '''
def _service_of(request: Request) -> _Service:
    """Pull the service off application state."""
    service: _Service = request.app.state.service
    return service


ServiceDep = Annotated[_Service, Depends(_service_of)]
TokenHeader = Annotated[str | None, Header(alias=wire.TOKEN_HEADER)]


def _require_service_token(service: ServiceDep, token: TokenHeader = None) -> None:
    """Dependency admitting only the service token."""
    service.check_service_token(token)


def _authorized_session(
    service: ServiceDep,
    session_id: Annotated[str, PathParam(pattern=wire.SESSION_ID_PATTERN)],
    token: TokenHeader = None,
) -> str:
    """Dependency authorizing a caller for one session, returning its id."""
    service.check_session_token(session_id, token)
    return session_id


ServiceAuth = Depends(_require_service_token)
AuthorizedSession = Annotated[str, Depends(_authorized_session)]
'''

NEW_BLOCK = '''
class SandboxContainer(containers.DeclarativeContainer):
    """dependency-injector container owning the service singleton (S4)."""

    service = providers.Object()


def _service_of(request: Request) -> _Service:
    """Pull the service out of the dependency-injector container."""
    service: _Service = SandboxContainer().service()
    return service


ServiceDep = Annotated[_Service, Depends(_service_of)]
TokenHeader = Annotated[str | None, Header(alias=wire.TOKEN_HEADER)]


def _require_service_token(service: ServiceDep, token: TokenHeader = None) -> None:
    """Dependency admitting only the service token."""
    service.check_service_token(token)


def _authorized_session(
    service: ServiceDep,
    session_id: Annotated[str, PathParam(pattern=wire.SESSION_ID_PATTERN)],
    token: TokenHeader = None,
) -> str:
    """Dependency authorizing a caller for one session, returning its id."""
    service.check_session_token(session_id, token)
    return session_id


ServiceAuth = Depends(_require_service_token)
AuthorizedSession = Annotated[str, Depends(_authorized_session)]
'''


def main(server_path: str, pyproject_path: str) -> None:
    src = open(server_path).read()
    if "SandboxContainer" in src:
        print("already patched")
        return
    assert OLD_BLOCK in src, "S2 block not found"
    src = src.replace(OLD_BLOCK, NEW_BLOCK)
    assert "SandboxContainer" in src

    imports_needle = "from pydantic_ai_backends.remote import wire\n"
    additions = "from dependency_injector import containers, providers\n"
    assert imports_needle in src
    src = src.replace(imports_needle, imports_needle + additions)

    override_needle = "    app.state.service = service\n"
    assert override_needle in src
    src = src.replace(
        override_needle,
        override_needle + "    SandboxContainer.service.override(providers.Object(service))\n",
    )
    open(server_path, "w").write(src)
    print(f"patched {server_path}")

    pp = open(pyproject_path).read()
    if "dependency-injector" not in pp:
        pp = pp.replace(
            '    "fastapi>=0.115.0",\n',
            '    "fastapi>=0.115.0",\n    "dependency-injector>=4.41.0",\n',
            1,
        )
        open(pyproject_path, "w").write(pp)
        print(f"patched {pyproject_path} (+ dependency-injector in server extra)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])