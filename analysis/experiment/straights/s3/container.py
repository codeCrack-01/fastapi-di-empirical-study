"""ReviewGate-S3 — external DI container (dependency-injector).

The S3 strategy routes dependency acquisition through a
`dependency_injector.DeclarativeContainer`: connections come from a singleton
session factory and auth decisions from a UserService. Handlers pull from the
same core modules the other strategies call — only the acquisition layer
differs.
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
    conn_factory = providers.Resource(db.session)
    user_service = providers.Factory(UserService)