"""ReviewGate — S2 framework-native DI spine (only strategy S2 uses this).

Mirrors the corpus hub chain: get_db -> get_current_user -> require_* guards.
"""

from __future__ import annotations

from fastapi import Depends, Request

from . import auth as core_auth
from .db import get_db


def get_current_user(request: Request, conn=Depends(get_db)) -> dict:
    return core_auth.current_user(conn, request)


def require_editor(user: dict = Depends(get_current_user)) -> dict:
    return core_auth.require_role(user, core_auth.ROLES["editor"])


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    return core_auth.require_role(user, core_auth.ROLES["admin"])