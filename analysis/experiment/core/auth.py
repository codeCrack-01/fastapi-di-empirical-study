"""ReviewGate — authentication + role guards (single source of truth).

Mirrors the corpus hub chain: a request-level bearer token resolves to a
user, and guards enforce role membership. All strategies share this logic;
only *how* the connection and user are acquired differs.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

ADMIN = "admin"
EDITOR = "editor"
USER = "user"

# role sets per route auth level; "public" routes skip auth entirely
ROLES = {
    "public": [],
    "user": [USER, EDITOR, ADMIN],
    "editor": [EDITOR, ADMIN],
    "admin": [ADMIN],
}


def bearer_token(headers) -> str | None:
    auth = headers.get("Authorization") or headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth[len("Bearer "):].strip()


def lookup_user(conn, token: str | None) -> dict | None:
    if not token:
        return None
    row = conn.execute(
        "SELECT id, username, email, role, auth_token, suspended FROM users WHERE auth_token = ?",
        (token,),
    ).fetchone()
    return dict(row) if row else None


def require_role(user: dict | None, roles: list[str]) -> dict:
    """Return the user or raise HTTPException; shared by every strategy.

    Callers guarantee user is non-None (authentication done upstream).
    """
    if not user or user["role"] not in roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


def current_user(conn, request: Request) -> dict:
    """Authenticate from the request headers. Shared by S0/S2/S3."""
    user = lookup_user(conn, bearer_token(request.headers))
    if not user or user["suspended"]:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user