"""ReviewGate-S3 — external DI container (dependency-injector).

The S3 strategy routes dependency acquisition through a
`dependency_injector.DeclarativeContainer`: every request pulls a fresh
per-request session from the container and auth decisions from a UserService.
Handlers pull from the same core modules the other strategies call — only the
acquisition layer differs. (A `providers.Resource` would be singleton-scoped
and share one connection across the whole worker; `providers.Factory` keeps
per-request lifetimes identical to S0/S2.)
"""

from __future__ import annotations

from dependency_injector import containers, providers

from core import auth, db


class UserService:
    """Thin adapter over core.auth so the S3 render can use a container object."""

    def current_user(self, conn, request):
        return auth.current_user(conn, request)

    def require_role(self, user, roles):
        return auth.require_role(user, roles)


class Container(containers.DeclarativeContainer):
    conn_factory = providers.Factory(db.session)
    user_service = providers.Factory(UserService)